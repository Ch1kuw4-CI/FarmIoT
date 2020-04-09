<?php

// タイムアウト時間を変更する
ini_set("max_execution_time",600);

$dateStr = date("Y/m/d");
$dl_date_from = $dateStr;
if(isset($_POST['date_from'])){
	if($_POST['date_from'] != ""){
		$dateStr = str_replace("/","",$_POST['date_from']);
		$dl_date_from = $_POST['date_from'];
		$timeStr = "000000";
	}
}
if(isset($_GET['date_from'])){
	if($_GET['date_from'] != ""){
		$dateStr = str_replace("/","",$_GET['date_from']);
		$dl_date_from = $_GET['date_from'];
		$timeStr = "000000";
	}
}

$dateStr = date("Y/m/d");
$dl_date_to = $dateStr;
if(isset($_POST['date_to'])){
	if($_POST['date_to'] != ""){
		$dateStr = str_replace("/","",$_POST['date_to']);
		$dl_date_to = $_POST['date_to'];
		$timeStr = "000000";
	}
}
if(isset($_GET['date_to'])){
	if($_GET['date_to'] != ""){
		$dateStr = str_replace("/","",$_GET['date_to']);
		$dl_date_to = $_GET['date_to'];
		$timeStr = "000000";
	}
}


//送信されたfromとtoの日付をチェック
if($dl_date_to < $dl_date_from) {
	$dummy_date = $dl_date_from;
	$dl_date_from = $dl_date_to;
	$dl_date_to = $dummy_date;
}


//ＣＳＶ出力
header("Content-Type: application/octet-stream");
header("Content-Disposition: attachment; filename=". str_replace("/","",$dl_date_from) . "-". str_replace("/","",$dl_date_to) . ".csv");


$mysqli = new mysqli ('localhost', 'root', 'pm#corporate1', 'FARM_IoT');
$mysqli->set_charset('utf8');

//測定値テーブル抽出クエリ
$sql = "SELECT * FROM farm WHERE DAY BETWEEN '" . $dl_date_from. "' AND '". $dl_date_to. "' ORDER BY day,time";


$res = $mysqli->query($sql);

// ヘッダー作成
echo "\"日付\",\"時刻\",\"土壌温度\",\"土壌湿度\",\"電気伝導度\",\"気温\",\"湿度\"\r\n";


while($row = $res->fetch_array()) {
  print("\"" . $row[0]. "\",\""	//日付
             . $row[1]. "\",\""	//時刻
             . $row[2]. "\",\""	//土壌温度
             . $row[3]. "\",\""	//土壌湿度
             . $row[4]. "\",\""	//電気伝導度
             . $row[5]. "\",\""	//気温
             . $row[6]. "\"\r\n");//湿度
}


$mysqli->close();

?>
