#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/8/8 8:51 PM
#@Author: ciwei
#@File  : 多态.py


class Dog(object):
    tooth =10
    def work(self):
        pass


class ArmyDog(Dog):
    def work(self):
        print('追击敌人...')


class DrugDog(Dog):
    def work(self):
        print('追击毒品...')



class Person(object):
    def work_with_dog(self,dog):
        dog.work()



Dog.tooth =20
# print(f'Dog tooth:{Dog.tooth}')

ad = ArmyDog()
ArmyDog.tooth =50
# print(f'ad tooth:{ad.tooth}')
ad.tooth = 30
# print(f'Dog tooth:{Dog.tooth}')
# print(f'ad tooth:{ad.tooth}')


dd = DrugDog()
print('dd tooth:%s'%(dd.tooth))

daqiu = Person()
daqiu.work_with_dog(ad)

daqiu.work_with_dog(dd)