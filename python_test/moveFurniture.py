#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/7 11:00 PM
#@Author: ciwei
#@File  : moveFurniture.py


class Furniture():
    def __init__(self,name,area):
        self.name = name
        self.area = area


class Home():
    def __init__(self,address,area):
        self.address = address
        self.area = area
        self.free_area = area
        self.furniture = []


    def __str__(self):
        return f'房子地理位置在{self.address},房屋面积是{self.area},剩余面积是{self.free_area},家具有{self.furniture}'

    def add_furniture(self,item):
        if item.area <= self.free_area:
            self.furniture.append(item.name)
            self.free_area -= item.area
        else:
            print(f'it is too big to not carry {item.name}')


bed = Furniture('safa',10)

jia1 = Home('sz',100)
print(jia1)

jia1.add_furniture(bed)
print(jia1)

ball = Furniture('ball_ground',101)
jia1.add_furniture(ball)
print(jia1)