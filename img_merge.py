# coding: UTF-8

import os
import sys
import datetime
from decimal import *
import shutil
import glob
import urllib.request
import cv2

#img_path
#save_path
#FPSと表示速度の計算
#save_name

now = datetime.datetime.now()

#1コマあたりの表示速度を元に計算したFPS
fps = None
#コピー後連番画像格納パス(ここに連番画像を格納する)
work_path = "/var/www/html/farm/images/work/"
#開始日
start_date = None
#終了日
end_date = None
#開始時間
start_time = None
#終了時間
end_time = None
#開始ファイル名
file_name_begin = None
#終了ファイル名
file_name_end = None
#カメラID
camera_id = None

#年、月、日、時
s_year = None
s_mon = None
s_day = None
s_hour = None
e_year = None
e_mon = None
e_day = None
e_hour = None


#総処理時間
tt = None
th = None

def main():
    """
    メイン関数
    """
    # 引数から、値を取得する

    #開始日
    global start_date
    start_date = sys.argv[1]
    #終了日
    global end_date
    end_date = sys.argv[2]
    #開始時間
    global start_time
    start_time = sys.argv[3]
    #終了時間
    global end_time
    end_time = sys.argv[4]
    #1コマあたりの表示速度
    global disp_speed
    disp_speed = sys.argv[5]
    #切り出し開始フォルダ名
    global file_name_begin
    f_name_begin = sys.argv[6]
    #切り出し終了フォルダ名
    global file_name_end
    f_name_end = sys.argv[7]
    #切り出し開始画像名
    file_name_begin = sys.argv[8]
    #切り出し終了画像名
    file_name_end = sys.argv[9]
    #カメラID
    global camera_id
    camera_id = sys.argv[10]

    #FPS計算処理を呼び出し
    calc_fps(disp_speed)

    #総処理時間計算処理を呼び出し
    calc_process_time()

    #ファイルリネーム処理を呼び出し
    file_rename()

    #ファイル結合処理を呼び出し
    img_merge()

