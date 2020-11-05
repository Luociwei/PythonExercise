#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 11:37 PM
#@Author: ciwei
#@File  : 元组字典拆包.py

#交换变量
a,b =1,2

a,b = b,a

print(a)
print(b)


def return_num():
    return 100,200

num1,num2 = return_num()
print(num2)
print(num1)


dict1 = {'name':'TOM','age':23}
a1,b1 = dict1
#对字典进行拆包，取出来的是key
print(a1)
print(b1)
print(dict1[a1])
print(dict1[b1])