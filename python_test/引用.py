#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/9 9:45 AM
#@Author: ciwei
#@File  : 引用.py


# 不可变类型:整型/浮点型/字符串/元组，可变类型:列表/字典/集合

a =1
b=a
print(b)

print(id(a))
print(id(b))

a=2
print(b)
print(id(a))
print(id(b))
#
# print(id(a))
# print(id(b))

# aa = [10,20]
# bb = aa
# print(bb)
#
# print(id(aa))
# print(id(bb))
#
#
# aa.append(30)
# print(aa)
# print(bb)
# print(id(aa))
# print(id(bb))



# def test1(a):
#     print(a)
#     print(id(a))
#
#     a+=a
#     print(a)
#     print(id(a))
#
#
# b = 100
#
# test1(b)
#
# c = [11,22]
# test1(c)
