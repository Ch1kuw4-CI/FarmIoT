<?php

/* サムネイル画面から受け取ったパラメータを変数に格納 */
if (isset($_REQUEST['file'])) {
    $f_name = $_REQUEST['file'];
}

/* カメラID、日付、時間を元に切り出し動画データの存在確認と、ボタン表示切り替え */
if (file_exists($f_name)) {
    //すでに生成された動画データが存在する場合、「再生」ボタンを表示する
    // echo '<input type="button" value="　再　生　" onClick="viewVideo(\'' . "serverimg/div_video/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".mp4" . '\');">';

    // $outname = "//192.168.3.12/video/div_video/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".mp4";
    echo '<a href="farm_imgdownload.php?filename=' . $f_name . '"><input style="width : 160px;height : 50px;" type="button" value="ダウンロード"></a>';
} else {
    // リクエストされた日付、時間を取得
    // $req_time = (string) $dateStr . substr((string) $timeStr, 0, 2);
    // // 現在の日付、時間を取得
    // $now = date("YmdH");

    // // リクエスト日付・時間と現在の日付・時間を比較
    // if ($req_time == (string) $now) {
    //     //リクエスト時に録画データは保存されていないため、「動画生成」ボタンは表示しない
    //     return;
    // } else {
    //     echo '<input type="button" id="make_movie_button" value="動画生成" onClick="make_movie();">';
    // }
    return;
}
