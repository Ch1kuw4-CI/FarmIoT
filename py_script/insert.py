#!/usr/bin/ python
# -*- coding: utf-8 -*-

from sshtunnel import SSHTunnelForwarder
import MySQLdb
import datetime
import get_soil_logger
import sht30

#temp1 = None
#temp2 = None
#soil = None


# 日付時刻取得
def daytime():
  global day
  global times
  now   = datetime.datetime.today()
  day   = now.strftime('%Y/%m/%d')
  times = now.strftime('%H:%M')


def dataset():
  # 温度湿度　2項目
  global temp1
  temp1 = sht30.main_d()
  # 温度　1項目
  #global temp2
  #temp2 = get_temp_2.main_b()
  # 土壌センサー　3項目
  global soil
  soil = get_soil_logger.main_c()
  #####TEST 実装時に削除する#####
  # soil = [10.0, 10.0, 10.0]
  #####TEST 実装時に削除する#####



# メイン処理
def sql_sshtunnel_connect():
  dataset()   # データ取得
  daytime()   # 日付時刻取得
  # サーバの仕様で直にMySQL接続できないので、一度サーバへSSH接続
  server = SSHTunnelForwarder(
          ("160.16.239.88", 22),
          ssh_password='pm#corporaet1',
          ssh_pkey='/root/.ssh/id_rsa',
          ssh_username="root",
          remote_bind_address=("160.16.239.88", 3306),
          local_bind_address=("127.0.0.1", 3306))
  server.start()
  # insert用処理準備
  columns_list = "(DAY, TIME, SOIL_TEMP, SOIL_WET, SOIL_EC, AIR_TEMP_1, AIR_WET) "
  insert_data = "values (%s, %s, %s, %s, %s, %s, %s)"
  sql = "insert into FARM_IoT.farm " + columns_list + insert_data
  # print(sql)
  conn = MySQLdb.connect(
    host='127.0.0.1', user='farm', password='pm#corporate1', db='FARM_IoT', charset='utf8', port=3306)
  try:
    cursor = conn.cursor()
    cursor.execute(sql, (day, times, soil[2], soil[0], soil[1], temp1[0], temp1[1]))
    conn.commit()
  except:
    print("DB Access Error!")
  finally:
    conn.close()
  server.close()


def debug_print():
  print(day)
  print(times)
  print(soil[0])
  print(soil[1])
  print(soil[2])
  print(temp1[0])
  print(temp1[1])

# メイン処理の呼び出し
sql_sshtunnel_connect()
#debug_print()
