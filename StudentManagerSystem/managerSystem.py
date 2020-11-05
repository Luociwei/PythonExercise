#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/6/1 9:58 上午
#@Author: ciwei
#@File  : managerSystem.py

from student import *


class StudentManager(object):
    def __init__(self):
        self.student_list = []


    def run(self):

        self.load_student()
        while True:

            self.show_memu()
            menu_num = int(input('please input your founction:'))
            if menu_num ==1:
                self.add_student()
            elif menu_num == 2:
                self.del_student()
            elif menu_num == 3:
                self.modify_student()
            elif menu_num == 4:
                self.search_student()
            elif menu_num == 5:
                self.show_student()
            elif menu_num == 6:
                self.save_student()
            elif menu_num == 7:
                break




    @staticmethod
    def show_memu():
        print('请选择如下功能: ')
        print('1:添加学员')
        print('2:删除学员')
        print('3:修改学员信息')
        print('4:查询学员信息')
        print('5:显示所有学员信息')
        print('6:保存学员信息')
        print('7:退出系统')



    def add_student(self):
        print('添加学员')
        name = input('ple input your name:')
        gender = input('ple input your gender:')
        tel = input('ple input your tel:')
        student = Student(name,gender,tel)

        self.student_list.append(student)

        print(self.student_list)

        print(student)



    def del_student(self):
        print('删除学员')
        del_name = input('ple input name you need to delete: ')
        for i in self.student_list:
            if del_name == i.name:
                self.student_list.remove(i)
                break

        else:
            print('not found')




    def modify_student(self):
        print('修改学员信息')
        modify_name = input('ple input name you need to modify: ')
        for i in self.student_list:
            if i.name == modify_name:
                i.name = input('ple input name: ')
                i.gender = input('ple input gender: ')
                i.tel = input('ple input tel: ')
                print(f'modify success,name:{i.name},gender:{i.gender},tel:{i.tel}')
                break

        else:
            print('not found')

    def search_student(self):
        print('查询学员信息')
        search_name = input('ple input name you need to search: ')
        for i in self.student_list:
            if i.name == search_name:

                # print('ssss:%s',i.name)

                print(f'search success,name:{i.name},gender:{i.gender},tel:{i.tel}')
                break

        else:
            print('not found')

    def show_student(self):
        print('显示所有学员信息')
        for i in self.student_list:
            print(f'{i.name}\t{i.gender}\t{i.tel}')


    def save_student(self):
        print('保存学员信息')
        f = open('student.data','w')
        new_list = [i.__dict__ for i in self.student_list]

        f.write(str(new_list))

        f.close()


    def load_student(self):
        print('加载学员信息')
        try:
            f = open('student.data','r')
        except:
            f = open('student.data','w')
        else:
            data = f.read()
            new_list = eval(data)
            self.student_list = [Student(i['name'],i['gender'],i['tel']) for i in new_list]
        finally:
            f.close()

