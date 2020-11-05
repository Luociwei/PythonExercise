#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/7 11:34 PM
#@Author: ciwei
#@File  : 继承.py

class Master(object):
    def __init__(self):
        self.kongfu = '古法煎饼果子配方'

    def make_cake(self):
        print(f'运用{self.kongfu}制作煎饼果子')




class School(Master):
    def __init__(self):
        self.kongfu = '黑马煎饼果子配方'

    def make_cake(self):
        print(f'运用{self.kongfu}制作煎饼果子')
        super().__init__()
        super().make_cake()

  # 默认使用第一个父类的同名属性和方法
# class Prentice(School,Master):
#     pass


class Prentice(School):
    def __init__(self):
        self.kongfu = '独创煎饼果子配方'
        self.__money =200000#私有属性，子类无法调用


    def get_money(self):
        print(f'money is:{self.__money}')
        return self.__money

    def set_money(self,value):
        if self.__check_value(value):  # 在类的内部调用类的私有方法
            # self.__class__.__count = value
            self.__money = value

    def __check_value(self, value):   # 定义类的私有方法 检查参数
        if isinstance(value, int):
            return True

    def __infoPrint(self):
        print('私有方法，子类无法调用')

    def make_cake(self):
        print(f'运用{self.kongfu}制作煎饼果子')

    def make_old_cake(self):
        super().__init__()
        super().make_cake()






    # def make_master(self):
    #     Master.__init__(self)
    #     Master.make_cake(self)
    #
    #
    # def make_school(self):
    #     School.__init__(self)
    #     School.make_cake(self)


class Tusun(Prentice):
    pass




# daqiu = Prentice()
# print(daqiu.kongfu)
# daqiu.make_cake()
#
# print(Prentice.__mro__)



tusun = Tusun()
# tusun.make_cake()
tusun.make_old_cake()
tusun.set_money(1000000)
tusun.get_money()
# tusun.make_school()
# tusun.make_master()

