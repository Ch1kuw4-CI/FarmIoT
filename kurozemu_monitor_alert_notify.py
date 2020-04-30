#!/usr/bin/env python abort_measure LINE alert 
#coding=utf-8
#----- くろぜむ農園：死活監視(測定値取得、画像生成)プログラム -----
#※マルキンサーバ上での動作は確認済、実際の大槌監視LinuxPCでは未確認なのでサーバ間での接続確認が必要

import requests
import mysql.connector
import os
import time , datetime
i

def LINE_notify(LINE_MESSAGE):
    url = "https://notify-api.line.me/api/notify"
#    token = #Here ACCESS-TOKEN input
    token = "ObFoG8pLNgIGpm04j7t0abp9wKMAJAuHHp08VFihIOb" # <----TEST用のLINEトークン
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  LINE_MESSAGE}
    r = requests.post(url ,headers = headers ,params=payload)



# 画像格納フォルダパス
IMAGE_DIR = "/var/www/html/farm/images"

# 今日の日付と5分前の時刻を取得
BEFORE_5min = time.time() - 300
BEFORE_5min = datetime.datetime.fromtimestamp(BEFORE_5min)
DATE_TODAY  = datetime.date.today()


# LINE通知のメッセージタイトルを設定
LINE_MESSAGE = " << くろぜむ監視アラート >>"
ALERT_FLG = "OFF" # LINEアラートが発生したら"ON"になる


# ****************************************
# ***** 計測が稼働しているかチェック *****
# ****************************************

# マルキンサーバの測定値テーブルに接続し直近の測定値を取得 
conn = mysql.connector.connect(user="root",password="pm#corporate1",host="160.16.239.88",database="FARM_IoT")
cur = conn.cursor()
cur.execute("select * from farm order by day desc, time desc limit 1;")
for row in cur.fetchall():
    DAY_TBL       = row[0]
    TIME_TBL      = row[1]
cur.close

# 測定値が直近のものか(5分前と比較)判断、測定が止まっていればアラート通知
DAYTIME = format(DAY_TBL) + " " + format(TIME_TBL) + ".999999"
if format(DAYTIME) < format(BEFORE_5min):
    # 古い測定値なので測定停止のアラート通知を行う
    cur.execute("select * from MONITOR_TBL where SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID = 'KEISOKU';")
    for row in cur.fetchall():
        MONITOR_FLG  = row[2]
    if MONITOR_FLG == "OK":
        ALERT_FLG = "ON" # アラート通知を"ON"にする（計測停止のLINE通知）
        LINE_MESSAGE = LINE_MESSAGE + "\n計測が停止しています。"
    # システム監視テーブルの更新
    cur.execute("UPDATE MONITOR_TBL SET MONITOR_STATUS = 'NG' , CHK_TIMESTAMP = NOW() WHERE SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID ='KEISOKU';")
    cur.close
else:
    cur.execute("select * from MONITOR_TBL where SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID = 'KEISOKU';")
    for row in cur.fetchall():
        MONITOR_FLG  = row[2]
    if MONITOR_FLG == "NG":
        ALERT_FLG = "ON" # アラート通知を"ON"にする（計測再開のLINE通知）
        LINE_MESSAGE = LINE_MESSAGE + "\n計測を再開しました。"
    # システム監視テーブルの更新（強制的にタイムスタンプを更新）
    cur.execute("UPDATE MONITOR_TBL SET MONITOR_STATUS = 'OK' , CHK_TIMESTAMP = NOW() WHERE SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID ='KEISOKU';")
    cur.close
conn.close


# ****************************************************************************
# ***** 画像が生成されているかチェック（カメラマスタ：M_CAMERAより抽出） *****
# ****************************************************************************
cur.execute("select * from M_CAMERA where CAMERA_STATUS = '1';")
for row in cur.fetchall():
    CAMERA_ID     = row[0]
    CAM_ITEM = "CAMERA" + format(CAMERA_ID)
    # フォルダの更新日をチェック
    FILE_TIMESTAMP = datetime.datetime.fromtimestamp(os.path.getmtime(IMAGE_DIR + "/" + format(CAMERA_ID) + "/" + format(DATE_TODAY).replace("-","")))
    # 画像生成が停止しているか判定
    cur2 = conn.cursor()
    if format(FILE_TIMESTAMP) < format(BEFORE_5min):
        # 画像フォルダのタイムスタンプが５分前より古いので画像停止のアラート通知を行う
        STR_SQL = "select * from MONITOR_TBL where SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID = '" + CAM_ITEM + "';"
        cur2.execute(STR_SQL)
        for row in cur.fetchall():
            MONITOR_FLG  = row[2]
        if MONITOR_FLG == "OK":
            ALERT_FLG = "ON" # アラート通知を"ON"にする（画像生成停止のLINE通知）
            LINE_MESSAGE = LINE_MESSAGE + "\n" + CAM_ITEM + " の画像生成が停止しています。"
            # システム監視テーブルの更新
        STR_SQL = "UPDATE MONITOR_TBL SET MONITOR_STATUS = 'NG' , CHK_TIMESTAMP = NOW() WHERE SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID = '" + CAM_ITEM + "';"
        cur2.execute(STR_SQL)
        cur2.close
    else:
        STR_SQL = "select * from MONITOR_TBL where SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID ='" + CAM_ITEM + "';"
        cur2.execute(STR_SQL)
        for row in cur.fetchall():
            MONITOR_FLG  = row[2]
        if MONITOR_FLG == "NG":
            ALERT_FLG = "ON" # アラート通知を"ON"にする（画像生成再開のLINE通知）
            LINE_MESSAGE = LINE_MESSAGE + "\n" + CAM_ITEM +" の画像生成を再開しました。"
        # システム監視テーブルの更新（強制的にタイムスタンプを更新）
        STR_SQL = "UPDATE MONITOR_TBL SET MONITOR_STATUS = 'OK' , CHK_TIMESTAMP = NOW() WHERE SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID ='" + CAM_ITEM + "';"
        cur2.execute(STR_SQL)
        cur2.close

cur.close
conn.commit()
conn.close


# **************************************
# ***** アラート発生の有無チェック *****
# **************************************

# 新たにアラートが発生、又は復旧した場合はLINE通知する
if ALERT_FLG == "ON":
#    LINE_notify(LINE_MESSAGE) # LINEへ通知　<--- この行をコメントアウトすればLINE通知が止まる
    print(LINE_MESSAGE) # LINE通知の代わりにテストでメッセージを確認する為の画面表示
