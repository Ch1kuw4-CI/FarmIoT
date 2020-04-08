<?php

ini_set("max_execution_time", 600);
if (isset($_REQUEST['filename'])) {
    $filename = $_REQUEST['filename'];
}

$url = $filename;
$header = get_headers($url, 1);

echo json_encode(array("name" => $url));

mb_http_output("pass");
header('Content-Type: application/force-download');
header('Content-Length: ' . filesize($url));
header('Content-disposition: attachment; filename="' .  basename($url) . '"');

// out of memoryエラーが出る場合に出力バッファリングを無効
while (ob_get_level() > 0) {
    ob_end_clean();
}
ob_start();

$fp = fopen($url, 'rb');

//ここに判定処理を追加
if (!$fp) {
    //正常に開けなかったら処理修了
    exit;
}

while (!feof($fp)) {
    $buf = fread($fp, 4096);
    echo $buf;
    ob_flush();
    flush();
}
fclose($fp);

ob_end_clean();
