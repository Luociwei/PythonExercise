#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/9 8:20 PM
#@Author: ciwei
#@File  : lambda.py

fn1 = lambda  a,b : a +b
print(fn1(1,2))

# 无参数
fn2 = lambda : 100
print(fn2())

# 默认参数
fn3 = lambda a,b,c=100 :a +b +c
print(fn3(10,20))

# 可变参数:*args 返回元组
fn4 = lambda  *args : args
print(fn4(10,20))
print(fn4(10,20,30))
print(fn4(10))


# 可变参数:**kargs 返回字典
fn5 = lambda  **kargs : kargs
print(fn5(name = 'python' , age =20))

#带判断
fn6 = lambda  a,b : a if a >b else b
print(fn6(100,300))


#列表数据排序
students = [{'name':'TOM','age':30},
            {'name':'louis','age':20},
            {'name':'jim','age':40}
            ]
students.sort(key=lambda x :x['age'])
print(students)
students.sort(key=lambda x :x['age'],reverse = True)
print(students)
