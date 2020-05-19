#!/usr/bin/env python abort_measure LINE alert
# coding=utf-8
# ----- 農地IoT測定値異常時のＬＩＮＥ通知 -----
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

# -----グローバル変数群-----
limit_tbl_item = None  # 規定値テーブルの項目名
current_value = None  # 既定値テーブルの現在値
smtp_addr = None  # 送信元アドレス
smtp = None  # 送信元接続情報
line_message = "<< 農業IoTアラート >>"  # LINE通知のメッセージタイトル
alert_flg = "OFF"  # LINEアラートが発生したら"ON"
# --------------------------

# 10分前の時刻を取得
before_10min = time.time() - 600
before_10min = datetime.datetime.fromtimestamp(before_10min)


def main():
    """
    メイン関数
    """

    # データ取得処理を呼び出し
    get_data()

    # 新たにアラートが発生、又は復旧した場合はLINE通知する
    if alert_flg == "ON":
        # LINEへ通知　<--- この行をコメントアウトすればLINE通知が止まる
        send_line_message(line_message)
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


def set_line_message(str_message):
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


def get_data():
    """
    測定値テーブルに接続して、測定値を取得する処理
    """

    data_cur = common.connect_database_project()

    # 直近のデータを取得するSQL句の発行
    sel_sql = "SELECT * FROM farm ORDER BY day DESC, time DESC LIMIT 1;"

    # SQLの実行
    data_cur.execute(sel_sql)

    for data_row in data_cur.fetchall():
        day_tbl = data_row[0]
        time_tbl = data_row[1]
        soil_temp = data_row[2]
        soil_wet = data_row[3]
        soil_ec = data_row[4]
        air_temp = data_row[5]
        air_wet = data_row[6]

        # デバッグ用。取得した値を出力する
        print("日付：" + str(day_tbl))
        print("時刻：" + str(time_tbl))
        print("土壌温度" + str(soil_temp))
        print("土壌湿度" + str(soil_wet))
        print("土壌電気伝導度" + str(soil_ec))
        print("気温" + str(air_temp))
        print("湿度" + str(air_wet))

    common.close_con_connect(common.pj_con, data_cur)

    # 測定値チェック処理の呼び出し
    check_data(day_tbl, time_tbl, soil_temp,
               soil_wet, soil_ec, air_temp, air_wet)


