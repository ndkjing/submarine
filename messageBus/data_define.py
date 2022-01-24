"""
定义数据类型
"""
import copy
import random
import time
# from utils import data_generate
from uuid import uuid4

import config
# 本地名称与发送名称映射
name_mappings = {
    # 'pool_id':'mapId',
    # 'ship_code':'deviceId',
    'water':
        {'pH': 'ph',
         'DO': 'doDo',
         'COD': 'cod',
         'EC': 'ec',
         'TD': 'td',
         'NH3_NH4': 'nh3Nh4',
         'TN': 'tn',
         'TP': 'tp'},

    'weather':
        {
            'wind_speed': 'windSpeed',
            'wind_direction': 'windDirection',
            'rainfall': 'rainfall',
            'illuminance': 'illuminance',
            'temperature': 'temperature',
            'humidity': 'humidity',
            'pm25': 'pm25',
            'pm10': 'pm10',
        }
}

# 当前真实数据列表 不在该表中的值使用生成数据
current_data = ['COD', 'wt', 'current_lng_lat', 'direction', 'speed', 'attitude_angle', 'b_online', 'ship_code',
                'pool_code']


# 生成船号
def get_ship_code():
    return str(uuid4())





class DataDefine:
    def __init__(self):
        """
        数据定义对象
        """
        # 订阅话题
        self.topics = (
            ('control_data_%s' % config.ship_code, 0),
            ('switch_%s' % config.ship_code, 0),
           )
        self.pool_code = ''
        self.water = self.water_data()
        self.weather = self.weather_data()
        self.status = self.status_data()
        self.control = self.control_data()
        self.detect = self.detect_data()

    # 水质数据
    def water_data(self):
        """
        :param value_from 数据来源
        解释　　　　　字典键名称　　数据类型　　
        水温       wt　　　　　 浮点数　　
        酸碱度       pH　　　　　 浮点数　　
        溶解氧　　　　DO          浮点数　　
        化学需氧量   COD　　　　  浮点数　　
        电导率      EC　　　   　浮点数　　
        浊度       TD　　　　   浮点数　　
        氨氮       NH3_NH4　　　浮点数　　
        总氮       TN　　　　   浮点数　　
        总磷       TP　　　   　浮点数　　
        """
        return_dict = {'wt': None,
                       "pH": None,
                       "DO": None,
                       "COD": None,
                       "EC": None,
                       "TD": None,
                       "NH3_NH4": None,
                       "TN": None,
                       "TP": None,
                       }
        return return_dict

    # 气象数据
    def weather_data(self):
        """
        解释　　　　　字典键名称　　数据类型　　
        风速    wind_speed    浮点数
        风向    wind_direction　　字符串：东南西北，东北，东南，西北，西南等
        降雨量  rainfall　　　　　浮点数
        光照度   illuminance　　　浮点数
        温度    temperature　　　　浮点数
        湿度    humidity　　　　浮点数
        PM2.5   pm25　浮点数
        PM10    pm10　浮点数
        """

        return_dict = {"wind_speed": None,
                       "wind_direction": None,
                       "rainfall": None,
                       "illuminance": None,
                       "temperature": None,
                       "humidity": None,
                       "pm25": None,
                       "pm10": None,
                       }
        return return_dict

    # 控制数据
    def control_data(self):
        """
        地图湖泊中间一个点经纬度坐标
        解释　　　　　字典键名称　   　数据类型　
        前进方向    move_direcion  　float  0：正前方：90 左 180：后 270：右  360:停止
        执行采样    b_sampling      整数枚举  0：不检测  1：检测
        执行抽水    b_draw          整数枚举  0：不抽水  1：抽水
        """
        return_dict = {'move_direction': 360,
                       'b_sampling': 0,
                       'b_draw': 0,
                       }
        return return_dict

    # 状态数据
    def status_data(self):
        """
        解释　　　　　字典键名称　　数据类型　　
        剩余电量      dump_energy   浮点数（0.0--1.0 百分比率）
        当前真实经纬度   current_lng_lat  列表［浮点数，浮点数］（［经度，纬度］）
        液位        liquid_level    浮点数（采样深度液位）
        漏水　　　　　b_leakage      布尔值（船舱内部是否漏水）
        船头方向　　　direction      浮点数（０.0－３６０　单位度）
        速度　　　　　speed　　　　　　浮点数　（ｍ/s）
        姿态        attitude_angle   列表[r,p,y]  (ｒ,p,y 为横滚，俯仰，偏航角度　取值均为浮点数０.0－３６０)
        在线／离线  　b_online      布尔值（船是否在线）
        归位状态：　　b_homing　　    布尔值    （是否返回充电桩）　　　
        充电状态：　　charge_energy　　浮点数（0.0--1.0  百分比率　在充电状态下的充电电量）　　　
        采样深度：　　sampling_depth　　浮点数(单位:ｍ)
        船号：　　　　ship_code      字符串（船出厂编号）
        湖泊编号     pool_code      字符串（湖泊编号）
        4G卡流量：　　data_flow       浮点数（单位：ＭＢ）
        采样量：　　　sampling_count　　整数（采样点的个数）
        船舱容量状态：　　capicity　　　浮点数（0.0--1.0  百分比率　垃圾收集船内部容量）
        """
        return_dict = {"dump_energy": None,
                       "current_lng_lat": None,
                       # "liquid_level": None,
                       # "b_leakage": None,
                       "direction": None,
                       "speed": None,
                       # "attitude_angle": None,
                       # "b_online": True,
                       # "b_homing": None,
                       # "charge_energy": None,
                       # "sampling_depth": None,
                       "ship_code": config.ship_code,
                       # "pool_code": None,
                       # "data_flow": None,
                       # "sampling_count": None,
                       # "capicity": None,
                       "totle_time": None,
                       "runtime": 0,
                       "totle_distance": None,
                       "run_distance": None
                       }
        return return_dict

    # 统计数据
    def statistics_data(self):
        """
        解释　　　　　字典键名称　　    数据类型　　
        工作时长   work_time  　　  浮点数(单位：秒)
        工作距离　　work_distance   浮点数（单位：米）
        采样点经纬度　sampling_lng_lat  列表［浮点数，浮点数］（数据说明［经度，纬度］）
        """
        return_dict = {"work_time": None,
                       "work_distance": None,
                       "sampling_lng_lat": None,
                       }
        return return_dict

    # 返回检测数据
    def detect_data(self):
        """
        返回检测数据
        :return: 检测数据字典
        """
        return_detect_data = {}
        return_detect_data['weather'] = self.weather
        return_detect_data['water'] = self.water
        return_detect_data['deviceId'] = config.ship_code
        return return_detect_data


if __name__ == '__main__':
    # 简单测试获取数据
    obj = DataDefine()
    # data_dict = {}
    # data_dict.update({'statistics_data': obj.statistics_data()})
    # data_dict.update({'status_data':obj.status_data()})
    # data_dict.update({'weather':obj.weather})
    # data_dict.update({'water':obj.water})
    # print(detect_data())
