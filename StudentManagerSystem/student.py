#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/6/1 9:58 上午
#@Author: ciwei
#@File  : student.py

class Student(object):
    def __init__(self,name,age,phone):
        self.name = name
        self.gender = age
        self.tel = phone


    def __str__(self):
        return f'{self.name},{self.gender},{self.tel}'



# aa = Student('louis','32','15766267019')
# print(aa)