def check_data(data_day, data_time, data_s_temp, data_s_wet, data_s_ec, data_a_temp, data_a_wet):
    """
    取得した測定値のチェック処理
    """
    global alert_flg
    global line_message
    global limit_tbl_item
    global current_value

    # 測定値が直近のものか(10分前と比較)判断、測定が止まっていればアラート通知
    day_time = format(data_day) + " " + format(data_time) + ".999999"

    # SYSTEMの値を取得するSQL
    sel_sys_sql = "SELECT * FROM limit_tbl WHERE item = 'SYSTEM'"

    # 測定値の時間と10分前の時間を比較する
    if format(day_time) <= format(before_10min):
        # 測定値が最新でない場合、測定停止のアラート通知を行う
        alert_cur = common.connect_database_project()

        # SYSTEMの値を更新するSQL
        upd_sys_sql = "UPDATE limit_tbl SET flg_sts = 'NG' WHERE item = 'SYSTEM'"

        # SELECTのSQLを実行する
        alert_cur.execute(sel_sys_sql)

        for row in alert_cur.fetchall():
            limit_tbl_flg = row[4]
        if limit_tbl_flg == "OK":
            alert_flg = "ON"  # アラート通知をONにする(発生のLINE通知)
            line_message = line_message + "\n計測が停止しています。"
            # しきい値テーブルの更新
            alert_cur.execute(upd_sys_sql)
        alert_cur.close()

    else:
        # 測定値が最新の場合、しきい値チェック処理
        check_cur = common.connect_database_project()
        update_cur = common.pj_con.cursor()

        # しきい値を取得するSQL
        sel_check_sql = "SELECT * FROM limit_tbl WHERE item IN ('SOIL_TEMP','SOIL_WET','AIR_TEMP_1','AIR_WET');"

        # しきい値を取得するSQLの実行
        check_cur.execute(sel_check_sql)

        # しきい値テーブルから取得した値を変数に格納
        for check_row in check_cur.fetchall():
            # テーブルの要素を変数に入れる
            limit_tbl_item = check_row[1]
            limit_tbl_max = check_row[2]
            limit_tbl_min = check_row[3]
            limit_tbl_flg = check_row[4]

            # 各項目で測定値をチェックする
            if limit_tbl_item == "SOIL_TEMP":  # 土壌温度
                current_value = data_s_temp
            elif limit_tbl_item == "SOIL_WET":  # 土壌湿度
                current_value = data_s_wet
            # elif limit_tbl_item == "soil_ec":  # 電気伝導度
            #     current_value = soil_ec
            elif limit_tbl_item == "AIR_TEMP_1":  # 気温
                current_value = data_a_temp
            elif limit_tbl_item == "AIR_WET":  # 湿度
                current_value = data_a_wet
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
                    line_message = set_line_message(
                        line_message) + "が範囲内になりました。"
                else:
                    pass
            elif current_value < limit_tbl_min:  # 最低値を下回った場合
                if limit_tbl_flg == "OK":  # フラグの値が"OK"ならLINEアラート通知（低下）
                    alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
                    line_message = set_line_message(
                        line_message) + "が設定値より低下しました。"
                else:
                    pass
                limit_tbl_flg = "NG"  # しきい値テーブルのフラグに"NG"を立てる

            elif current_value > limit_tbl_max:  # 最大値を上回った場合
                if limit_tbl_flg == "OK":  # フラグの値が"OK"ならLINEアラート通知（超過）
                    alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
                    line_message = set_line_message(
                        line_message) + "が設定値を超過しました。"
                else:
                    pass
                limit_tbl_flg = "NG"  # しきい値テーブルのフラグに"NG"を立てる

            # しきい値テーブルの更新
            upd_limit_sql = "UPDATE limit_tbl SET flg_sts = %s WHERE item = %s"
            update_cur.execute(upd_limit_sql, (limit_tbl_flg, limit_tbl_item))

        # しきい値テーブルの更新（測定値、取得再開の判定）
        check_cur.execute("SELECT * FROM limit_tbl WHERE item = 'SYSTEM';")

        for check_row in check_cur.fetchall():
            limit_tbl_flg = check_row[4]
        if limit_tbl_flg == "NG":
            alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
            line_message = line_message + "\n計測が再開されました。"
            # リミットテーブルの更新
            update_sql = "UPDATE limit_tbl SET flg_sts = 'OK' WHERE item = 'SYSTEM';"
            update_cur.execute(update_sql)

        check_cur.close()
        update_cur.close()

# # 測定値テーブルに接続し直近の測定値を取得
# conn = mysql.connector.connect(
#     user="root", password="pm#corporate1", host="localhost", database="FARM_IoT")
# cur = conn.cursor()
# cur.execute("select * from farm order by day desc, time desc limit 1;")
# for row in cur.fetchall():
#     day_tbl = row[0]
#     time_tbl = row[1]
#     soil_temp = row[2]
#     soil_wet = row[3]
#     soil_ec = row[4]
#     air_temp = row[5]
#     air_wet = row[6]
# cur.close()

# # 測定値が直近のものか(10分前と比較)判断、測定が止まっていればアラート通知
# DAYTIME = format(day_tbl) + " " + format(time_tbl) + ".999999"
# if format(DAYTIME) > format(before_10min):
#     # 最新の測定値なのでしきい値チェックを行う
#     # しきい値テーブルからレコード取得
#     cur = conn.cursor()
#     cur2 = conn.cursor()
# # --< 2020/04/15 UPDATE-START >--
# #    cur.execute("select * from limit_tbl where item <> 'SYSTEM';")
#     cur.execute(
#         "select * from limit_tbl where item in ('SOIL_TEMP','SOIL_WET','AIR_TEMP_1','AIR_WET');")
# # --< 2020/04/15 UPDATE-END >--
#     for row in cur.fetchall():
#         # テーブルの要素を変数に入れる
#         limit_tbl_item = row[1]
#         limit_tbl_max = row[2]
#         limit_tbl_min = row[3]
#         limit_tbl_flg = row[4]

