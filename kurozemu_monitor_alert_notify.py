"""
 ----- くろぜむ農園：死活監視(測定値取得、画像生成)プログラム -----
"""

#!/usr/bin/env python abort_measure LINE alert
# coding=utf-8

import os
import time
import datetime
import requests
import mysql.connector
from common_module import common  # 共通モジュールのimport


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

# -----定数-----
IMAGE_DIR = "/var/www/html/farm/images"  # 画像格納フォルダパス

# ---------------------------------------

# -----グローバル変数群-----
limit_tbl_item = None  # 規定値テーブルの項目名
current_value = None  # 既定値テーブルの現在値
smtp_addr = None  # 送信元アドレス
smtp = None  # 送信元接続情報
line_message = "<< くろぜむ監視アラート >>"  # LINE通知のメッセージタイトル
alert_flg = "OFF"  # LINEアラートが発生したら"ON"
# --------------------------

# 現在の日付と5分前の時刻を取得
before_5min = time.time() - 300
before_5min = datetime.datetime.fromtimestamp(before_5min)
date_today = datetime.date.today()


def main():
    """
    メイン関数
    """
    get_data()  # データ取得処理の呼び出し
    check_image()  # 画像生成チェック処理の呼び出し

    # 新たにアラートが発生、又は復旧した場合はLINE通知する
    if alert_flg == "ON":
        # LINEへ通知
        send_line_message(line_message)  # <--- この行をコメントアウトすればLINE通知が止まる
        print(line_message)  # LINE通知の代わりにテストでメッセージを確認する為の画面表示


def send_line_message(str_message):
    """
    LINE Notifyの接続処理
    """

    url = "https://notify-api.line.me/api/notify"

    # LINEトークン取得処理
    common.get_line_token()

    headers = {"Authorization": "Bearer " + common.line_token}
    payload = {"message":  str_message}
    # *********************************************************
    # 動作確認のためコメントアウト
    # r = requests.post(url, headers=headers, params=payload)
    # *********************************************************


def get_data():
    """
    直近の測定値を取得する処理
    """
    data_cur = common.connect_database_project()

    # 直近のデータを取得するSQL句の発行
    sel_sql = "SELECT * FROM farm ORDER BY desc, time DESC LIMIT 1;"

    # SQLを実行する
    data_cur.execute(sel_sql)

    for row in data_cur.fetchall():
        d_day = row[0]
        d_time = row[1]

    common.close_con_connect(common.pj_con, data_cur)

    check_data(d_day, d_time)


def check_data(data_day, data_time):
    """
    測定値が取得できているかチェックする関数
    """

    global alert_flg
    global line_message

    # 共通データベースにアクセスする
    check_cur = common.connect_database_common()

    # 監視テーブルから、プロジェクトのデータを取得するSQL
    sel_sql = "SELECT * FROM m_monitor WHERE system_name = '" + \
        common.pj_name + "' AND monitor_name = 'KEISOKU';"

    # 監視テーブルの値をOKで更新するSQL
    upd_ok_sql = "UPDATE m_monitor SET MONITOR_STATUS = 'OK' , \
        CHK_TIMESTAMP = NOW() WHERE SYSTEM_ID = '" + \
        common.pj_name + "' AND monitor_name ='KEISOKU';"

    upd_ng_sql = "UPDATE m_monitor SET MONITOR_STATUS = 'NG' , \
        CHK_TIMESTAMP = NOW() WHERE SYSTEM_ID = '" + \
        common.pj_name + "' AND monitor_name ='KEISOKU';"

    # 監視履歴テーブルの値をOKでINSERTするSQL
    ins_ok_sql = "INSERT INTO h_monitor ( \
        system_id, system_name, monitor_name, monitor_status, check_time) \
        VALUES ("

    # 監視履歴テーブルの値をNGでINSERTするSQL
    ins_ng_sql = "INSERT INTO h_monitor ( \
        system_id, system_name, monitor_name, monitor_status, check_time) \
        VALUES( "

    # 時刻の表示が「05：00:00」でなく「5:00:00」のため桁合わせ
    if len(format(data_time)) == 7:
        day_time = format(data_day) + " 0" + format(data_time) + ".999999"
    else:
        day_time = format(data_day) + " " + format(data_time) + ".999999"

    # 測定値が直近のものか(5分前と比較)判断、測定が止まっていればアラート通知
    if format(day_time) < format(before_5min):
        # 古い測定値なので測定停止のアラート通知を行う
        check_cur.execute(sel_sql)

        for monitor_row in check_cur.fetchall():
            sys_id = monitor_row[0]
            sys_name = monitor_row[1]
            monitor_name = monitor_row[2]
            monitor_status = monitor_row[3]
        if monitor_status == "OK":
            alert_flg = "ON"  # アラート通知を"ON"にする（計測停止のLINE通知）
            line_message = line_message + "\n計測が停止しています。"

        # INSERT句の生成
        ins_ng_sql = ins_ng_sql + sys_id + ", '" + sys_name + \
            "', '" + monitor_name + "', 'NG', NOW() )"

        # システム監視テーブルのUPDATE
        check_cur.execute(upd_ng_sql)

        # 監視履歴テーブルのINSERT
        check_cur.execute(ins_ng_sql)

    else:
        check_cur.execute(sel_sql)
        for monitor_row in check_cur.fetchall():
            sys_id = monitor_row[0]
            sys_name = monitor_row[1]
            monitor_name = monitor_row[2]
            monitor_status = monitor_row[3]
        if monitor_status == "NG":
            alert_flg = "ON"  # アラート通知を"ON"にする（計測再開のLINE通知）
            line_message = line_message + "\n計測を再開しました。"

        # INSERT句の生成
        ins_ok_sql = ins_ok_sql + sys_id + ", '" + sys_name + \
            "', '" + monitor_name + "', 'OK', NOW() )"
        # システム監視テーブルのUPDATE（強制的にタイムスタンプを更新）
        check_cur.execute(upd_ok_sql)

        # 監視履歴テーブルのINSERT
        check_cur.execute(ins_ok_sql)

    common.close_con_connect(common.common_con, check_cur)


