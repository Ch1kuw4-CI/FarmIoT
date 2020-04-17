<?php
ini_set("max_execution_time", 180);
// date_default_timezone_set('Asia/Tokyo');

session_start();
if (!isset($_SESSION['USER'])) {
  header('Location: farm_index.php');
  exit;
}

$dateStr = date("Ymd");
$timeStr = date("Hi00");
$org_date = date("Y/m/d");
if (isset($_POST['date'])) {
  if ($_POST['date'] != "") {
    $dateStr = str_replace("/", "", $_POST['date']);
    $org_date = $_POST['date'];
    $timeStr = "000000";
  }
}
if (isset($_GET['date'])) {
  if ($_GET['date'] != "") {
    $dateStr = str_replace("/", "", $_GET['date']);
    $org_date = $_GET['date'];
    $timeStr = "000000";
  }
}
if (isset($_POST['time'])) {
  if ($_POST['time'] != "") {
    $timeStr = str_replace(":", "", $_POST['time']);
  }
}
if (isset($_GET['time'])) {
  if ($_GET['time'] != "") {
    $timeStr = str_replace(":", "", $_GET['time']);
  }
}

$org_date2 = $dateStr;
if (isset($_POST['date_from'])){
	if ($_POST['date_from'] != ""){
		$dateStr = str_replace("/","",$_POST['date_from']);
		$org_date2 = $_POST['date_from'];
		$timeStr = "000000";
	}
}

if (isset($_GET['date_from'])){
	if ($_GET['date_from'] != ""){
		$dateStr = str_replace("/","",$_GET['date_from']);
		$org_date2 = $_GET['date_from'];
		$timeStr = "000000";
	}
}

$org_date3 = $dateStr;
if (isset($_POST['date_to'])){
	if ($_POST['date_to'] != ""){
		$dateStr = str_replace("/","",$_POST['date_to']);
		$org_date3 = $_POST['date_to'];
		$timeStr = "000000";
	}
}
if (isset($_GET['date_to'])){
	if ($_GET['date_to'] != ""){
		$dateStr = str_replace("/","",$_GET['date_to']);
		$org_date3 = $_GET['date_to'];
		$timeStr = "000000";
	}
}

$dArray;

