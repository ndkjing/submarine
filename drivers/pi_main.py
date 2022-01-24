import os
import sys
import threading
import pigpio
import time
import copy
import math

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from utils import log
from storage import save_data
from drivers import pi_softuart, com_data
import config
from moveControl.pathTrack import simple_pid
from drivers import com_data

logger = log.LogHandler('pi_log')


class PiMain:
    def __init__(self, single_list=None,func_list=None,logger_=None):
        if logger_ is not None:
            self.logger_obj = logger_
        else:
            self.logger_obj = logger
        # 串口数据收发对象
        if config.b_com_stc:
            self.stc_obj = self.get_com_obj(port=config.stc_port,
                                            baud=config.stc_baud,
                                            timeout=config.stc_timeout
                                            )
        self.b_receive_pos = False  # 收到新的姿态数据置位True
        self.pos_list = []  # 存放姿态角度  和经纬度
        self.b_receive_status = False  # 收到新的姿态数据置位True
        self.move = None  # 存放单片机收到运动 信息
        self.deep = None  # 存放姿态角度
        self.tem = None  # 存放姿态角度
        self.gps = None  # 存放姿态角度
        self.energy = None  # 存放姿态角度
        self.switch_list = None  # 存放姿态角度
        if config.is_single:
            self.single_list = single_list
            for index, s_i in enumerate(self.single_list):
                s_i.connect(func_list[index])
    # 获取串口对象
    @staticmethod
    def get_com_obj(port, baud, logger_=None, timeout=0.1):
        return com_data.ComData(
            port,
            baud,
            timeout=timeout,
            logger=logger_)

    @staticmethod
    def dump_energy_cal(adc):
        """
        输入ADC采集电压返回剩余电量
        电量与电压对应关系  各个阶段之内用线性函数计算  下表为实验数据
        电量     电压      6S电池     ADC采集数值
        100%----4.20V     25.2      3900
        90%-----4.06V     24.36     3755
        80%-----3.98V     23.88     3662
        70%-----3.92V     23.52     3561
        60%-----3.87V     23.22     3536
        50%-----3.82V     22.92     3535
        40%-----3.79V▲    22.74     3520
        30%-----3.77V     22.62     3432
        20%-----3.74V     22.44     3461
        0%-----3.7V       22.2      3318
        """
        adc_list = [3900, 3755, 3662, 3561, 3536, 3520, 3432, 3318]
        cap_list = [100, 90, 80, 70, 60, 40, 20, 1]
        # for index, adc_item in enumerate(adc_list):
        #     if index == 0:
        #         if adc > adc_item:
        #             return_cap = cap_list[index]
        #             break
        #     elif index == (len(adc_list) - 1):
        #         if adc < adc_item:
        #             return_cap = cap_list[index]
        #             break
        #     else:
        #         if adc_list[index + 1] < adc < adc_list[index]:
        #             return_cap = cap_list[index + 1] + (adc - adc_list[index + 1]) / (
        #                         adc_list[index] - adc_list[index + 1])
        if adc_list[0] <= adc:
            return_cap = cap_list[0]
        elif adc_list[1] <= adc < adc_list[0]:
            return_cap = cap_list[1] + (adc - adc_list[1]) * (cap_list[0] - cap_list[1]) / (
                    adc_list[0] - adc_list[1])
        elif adc_list[2] <= adc < adc_list[1]:
            return_cap = cap_list[2] + (adc - adc_list[2]) * (cap_list[1] - cap_list[2]) / (
                    adc_list[1] - adc_list[2])
        elif adc_list[3] <= adc < adc_list[2]:
            return_cap = cap_list[3] + (adc - adc_list[3]) * (cap_list[2] - cap_list[3]) / (
                    adc_list[2] - adc_list[3])
        elif adc_list[4] <= adc < adc_list[3]:
            return_cap = cap_list[4] + (adc - adc_list[4]) * (cap_list[3] - cap_list[4]) / (
                    adc_list[3] - adc_list[4])
        elif adc_list[5] <= adc < adc_list[4]:
            return_cap = cap_list[5] + (adc - adc_list[5]) * (cap_list[4] - cap_list[5]) / (
                    adc_list[4] - adc_list[5])
        elif adc_list[6] <= adc < adc_list[5]:
            return_cap = cap_list[6] + (adc - adc_list[6]) * (cap_list[5] - cap_list[6]) / (
                    adc_list[5] - adc_list[6])
        elif adc_list[7] <= adc < adc_list[6]:
            return_cap = cap_list[7] + (adc - adc_list[7]) * (cap_list[6] - cap_list[7]) / (
                    adc_list[6] - adc_list[7])
        else:
            return_cap = 1  # 小于最小电量置为1
        return int(return_cap)

    # 读取单片机数据 软串口
    def get_stc_data(self):
        """
        读取单片机数据
        :return:
        """
        while True:
            stc_data_read_dict = self.stc_obj.read_sub_data()
            print('stc_data_read_dict',stc_data_read_dict)
            if stc_data_read_dict and stc_data_read_dict.get('pos'):
                self.b_receive_pos = True
                self.pos_list = stc_data_read_dict.get('pos')
            if stc_data_read_dict and stc_data_read_dict.get('deep'):
                self.deep = stc_data_read_dict.get('deep')
                self.tem = stc_data_read_dict.get('tem')
            if stc_data_read_dict and stc_data_read_dict.get('switch'):
                self.switch_list = stc_data_read_dict.get('switch')
            if stc_data_read_dict and stc_data_read_dict.get('energy'):
                self.energy = stc_data_read_dict.get('energy')
            time.sleep(config.stc_timeout)


