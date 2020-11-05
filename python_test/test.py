#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2020/6/1 1:30 下午
# @Author: ciwei
# @File  : test.py

import hm_01_面对象


haier1 = hm_01_面对象.Washer(300,400)
print(haier1)
haier1.wash()


import cook

digua = cook.SweetPotato()
digua.cook(2)
digua.add_condiments('辣椒')
print(digua)