#         # 各項目で測定値をチェックする
#         if limit_tbl_item == "SOIL_TEMP":  # 土壌温度
#             current_value = soil_temp
#         elif limit_tbl_item == "SOIL_WET":  # 土壌湿度
#             current_value = soil_wet
#         elif limit_tbl_item == "soil_ec":  # 電気伝導度
#             current_value = soil_ec
#         elif limit_tbl_item == "AIR_TEMP_1":  # 気温
#             current_value = air_temp
#         elif limit_tbl_item == "AIR_WET":  # 湿度
#             current_value = air_wet
#         else:
#             pass

#         # しきい値チェック（３回連続で範囲内のときフラグを"OK"に戻す）
#         if (current_value >= limit_tbl_min) and (current_value <= limit_tbl_max):  # 正常の範囲内
#             if limit_tbl_flg == "OK":  # フラグの値が"OK"なら何もしない
#                 pass
#             elif limit_tbl_flg == "NG":  # フラグの値が"NG"なら"1"を立てる
#                 limit_tbl_flg = "1"
#             elif limit_tbl_flg == "1":  # フラグの値が"1"なら"2"を立てる
#                 limit_tbl_flg = "2"
#             elif limit_tbl_flg == "2":  # フラグの値が"2"なら"OK"を立て、復旧のLINEメッセージを設定
#                 alert_flg = "ON"  # アラート通知を"ON"にする（復旧のLINE通知）
#                 limit_tbl_flg = "OK"
#                 line_message = set_line_message(line_message) + "が範囲内になりました。"
#             else:
#                 pass
#         elif current_value < limit_tbl_min:  # 最低値を下回った場合
#             if limit_tbl_flg == "OK":  # フラグの値が"OK"ならLINEアラート通知（低下）
#                 alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
#                 line_message = set_line_message(line_message) + "が設定値より低下しました。"
#             else:
#                 pass
#             limit_tbl_flg = "NG"  # しきい値テーブルのフラグに"NG"を立てる

#         elif current_value > limit_tbl_max:  # 最大値を上回った場合
#             if limit_tbl_flg == "OK":  # フラグの値が"OK"ならLINEアラート通知（超過）
#                 alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
#                 line_message = set_line_message(line_message) + "が設定値を超過しました。"
#             else:
#                 pass
#             limit_tbl_flg = "NG"  # しきい値テーブルのフラグに"NG"を立てる

#         # しきい値テーブルの更新
#         sql = "UPDATE limit_tbl SET flg_sts = %s WHERE item = %s"
#         cur2.execute(sql, (limit_tbl_flg, limit_tbl_item))

#     # しきい値テーブルの更新（測定値、取得再開の判断）
#     cur2.execute("select * from limit_tbl where item = 'SYSTEM';")
#     for row in cur2.fetchall():
#         limit_tbl_flg = row[4]
#     if limit_tbl_flg == "NG":
#         alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
#         line_message = line_message + "\n計測が再開されました。"
#         # しきい値テーブルの更新
#         cur2.execute(
#             "UPDATE limit_tbl SET flg_sts = 'OK' WHERE item = 'SYSTEM';")

#     cur2.close()
#     cur.close()
# else:  # 古い測定値なので測定停止のアラート通知を行う
#     cur = conn.cursor()
#     cur.execute("select * from limit_tbl where item = 'SYSTEM';")
#     for row in cur.fetchall():
#         limit_tbl_flg = row[4]
#     if limit_tbl_flg == "OK":
#         alert_flg = "ON"  # アラート通知を"ON"にする（発生のLINE通知）
#         line_message = line_message + "\n計測が停止しています。"
#         # しきい値テーブルの更新
#         cur.execute(
#             "UPDATE limit_tbl SET flg_sts = 'NG' WHERE item = 'SYSTEM';")
#     cur.close()
# conn.close()


# メイン関数を実行
if __name__ == "__main__":
    main()