if __name__ == '__main__':
    pi_main_obj = PiMain()
    # if os.path.exists(config.b_com_stc):
    #     com_data_obj = com_data.ComData(
    #         config.stc_port,
    #         config.stc_baud,
    #         timeout=config.stc2pi_timeout,
    #         logger=logger)
    loop_change_pwm_thread = threading.Thread(target=pi_main_obj.loop_change_pwm)
    loop_change_pwm_thread.start()

    while True:
        try:
            # 按键后需要按回车才能生效
            print('w,a,s,d 为前后左右，q为停止\n'
                  'r 初始化电机\n'
                  'R lora遥控器数据读取，R 读一次  R1一直读\n'
                  't 控制抽水舵机和抽水\n'
                  'f  读取单片机数据\n'
                  'g  获取gps数据\n'
                  'j  读取rtk数据\n'
                  'h  单次获取罗盘数据  h1 持续读取罗盘数据求角速度\n'
                  'H  读取维特罗盘数据  校准 s  开始  e 结束  a 设置自动回传  i 初始化 其他为读取\n'
                  'z 退出\n'
                  'x  2.4g遥控器输入\n'
                  'c  声呐数据\n'
                  'b  毫米波数据\n'
                  'n  距离字典\n'
                  'A0 A1  关闭和开启水泵\n'
                  'B0 B1  关闭和开启舷灯\n'
                  'C0 C1  关闭和开启前面大灯\n'
                  'D0 D1  关闭和开启声光报警器\n'
                  'E0 E1 E2 E3 E4  状态灯\n'
                  )
            key_input = input('please input:')
            # 前 后 左 右 停止  右侧电机是反桨叶 左侧电机是正桨叶
            gear = None
            if key_input.startswith('w') or key_input.startswith(
                    'a') or key_input.startswith('s') or key_input.startswith('d'):
                try:
                    print(config.left_pwm_pin, )
                    if len(key_input) > 1:
                        gear = int(key_input[1])
                except Exception as e:
                    print({'error': e})
                    gear = None
            if key_input.startswith('w'):
                if gear is not None:
                    if gear >= 4:
                        gear = 4
                    print(1600 + 100 * gear, 1600 + 100 * gear)
                    pi_main_obj.forward(
                        1600 + 100 * gear, 1600 + 100 * gear)
                else:
                    pi_main_obj.forward()
            elif key_input.startswith('a'):
                if gear is not None:
                    if gear >= 4:
                        gear = 4
                    pi_main_obj.left(
                        1400 - 100 * gear, 1600 + 100 * gear)
                else:
                    pi_main_obj.left()
            elif key_input.startswith('s'):
                if gear is not None:
                    if gear >= 4:
                        gear = 4
                    print(1400 - 100 * gear, 1400 - 100 * gear)
                    pi_main_obj.backword(
                        1400 - 100 * gear, 1400 - 100 * gear)
                else:
                    pi_main_obj.backword()
            elif key_input.startswith('d'):
                if gear is not None:
                    if gear >= 4:
                        gear = 4
                    pi_main_obj.right(
                        1600 + 100 * gear, 1400 - 100 * gear)
                else:
                    pi_main_obj.right()
            elif key_input == 'q':
                pi_main_obj.stop()
            elif key_input.startswith('r'):
                pi_main_obj.init_motor()
            elif key_input.startswith('R'):
                if len(key_input) > 1 and key_input[1] == '1':
                    pi_main_obj.get_remote_control_data(debug=True)
                    pi_main_obj.check_remote_pwm()
                else:
                    pi_main_obj.remote_control_obj.read_remote_control(debug=True)
            elif key_input.startswith('t'):
                if len(key_input) > 1:
                    try:
                        pwm_deep = int(key_input[1:])
                        print('pwm_deep', pwm_deep)
                        pi_main_obj.set_draw_deep(deep_pwm=pwm_deep)
                    except Exception as e:
                        print('pwm_deep', e)
                else:
                    pi_main_obj.set_draw_deep(deep_pwm=config.min_deep_steer_pwm)  # 旋转舵机
                    time.sleep(3)
                    pi_main_obj.stc_obj.pin_stc_write('A1Z', debug=True)
                    time.sleep(5)
                    pi_main_obj.stc_obj.pin_stc_write('A0Z', debug=True)
                    pi_main_obj.set_draw_deep(deep_pwm=config.max_deep_steer_pwm)
                    time.sleep(3)
            # 获取读取单片机数据
            elif key_input.startswith('f'):
                stc_data = pi_main_obj.stc_obj.read_stc_data(debug=True)
                print('stc_data', stc_data)
            elif key_input.startswith('g'):
                gps_data = pi_main_obj.gps_obj.read_gps(debug=True)
                print('gps_data', gps_data)
            elif key_input.startswith('j'):
                gps_data = pi_main_obj.rtk_obj.read_gps(True)
                print('gps_data', gps_data)
                # rtk_data = .read_gps(debug=True)
                # print('rtk_data', rtk_data)
            elif key_input.startswith('h'):
                if len(key_input) == 1:
                    key_input = input('input:  C0  开始  C1 结束 其他为读取 >')
                    if key_input == 'C0':
                        theta_c = pi_main_obj.compass_obj.read_compass(send_data='C0', debug=True)
                    elif key_input == 'C1':
                        theta_c = pi_main_obj.compass_obj.read_compass(send_data='C1', debug=True)
                    else:
                        theta_c = pi_main_obj.compass_obj.read_compass(debug=True)
                    print('theta_c', theta_c)
                elif len(key_input) > 1 and int(key_input[1]) == 1:
                    pi_main_obj.get_compass_data(debug=True)
            elif key_input.startswith('H'):
                key_input = input('input:  清除磁偏角:s  开始校准:e 结束校准:a 设置自动回传  i 初始化 其他为读取 >')
                if key_input == 's':
                    theta = pi_main_obj.weite_compass_obj.read_weite_compass(send_data="AT+CALI=2\r\n",
                                                                             debug=True, )
                elif key_input == 'e':
                    theta = pi_main_obj.weite_compass_obj.read_weite_compass(send_data="AT+CALI=1\r\n",
                                                                             debug=True)
                elif key_input == 'a':
                    theta = pi_main_obj.weite_compass_obj.read_weite_compass(send_data="AT+CALI=0\r\n",
                                                                             debug=True)
                elif key_input == 'i':
                    theta = pi_main_obj.weite_compass_obj.read_weite_compass(send_data='41542B494E49540D0A',
                                                                             debug=True)
                elif len(key_input) > 1 and int(key_input[1]) == 1:
                    pi_main_obj.get_weite_compass_data(debug=False)
                else:
                    theta = pi_main_obj.weite_compass_obj.read_weite_compass(send_data=None,
                                                                             debug=False)
            elif key_input.startswith('x'):
                while True:
                    try:
                        time.sleep(0.1)
                        print('b_start_remote', pi_main_obj.b_start_remote)
                        print('channel_row_input_pwm', pi_main_obj.channel_row_input_pwm)
                        print('channel_col_input_pwm', pi_main_obj.channel_col_input_pwm)
                        if pi_main_obj.b_start_remote:
                            pi_main_obj.set_pwm(set_left_pwm=pi_main_obj.channel_row_input_pwm,
                                                set_right_pwm=pi_main_obj.channel_col_input_pwm)
                    except KeyboardInterrupt:
                        break
            # 读取毫米波雷达
            elif key_input.startswith('b'):
                millimeter_wave_data = pi_main_obj.millimeter_wave_obj.read_millimeter_wave(debug=True)
                print('millimeter_wave', millimeter_wave_data)
            elif key_input.startswith('n'):
                pi_main_obj.get_distance_dict_millimeter(debug=True)
            elif key_input.startswith('m'):
                pi_main_obj.init_motor()
            elif key_input[0] in ['A', 'B', 'C', 'D', 'E']:
                print('len(key_input)', len(key_input))
                if len(key_input) == 2 and key_input[1] in ['0', '1', '2', '3', '4']:
                    send_data = key_input + 'Z'
                    print('send_data', send_data)
                    if config.b_com_stc:
                        pi_main_obj.com_data_obj.send_data(send_data)
                        row_com_data_read = pi_main_obj.com_data_obj.readline()
                        print('row_com_data_read', row_com_data_read)
                    elif config.b_pin_stc:
                        pi_main_obj.stc_obj.send_stc_data(send_data)

            # TODO
            # 角度控制
            # 到达目标点控制
            # 简单走矩形区域
            # 退出
            elif key_input.startswith('Z'):
                pi_main_obj.turn_angular_velocity(debug=True)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print({'error': e})
            continue
