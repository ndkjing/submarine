import demo1
from blinker import signal

class class1:

    def __init__(self):
        self.s1 = signal('king1')
        self.s2 = signal('king2')
        self.s3 = signal('king3')
        self.obj = demo1.SingleClass([self.s1,self.s2,self.s3],[self.animal_1,self.animal_2,self.animal_3])


    def animal_1(self, args):
        print('class1',args,type(args))
    def animal_2(self, args):
        print('class2',args,type(args))
    def animal_3(self, args):
        print('class3',args,type(args))
# 定义一个信号

c1 = class1()