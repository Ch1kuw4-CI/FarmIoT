#  coding: UTF-8

import os
import glob

#dlフォルダのパスを設定する
dl_path = "/var/www/html/farm/images/dl/"

def main():
    """
    メイン関数
    """

    #削除処理の呼び出し
    delete_dl()

def delete_dl():
    """
    dlフォルダの中身を削除する関数
    """

    #delete_list変数に、dlフォルダ内の削除するファイル(mp4すべて)を指定
    delete_list = glob.glob(dl_path + "*.mp4")

    #delete_file内をループ、ファイル削除を実行
    for file in delete_list:
        os.remove(file)

#メイン関数の実行
if __name__ == "__main__":
    main()