def check_image():
    """
    画像が生成されているかチェックする関数
    """
    global alert_flg
    global line_message
    global limit_tbl_item

    # M_CAMERAに接続するための処理
    check_camera_cur = common.connect_database_project()

    # m_monitorに接続するための処理
    check_monitor_cur = common.connect_database_common()

    sel_camera_sql = "SELECT * FROM M_CAMERA WHERE CAMERA_STATUS = '1';"

    # 監視対象のプロジェクト名、対象システムを指定して、監視テーブルの値を取得するSQL。monitor_nameのあとにはcam_itemを入れる
    sel_monitor_sql = "SELECT * FROM m_monitor WHERE system_name = '" + \
        common.pj_name + "' AND monitor_name = '"

    # 監視テーブルの値をOKでUPDATEするSQL
    upd_ok_sql = "UPDATE m_monitor SET MONITOR_STATUS = 'OK' , CHK_TIMESTAMP = NOW() \
                    WHERE SYSTEM_ID = '" + common.pj_name + "' AND monitor_name = '"

    # 監視テーブルの値をNGUPDATEするSQL
    upd_ng_sql = "UPDATE m_monitor SET MONITOR_STATUS = 'NG' , CHK_TIMESTAMP = NOW() \
                    WHERE SYSTEM_ID = '" + common.pj_name + "' AND monitor_name = '"

    # 監視履歴テーブルの値をOKでINSERTするSQL
    ins_ok_sql = "INSERT INTO h_monitor ( \
        system_id, system_name, monitor_name, monitor_status, check_time) \
        VALUES ("

    # 監視履歴テーブルの値をNGでINSERTするSQL
    ins_ng_sql = "INSERT INTO h_monitor ( \
        system_id, system_name, monitor_name, monitor_status, check_time) \
        VALUES( "

    check_camera_cur.execute(sel_camera_sql)

    # 取得したカメラ台数分ループし、チェックする
    for row in check_camera_cur.fetchall():
        camera_id = row[0]
        cam_item = "CAMERA" + format(camera_id)
        # フォルダの更新日をチェック
        FILE_TIMESTAMP = datetime.datetime.fromtimestamp(os.path.getmtime(
            IMAGE_DIR + "/" + format(camera_id) + "/" + format(date_today).replace("-", "")))

        # 画像生成が停止しているか判定
        if format(FILE_TIMESTAMP) < format(before_5min):
            # 画像フォルダのタイムスタンプが５分前より古いので画像停止のアラート通知を行う

            # 監視テーブルの値を取得するSQLに、cam_itemを指定して完成させる
            sel_monitor_sql = sel_monitor_sql + cam_item + "';"

            # 監視テーブルの値を取得
            check_monitor_cur.execute(sel_monitor_sql)

            for monitor_row in check_monitor_cur.fetchall():
                sys_id = monitor_row[0]
                sys_name = monitor_row[1]
                monitor_name = monitor_row[2]
                monitor_status = monitor_row[3]
            if monitor_status == "OK":
                alert_flg = "ON"  # アラート通知を"ON"にする（画像生成停止のLINE通知）
                line_message = line_message + "\n" + cam_item + " の画像生成が停止しています。"

            # INSERT句の生成
            ins_ng_sql = ins_ng_sql + sys_id + ", '" + sys_name + \
                "', '" + monitor_name + "', 'NG', NOW() )"

            # システム監視テーブルの更新
            upd_ng_sql = upd_ng_sql + cam_item + "';"
            check_monitor_cur.execute(upd_ng_sql)

            # 監視履歴テーブルのINSERT
            check_monitor_cur.execute(ins_ng_sql)

            check_monitor_cur.close()
        else:
            # 監視テーブルの値を取得するSQLに、cam_itemを指定して完成させる
            sel_monitor_sql = sel_monitor_sql + cam_item + "';"

            check_monitor_cur.execute(sel_monitor_sql)
            for monitor_row in check_monitor_cur.fetchall():
                monitor_status = monitor_row[3]
            if monitor_status == "NG":
                alert_flg = "ON"  # アラート通知を"ON"にする（画像生成再開のLINE通知）
                line_message = line_message + "\n" + cam_item + " の画像生成を再開しました。"

            # INSERT句の生成
            ins_ng_sql = ins_ng_sql + sys_id + ", '" + sys_name + \
                "', '" + monitor_name + "', 'NG', NOW() )"

            # システム監視テーブルの更新（強制的にタイムスタンプを更新）
            upd_ok_sql = upd_ok_sql + cam_item + "';"
            check_monitor_cur.execute(upd_ok_sql)

            # 監視履歴テーブルのINSERT
            check_monitor_cur.execute(ins_ok_sql)

            check_monitor_cur.close()

    # SQLのコミット
    common.pj_con.commit()
    common.common_con.commit()

    # 後処理
    check_camera_cur.close()
    common.pj_con.close()
    common.common_con.close()
