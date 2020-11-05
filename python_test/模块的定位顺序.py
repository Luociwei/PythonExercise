#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 9:53 PM
#@Author: ciwei
#@File  : 模块的定位顺序.py

#
# 模块搜索路径
# 当你导入一个模块，Python解析器对模块位置的搜索顺序是：
# 1、当前目录
# 2、如果不在当前目录，Python则搜索在shell变量PYTHONPATH下的每个目录。
# 由sys模块的sys.path方法来规定
#
# 因为sys.path返回的数据类型是列表
# 1、列表可以修改、我们导入的范围也可以通过修改sys.path这个列表获得暂时的修改。例如通过 sys.path.append()添加目录，导入额外目录的模块。
# 2、’列表是有序的，当搜索的过程当中，在第一个路径下搜索到了，就停止搜索。而且sys.path第一个路径是脚本的当前路径，
# 所以禁止大家将自己的脚本命名成模块的名称。因此需要注意的是：自己模块命名的时候不能和系统的模块名称相同。
#
# .pyc临时文件
# 为了提高加载模块的速度，python解释器会在__pycache__目录中下缓存每个模块编译后的版本，之后，再次被导入时，实际上导入的是这个.pyc的临时文件。



#1.自己的文件名不能和已有模块重复,如果重复导致模块无法使用 --random
# import random
# num = random.randint(1,5)

#2.当使用from xx import 功能 导入模块的功能的时候，如果功能名字重复，导入的时候
#定义或后导入的这个同名功能

# from time import sleep
#
# def sleep():
#     print('sleep ssss')
#
# sleep(20)



#3.注意不能给功能名赋值
import time
print(time)
print(time.sleep(33))
time =1
print(time)