def calc_fps(disp_speed):
    """
    1コマあたりの表示速度から、FPS値を計算する処理
    """
    global fps

    #FPS = 1(sec) / 1コマあたりの表示速度(sec)
    fps = 1.0 / float(disp_speed)
    #FPS値は小数第2位までにする
    fps = Decimal(str(fps)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calc_process_time():
    """
    総処理時間を計算する関数
    """
    global start_time
    global end_time
    global start_date
    global end_date
    global s_year
    global s_mon
    global s_day
    global s_hour
    global e_year
    global e_mon
    global e_day
    global e_hour

    #開始日＋時間、終了日＋時間を比較するため、結合してDateTimeオブジェクトに格納
    #取得した日付・時間を分解
    s_year = start_date[:4]
    s_mon = start_date[4:6]
    s_day = start_date[-2:]
    s_hour = start_time[:2]
    dt_start = datetime.datetime(year=int(s_year), month=int(s_mon), day=int(s_day), hour=int(s_hour))

    #取得した日付・時間を分解
    e_year = end_date[:4]
    e_mon = end_date[4:6]
    e_day = end_date[-2:]
    e_hour = end_time[:2]
    dt_end = datetime.datetime(year=int(e_year), month=int(e_mon), day=int(e_day), hour=int(e_hour))

#確認用
    # print("testあああああああああああ")
    # print(s_year)
    # print(s_mon)
    # print(s_day)
    # print(s_hour)
    # print(e_year)
    # print(e_mon)
    # print(e_day)
    # print(e_hour)

    #終了時間－開始時間＝総時間(tt = total time)
    global tt
    tt = dt_end - dt_start

    #トータル秒数を元に、総切り出し時間を計算する(総秒数 / 60sec / 60min)
    global th
    th = (tt.total_seconds()) / 60 /60

    # print("総切り出し時間は：" + str(th))

def file_rename():
    """
    連結したい画像をworkフォルダにコピーしながら、ファイル名を連番にリネームする関数
    """

    #総時間との比較用カウント変数
    cnt_tt = 1

    # s_hour = start_time[:2]
    # s_day = start_date[-2:]
    # e_hour = end_time[:2]

    #処理時間の初期値を格納する
    pro_year = s_year
    pro_mon = s_mon
    pro_day = s_day
    pro_time = s_hour

    #処理日付の初期値を格納する
    pro_date = datetime.date(year=int(pro_year), month=int(pro_mon), day=int(pro_day))
    pro_date = str(pro_date).replace("-", "")

    #処理時間を保持するためのカウント
    count = 1

    #s_hourを元に切り出しファイル名をずらしていく
    file_name_next = file_name_begin

    #終了時間のファイルになるまでループさせる
    while True:
        # print("cnt_tt =======================================-" + str(cnt_tt))
        # print("pro_day ===== " + pro_day)
        # print("pro_time ===== " + pro_time)

        file_name_next = file_name_next[:-20]

        # print("結合する処理日付" + pro_date)

        #次の処理開始時間を文字列結合する
        file_name_next = file_name_next + pro_date + "/" + pro_date + "_" + pro_time

        # print("file_name_next:" + file_name_next)
        # print("pro_time:" + pro_time)

        #切り出し開始時間からのファイルを取得
        # files = glob.glob(file_name_next + "*.jpg")
        files = sorted(glob.glob(file_name_next + "*00.jpg"))

        # print(file_name_next)
        # print(files)
        # print(work_path)

        #連番を付与しながらコピーする処理
        for i, f in enumerate(files, count):
            ftitle, fext = os.path.splitext(f)
            shutil.copy(f, work_path + '{0:05d}'.format(i) + fext)
            count = count + 1
            # print(f)

        #次のループを回すための後処理
        if int(pro_time) == 23:
            #ファイル名の時間が24になる前に00に戻す
            pro_time = 0

            #日付の計算
            pro_date = datetime.date(year=int(s_year), month=int(s_mon), day=int(s_day))
            # print("計算前の処理日付" + str(pro_date))
            pro_date = pro_date + datetime.timedelta(days=1) #1日加算
            pro_date = str(pro_date).replace("-", "")
            # print("計算後の処理日付" + str(pro_date))
            # print("計算後の処理時間" + str(pro_time))
        else:
            #処理時間をずらす
            pro_time = int(pro_time) + 1

        #10より小さい場合は頭に0付与
        if int(pro_time) < 10:
            # pro_time = "0" + str(pro_time) + "00"
            pro_time = "0" + str(pro_time)
        else:
            # pro_time = str(pro_time) + "00"
            pro_time = str(pro_time)

        #カウントした時間が総時間を超えたら終了
        global th
        cnt_tt = int(cnt_tt) + 1
        if cnt_tt > int(th):
            # print("cnt_tt:" + str(cnt_tt) + " th:" + str(th))
            break

def img_merge():
    """
    画像を結合する関数
    """

    #画像ファイルのパス
    img_path = work_path + "%05d.jpg"

    #VideoCaptureを生成する
    cap = cv2.VideoCapture(str(img_path))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # print(f"width: {width}, height: {height}, fps: {fps}")

    #コーデックの指定
    # fourcc = cv2.VideoWriter_fourcc("H", "2", "6", "4")
    fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")

    #日付ごとの保存フォルダを作成
    save_path = "/var/www/html/farm/images/dl"
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    #保存ファイル名
    #開始日(開始時間)-終了日(終了時間)
    save_name = save_path + "/" + start_date + "_" + start_time + "00-" + end_date + "_" + end_time + "00_cam" + camera_id + ".mp4";

    f_name = start_date + "_" + start_time + "00-" + end_date + "_" + end_time + "00_cam" + camera_id + ".mp4";

    #保存するファイルの存在確認。既に存在する場合は一度削除
    if os.path.isfile(save_name):
        os.remove(save_name)

    #保存する動画の設定
    #ファイル名、コーデック、FPS値、サイズ
    video = cv2.VideoWriter(save_name, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        video.write(frame)

    video.release()

    # #結合処理終了後、workの中身を削除する
    delete_list = glob.glob(work_path + "*.jpg")
    for file in delete_list:
        # print("remove:{0}".format(file))
        os.remove(file)


    user = os.getlogin()
    #print(os.getlogin())
    from_path = "/var/www/html/farm/images/dl/" +f_name
    #ユーザー毎のダウンロードフォルダを取得
    # d_pass = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads') + "/";
    # d_name = d_pass + f_name
    print(from_path)
    print(f_name)

    # print("path"+ from_path + "name:" + f_name + "d_name" + d_name)
    # download(from_path, d_name)


def download(save_name, f_name):

    # url = save_name
    # title = f_name
    # urllib.request.urlretrieve(url, title)

    #結合処理終了後、dlの中身を削除する
    # dl_path = "/var/www/html/farm/images/dl/"
    # delete_list = glob.glob(dl_path + "*mp4")
    # for file in delete_list:
    #     print("remove:{0}".format(file))
    #     os.remove(file)
    pass


#メイン関数の実行
if __name__ == "__main__":
    main()

