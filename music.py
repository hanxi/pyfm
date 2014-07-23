#!/usr/bin/python
# coding: utf-8

import sys
import os
import threading
import time
import random
import json
import getopt
import getpass
import requests
import keybinder
import gst
import gtk

# 基础类
class MusicBase:
    def __init__(self):
        self.app_name = 'radio_desktop_win'
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

    # 开启主播放线程
    def run(self):
        self.thread = threading.Thread(target=self.mainloop)
        self.thread.start()

    # 销毁播放器，目前尚未找到结束播放线程的方法
    def destroy(self):
        self.thread._Thread__stop()

# 主播放Console界面
class MusicMainConsole():
    def __init__(self):
        self.fm = MusicBase()
        self.fm.run()
        bus = self.fm.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

    # gst 消息处理
    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.next(bus)

    # 下一首
    def next(self, widget):
        self.fm.next()
        print "播放：",self.fm.title

# 主播放图形界面
class MusicMain(gtk.Window):
    def __init__(self):
        super(MusicMain, self).__init__()

        self.fm = MusicBase()
        self.fm.run()

        self.set_title('随机音乐')
        self.set_size_request(180, 180)
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.createInterior()
        self.show_all()
        self.connect('key-press-event', self.onKeypress)
        self.connect('destroy', self.destroy)

        self.musicName.set_text(self.fm.title)
        
        bus = self.fm.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

    # gst 消息处理
    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.next(bus)

    # 创建主界面
    def createInterior(self):
        fixed = gtk.Fixed()
        self.add(fixed)

        # 歌曲名字
        self.musicName = gtk.Label(u'')
        self.musicName.set_selectable(True)
        self.musicName.set_line_wrap(True)
        self.musicName.set_size_request(160, 80)
        fixed.put(self.musicName, 10, 10)

        # 播放/暂停按钮
        self.pauseImage = gtk.Image()
        self.pauseImage.set_from_stock(
            gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)
        self.pauseButton = gtk.Button()
        self.pauseButton.add(self.pauseImage)
        self.pauseButton.connect('clicked', self.pause)
        self.pauseButton.set_relief(gtk.RELIEF_NONE)
        self.pauseButton.set_can_focus(False)
        self.pauseButton.set_tooltip_text('暂停')
        fixed.put(self.pauseButton, 34, 120)

        # 下一首按钮
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_MEDIA_NEXT, gtk.ICON_SIZE_BUTTON)
        button = gtk.Button()
        button.add(image)
        button.connect('clicked', self.next)
        button.set_relief(gtk.RELIEF_NONE)
        button.set_can_focus(False)
        button.set_tooltip_text('下一首')
        fixed.put(button, 80, 120)

    # 退出
    def destroy(self, widget):
        self.fm.destroy()
        gtk.main_quit()

    # 播放/暂停
    def pause(self, widget):
        self.fm.pause()
        if self.fm.playing:
            self.pauseImage.set_from_stock(
                gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)
            self.pauseButton.set_tooltip_text('暂停')
        else:
            self.pauseImage.set_from_stock(
                gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
            self.pauseButton.set_tooltip_text('播放')

    # 下一首
    def next(self, widget):
        self.fm.next()
        self.musicName.set_text(self.fm.title)

    # 按键处理
    def onKeypress(self, widget, event):
        # 下一首
        if event.keyval == gtk.keysyms.n \
            or event.keyval == gtk.keysyms.Right:
            self.next(widget)
        # 暂停
        elif event.keyval == gtk.keysyms.space \
            or event.keyval == gtk.keysyms.p:
            self.pause(widget)

if __name__ == '__main__':
    gtk.threads_init()
    random.seed(time.time())
    MusicMain()
    gtk.main()
