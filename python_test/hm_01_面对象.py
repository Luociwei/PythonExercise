#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/5/29 3:45 下午
#@Author: ciwei
#@File  : hm_01_面对象.py

class Washer(object):

    def __init__(self,width,height):
        self.width = width
        self.height = height
        print(f'height is {self.height}--width is {self.width}')

    def wash(self):
        print(self)
        print('sssss')


haier1 = Washer(300,900)
print(haier1)
haier1.wash()


