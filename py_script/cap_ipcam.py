#!/usr/bin/ python
# -*- coding: utf-8 -*-

import datetime
import os
import cv2
import subprocess

# 日付情報をグローバルで格納
global now
global day
global d_time
now = datetime.datetime.now()
day = now.strftime('%Y%m%d')
d_time = now.strftime('%H%M')

def main():
    # スマートではないけれど、カメラごとの情報を入れ直してそれぞれ2回呼び出しています
    # 1台目の情報　192.168.5.101
    global ipcam
    global im_path
    global serverpath
    ipcam = "rtsp://admin:pm#corporate2@192.168.5.101/554/Streaming/Channels/1"
    im_path = '/home/pi/mainsys/images/1/'
    serverpath = "/home/miura/images/1/"
    get_camera_info()
    image_cap()
    fileup()
    # 2台目の情報　192.168.5.102
    ipcam = "rtsp://admin:pm#corporate2@192.168.5.102/554/Streaming/Channels/1"
    im_path = '/home/pi/mainsys/images/2/'
    serverpath = "/home/miura/images/2/"
    get_camera_info()
    image_cap()
    fileup()

def get_camera_info():
    # 各種設定情報の格納用関数
    # カメラ情報の取得と格納 Channel/1 メインストリーム Channel/2 サブストリーム
    global cap
    cap = cv2.VideoCapture(ipcam)
    global fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    global size
    size = (width,height)



def image_cap():
    # 静止画の撮影用関数
    img_di = str(im_path) + day
    if not os.path.exists(img_di):
        os.mkdir(img_di)
    # 書込設定
    global imnam
    imnam = str(img_di) + '/' + day + '_' + d_time + '00.jpg'
    global imnam_mini
    imnam_mini = str(img_di) + '/' + day + '_' + d_time + '00_mini.jpg'
    # 撮影開始
    cap = cv2.VideoCapture(ipcam)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 3)
    ret, frame = cap.read()
    if ret == True:
        cv2.imwrite(imnam, frame)
    if ret == False:
        print("imageerror")
    #print(cap)
    # 終了
    cap.release()
    # サムネイル画像作成　大きさは固定なので値そのまま書き込み
    #print(imnam)
    mini = cv2.imread(imnam)
    mini2 = cv2.resize(mini, (85, 48))
    cv2.imwrite(imnam_mini, mini2)

def fileup():
    # ファイルのアップロード　コマンド呼び出しで対応
    mkcall = 'sudo ssh root@160.16.239.88 mkdir -p ' + serverpath + day
    subprocess.call(mkcall.split())
    upcall = 'sudo scp -C ' + imnam + ' root@160.16.239.88:' + serverpath + day + '/'
    subprocess.call(upcall.split())
    upcall = 'sudo scp -C ' + imnam_mini + ' root@160.16.239.88:' + serverpath + day + '/'
    subprocess.call(upcall.split())
    #print(imnam)
    #print(imnam_mini)
    #print(upcall)

# main関数を呼び出す
if __name__ == '__main__':
    main()
