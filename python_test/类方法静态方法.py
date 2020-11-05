#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 9:04 PM
#@Author: ciwei
#@File  : 类方法静态方法.py

class Dog(object):
    __tooth =10

    @classmethod
    def get_tooth(cls):
        return cls.__tooth


    @staticmethod
    def info_print():
        print('静态方法,不需要使用实例对象和类属性和方法')

