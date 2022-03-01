"""
管理数据收发
"""
from blinker import signal
import time
import json
import copy
import os
import math
import enum
import numpy as np
import random
from collections import deque
from utils import check_network
from messageBus import data_define
from externalConnect import server_data
from utils.log import LogHandler
from drivers import audios_manager, pi_main
import config


class DataManager:
    def __init__(self):
        self.data_define_obj = data_define.DataDefine()
        # 日志对象
        self.logger = LogHandler('data_manager_log', level=20)
        self.data_save_logger = LogHandler('data_save_log', level=20)
        self.com_data_read_logger = LogHandler('com_data_read_logger', level=20)
        self.com_data_send_logger = LogHandler('com_data_send_logger', level=20)
        self.server_log = LogHandler('server_data', level=20)
        self.gps_log = LogHandler('gps_log', level=20)
        # mqtt服务器数据收发对象
        self.server_data_obj = server_data.ServerData(self.server_log, topics=self.data_define_obj.topics)
        self.pi_main_obj = None

        if config.is_single:
            # 定义一个信号
            self.single_move = signal('single_move')
            self.single_line = signal('single_line')
        if config.current_platform == config.CurrentPlatform.pi:
            if config.is_single:
                self.pi_main_obj = pi_main.PiMain([self.single_move, self.single_line],
                                                  [self.send_stc_motor_single, self.send_stc_motor_single])
            else:
                self.pi_main_obj = pi_main.PiMain()

    # 发送给单片机控制电机数据
    def send_stc_motor_single(self, args):
        delay_time = 0.35
        if self.server_data_obj.mqtt_send_get_obj.control_move_direction != 0 and \
                time.time() - self.server_data_obj.mqtt_send_get_obj.control_move_time < delay_time:
            motor_list = DataManager.direction_to_motor(
                self.server_data_obj.mqtt_send_get_obj.control_move_direction)
            self.pi_main_obj.stc_obj.send_data("P%d,%dZ\n" % (motor_list[0], motor_list[1]))
            print("P%d,%dZ\n" % (motor_list[0], motor_list[1]))
            time.sleep(0.01)
            self.pi_main_obj.stc_obj.send_data("S%d,%dZ\n" % (motor_list[2], motor_list[3]))
            time.sleep(0.01)
        elif time.time() - self.server_data_obj.mqtt_send_get_obj.control_move_time > delay_time:
            self.server_data_obj.mqtt_send_get_obj.control_move_direction = 0
        if self.server_data_obj.mqtt_send_get_obj.control_move_direction == 0:
            self.pi_main_obj.stc_obj.send_data("S3,3Z\n")
            time.sleep(0.01)
            self.pi_main_obj.stc_obj.send_data("P1500,1500Z\n")
        if self.server_data_obj.mqtt_send_get_obj.line != 3 and \
                time.time() - self.server_data_obj.mqtt_send_get_obj.line_time < delay_time:
            self.pi_main_obj.stc_obj.send_data("L%dZ\n" % self.server_data_obj.mqtt_send_get_obj.line)
            time.sleep(0.01)
        elif time.time() - self.server_data_obj.mqtt_send_get_obj.line_time > delay_time:
            self.server_data_obj.mqtt_send_get_obj.line = 3
        if self.server_data_obj.mqtt_send_get_obj.line == 3:
            self.pi_main_obj.stc_obj.send_data("L3Z\n")

    @staticmethod
    def direction_to_motor(move_direction):
        """
        接受控制方向输出电机控制pwm波值和步进电机运动方向
        """
        pwm1 = 1500
        pwm2 = 1500
        step_motor1 = 3
        step_motor2 = 3
        if move_direction == 1:
            pwm1 = 1800
        elif move_direction == 2:
            pwm1 = 1250
        elif move_direction == 3:
            pwm2 = 1700
        elif move_direction == 4:
            pwm2 = 1300
        elif move_direction == 5:
            step_motor1 = 1
            step_motor2 = 1
        elif move_direction == 6:
            step_motor1 = 2
            step_motor2 = 2
        return [pwm1, pwm2, step_motor1, step_motor2]

    # 发送给单片机控制电机数据
    def send_stc_motor(self):
        delay_time = 0.35
        while True:
            time.sleep(0.01)
            if not config.home_debug and self.pi_main_obj:
                if self.server_data_obj.mqtt_send_get_obj.control_move_direction != 0 and \
                        time.time() - self.server_data_obj.mqtt_send_get_obj.control_move_time < delay_time:
                    motor_list = DataManager.direction_to_motor(
                        self.server_data_obj.mqtt_send_get_obj.control_move_direction)
                    self.pi_main_obj.stc_obj.send_data("P%d,%dZ\n" % (motor_list[0], motor_list[1]))
                    print("P%d,%dZ\n" % (motor_list[0], motor_list[1]))
                    time.sleep(0.01)
                    self.pi_main_obj.stc_obj.send_data("S%d,%dZ\n" % (motor_list[2], motor_list[3]))
                    time.sleep(0.01)
                elif time.time() - self.server_data_obj.mqtt_send_get_obj.control_move_time > delay_time:
                    self.server_data_obj.mqtt_send_get_obj.control_move_direction = 0
                if self.server_data_obj.mqtt_send_get_obj.control_move_direction == 0:
                    self.pi_main_obj.stc_obj.send_data("S3,3Z\n")
                    time.sleep(0.01)
                    self.pi_main_obj.stc_obj.send_data("P1500,1500Z\n")
                if self.server_data_obj.mqtt_send_get_obj.line != 3 and \
                        time.time() - self.server_data_obj.mqtt_send_get_obj.line_time < delay_time:
                    self.pi_main_obj.stc_obj.send_data("L%dZ\n" % self.server_data_obj.mqtt_send_get_obj.line)
                    time.sleep(0.01)
                elif time.time() - self.server_data_obj.mqtt_send_get_obj.line_time > delay_time:
                    self.server_data_obj.mqtt_send_get_obj.line = 3
                if self.server_data_obj.mqtt_send_get_obj.line == 3:
                    self.pi_main_obj.stc_obj.send_data("L3Z\n")

    # 发送给服务器数据必须使用线程发送mqtt状态数据
    def send_mqtt_status_data(self):
        while True:
            time.sleep(config.pi2mqtt_interval)
            if not config.home_debug and self.pi_main_obj:
                status_data = {
                    'move': str(self.server_data_obj.mqtt_send_get_obj.control_move_direction),
                    "gps": "0",
                }
                if self.pi_main_obj.pos_list == 5 and self.pi_main_obj.pos_list[3] > 10 and self.pi_main_obj.pos_list[
                    4] > 10:
                    status_data.update({'gps': "1"})
                if self.pi_main_obj.deep:
                    status_data.update({"deep": str(self.pi_main_obj.deep)})
                else:
                    status_data.update({"deep": ""})
                if self.pi_main_obj.tem:
                    status_data.update({"tem": str(self.pi_main_obj.tem)})
                else:
                    status_data.update({"tem": ""})
                if self.pi_main_obj.energy:
                    status_data.update({"energy": str(self.pi_main_obj.energy)})
                else:
                    status_data.update({"energy": ""})
            else:
                status_data = {
                    "move": "1",
                    "deep": "0.5",
                    "tem": "19.7",
                    "gps": "[115.321321,30.673213]",
                    "energy": "67.3"
                }
            # 向mqtt发送数据
            self.send(method='mqtt', topic='status_data_%s' % config.ship_code, data=json.dumps(status_data),
                      qos=0)
            if time.time() % 5 < 1:
                self.logger.info({'status_data_': json.dumps(status_data)})

    # 高频率发送姿态数据
    def send_high_f_status_data(self):
        while 1:
            time.sleep(config.high_f_pi2mqtt_interval)
            # 判断数据是否有修改过
            # print('self.pi_main_obj.b_receive_pos', self.pi_main_obj.b_receive_pos)
            if not config.home_debug and self.pi_main_obj and self.pi_main_obj.b_receive_pos:
                high_f_status_data = {
                    "pos_r": self.pi_main_obj.pos_list[0],
                    "pos_p": self.pi_main_obj.pos_list[1],
                    "pos_y": self.pi_main_obj.pos_list[2],
                }
                self.send(method='mqtt', topic='high_f_status_data_%s' % config.ship_code,
                          data=json.dumps(high_f_status_data),
                          qos=0)
                self.pi_main_obj.b_receive_pos = False
                if time.time() % 5 < 1:
                    self.logger.info({'high_f_status_data': json.dumps(high_f_status_data)})

    # 发送数据
    def send(self, method, data, topic='test', qos=0, http_type='POST', url='', parm_type=1):
        """
        :param url:
        :param http_type:
        :param qos:
        :param topic:
        :param data: 发送数据
        :param method 获取数据方式　http mqtt com
        """
        assert method in ['http', 'mqtt', 'com'], 'method error not in http mqtt com'
        if method == 'http':
            return_data = self.server_data_obj.send_server_http_data(http_type, data, url, parm_type=parm_type)
            if not return_data:
                return False
            self.logger.info({'请求 url': url, 'status_code': return_data.status_code})
            # 如果是POST返回的数据，添加数据到地图数据保存文件中
            if http_type == 'POST' and r'map/save' in url:
                content_data = json.loads(return_data.content)
                self.logger.info({'map/save content_data success': content_data["success"]})
                if not content_data["success"]:
                    self.logger.error('POST请求发送地图数据失败')
                # POST 返回湖泊ID
                pool_id = content_data['data']['id']
                return pool_id
            # http发送检测数据给服务器
            elif http_type == 'POST' and r'data/save' in url:
                content_data = json.loads(return_data.content)
                self.logger.debug({'data/save content_data success': content_data["success"]})
                if not content_data["success"]:
                    self.logger.error('POST发送检测请求失败')
            # http发送采样数据给服务器
            elif http_type == 'POST' and r'data/sampling' in url:
                content_data = json.loads(return_data.content)
                self.logger.debug({'data/save content_data success': content_data["success"]})
                if not content_data["success"]:
                    self.logger.error('POST发送采样请求失败')
            elif http_type == 'GET' and r'device/binding' in url:
                content_data = json.loads(return_data.content)
                if not content_data["success"]:
                    self.logger.error('GET请求失败')
                save_data_binding = content_data["data"]
                return save_data_binding
            elif http_type == 'GET' and r'task/getOne' in url:
                if return_data:
                    content_data = json.loads(return_data.content)
                    if not content_data["success"]:
                        self.logger.info({'content_data': content_data})
                        self.logger.error('task GET请求失败')
                    task_data = content_data["data"]
                    self.logger.info({'content_data': content_data})
                    return task_data
                else:
                    return
            elif http_type == 'POST' and r'task/upDataTask' in url:
                if return_data:
                    content_data = json.loads(return_data.content)
                    self.logger.info({'content_data': content_data})
                    if not content_data["success"]:
                        self.logger.error('upDataTask请求失败')
                    else:
                        return True
            elif http_type == 'POST' and r'task/delTask' in url:
                if return_data:
                    content_data = json.loads(return_data.content)
                    self.logger.info({'content_data': content_data})
                    if not content_data["success"]:
                        self.logger.error('delTask请求失败')
                    else:
                        return True
            elif http_type == 'GET' and r'mileage/getOne' in url:
                if return_data:
                    content_data = json.loads(return_data.content)
                    if not content_data["success"]:
                        self.logger.error('mileage/getOne GET请求失败')
                    task_data = content_data.get("data")
                    if task_data:
                        self.logger.info({'mileage/getOne': task_data.get('items')})
                        return task_data.get('items')
                    return False
                else:
                    return False
            else:
                # 如果是GET请求，返回所有数据的列表
                content_data = json.loads(return_data.content)
                if not content_data["success"]:
                    self.logger.error('GET请求失败')
                else:
                    return True
        elif method == 'mqtt':
            self.server_data_obj.send_server_mqtt_data(data=data, topic=topic, qos=qos)

    def connect_mqtt_server(self):
        while True:
            if not self.server_data_obj.mqtt_send_get_obj.is_connected:
                self.server_data_obj.mqtt_send_get_obj.mqtt_connect()
            time.sleep(5)

    # 检测网络延时
    def check_ping_delay(self):
        # 检查网络
        while True:
            time.sleep(10)
            if not self.server_data_obj.mqtt_send_get_obj.is_connected:
                continue
            ping = check_network.get_ping_delay()
            if not check_network.get_ping_delay():
                self.logger.error('当前无网络信号')
                self.server_data_obj.mqtt_send_get_obj.is_connected = 0
