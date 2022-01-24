"""
网络数据收发
"""
import config
from utils import poweroff_restart
import copy
import paho.mqtt.client as mqtt
import time
import json
import requests


class ServerData:
    def __init__(self, logger,
                 topics):
        self.logger = logger
        self.topics = topics
        self.mqtt_send_get_obj = MqttSendGet(self.logger, topics=topics)

    # 发送数据到服务器http
    def send_server_http_data(self, request_type, data, url, parm_type=1):
        """
        @param request_type:
        @param data:
        @param url:
        @param parm_type: 1 data 方式  2 params 方式
        @return:
        """
        try:
            # 请求头设置
            payload_header = {
                'Content-Type': 'application/json',
            }
            assert request_type in ['POST', 'GET']
            # self.logger.info(url)
            if request_type == 'POST':
                if parm_type == 1:
                    dump_json_data = json.dumps(data)
                    return_data = requests.post(
                        url=url, data=dump_json_data, headers=payload_header, timeout=8)
                else:
                    if isinstance(data, dict):
                        dump_json_data = data
                    else:
                        dump_json_data = json.dumps(data)
                    return_data = requests.post(
                        url=url, params=dump_json_data, headers=payload_header, timeout=8)
            else:
                if data:
                    dump_json_data = json.dumps(data)
                    return_data = requests.get(url=url, params=dump_json_data, timeout=8)
                else:
                    return_data = requests.get(url=url, timeout=8)
            return return_data
        except Exception as e:
            return None

    # 发送数据到服务器mqtt
    def send_server_mqtt_data(self, topic='test', data="", qos=1):
        self.mqtt_send_get_obj.publish_topic(topic=topic, data=data, qos=qos)


def send_http_log(request_type, data, url, parm_type=1):
    assert request_type in ['POST', 'GET']
    payload_header = {
        'Content-Type': 'application/json',
    }
    try:
        if request_type == 'POST':
            if parm_type == 1:
                dump_json_data = json.dumps(data)
                return_data = requests.post(
                    url=url, data=dump_json_data, headers=payload_header, timeout=5)
                print('return_data', return_data)
            else:
                if isinstance(data, dict):
                    dump_json_data = data
                else:
                    dump_json_data = json.dumps(data)
                return_data = requests.post(
                    url=url, params=dump_json_data, headers=payload_header, timeout=5)
        else:
            if data:
                dump_json_data = json.dumps(data)
                return_data = requests.get(url=url, params=dump_json_data, timeout=5)
            else:
                return_data = requests.get(url=url, timeout=5)
        return return_data
    except Exception as e:
        return None

    # class HttpSendGet:
    #     """
    #     处理ｊｓｏｎ数据收发
    #     """
    #
    #     def __init__(self, base_url='127.0.0.1'):
    #         self.base_url = base_url
    #
    #     def send_data(self, uri, data):
    #         """
    #         :param uri 发送接口uri
    #         :param data  需要发送数据
    #         """
    #         send_url = self.base_url + uri
    #         response = requests.post(send_url, data=data)
    #
    #     def get_data(self, uri):
    #         """
    #         :param uri 发送接口uri
    #         """
    #         get_url = self.base_url + uri
    #         response = requests.get(uri)


# class HttpSendGet:
#     """
#     处理ｊｓｏｎ数据收发
#     """
#
#     def __init__(self, base_url='127.0.0.1'):
#         self.base_url = base_url
#
#     def send_data(self, uri, data):
#         """
#         :param uri 发送接口uri
#         :param data  需要发送数据
#         """
#         send_url = self.base_url + uri
#         response = requests.post(send_url, data=data)
#
#     def get_data(self, uri):
#         """
#         :param uri 发送接口uri
#         """
#         get_url = self.base_url + uri
#         response = requests.get(uri)


