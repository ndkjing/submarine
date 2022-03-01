"""
推送摄像头流到服务器
"""
import os
import time

while True:
    try:
        if os.path.exists('/dev/video0'):
            os.system("ffmpeg -s 640*480 -i /dev/video0 -vcodec libx264 -max_delay 100 -g 5 -b 500000 -tune zerolatency -preset ultrafast -f flv rtmp://116.62.44.118:1935/live/index")
        else:
            time.sleep(1)
            continue
    except KeyboardInterrupt:
        break