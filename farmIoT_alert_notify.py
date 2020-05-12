#!/usr/bin/env python abort_measure LINE alert
# coding=utf-8
# ----- 農地IoT測定値異常時のＬＩＮＥ通知 -----
import time
import datetime
import requests
import mysql.connector


# -----データベースの情報を格納する定数-----
COMMON_DB_USER = "root"  # 共通DBのユーザ名
COMMON_DB_PASS = "pm#corporate1"  # 共通DBのパスワード
COMMON_DB_HOST = "localhost"  # 共通DBのホスト名
COMMON_DB_NAME = "common_db"  # 共通DBのDB名

PJ_DB_USER = "root"  # プロジェクトで使用するDBのユーザ名
PJ_DB_PASS = "pm#corporate1"  # プロジェクトで使用するDBのパスワード
PJ_DB_HOST = "localhost"  # プロジェクトで使用するDBのホスト名
PJ_DB_NAME = "FARMM_IoT"  # プロジェクトで使用するDB名
# ---------------------------------------

# -----グローバル変数群-----
pj_name = "kurozemu"  # プロジェクト名
limit_tbl_item = None  # 規定値テーブルの項目名
current_value = None  # 既定値テーブルの現在値
smtp_addr = None  # 送信元アドレス
smtp = None  # 送信元接続情報
line_token = ""  # LINEトークン
common_pj = None  # 共通データベースへの接続情報を保持する変数
pj_con = None  # プロジェクトごとのデータベースへの接続情報を保持する変数
line_message = "<< 農業IoTアラート >>"  # LINE通知のメッセージタイトル
alert_flg = "OFF"  # LINEアラートが発生したら"ON"
# --------------------------

# 10分前の時刻を取得
before_10min = time.time() - 600
before_10min = datetime.datetime.fromtimestamp(before_10min)

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

def MESSAGE_SET(str_message):
    """
    LINEへ通知するメッセージを設定する処理
    """
    if limit_tbl_item == "SOIL_TEMP":
        str_message = str_message + "\n土壌温度(" + format(current_value) + "℃)"
    elif limit_tbl_item == "SOIL_WET":
        str_message = str_message + "\n土壌湿度(" + format(current_value) + "%)"
    elif limit_tbl_item == "soil_ec":
        str_message = str_message + \
            "\n土壌電気伝導度(" + format(current_value) + "mS/cm)"
    elif limit_tbl_item == "AIR_TEMP_1":
        str_message = str_message + "\n気温(" + format(current_value) + "℃)"
    elif limit_tbl_item == "AIR_WET":
        str_message = str_message + "\n湿度(" + format(current_value) + "%)"
    else:
        pass
    return str_message

# 測定値テーブルに接続し直近の測定値を取得
conn = mysql.connector.connect(
    user="root", password="pm#corporate1", host="localhost", database="FARM_IoT")
cur = conn.cursor()
cur.execute("select * from farm order by day desc, time desc limit 1;")
for row in cur.fetchall():
    day_tbl = row[0]
    time_tbl = row[1]
    soil_temp = row[2]
    soil_wet = row[3]
    soil_ec = row[4]
    air_temp = row[5]
    air_wet = row[6]
cur.close()

# 測定値が直近のものか(10分前と比較)判断、測定が止まっていればアラート通知
DAYTIME = format(day_tbl) + " " + format(time_tbl) + ".999999"
if format(DAYTIME) > format(before_10min):
    # 最新の測定値なのでしきい値チェックを行う
    # しきい値テーブルからレコード取得
    cur = conn.cursor()
    cur2 = conn.cursor()
# --< 2020/04/15 UPDATE-START >--
#    cur.execute("select * from limit_tbl where item <> 'SYSTEM';")
    cur.execute(
        "select * from limit_tbl where item in ('SOIL_TEMP','SOIL_WET','AIR_TEMP_1','AIR_WET');")
