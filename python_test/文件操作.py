#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/9 9:43 PM
#@Author: ciwei
#@File  : 文件操作.py

# f = open('test.txt','r')
# con_line = f.readline()
# print(con_line)
# con_lines = f.readlines()
# print(con_lines)
# for line in con_lines:
#     print(line)
#
# f.close()

f = open('test.txt','a+')

f.seek(0,0)#(偏移量,启始位置)0:开头 1:当前 2:结尾
con_line = f.readlines()
print(con_line)

f.seek(0,2)
f.write('fbsssssv'+'\n')
#
f.close()

#文件备份
# old_name = input('please input your file name: ')
# index = old_name.rfind('.')
# new_name = old_name[:index] + '备份' + old_name[index:]

#
# for num in range(1,3):
#     print(num)