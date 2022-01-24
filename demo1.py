from blinker import signal


class SingleClass:
    def __init__(self,s,animal_one):
        # 定义一个信号

        self.s = s
        # 信号注册一个接收者
        for index,s_i in enumerate(self.s):
            s_i.connect(animal_one[index])
        for index, s_i in enumerate(self.s):
            s_i.send({"move":index})

if "__main__" == __name__:
    pass
    # 发送信号
    # s.send()
