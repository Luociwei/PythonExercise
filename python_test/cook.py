#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/7 10:43 PM
#@Author: ciwei
#@File  : cook.py

class SweetPotato():
    def __init__(self):
        self.cook_time =0
        self.cook_state = '生的'
        self.condiments = []
        self.condiments_str = ''

    def cook(self,time):

        self.cook_time += time
        if 0<= self.cook_time <3:
            self.cook_state = '生的'
        elif 3 <= self.cook_time < 5:
            self.cook_state = '半生不熟'

        elif 5 <= self.cook_time < 8:
            self.cook_state = '熟了'

        elif self.cook_time >= 8:
            self.cook_state = '烤糊了'


    def add_condiments(self,condiment):
        self.condiments.append(condiment)

    def get_condiments(self):
        
        for str in self.condiments:
            self.condiments_str = self.condiments_str + str + ','


    def __str__(self):
        print(self.condiments)
        return '这个地瓜的被烤过的时间是'+str(self.cook_time)+',状态:'+str(self.cook_state)+'调料:'+self.condiments_str
        # return '这个地瓜的被烤过的时间是%d,状态:%s,调料:%s'%(self.cook_time,self.cook_state,self.condiments)
        # return f'这个地瓜的被烤过的时间是{self.cook_time},状态:{self.cook_state},调料:{self.condiments}'



digua1 = SweetPotato()
digua1.cook(2)
digua1.add_condiments('辣椒')
print(digua1)

digua1.cook(2)
digua1.add_condiments('酱油')
print(digua1)