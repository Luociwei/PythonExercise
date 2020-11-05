
class Student(object):

    def __int__(self,name, gender, tel):


        self.name = name
        self.gender = gender
        self.tel = tel


    def __str__(self):
        return f'{self.name}, {self.gender}, {self.tel}'

    a = Student('louis', 'nan', '33')

    print(a)