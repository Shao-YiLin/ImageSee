# _*_ coding: utf-8 _*_
"""
@Author : ylshao
@Date : 2022/6/29 15:14
@LastEditTime : 2022/6/29 15:14
@LastEditors : 2022/6/29 15:14
@vertion: V 0.1
"""
import base64
import os
import sys
import time
import tkinter
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
from PIL import Image, ImageTk
import windnd
import PythonMagick

from icon import img

BOTTOM_HEIGHT = 80

WIDTH = 1000
HEIGHT = 800
PNG_TO_ICO = 0
ExtensionNameList = ["jpg", "jpeg", "png", "ico", "gif", "webp"]
ExtensionNameListAsterisk = []

for _li in ExtensionNameList:
    ExtensionNameListAsterisk.append("*." + _li)
FileTypeList = [('图片', ExtensionNameListAsterisk), ('All Files', '*')]


class rootWin:
    def __init__(self, root):
        # 缓存位移，每次加载图片或者图片回归中间都会变为0
        self.cacheY = 0
        self.cacheX = 0
        # 基础位移
        self.baseX = 0
        self.baseY = 0
        # 位移差值，作为图片显示位置的依据
        self.deltY = 0
        self.deltX = 0
        self.zoomMultiples = 1.0
        self.image = None
        self.window_height = WIDTH
        self.window_width = HEIGHT
        self.imageList = []
        self.imageIndex = 0
        self.img = None
        self.root = root
        self.winSet()
        self.menuPlace()
        self.canvas = tkinter.Canvas(self.root, width=self.window_width, height=self.window_height - BOTTOM_HEIGHT)  # 画布
        # 绑定事件动作
        self.canvas.bind('<Double-Button-1>',
                         lambda event: self.getImgPath(filedialog.askopenfilename(filetypes=FileTypeList)))
        self.canvas.bind('<B1-Motion>', self.lbMotionEvent)
        self.canvas.bind('<Button-1>', self.lbClickEvent)
        self.canvas.bind('<ButtonRelease-1>', self.lbReleaseEvent)
        windnd.hook_dropfiles(self.root, func=self.dragFile)
        self.root.bind('<Left>', lambda event: self.getPrevImg())
        self.root.bind('<Right>', lambda event: self.getNextImg())
        self.root.bind('<Configure>', self.root_resize)
        self.root.bind('<MouseWheel>', self.imgZoom)

        self.canvas.pack(side=TOP)
        self.buttonsPlace()

        # 创建图片详细信息标签
        self.imageDetailLabel = Label(self.root, text="", anchor=W, padx=10, pady=5)
        self.imageDetailLabel.pack(side=BOTTOM, fill=X)

        # 打开方式
        if len(sys.argv) >= 2:
            # print(sys.argv)
            self.getImgPath(sys.argv[1])

    # 初始化移动数据
    def moveInit(self):
        # 缓存位移，每次加载图片或者图片回归中间都会变为0
        self.cacheY = 0
        self.cacheX = 0
        # 基础位移
        self.baseX = 0
        self.baseY = 0
        # 位移差值，作为图片显示位置的依据
        self.deltY = 0
        self.deltX = 0

    # 显示图片事件
    def imageShow(self, LoadEn=True):
        if LoadEn:
            try:
                self.image = Image.open(self.imageList[self.imageIndex])  # 打开图片放到image中
            except IndexError:
                return
        if self.image is None:
            return
        self.moveInit()
        self.zoomMultiples = 1.0    # 重置缩放倍数
        w, h = self.image.size  # 获取image的长和宽
        if w < self.window_width and h < self.window_height:
            re_image = self.image
        else:
            _mLength = max(w, h)  # 取最大的一边作为缩放的基准
            if _mLength == w:
                self.zoomMultiples = self.window_width / _mLength  # 缩放倍数
            else:
                self.zoomMultiples = (self.window_height - 50) / _mLength  # 缩放倍数
            # print(self.zoomMultiples,_mLength,w,h,int(h * _mul))
            w1 = int(w * self.zoomMultiples)
            h1 = int(h * self.zoomMultiples)
            try:
                re_image = self.image.resize((w1, h1))
            except ValueError:
                return
        self.img = ImageTk.PhotoImage(re_image)  # 在canvas中展示图片
        self.canvas.create_image(self.window_width // 2, (self.window_height - BOTTOM_HEIGHT) // 2, anchor=CENTER, image=self.img)

        self.updateImageDetail(self.imageList[self.imageIndex])

    # 放大图片
    def imgAmplification(self, event):
        print(event.x, event.y, event.delta)
        if self.zoomMultiples <= 9.90:
            self.zoomMultiples += 0.10
        try:
            w, h = self.image.size  # 获取image的长和宽
            wl = int(w * self.zoomMultiples)
            hl = int(h * self.zoomMultiples)
            # try:
            re_image = self.image.resize((wl, hl))
            # except ValueError:
            #     return
            self.img = ImageTk.PhotoImage(re_image)  # 在canvas中展示图片
            self.canvas.create_image(self.window_width // 2 + self.deltX,
                                     (self.window_height - BOTTOM_HEIGHT) // 2 + self.deltY,
                                     anchor=CENTER,
                                     image=self.img)
        except AttributeError:
            pass

    # 缩小图片
    def imgNarrow(self, event):
        print(event.x, event.y, event.delta)
        if self.zoomMultiples >= 0.20:
            self.zoomMultiples -= 0.10
        try:
            w, h = self.image.size  # 获取image的长和宽
            wl = int(w * self.zoomMultiples)
            hl = int(h * self.zoomMultiples)
            # try:
            re_image = self.image.resize((wl, hl))
            # except ValueError:
            #     return
            self.img = ImageTk.PhotoImage(re_image)  # 在canvas中展示图片
            self.canvas.create_image(self.window_width // 2 + self.deltX,
                                     (self.window_height - BOTTOM_HEIGHT) // 2 + self.deltY,
                                     anchor=CENTER,
                                     image=self.img)
        except AttributeError:
            pass

    # 鼠标左键点击事件
    def lbClickEvent(self, event):
        self.baseX = event.x
        self.baseY = event.y
        print(event.x, event.y)

    # 鼠标左键释放事件
    def lbReleaseEvent(self, event):
        self.cacheX = self.deltX
        self.cacheY = self.deltY

    # 鼠标左键拖动事件
    def lbMotionEvent(self, event):
        self.canvas.delete('all')
        self.deltX = self.cacheX + event.x - self.baseX
        self.deltY = self.cacheY + event.y - self.baseY
        print("delt:", self.deltX, self.deltY)
        self.canvas.create_image(self.window_width // 2 + self.deltX, (self.window_height - BOTTOM_HEIGHT) // 2 + self.deltY,
                                 anchor=CENTER, image=self.img)

    # 滚轮缩放事件
    def imgZoom(self, event):
        if event.delta > 0:
            self.imgAmplification(event)
        else:
            self.imgNarrow(event)

    # 改变窗口大小事件
    def root_resize(self, event=None):
        if self.window_width != self.root.winfo_width() or self.window_height != self.root.winfo_height():
            if self.window_width != self.root.winfo_width():
                self.window_width = self.root.winfo_width()
            if self.window_height != self.root.winfo_height():
                self.window_height = self.root.winfo_height()
        self.canvas.config(width=self.window_width, height=self.window_height - BOTTOM_HEIGHT)
        self.imageShow(LoadEn=False)

    # 图片拖动到窗口事件
    def dragFile(self, file):
        # 只接受第一张照片
        filePath = file[0].decode('gbk')
        self.getImgPath(filePath)

    def updataImgList(self, basePath):
        if basePath[-1] != '/':
            basePath += '/'
        imgList = os.listdir(basePath)
        self.imageList.clear()
        for li in imgList:
            extensionName = li[li.rfind('.') + 1:]
            if extensionName in ExtensionNameList:
                self.imageList.append(basePath + li)
                # print(basePath + li)

    # 获取文件路径
    def getFilePath(self, file):
        basePath = file
        if basePath == "":
            return
        # print(self.Filepath[:self.Filepath.rfind('/')+1])
        self.updataImgList(basePath)
        self.imageIndex = 0
        self.imageShow()

    # 获取图片路径
    def getImgPath(self, file):
        filePath = file
        if filePath == "":
            return
        if filePath[filePath.rfind('.') + 1:] not in ExtensionNameList:
            tkinter.messagebox.showerror("错误", "文件格式不正确")
            return
        # print(self.Filepath[:self.Filepath.rfind('/')+1])
        filePath = filePath.replace('\\', '/')
        basePath = filePath[:filePath.rfind('/') + 1]
        self.updataImgList(basePath)
        self.imageIndex = self.imageList.index(basePath + filePath[filePath.rfind('/') + 1:])
        self.imageShow()

    # 下一张图片
    def getNextImg(self):
        self.imageIndex += 1
        if self.imageIndex > len(self.imageList) - 1:
            self.imageIndex = 0
        # 更新索引
        filePath = self.imageList[self.imageIndex].replace('\\', '/')
        basePath = filePath[:filePath.rfind('/') + 1]
        self.updataImgList(basePath)
        self.imageShow()

    # 上一张图片
    def getPrevImg(self):
        self.imageIndex -= 1
        if self.imageIndex < 0:
            self.imageIndex = len(self.imageList) - 1
        # 更新索引
        filePath = self.imageList[self.imageIndex].replace('\\', '/')
        basePath = filePath[:filePath.rfind('/') + 1]
        self.updataImgList(basePath)
        self.imageShow()

    # 删除图片
    def delThisImg(self):
        # 删除图片
        if len(self.imageList) == 0:
            return

        # 获取当前显示的图片路径
        currentImagePath = self.imageList[self.imageIndex]

        # 从图片列表中移除已删除的图片
        self.imageList.remove(currentImagePath)

        # 更新图片索引
        if self.imageIndex >= len(self.imageList):
            self.imageIndex = len(self.imageList) - 1

        # 如果还有剩余图片，显示下一张图片
        if len(self.imageList) > 0:
            self.imageShow()
        else:
            # 如果没有剩余图片，清空显示区域
            self.clearImageShow()

        # 删除当前图片
        try:
            os.remove(currentImagePath)
            # tkinter.messagebox.showinfo("成功", "图片删除成功")
        except OSError:
            tkinter.messagebox.showerror("错误", "图片删除失败")
            return
        # 更新索引
        filePath = self.imageList[self.imageIndex].replace('\\', '/')
        basePath = filePath[:filePath.rfind('/') + 1]
        self.updataImgList(basePath)

    # 格式转换
    def formatConversion(self, species, path):
        # 获取图片格式
        imgFormat = path[path.rfind(".") + 1:]
        if species == PNG_TO_ICO:
            if imgFormat != ".ico":
                path = path + ".ico"
            # 如果当前没有图片
            if len(self.imageList) == 0:
                return
            print("png to ico"+path)
            icoImg = PythonMagick.Image(self.imageList[self.imageIndex])
            icoImg.sample('128x128')
            icoImg.write(path)

    def clearImageShow(self):
        # 清空图片列表和索引
        self.imageList = []
        self.imageIndex = 0

        # 清空图片显示区域
        self.canvas.delete("all")

    # 更新图片详细信息
    def updateImageDetail(self, image):
        width, height = self.image.size
        self.imageDetailLabel.config(
            text="图片名称: {}\t图片尺寸: {}x{}".format(image, width, height))

    # 菜单
    def menuPlace(self):
        main_menu = Menu(self.root)
        # 新增命令菜单项，使用 add_command() 实现
        fileMenu = Menu(main_menu, tearoff=False)
        fileMenu.add_command(label="打开", accelerator="Ctrl+O",
                             command=lambda: self.getImgPath(filedialog.askopenfilename(filetypes=FileTypeList)))
        fileMenu.add_command(label="打开文件夹", accelerator="Ctrl+F",
                             command=lambda: self.getFilePath(filedialog.askdirectory()))

        self.root.bind("<Control-O>", lambda event: self.getImgPath(filedialog.askopenfilename(filetypes=FileTypeList)))
        self.root.bind("<Control-o>", lambda event: self.getImgPath(filedialog.askopenfilename(filetypes=FileTypeList)))
        self.root.bind("<Control-F>", lambda event: self.getFilePath(filedialog.askdirectory()))
        self.root.bind("<Control-f>", lambda event: self.getFilePath(filedialog.askdirectory()))

        conversionMenu = Menu(main_menu, tearoff=False)
        conversionMenu.add_command(label="->ICO",
                                   command=lambda: self.formatConversion(PNG_TO_ICO, filedialog.asksaveasfilename(filetypes=[("图标", "*.ico")])))

        main_menu.add_cascade(label="文件", menu=fileMenu)
        main_menu.add_cascade(label="格式转换", menu=conversionMenu)
        self.root.config(menu=main_menu)

    # 按钮
    def buttonsPlace(self):
        photo = PhotoImage(file=r".\img\last.png")
        self.photoLast = photo.subsample(6, 6)

        photo = PhotoImage(file=r".\img\del.png")
        self.photoDel = photo.subsample(10, 10)

        photo = PhotoImage(file=r".\img\next.png")
        self.photoNext = photo.subsample(6, 6)

        buttonFrame = Frame(self.root)
        buttonFrame.pack(side=TOP, pady=10)
        prevButton = Button(buttonFrame, image=self.photoLast, height=25, width=30, command=self.getPrevImg)
        prevButton.pack(side=LEFT, padx=5)
        delButton = Button(buttonFrame, image=self.photoDel, height=25, width=30, command=self.delThisImg)
        delButton.pack(side=LEFT, padx=5)
        lastButton = Button(buttonFrame, image=self.photoNext, height=25, width=30, command=self.getNextImg)
        lastButton.pack(side=LEFT, padx=5)

    # 窗口设置
    def winLocation(self, width, height):
        # 屏幕宽度以及屏幕高度
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        dialog_width = width
        dialog_height = height
        self.root.geometry("%dx%d+%d+%d" % (
            dialog_width, dialog_height, (screenwidth - dialog_width) / 2, (screenheight - dialog_height) / 2))

    def winSet(self):
        # 绘制窗口，设置基本信息
        self.root.attributes("-disabled", 1)
        self.root.attributes("-disabled", 0)
        self.winLocation(1000, 800)
        self.icoEncode()
        self.root.title("图片查看器")
        self.root.minsize(WIDTH // 3, HEIGHT // 3)

    def icoEncode(self):
        # 读取base64转码后的数据，并设置压缩图标
        path = sys.argv[0][:sys.argv[0].rfind('\\') + 1] + "imageSee.ico"
        with open(path, "wb+") as picture:
            picture.write(base64.b64decode(img))
        try:
            self.root.iconbitmap(path)
        except BaseException:
            print(sys.argv[0], path)
        # os.remove(path)

