#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 10:39 PM
#@Author: ciwei
#@File  : 异常异常.py


try:
    print(num)
except Exception as result:
    print(result)
else:
    print('no error')
finally:
    print('perform next')



try:
    f = open('test.txt','r')

except Exception as result:
    f = open('test.txt','w')
else:
    print('no error')

finally:
    f.close()