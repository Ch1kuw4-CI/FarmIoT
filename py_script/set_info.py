"""
各種設定値を取得する処理
"""

#!/usr/bin/ python
# -*- coding: utf-8 -*-

import datetime
import configparser
import json

# 情報を読み込んで整理するやつ
# 読み込むiniファイル
system_ini = '/home/pi/mainsys/system.ini'
connect_ini = '/home/pi/mainsys/connect.ini'
quality_ini = '/home/pi/mainsys/quality.ini'


def main():
    """
    メイン関数
    """
    print('system information.')
    # system_info()
    #get_camera_rstp()
    #get_camera_list()
    #get_dir_info()
    #get_daytime()
    #get_image_info()
    #get_ssh_connect()


def system_info():
    """
    設定値読み込みと一覧表示　確認用関数
    """

    global system_ini
    global connect_ini
    global quality_ini

    config = configparser.ConfigParser()
    # 基本情報読み込み
    now = datetime.datetime.now()
    day = now.strftime('%Y%m%d')
    d_time = now.strftime('%H%M')
    config.read(system_ini)                                             # システム情報ini
    data_dir = config.get('sys_info', 'data_dir')                         # ローカル
    cloud_server_dir = config.get('sys_info', 'cloud_server_dir')         # クラウドサーバdir
    cloud_server_address = config.get('sys_info', 'cloud_server_address')       # クラウドサーバaddress
    cloud_server_pass = config.get('sys_info', 'cloud_server_pass')       # クラウドサーバpass
    # 各種接続情報読み込み
    config.read(connect_ini)                                            # 接続情報ini
    ssh_username = config.get('conn_ssh', 'ssh_username')                 # SSHユーザ名
    ssh_key = config.get('conn_ssh', 'ssh_key')                           # 鍵
    camera_user = config.get('camera', 'camera_user')                     # カメラユーザID
    camera_pass = config.get('camera', 'camera_pass')                     # カメラパスワード
    camera_list = config.get('camera', 'camera_list')                     # カメラ台数
    camera_address = config.get('camera', 'camera_address').split(',')    # カメラIP
    camera_type = json.loads(config.get('camera', 'camera_type'))         # カメラ属性　1陸　2水中
    config = configparser.ConfigParser()
    config.read(quality_ini)
    org = config.get('image_info', 'org')                       # 0 撮影オリジナル
    upload = config.get('image_info', 'upload')                 # 1 アップロード用
    mini = config.get('image_info', 'mini')                    # 2 サムネイル用
    # ALL出力
    print(now)
    print(day)
    print(d_time)
    print(data_dir)
    print(cloud_server_dir)
    print(cloud_server_address)
    print(cloud_server_pass)
    print(ssh_username)
    print(ssh_key)
    print(camera_user)
    print(camera_pass)
    print(camera_list)
    print(camera_address)
    print(camera_type)
    print(org)
    print(upload)
    print(mini)




def get_camera_rstp():
    """
    カメラ情報を取得する関数
    """

    global connect_ini

    config = configparser.ConfigParser()
    config.read(connect_ini)                                            # 接続情報ini
    camera_user = config.get('camera', 'camera_user')                     # カメラユーザID
    camera_pass = config.get('camera', 'camera_pass')                     # カメラパスワード
    camera_list = config.get('camera', 'camera_list')                     # カメラ台数
    camera_address = config.get('camera', 'camera_address').split(',')    # カメラIP
    camera_type = json.loads(config.get('camera', 'camera_type'))         # カメラ属性　1陸　2水中
    #print(camera_user)
    #print(camera_pass)
    #print(camera_list)
    #print(camera_address)
    #print(camera_type)
    i = 0
    url = []
    for i in range(int(camera_list)):
        #print(i)
        if int(camera_type[i]) == 1:
            url.append('rtsp://' + camera_user + ':' + camera_pass + '@' + camera_address[i] + '/554/Streaming/Channels/1')
            #print(url[i])
            i = i + 1
        elif int(camera_type[i]) == 2:
            url.append('rtsp://' + camera_address[i] + '/user=' + camera_user + '_password=' +camera_pass + '_channel=1_stream=1.sdp')
            #print(url[i])
            i = i + 1
        else:
            print('camera_type None.')
    i = 0
    #print('result')
    #for i in range(int(camera_list)):
        #print(url[i])
        #i = i + 1
    #print(url)
    return url


def get_camera_list():
    """
    カメラ一覧を取得する関数
    """

    global connect_ini

    config = configparser.ConfigParser()
    config.read(connect_ini)
    camera_list = config.get('camera', 'camera_list')
    #print(camera_list)
    return camera_list


def get_dir_info():
    """
    ディレクトリ情報を取得する関数
    """

    global system_ini

    config = configparser.ConfigParser()
    config.read(system_ini)
    main_dir = config.get('sys_info', 'main_dir')                   # 0 メインシステムのディレクトリ
    data_dir = config.get('sys_info', 'data_dir')                   # 1 ローカルデータのディレクトリ
    cloud_server_dir = config.get('sys_info', 'cloud_server_dir')   # 2 クラウドサーバのディレクトリ
    dir_info = [main_dir, data_dir, cloud_server_dir]
    #print(dir_info)
    return dir_info


# 日付時刻情報の取得
def get_daytime():
    """
    日付時刻情報を取得する関数
    """

    now = datetime.datetime.now()
    day = now.strftime('%Y%m%d')                                # 0 日付YYMMDD
    d_time = now.strftime('%H%M')                               # 1 時刻HHMM
    daytime = [day, d_time]
    #print(daytime)
    return daytime


def get_image_info():
    """
    画質情報を取得する関数
    """

    global quality_ini

    config = configparser.ConfigParser()
    config.read(quality_ini)
    org = config.get('image_info', 'org')                       # 0 撮影オリジナル
    upload = config.get('image_info', 'upload')                 # 1 アップロード用
    mini = config.get('image_info', 'mini')                    # 2 サムネイル用
    #print(image_info)
    return org, upload, mini


def get_ssh_connect():
    """
    SSH接続情報を取得する関数
    """

    global connect_ini

    config = configparser.ConfigParser()
    config.read(connect_ini)
    server_address = config.get('conn_ssh', 'server_address')   # 0 クラウドサーバアドレス
    server_port = config.get('conn_ssh', 'server_port')         # 1 SSHポート
    ssh_username = config.get('conn_ssh', 'ssh_username')       # 2 アクセス用ユーザ名
    ssh_pass = config.get('conn_ssh', 'ssh_pass')               # 3 SSHパスワード
    ssh_key = config.get('conn_ssh', 'ssh_key')                 # 4 認証鍵
    access_port = config.get('conn_ssh', 'access_port')         # 5 アクセスポート

    # SSH接続情報のreturn
    return server_address, server_port, ssh_username, ssh_pass, ssh_key, access_port

# main関数を呼び出す（直接このスクリプトを呼び出した場合は全情報を出力するようにする
if __name__ == '__main__':
    main()
