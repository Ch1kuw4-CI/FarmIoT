<?php

/*******************************************************************
静止画から、連結した動画データ作成を呼び出す処理
 ******************************************************************/

// タイムアウト時間を変更する
ini_set("max_execution_time", 180);
sleep(5);

if (isset($_REQUEST['start_date'])) {
    // 区切りのスラッシュを削除して格納する
    $start_date = str_replace("/", "",  $_REQUEST['start_date']);
    // echo $start_date;
}
if (isset($_REQUEST['end_date'])) {
    $end_date = $_REQUEST['end_date'];
    // echo $end_date;
}
if (isset($_REQUEST['start_time'])) {
    $start_time = $_REQUEST['start_time'];
    // echo $start_time;
}
if (isset($_REQUEST['end_time'])) {
    $end_time = $_REQUEST['end_time'];
    // echo $end_time;
}
if (isset($_REQUEST['disp_speed'])) {
    $disp_speed = $_REQUEST['disp_speed'];
    // echo $disp_speed;
}
if (isset($_REQUEST['camera'])) {
    $camera_id = $_REQUEST['camera'];
    // echo $camera_id;
}

// 画像データが格納されているおおもとのパス
// $img_path = "//192.168.3.12/video/img";
$img_path = "/var/www/html/farm/images";


/*****************************************************
切り出し開始・終了日の設定とエラーチェック
/****************************************************/
#切り出し開始の画像格納フォルダ
$f_name_begin = $img_path . "/" . $camera_id . "/" . $start_date;
#切り出し終了の画像格納フォルダ
if ($start_date == $end_date) {
    #開始日と終了日が同一の場合、開始フォルダと終了フォルダは同じフォルダになる
    $f_name_end = $f_name_begin;
} elseif ($start_date < $end_date) {
    #終了日が開始日より大きい場合、終了日をセット
    $f_name_end = $img_path . "/" . $camera_id . "/" . $end_date;
} else {
    #終了日が開始日より小さい場合、エラーメッセージを表示
    // echo "終了日は開始日より後ろの日付を選択";
}

/*****************************************************
切り出し開始・終了時間の設定とエラーチェック
/****************************************************/
#切り出し開始時間
$file_name_begin = $f_name_begin . "/" . $start_date . "_" . $start_time;
#開始時間以下のファイルを取るため、globで取得

#切り出し終了時間
$file_name_end = $f_name_end . "/" . $end_date . "_" . $end_time;

/*****************************************************
指定したファイルを、動画切り出し処理のPythonに渡して実行する
/****************************************************/

//確認用にPwdコマンドを打つ
$test_cmd = "id";
exec($test_cmd, $result, $val);
// echo "id：" . $result[0] . "実行結果:" . $val;

exec('su -', $ret_array);

// Pythonファイルに引数を渡して実行する
$cmd_py = "/usr/local/bin/python /var/www/html/farm/img_merge.py";
$exec_py = "$cmd_py $start_date $end_date $start_time $end_time $disp_speed $f_name_begin $f_name_end $file_name_begin $file_name_end $camera_id";
// $exec_py = '/usr/local/bin/python /var/www/html/farm/img_merge.py 20200325 20200325 02 03 1 /var/www/html/farm/images/1/20200325 /var/www/html/farm/images/1/20200325 /var/www/html/farm/images/1/20200325/20200325_02 /var/www/html/farm/images/1/20200325/20200325_03 1';
exec($exec_py, $result_py, $result_val);

// $url = $result_py[0];
// $download_name = $result_py[1];
// $header = get_headers($url, 1);

// echo json_encode(array("name" => $url));

// mb_http_output("pass");
// header('Content-Type: application/force-download');
// header('Content-Length: ' . filesize($url));
// header('Content-disposition: attachment; filename="' .  basename($url) . '"');

// // out of memoryエラーが出る場合に出力バッファリングを無効
// while (ob_get_level() > 0) {
//     ob_end_clean();
// }
// ob_start();

// $fp = fopen($url, 'rb');

// //ここに判定処理を追加
// if (!$fp) {
//     //正常に開けなかったら処理修了
//     exit;
// }

// while (!feof($fp)) {
//     $buf = fread($fp, 4096);
//     echo $buf;
//     ob_flush();
//     flush();
// }
// fclose($fp);

// ob_end_clean();

echo "実行コマンド" . $exec_py;
echo "実行結果" . $result_py[0];
echo "静止画データ結合成功" . $result_val;
