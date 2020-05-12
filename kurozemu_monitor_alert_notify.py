#!/usr/bin/env python abort_measure LINE alert 
#coding=utf-8
#----- くろぜむ農園：死活監視(測定値取得、画像生成)プログラム -----
#※マルキンサーバ上での動作は確認済、実際の大槌監視LinuxPCでは未確認なのでサーバ間での接続確認が必要

import requests
import mysql.connector
import os
import time , datetime



# -----データベースの情報を格納する定数-----
COMMON_DB_USER = "root"  # 共通DBのユーザ名
COMMON_DB_PASS = "pm#corporate1"  # 共通DBのパスワード
COMMON_DB_HOST = "localhost"  # 共通DBのホスト名
COMMON_DB_NAME = "common_db"  # 共通DBのDB名

PJ_DB_USER = "root"  # プロジェクトで使用するDBのユーザ名
PJ_DB_PASS = "pm#corporate1"  # プロジェクトで使用するDBのパスワード
PJ_DB_HOST = "localhost"  # プロジェクトで使用するDBのホスト名
PJ_DB_NAME = "FARM_IoT"  # プロジェクトで使用するDB名
# ---------------------------------------

# -----グローバル変数群-----
pj_name = "monitor"  # プロジェクト名
limit_tbl_item = None  # 規定値テーブルの項目名
current_value = None  # 既定値テーブルの現在値
smtp_addr = None  # 送信元アドレス
smtp = None  # 送信元接続情報
line_token = ""  # LINEトークン
common_pj = None  # 共通データベースへの接続情報を保持する変数
pj_con = None  # プロジェクトごとのデータベースへの接続情報を保持する変数
line_message = "<< くろぜむ監視アラート >>"  # LINE通知のメッセージタイトル
alert_flg = "OFF"  # LINEアラートが発生したら"ON"
# --------------------------

def connect_database_common():
    """
    共通データベースにアクセスする処理
    """
    global common_pj

    common_pj = mysql.connector.connect(
        user=COMMON_DB_USER, password=COMMON_DB_PASS, host=COMMON_DB_HOST, database=COMMON_DB_NAME)


def connect_database_project():
    """
    プロジェクトごとのデータベースにアクセスする処理
    """
    global pj_con

    pj_con = mysql.connector.connect(
        user=PJ_DB_USER, password=PJ_DB_PASS, host=PJ_DB_HOST, database=PJ_DB_NAME)


def close_con_connect(con_name, cur_name):
    """
    引数で受け取った、データベース接続情報と、カーソルをCloseする処理
    """
    con_name.close()
    cur_name.close()

def get_line_token():
    """
    共通データベースからLINEトークンを取得する処理
    """
    # グローバル変数に代入するために宣言
    global line_token

    # データベース接続処理
    connect_database_common()

    # 共通データベースのカーソルを取得
    line_cur = common_pj.cursor()
    line_cur.execute(
        "SELECT * FROM m_common_token WHERE project_name='" + pj_name + "'")

    for line_row in line_cur.fetchall():
        # line_id = line_row[0]
        line_token = line_row[1]

    # 後処理としてクローズ処理を実行する
    close_con_connect(common_pj, line_cur)


def LINE_notify(str_message):
    """
    LINE Notifyの接続処理
    """

    url = "https://notify-api.line.me/api/notify"

    #LINEトークン取得処理
    get_line_token()

    headers = {"Authorization": "Bearer " + line_token}
    payload = {"message":  str_message}
    r = requests.post(url, headers=headers, params=payload)


# 画像格納フォルダパス
IMAGE_DIR = "/var/www/html/farm/images"

# 今日の日付と5分前の時刻を取得
BEFORE_5min = time.time() - 300
BEFORE_5min = datetime.datetime.fromtimestamp(BEFORE_5min)
DATE_TODAY  = datetime.date.today()


# ****************************************
# ***** 計測が稼働しているかチェック *****
# ****************************************

# マルキンサーバの測定値テーブルに接続し直近の測定値を取得 
conn = mysql.connector.connect(user=PJ_DB_USER,password=PJ_DB_PASS,host=PJ_DB_HOST,database=PJ_DB_NAME)
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
        line_message = line_message + "\n計測が停止しています。"
    # システム監視テーブルの更新
    cur.execute("UPDATE MONITOR_TBL SET MONITOR_STATUS = 'NG' , CHK_TIMESTAMP = NOW() WHERE SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID ='KEISOKU';")
    cur.close
else:
    cur.execute("select * from MONITOR_TBL where SYSTEM_ID = 'KUROZEMU' AND MONITOR_ID = 'KEISOKU';")
    for row in cur.fetchall():
        MONITOR_FLG  = row[2]
    if MONITOR_FLG == "NG":
        ALERT_FLG = "ON" # アラート通知を"ON"にする（計測再開のLINE通知）
        line_message = line_message + "\n計測を再開しました。"
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
            line_message = line_message + "\n" + CAM_ITEM + " の画像生成が停止しています。"
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
            line_message = line_message + "\n" + CAM_ITEM +" の画像生成を再開しました。"
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
    LINE_notify(line_message) # LINEへ通知　<--- この行をコメントアウトすればLINE通知が止まる
    print(line_message) # LINE通知の代わりにテストでメッセージを確認する為の画面表示