class MqttSendGet:
    """
    处理mqtt数据收发
    """

    def __init__(
            self,
            logger,
            topics,
            mqtt_host=config.mqtt_host,
            mqtt_port=config.mqtt_port,
            client_id=config.ship_code

    ):
        self.topics = topics
        self.logger = logger
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        if config.current_platform == config.CurrentPlatform.pi:
            client_id = client_id + '_pi'
            self.mqtt_user = 'linux_pi'
        elif config.current_platform == config.CurrentPlatform.linux:
            client_id = client_id + 'linux'
            self.mqtt_user = 'linux'
        else:
            client_id = client_id + 'windows'
            self.mqtt_user = 'windows'
        self.mqtt_passwd = 'public'
        self.mqtt_client = mqtt.Client(client_id=client_id)
        self.mqtt_client.username_pw_set(self.mqtt_user, password=self.mqtt_passwd)
        self.mqtt_client.on_connect = self.on_connect_callback
        self.mqtt_client.on_publish = self.on_publish_callback
        # self.mqtt_client.on_subscribe = self.on_message_come
        self.mqtt_client.on_message = self.on_message_callback
        # 停止0
        # 前进1
        # 后退2
        # 左转3
        # 右转4
        # 上升5
        # 下降6
        self.control_move_direction = 0  # 运动控制方向
        self.control_move_time = 0  # 记录收到值的时间
        self.line = 3  # 收放线控制  1 收  2 放  3停止
        self.line_time = 0  # 记录收到控制线时间
        # 是否接受到电脑端点击过任何按键
        self.b_receive_mqtt = False
        self.is_connected = 0  # mqtt是否已经连接上

    # 连接MQTT服务器
    def mqtt_connect(self):
        if not self.is_connected:
            try:
                self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 30)
                # 开启接收循环，直到程序终止
                self.mqtt_client.loop_start()
                self.is_connected = 1
                # 启动后自动订阅话题
                for topic_, qos_ in self.topics:
                    self.subscribe_topic(topic=topic_, qos=qos_)
            except TimeoutError:
                return
            except Exception as e:
                print('mqtt_connect error', e)
                return

    # 建立连接时候回调
    def on_connect_callback(self, client, userdata, flags, rc):
        self.logger.info('Connected with result code:  ' + str(rc))

    # 发布消息回调
    def on_publish_callback(self, client, userdata, mid):
        pass

    # 消息处理函数回调
    def on_message_callback(self, client, userdata, msg):
        try:
            # 回调更新控制数据
            topic = msg.topic
            # 处理控制数据
            if topic == 'control_data_%s' % config.ship_code:
                self.b_receive_mqtt = True
                control_data = json.loads(msg.payload)
                if control_data.get('move_direction') is None:
                    self.logger.error('control_data_处理控制数据没有move_direction')
                    return
                self.control_move_time = time.time()
                self.control_move_direction = int(control_data.get('move_direction'))
                self.logger.info({'topic': topic,
                                  'control_move_direction': self.control_move_direction,
                                  'mode': control_data.get('mode')
                                  })
            # 处理开关信息
            if topic == 'switch_%s' % config.ship_code:
                self.b_receive_mqtt = True
                switch_data = json.loads(msg.payload)
                # 改变了暂时没用
                if switch_data.get('line') is not None:
                    self.line = int(switch_data.get('line'))
                    self.line_time = time.time()
                    self.logger.info({'topic': topic,
                                      'line': self.line
                                      })
        except Exception as e:
            self.logger.error({'error': e})

    # 发布消息
    def publish_topic(self, topic, data, qos=0):
        """
        向指定话题发布消息
        :param topic 发布话题名称
        :param data 　发布消息
        :param qos　　发布质量
        """
        if isinstance(data, list):
            data = str(data)
            self.mqtt_client.publish(topic, payload=data, qos=qos)
        elif isinstance(data, dict):
            data = json.dumps(data)
            self.mqtt_client.publish(topic, payload=data, qos=qos)
        elif isinstance(data, int) or isinstance(data, float):
            data = str(data)
            self.mqtt_client.publish(topic, payload=data, qos=qos)
        else:
            self.mqtt_client.publish(topic, payload=data, qos=qos)

    # 订阅消息
    def subscribe_topic(self, topic='qqq', qos=0):
        """
        :param topic 订阅的话题
        :param qos　　发布质量
        """
        self.logger.info({'topic': topic, 'qos': qos})
        self.mqtt_client.subscribe(topic, qos)