# --< 2020/04/15 UPDATE-END >--
    for row in cur.fetchall():
        # テーブルの要素を変数に入れる
        limit_tbl_item = row[1]
        limit_tbl_max = row[2]
        limit_tbl_min = row[3]
        limit_tbl_flg = row[4]

        # 各項目で測定値をチェックする
        if limit_tbl_item == "SOIL_TEMP":  # 土壌温度
            current_value = soil_temp
        elif limit_tbl_item == "SOIL_WET":  # 土壌湿度
            current_value = soil_wet
        elif limit_tbl_item == "soil_ec":  # 電気伝導度
            current_value = soil_ec
        elif limit_tbl_item == "AIR_TEMP_1":  # 気温
            current_value = air_temp
        elif limit_tbl_item == "AIR_WET":  # 湿度
            current_value = air_wet
        else:
            pass

        # しきい値チェック（３回連続で範囲内のときフラグを"OK"に戻す）
        if (current_value >= limit_tbl_min) and (current_value <= limit_tbl_max):  # 正常の範囲内
            if limit_tbl_flg == "OK":  # フラグの値が"OK"なら何もしない
                pass
            elif limit_tbl_flg == "NG":  # フラグの値が"NG"なら"1"を立てる
                limit_tbl_flg = "1"
            elif limit_tbl_flg == "1":  # フラグの値が"1"なら"2"を立てる
                limit_tbl_flg = "2"
            elif limit_tbl_flg == "2":  # フラグの値が"2"なら"OK"を立て、復旧のLINEメッセージを設定
                alert_flg = "ON"  # アラート通知を"ON"にする（復旧のLINE通知）
                limit_tbl_flg = "OK"
                line_message = MESSAGE_SET(line_message) + "が範囲内になりました。"
            else:
                pass
        elif current_value < limit_tbl_min:  # 最低値を下回った場合
            if limit_tbl_flg == "OK":  # フラグの値が"OK"ならLINEアラート通知（低下）
                alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
                line_message = MESSAGE_SET(line_message) + "が設定値より低下しました。"
            else:
                pass
            limit_tbl_flg = "NG"  # リミットテーブルのフラグに"NG"を立てる

        elif current_value > limit_tbl_max:  # 最大値を上回った場合
            if limit_tbl_flg == "OK":  # フラグの値が"OK"ならLINEアラート通知（超過）
                alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
                line_message = MESSAGE_SET(line_message) + "が設定値を超過しました。"
            else:
                pass
            limit_tbl_flg = "NG"  # リミットテーブルのフラグに"NG"を立てる

        # リミットテーブルの更新
        sql = "UPDATE limit_tbl SET flg_sts = %s WHERE item = %s"
        cur2.execute(sql, (limit_tbl_flg, limit_tbl_item))

    # リミットテーブルの更新（測定値、取得再開の判断）
    cur2.execute("select * from limit_tbl where item = 'SYSTEM';")
    for row in cur2.fetchall():
        limit_tbl_flg = row[4]
    if limit_tbl_flg == "NG":
        alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
        line_message = line_message + "\n計測が再開されました。"
        # リミットテーブルの更新
        cur2.execute(
            "UPDATE limit_tbl SET flg_sts = 'OK' WHERE item = 'SYSTEM';")

    cur2.close()
    cur.close()
else:  # 古い測定値なので測定停止のアラート通知を行う
    cur = conn.cursor()
    cur.execute("select * from limit_tbl where item = 'SYSTEM';")
    for row in cur.fetchall():
        limit_tbl_flg = row[4]
    if limit_tbl_flg == "OK":
        alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
        line_message = line_message + "\n計測が停止しています。"
        # リミットテーブルの更新
        cur.execute(
            "UPDATE limit_tbl SET flg_sts = 'NG' WHERE item = 'SYSTEM';")
    cur.close()
conn.close()

# 新たにアラートが発生、又は復旧した場合はLINE通知する
if alert_flg == "ON":
    LINE_notify(line_message)  # LINEへ通知　<--- この行をコメントアウトすればLINE通知が止まる
    print(line_message)  # LINE通知の代わりにテストでメッセージを確認する為の画面表示
