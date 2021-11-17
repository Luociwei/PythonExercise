#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 11:21 PM
#@Author: ciwei
#@File  : 函数参数.py


def user_info(name,age,gender):
    print('您的名字是%s,年龄是%s,性别是%s'%(name,age,gender))


#关键字参数
user_info('louis',age = 32,gender='boy')
user_info('louis',gender='boy',age = 33)


#缺省参数
def user_info1(name='TOM',age=23,gender='BOY'):
    print('您的名字是%s,年龄是%s,性别是'%(name,age,gender))

user_info1()
user_info1('jim')


#不定长参数也叫可变参数--返回元组
def user_info2(*args):
    print(args)

user_info2()
user_info2('1','2','3')


def user_info3(**kargs):
    print(kargs)

user_info3()
user_info3(name='1',age='2',id='3')