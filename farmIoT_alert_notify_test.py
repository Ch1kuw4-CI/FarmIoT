#!/usr/bin/env python abort_measure LINE alert 
#coding=utf-8
#----- 農地IoT測定値異常時のＬＩＮＥ通知 -----
import requests
import mysql.connector


def LINE_notify(LINE_MESSAGE):
    url = "https://notify-api.line.me/api/notify"
#    token = #Here ACCESS-TOKEN input
    token = "ObFoG8pLNgIGpm04j7t0abp9wKMAJAuHHp08VFihIOb" #<-TEST用のLINEトークン
#    token = "EujRE1ZyuRxXT8JCpwM2Z6o3zfQ5pGIrjbjTbK2aykp" # <--くろぜむアラート用のLINEトークン
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  LINE_MESSAGE}

    r = requests.post(url ,headers = headers ,params=payload)


# LINEへ通知するメッセージを設定
def MESSAGE_SET(STR_MESSAGE):
    if LIMIT_TBL_ITEM == "SOIL_TEMP":
        STR_MESSAGE = STR_MESSAGE + "\n土壌温度(" + format(CURRENT_VALUE) + "℃)"
    elif LIMIT_TBL_ITEM == "SOIL_WET":
        STR_MESSAGE = STR_MESSAGE + "\n土壌湿度(" + format(CURRENT_VALUE) + "%)"
    elif LIMIT_TBL_ITEM == "SOIL_EC":
        STR_MESSAGE = STR_MESSAGE + "\n土壌電気伝導度(" + format(CURRENT_VALUE) + "mS/cm)"
    elif LIMIT_TBL_ITEM == "AIR_TEMP_1":
        STR_MESSAGE = STR_MESSAGE + "\n気温(" + format(CURRENT_VALUE) + "℃)"
    elif LIMIT_TBL_ITEM == "AIR_WET":
        STR_MESSAGE = STR_MESSAGE + "\n湿度(" + format(CURRENT_VALUE) + "%)"
    else:
        pass
    return STR_MESSAGE



# LINE通知のメッセージタイトルを設定
LINE_MESSAGE = "テスト << 農業IoTアラート >>"
ALERT_FLG = "OFF" # LINEアラートが発生したら"ON"になる


# 測定値テーブルに接続し直近の測定値を取得 
conn = mysql.connector.connect(user="root",password="pm#corporate1",host="localhost",database="FARM_IoT")
cur = conn.cursor()
cur.execute("select * from farm order by day desc, time desc limit 1;")
for row in cur.fetchall():
    SOIL_TEMP = row[2]
    SOIL_WET  = row[3]
    SOIL_EC   = row[4]
    AIR_TEMP1 = row[5]
    AIR_WET   = row[6]
cur.close

# しきい値テーブルからレコード取得
cur = conn.cursor()
cur2 = conn.cursor()
cur.execute("select * from limit_tbl;")
for row in cur.fetchall():
    # テーブルの要素を変数に入れる
    LIMIT_TBL_ITEM = row[1]
    LIMIT_TBL_MAX  = row[2]
    LIMIT_TBL_MIN  = row[3]
    LIMIT_TBL_FLG  = row[4]

    # 各項目で測定値をチェックする
    if LIMIT_TBL_ITEM == "SOIL_TEMP": # 土壌温度
        CURRENT_VALUE = SOIL_TEMP
    elif LIMIT_TBL_ITEM == "SOIL_WET": # 土壌湿度
        CURRENT_VALUE = SOIL_WET
    elif LIMIT_TBL_ITEM == "SOIL_EC": # 電気伝導度
        CURRENT_VALUE = SOIL_EC
    elif LIMIT_TBL_ITEM == "AIR_TEMP_1": # 気温
        CURRENT_VALUE = AIR_TEMP1
    elif LIMIT_TBL_ITEM == "AIR_WET": # 湿度
        CURRENT_VALUE = AIR_WET
    else:
        pass

    # しきい値チェック（３回連続で範囲内のときフラグを"OK"に戻す）
    if (CURRENT_VALUE >= LIMIT_TBL_MIN) and (CURRENT_VALUE <= LIMIT_TBL_MAX): # 正常の範囲内
        if (LIMIT_TBL_FLG == "OK"): # フラグの値が"OK"なら何もしない
            pass
        elif (LIMIT_TBL_FLG == "NG"): # フラグの値が"NG"なら"1"を立てる
            LIMIT_TBL_FLG = "1"
        elif (LIMIT_TBL_FLG == "1"): # フラグの値が"1"なら"2"を立てる
            LIMIT_TBL_FLG = "2"
        elif (LIMIT_TBL_FLG == "2"): # フラグの値が"2"なら"OK"を立て、復旧のLINEメッセージを設定
            ALERT_FLG = "ON" # アラート通知を"ON"にする（復旧のLINE通知）
            LIMIT_TBL_FLG = "OK"
            LINE_MESSAGE = MESSAGE_SET(LINE_MESSAGE) + "が範囲内になりました。"
        else:
            pass
    elif (CURRENT_VALUE < LIMIT_TBL_MIN): # 最低値を下回った場合
        if (LIMIT_TBL_FLG == "OK"): # フラグの値が"OK"ならLINEアラート通知（低下）
            ALERT_FLG = "ON" # アラート通知を"ON"にする（発生のLINE通知）
            LINE_MESSAGE = MESSAGE_SET(LINE_MESSAGE) + "が設定値より低下しました。"
        else:
            pass
        LIMIT_TBL_FLG = "NG" # リミットテーブルのフラグに"NG"を立てる

    elif (CURRENT_VALUE > LIMIT_TBL_MAX): # 最大値を上回った場合
        if (LIMIT_TBL_FLG == "OK"): # フラグの値が"OK"ならLINEアラート通知（超過）
            ALERT_FLG = "ON" # アラート通知を"ON"にする（発生のLINE通知）
            LINE_MESSAGE = MESSAGE_SET(LINE_MESSAGE) + "が設定値を超過しました。"
        else:
            pass
        LIMIT_TBL_FLG = "NG" # リミットテーブルのフラグに"NG"を立てる

    # リミットテーブルの更新
    sql = "UPDATE limit_tbl SET flg_sts = %s WHERE item = %s"
    cur2.execute(sql, (LIMIT_TBL_FLG, LIMIT_TBL_ITEM))

cur2.close
cur.close
conn.close



# 新たにアラートが発生、又は復旧した場合はLINE通知する
if ALERT_FLG == "ON":
    LINE_notify(LINE_MESSAGE) # LINEへ通知
    print(LINE_MESSAGE)
