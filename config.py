# 保存地图数据路径
import enum
import json
import os
import platform
import ship_code_config
root_path = os.path.dirname(os.path.abspath(__file__))
# 船编号
ship_code = ship_code_config.ship_code
# 串口位置和波特率
# 单片机
# stc_port = '/dev/ttyAMA0'
b_stc_com = 1
# stc_port = '/dev/ttyUSB0'
stc_port = '/dev/ttyAMA0'
stc_baud = 115200
if b_stc_com and os.path.exists(stc_port):
    b_com_stc = 1
else:
    b_com_stc = 0
stc_timeout = 0.05  # 读取单片机延时
pi2mqtt_interval = 0.5  # 发送mqtt话题数据间隔
high_f_pi2mqtt_interval = 0.2  # 高频率发送mqtt话题数据间隔
# mqtt服务器ip地址和端口号
mqtt_host = '116.62.44.118'
# mqtt_host = '47.97.183.24'
mqtt_port = 1883
is_single=True    # 是否使用信号放接受方式
class CurrentPlatform(enum.Enum):
    windows = 1
    linux = 2
    pi = 3
    others = 4


sysstr = platform.system()
if sysstr == "Windows":
    print("Call Windows tasks")
    current_platform = CurrentPlatform.windows
elif sysstr == "Linux":  # 树莓派上也是Linux
    print("Call Linux tasks")
    # 公司Linux电脑名称
    if platform.node() == 'raspberrypi':
        current_platform = CurrentPlatform.pi
    else:
        current_platform = CurrentPlatform.linux
else:
    print("other System tasks")
    current_platform = CurrentPlatform.others

home_debug = True
if current_platform == CurrentPlatform.pi:
    home_debug = False

"""
电量与电压对应关系  各个阶段之内用线性函数计算
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

common_log_time = 10

if __name__ == '__main__':
    pass
