#!/usr/bin/python
# coding: utf-8

import sys
import os
import threading
import time
import random
import json
import signal
import gst

# 基础类
class MusicBase:
    def __init__(self):
        self.app_name = 'console_fm'
        self.appPath = os.path.realpath(sys.path[0])
        jsonStr = open(self.appPath+'/music2type.json').read()
        self.music2type = json.loads(jsonStr)
        noneType = []
        for k in self.music2type.keys():
            if len(self.music2type[k])==0:
                noneType.append(k)
        for v in noneType:
            del self.music2type[v]
        self.player = gst.element_factory_make('playbin', 'player')
        self.event = threading.Event()
        self.playing = False
        next(self)
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

    # gst 消息处理
    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.next(bus)

    # 主线程函数，循环播放
    def mainloop(self):
        while True:
            #print self.title,self.url
            self.player.set_property('uri', self.url)
            self.player.set_state(gst.STATE_PLAYING)
            self.playing = True

            # 让线程进入等待状态，等待激活信号
            self.event.wait()
            self.event.clear()

    # 播放/暂停
    def pause(self):
        if self.playing:
            self.player.set_state(gst.STATE_PAUSED)
            self.playing = False
            print '暂停'
        else:
            self.player.set_state(gst.STATE_PLAYING)
            self.playing = True
            print '继续播放'

    # 下一首
    def next(self):
        self.player.set_state(gst.STATE_NULL)
        self.event.set()
        key = random.choice(self.music2type.keys())
        self.title = random.choice(self.music2type[key].keys())
        self.url = self.music2type[key][self.title]
        print "播放：",self.title

    # 开启主播放线程
    def run(self):
        self.thread = threading.Thread(target=self.mainloop)
        self.thread.setDaemon(True)
        self.thread.start()
        while True:
            if not self.thread.isAlive(): break

    # 销毁播放器，目前尚未找到结束播放线程的方法
    def destroy(self):
        self.thread._Thread__stop()

# 主播放Console界面
class MusicMainConsole():
    def __init__(self):
        self.fm = MusicBase()
        self.fm.run()

def sigint_handler(signum, frame): 
    print ("exit")
    sys.exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    random.seed(time.time())
    MusicMainConsole()

