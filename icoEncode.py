# _*_ coding: utf-8 _*_
"""
@Author : ylshao
@Date : 2022/7/1 14:50
@LastEditTime : 2022/7/1 14:50
@LastEditors : 2022/7/1 14:50
@vertion: V 0.1
"""
# base64转码，将转码后的文件存入icon.py中
import base64

with open("imageSee.ico", "rb") as open_icon:
    b64str = base64.b64encode(open_icon.read())
write_data = "img = %s" % b64str

with open("icon.py", "w+") as f:
    f.write(write_data)
