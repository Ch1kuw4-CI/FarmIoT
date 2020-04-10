<?php

/* サムネイル画面から受け取ったパラメータを変数に格納 */
if (isset($_REQUEST['file'])) {
    $f_name = $_REQUEST['file'];
}

/* カメラID、日付、時間を元に結合した動画データの存在確認と、ボタン表示切り替え */
if (file_exists($f_name)) {
    echo '<a href="farm_imgdownload.php?filename=' . $f_name . '" target="_blank" ><input style="width : 160px;height : 50px;" type="button" value="ダウンロード"></a>';
} else {

    return;
}
