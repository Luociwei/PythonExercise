#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 10:20 PM
#@Author: ciwei
#@File  : 导入包.py

#导入方法一

#import mypackage.m_module1
#import mypackage.m_module2

#mypackage.m_module1.info_print1()
#mypackage.m_module2.info_print2()


#导入方法二:设置__init__.py文件里面的all列表,添加的是允许导入的模块

from mypackage import * #配合all列表一起使用

m_module1.info_print1()