if (file_exists("/var/www/html/infos/" . $dateStr . ".dat")) {
  $data = File("/var/www/html/infos/" . $dateStr . ".dat");
  $label;
  $temperature;
  $humidity;
  $water_temp;
  foreach ($data as $row) {
    $row = preg_replace("/\n/", "", $row);
    $tmp = explode(",", $row);
    $dArray{
      str_replace(":", "", $tmp[0])} = $tmp;
  }
}
$max =  array_fill(1, 10, -999);
$min =  array_fill(1, 10, 999);
$data = array();
for ($i = 0; $i < 1440; $i++) {
  $h = str_pad(floor($i / 60), 2, 0, STR_PAD_LEFT);
  $m = str_pad(floor($i % 60), 2, 0, STR_PAD_LEFT);
  if ($m % 10 == 0) {
    if ($m == "00") {
      $label .= "'" . $h . "時',";
    } else {
      $label .= "'',";
    }
    if (isset($dArray{
      $h . $m . "00"})) {
      for ($j = 1; $j < 10; $j++) {
        if (isset($dArray{
          $h . $m . "00"}[$j]) && $dArray{
          $h . $m . "00"}[$j] != "") {
          $data[$j] .= "'" . $dArray{
            $h . $m . "00"}[$j] . "',";
          if ($max[$j] < $dArray{
            $h . $m . "00"}[$j]) {
            $max[$j] = ceil($dArray{
              $h . $m . "00"}[$j]);
          }
          if ($min[$j] > $dArray{
            $h . $m . "00"}[$j]) {
            $min[$j] = floor($dArray{
              $h . $m . "00"}[$j]);
          }
        } else {
          $data[$j] .= ",";
        }
      }
    } else {
      for ($j = 1; $j < 10; $j++) {
        $data[$j] .= ",";
      }
    }
  }
}
$mainImg = "img/Noimage_image.png";
if (file_exists("/var/www/html/images/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".jpg")) {
  $mainImg = "images/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".jpg";
}




// MySQLより該当日の測定値(平均)を取得（グラフ表示で使用）
$mysqli = new mysqli('localhost', 'root', 'pm#corporate1', 'FARM_IoT');
$sql = "select  substring(date_format(TIME,'%H:%i'),1,4) AS JIKAN,round(AVG(SOIL_TEMP),2) as SOIL_TEMP,round(AVG(SOIL_WET),2) as SOIL_WET,round(AVG(SOIL_EC),2) as SOIL_EC,round(AVG(AIR_TEMP_1),2) as AIR_TEMP1,round(AVG(AIR_WET),2) as AIR_WET FROM farm where DAY = '";
$sql = $sql . str_replace("/","-",$org_date);
$sql = $sql . "' GROUP BY substring(date_format(TIME,'%H:%i'),1,4) order by JIKAN";
$res = $mysqli->query($sql);
$result1 = "";
$result2 = "";
$result3 = "";
$result4 = "";
$result5 = "";

$i_next = 0;
$j_next = 0;
while ($row = $res->fetch_array()) {
  for ($i = $i_next; $i < 25; $i++) {
    for ($j = $j_next; $j < 6; $j++) {
      if (substr($row[0], 0, 2) == $i and substr($row[0], 3, 1) == $j) {
        $result1 = $result1 . $row[1] . ",";
        $result2 = $result2 . $row[2] . ",";
        $result3 = $result3 . $row[3] . ",";
        $result4 = $result4 . $row[4] . ",";
        $result5 = $result5 . $row[5] . ",";
        if ($j == 5) {
          $j_next = 0;
          $i_next = $i + 1;
        } else {
          $j_next = $j + 1;
          $i_next = $i;
        }
        break 2;
      } elseif (substr($row[0], 0, 2) > $i) {
        $result1 = $result1 . ",";
        $result2 = $result2 . ",";
        $result3 = $result3 . ",";
        $result4 = $result4 . ",";
        $result5 = $result5 . ",";
        if ($j == 5) {
          $j_next = 0;
        }
      } elseif (substr($row[0], 0, 2) >= $i and substr($row[0], 3, 1) > $j) {
        $result1 = $result1 . ",";
        $result2 = $result2 . ",";
        $result3 = $result3 . ",";
        $result4 = $result4 . ",";
        $result5 = $result5 . ",";
        if ($j == 5) {
          $j_next = 0;
        }
      }
    }
  }
}

//MySQLより最新の測定値情報を取得
$sql = "select * from farm order by day desc,time desc limit 1";
$res = $mysqli->query($sql);
$row = $res->fetch_array();

$day = $row[0];
$time = $row[1];
$soil_temp = $row[2];
$soil_wet = $row[3];
$soil_ec = $row[4];
$air_temp = $row[5];
$air_wet = $row[6];

$mysqli->close();


?>
<!DOCTYPE html>
<html>

<head>
  <meta http-equiv="Refresh" content="60">
  <title>グラフ</title>
  <meta name="viewport" content="width=device-width">
  <link rel="stylesheet" href="css/jquery-ui.min.css" />

  <script src="js/jquery-1.11.0.min.js"></script>
  <script src="js/chart.js"></script>

  <script src="js/jquery.ui.core.min.js"></script>
  <script src="js/jquery.ui.datepicker.min.js"></script>
  <script src="js/jquery.ui.datepicker-ja.min.js"></script>
  <!--単体フォーム用-->
  <script type="text/javascript">
    $(function() {
      $("#xxdate").datepicker({
        changeYear: true, // 年選択をプルダウン化
        changeMonth: true // 月選択をプルダウン化
      });

      $("#xxdate2").datepicker({
        changeYear: true, // 年選択をプルダウン化
        changeMonth: true // 月選択をプルダウン化
      });

      $("#xxdate3").datepicker({
        changeYear: true, // 年選択をプルダウン化
        changeMonth: true // 月選択をプルダウン化
      });

      // 日本語化
      $.datepicker.regional['ja'] = {
        closeText: '閉じる',
        prevText: '<前',
        nextText: '次>',
        currentText: '今日',
        monthNames: ['1月', '2月', '3月', '4月', '5月', '6月',
          '7月', '8月', '9月', '10月', '11月', '12月'
        ],
        monthNamesShort: ['1月', '2月', '3月', '4月', '5月', '6月',
          '7月', '8月', '9月', '10月', '11月', '12月'
        ],
        dayNames: ['日曜日', '月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日'],
        dayNamesShort: ['日', '月', '火', '水', '木', '金', '土'],
        dayNamesMin: ['日', '月', '火', '水', '木', '金', '土'],
        weekHeader: '週',
        dateFormat: 'yy/mm/dd',
        firstDay: 0,
        isRTL: false,
        showMonthAfterYear: true,
        yearSuffix: '年'
      };
      $.datepicker.setDefaults($.datepicker.regional['ja']);
    });

    function goMovie() {
      aForm.action = "farm_main.php";
      aForm.submit();
    }

    function onGraph() {
      aForm.action = "farm_graph.php";
      aForm.submit();
    }

    function onDownload() {
      aForm.action = "farm_csvdownload.php";
      aForm.submit();
    }
  </script>
  <style>
    /* 年プルダウンの変更 */
    select.ui-datepicker-year {
      height: 2em !important;
      /* 高さ調整 */
      margin-right: 5px !important;
      /* 「年」との余白設定 */
      width: 70px !important;
      /* 幅調整 */
    }

    /* 月プルダウンの変更 */
    select.ui-datepicker-month {
      height: 2em !important;
      /* 高さ調整 */
      margin-left: 5px !important;
      /* 「年」との余白設定 */
      width: 70px !important;
      /* 幅調整 */
    }
  </style>

</head>

<body>
  <form action="farm_main.php" method="post" name="aForm">
    <input type="text" name="date" id="xxdate" readonly="readonly" value="<?php echo $org_date; ?>">
    <input type="button" value="　撮影画像　" onClick="goMovie();"><input type="button" value="　グラフ　" onClick="onGraph();">
    <hr>
    <input type="button" value="グラフデータダウンロード" onclick="onDownload();"> <input type="text" name="date_from" id="xxdate2" readonly="readonly" value="<?php echo $org_date; ?>"> ～ <input type="text" name="date_to" id="xxdate3" readonly="readonly" value="<?php echo $org_date; ?>">
  </form>

  <?php echo $org_date; ?>

  <style type="text/css">
  span.abc {
    display: inline-block;
  }
  </style>

  <strong>
    <font color="white" size="5">
      <div align="center">
        <span class="abc" style="background-color:#000000"><?php echo $day . " " . substr($time, 0, 5) . " 時点"; ?></span>
        <span class="abc" style="background-color:#000000">土壌温度：<?php echo $soil_temp . "℃"; ?></span>
        <span class="abc" style="background-color:#000000">土壌湿度：<?php echo $soil_wet . "％"; ?></span>
        <span class="abc" style="background-color:#000000">電気伝導度：<?php echo $soil_ec . "mS/cm"; ?></span>
        <span class="abc" style="background-color:#000000">気温：<?php echo $air_temp . "℃"; ?></span>
        <span class="abc" style="background-color:#000000">湿度：<?php echo $air_wet . "％"; ?></span>
      </div>

    </font>
  </strong>

  <canvas id="myChart1"></canvas>
  <canvas id="myChart2"></canvas>


</body>

</html>
<script>
  var complexChartOption1 = {
    responsive: false,
    maintainAspectRatio: false,
    scales: {
      xAxes: [ // Ｘ軸設定
        {
          display: true,
          barPercentage: 1,
          //categoryPercentage: 1.8,
          gridLines: {
            display: false
          },
        }
      ],
      yAxes: [{
        id: "y-axis-1",
        type: "linear",
        position: "left",
        scaleLabel: {
          display: true,
          labelString: "気温（℃）"
        },
        ticks: {
          max: 50, //<?php echo $max[1] + 10; ?>,
          min: -10, //<?php echo $min[1] - 10; ?>,
          stepSize: 10
        },
        gridLines: {
          drawOnChartArea: true,
        }
      }],
    }
  };
  var complexChartOption2 = {
    responsive: false,
    maintainAspectRatio: false,
    scales: {
      xAxes: [ // Ｘ軸設定
        {
          display: true,
          barPercentage: 0.9,
          //categoryPercentage: 1.8,
          gridLines: {
            display: false
          },
        }
      ],
      yAxes: [{
        id: "y-axis-1",
        type: "linear",
        position: "left",
        scaleLabel: {
          display: true,
          labelString: "湿度（％）"
        },
        ticks: {
          max: 100, //<?php echo $max[1] + 10; ?>,
          min: 0, //<?php echo $min[1] - 10; ?>,
          stepSize: 10
        },
      }, {
        id: "y-axis-2",
        type: "linear",
        position: "right",
        scaleLabel: {
          display: true,
          labelString: "電気伝導度EC(mS/cm)"
        },
        ticks: {
          max: 2.0, //<?php echo $max[2] + 10; ?>,
          min: 0.0, //<?php echo $min[2] - 10; ?>,
          stepSize: 0.2
        },
        gridLines: {
          drawOnChartArea: false,
        }
      }],
    }
  };
</script>

<script>
  var ctx = document.getElementById("myChart1").getContext("2d");
  ctx.canvas.width = window.innerWidth -69;
  ctx.canvas.height = 250;
  var myChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [<?php echo $label; ?>],
      datasets: [{
          type: "line",
          label: "土壌温度(℃)",
          data: [<?php echo $result1; ?>],
          borderColor: "rgba(255, 255, 0,0.4)",
          backgroundColor: "rgba(255, 255, 0,0.4)",
          fill: false, // 中の色を抜く
          yAxisID: "y-axis-1",
        },
        {
          type: "line",
          label: "気温(℃)",
          data: [<?php echo $result4; ?>],
          borderColor: "rgba(0,255,255,0.4)",
          backgroundColor: "rgba(0,255,255,0.4)",
          fill: false, // 中の色を抜く
          yAxisID: "y-axis-1",
        }
      ]
    },
    options: complexChartOption1
  });

  var ctx = document.getElementById("myChart2").getContext("2d");
  ctx.canvas.width = window.innerWidth - 20;
  ctx.canvas.height = 250;
  var myChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [<?php echo $label; ?>],
      datasets: [{
          type: "line",
          label: "電気伝導度EC(ms/cm)",
          data: [<?php echo $result3; ?>],
          borderColor: "rgba(0, 255, 0,0.4)",
          backgroundColor: "rgba(0, 255, 0,0.4)",
          fill: false, // 中の色を抜く
          yAxisID: "y-axis-2",
        },
        {
          type: "bar",
          label: "土壌湿度(％)",
          data: [<?php echo $result2; ?>],
          borderColor: "rgba(128,0,128,0.4)",
          backgroundColor: "rgba(128,0,128,0.4)",
          fill: false, // 中の色を抜く
          yAxisID: "y-axis-1",
        },
        {
          type: "bar",
          label: "湿度(％)",
          data: [<?php echo $result5; ?>],
          borderColor: "rgba(128,128,0,0.4)",
          backgroundColor: "rgba(128,128,0,0.4)",
          fill: false, // 中の色を抜く
          yAxisID: "y-axis-1",
        }
      ]
    },
    options: complexChartOption2
  });
</script>