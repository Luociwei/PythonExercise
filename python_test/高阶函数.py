#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/9 8:12 PM
#@Author: ciwei
#@File  : 高阶函数.py

def sum_num(a,b,f):
    return f(a) + f(b)

result1 = sum_num(-1,5,abs)

result2 = sum_num(1.1,1.4,round)

list1 = [1,2,3,4,5,6,7,8]
# map()
# def func(x):
#     return x ** 2

# result3 = map(func,list1)
# print(list(result3))

# result4 = map(lambda x : x**2,list1)
# print(list(result4))

# reduce()
# import functools
# def func(a,b):
#     return a+b
#
# result5 = functools.reduce(func,list1)
# result5 = functools.reduce(lambda a,b : a +b,list1)
# print(result5)

result6 =filter(lambda x : x %2==0,list1)
print(list(result6))





