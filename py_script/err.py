"""
共通エラー処理
"""

#!/usr/bin/ python
# -*- coding: utf-8 -*-

import configparser
import os
import time

sys_dir = None
e_limit = None

#共通エラー処理 エラーカウンタが10を超えると再起動します
def main():
    """
    メイン関数
    """

    global sys_dir
    global e_limit

    config = configparser.ConfigParser()
    config.read('/home/pi/mainsys/system.ini')
    sys_dir = config.get('sys_info', 'main_dir')
    e_limit = config.get('sys_info', 'err_limit')
    # print(sys_dir)
    error_counter()


def error_counter():
    """
    エラーカウント処理
    エラーカウントの規定値を設定し、超えた場合は再起動する
    """

    global sys_dir
    global e_limit

    with open(sys_dir + 'e_cnt.dat', 'r') as f_err:
        err = f_err.read()
    e_counta = int(err) + 1
    # print(err)
    if e_counta >= (int(e_limit)):  # エラーカウントが規定数を超えた場合再起動
        with open(sys_dir + 'error.log', 'a') as error_message:
            error_message.write('Error Count 10 Over. System Reboot.')
        with open(sys_dir + 'e_cnt.dat', 'w') as f_err:
            f_err.write('1')
        time.sleep(1)
        os.system('sudo reboot')
    elif e_counta <= (int(e_limit) - 1): # 規定数以下はカウントを+1してエラーメッセージを返す
        with open(sys_dir + 'e_cnt.dat', 'w') as f_err:
            f_err.write(str(e_counta))
        e_msg = 'Error Count ' + str(e_counta) + '.'
        # print(e_msg)
        with open(sys_dir + 'error.log', 'a') as error_message:
            error_message.write(e_msg)
        return e_msg


if __name__ == '__main__':
    main()
