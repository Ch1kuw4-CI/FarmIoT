"""
プロジェクト内の共通処理関数群
"""
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
line_token = ""  # LINEトークン
common_pj = None  # 共通データベースへの接続情報を保持する変数
pj_con = None  # プロジェクトごとのデータベースへの接続情報を保持する変数
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
