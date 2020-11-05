#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 10:57 PM
#@Author: ciwei
#@File  : 自定义异常.py

class ShortInputError(Exception):
    def __init__(self,length,min_length):
        self.length = length
        self.min_len = min_length


    def __str__(self):
        return f'你输入的长度是{self.length},不能小于{self.min_len}个字符'




if __name__== '__main__':

    try:
        con = input('ple input password:')
        if len(con) < 3:
            raise ShortInputError(len(con),3)

    except Exception as result:
        print(result)

    else:
        print('password no error')