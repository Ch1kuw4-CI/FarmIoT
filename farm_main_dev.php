<?php
session_start();
ini_set("max_execution_time", 180);
date_default_timezone_set('Asia/Tokyo');

$org_date = date("Ymd");
$dateStr = date("Ymd");
$timeStr = date("Hi00");

/*********************************/
if (isset($_REQUEST['date'])) {
  $dateStr = str_replace("/", "", $_REQUEST['date']);
  $org_date = $_REQUEST['date'];
  $timeStr = "000000";
}
if (isset($_REQUEST['time'])) {
  $timeStr = str_replace(":", "", $_REQUEST['time']);
  $times = $_REQUEST['time'];
}
if (isset($_REQUEST['start_date'])) {
  $start_date = str_replace("/", "", $_REQUEST['start_date']);
  //   echo $start_date;
}
if (isset($_REQUEST['end_date'])) {
  $end_date = str_replace("/", "", $_REQUEST['end_date']);
  //   echo $end_date;
}
if (isset($_REQUEST['start_time'])) {
  $start_time = str_replace("/", "", $_REQUEST['start_time']);
  //   echo $start_time;
}
if (isset($_REQUEST['end_time'])) {
  $end_time = str_replace("/", "", $_REQUEST['end_time']);
  //   echo $end_time;
}
if (isset($_REQUEST['disp_speed'])) {
  $disp_speed = $_REQUEST['disp_speed'];
  //   echo $disp_speed;
}
if (isset($_REQUEST['camera'])) {
  $camera_id = $_REQUEST['camera'];
  //   echo $camera_id;
}
/*********************************/

$dArray;

$data = array();

$sample = 0;

$count = 0;
for ($i = 0; $i < 1440; $i++) {
  $h = str_pad(floor($i / 60), 2, 0, STR_PAD_LEFT);
  $m = str_pad(floor($i % 60), 2, 0, STR_PAD_LEFT);
  if ($m % 10 == 0) {
    if (isset($dArray{
      $h . $m . "00"})) {
      for ($j = 1; $j < 10; $j++) {
        if ($sample == 1) {
          if ($j == 6) {
            if ($count % 2 == 0) {
              $data[6] .= "4,";
            } else {
              $data[6] .= "8,";
            }
            $count++;
          } else {
            if (isset($dArray{
              $h . $m . "00"}[$j])) {
              if ($dArray{
                $h . $m . "00"}[$j] != "0.0") {
                $data[$j] .= $dArray{
                  $h . $m . "00"}[$j] . ",";
              } else {
                $data[$j] .= ",";
              }
            } else {
              $data[$j] .= ",";
            }
          }
        } else {
          if (isset($dArray{
            $h . $m . "00"}[$j])) {
            if ($dArray{
              $h . $m . "00"}[$j] != "0.0") {
              $data[$j] .= $dArray{
                $h . $m . "00"}[$j] . ",";
            } else {
              $data[$j] .= ",";
            }
          } else {
            $data[$j] .= ",";
          }
        }
      }
    }
  }
}

/********************************************************************/
//カメラマスタに接続して、カメラの情報を取得、プルダウンにして表示する
// MySQLへ接続(DB_HOST,DB_USER,DB_PASS)
$mysqli = new mysqli('localhost', 'root', 'pm#corporate1', 'FARM_IoT');
if ($mysqli->connect_error) {
  echo $mysqli->connect_error;
  exit();
} else {
  $mysqli->set_charset("utf8");
}
//カメラ情報を取得するSELECT文格納
$selStr = "SELECT * FROM M_CAMERA WHERE CAMERA_STATUS = 1";

// プルダウン選択前の$camera_idの初期値はカメラ1としておく
if (empty($camera_id)) {
  $camera_id = 1;
}

//プルダウン作成変数の初期化
$camera_data = '';

// カメラのプルダウンで選択した情報を自画面で送信、取得して$camera_id変数に保持する
if (isset($_REQUEST['camera'])) {
  $camera_id = $_REQUEST['camera'];
}

// クエリの実行
if ($result = $mysqli->query($selStr)) {
  while ($row = $result->fetch_assoc()) {
    //row['カラム名']で、各カラムの値を取得する
    //テーブルのデータをOptionタグに成形
    //取得したカメラステータスを表示
    // $status = $row['CAMERA_TYPE'];
    // if ($status === '1') {
    //   $camera_type = '(陸上)';
    // } else {
    //   $camera_type = '(水中)';
    // }

    if ($row['CAMERA_ID'] == $camera_id) {
      //カメラのIDをプルダウンに格納
      $camera_data .= "<option value='" . $row['CAMERA_ID'];
      $camera_data .= "' selected>カメラ:" . $row['CAMERA_ID'] . "</option>";
    } else {
      //カメラのIDをプルダウンに格納
      $camera_data .= "<option value='" . $row['CAMERA_ID'];
      $camera_data .= "'>カメラ:" . $row['CAMERA_ID'] . "</option>";
    }
  }
}
/********************************************************************/

// file_existsで検索する場合はIPアドレスから指定してあげる。
// それ以外はエイリアスのパスで指定する
$mainImg = "img/Noimage_image.png";
$subImg = "img/Noimage_image.png";
// カメラ毎の画像フォルダを参照するように修正 20200130
// if (file_exists("images/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".jpg")) {
//   $mainImg = "images/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".jpg";
//   $subImg = "images/" . $dateStr . "/" . $dateStr . "_" . $timeStr . "_mini.jpg";
// }
if (file_exists("images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".jpg")) {
  $mainImg = "images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $timeStr . ".jpg";
  $subImg = "images/"  . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $timeStr . "_mini.jpg";
}
?>

<!DOCTYPE html>
<html>

<head>
  <!-- 画面のリフレッシュ時間を設定：5分 -->
  <meta http-equiv="Refresh" content="300" name="refTime">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>開発用テスト画面_撮影画像</title>
  <!-- <meta name="viewport" content="width=device-width"> -->
  <link rel="stylesheet" href="css/jquery-ui.min.css" />
  <link rel="stylesheet" href="css/main_dev.css" />
  <link href="css/lightbox.css" rel="stylesheet" />
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
  <script src="js/chart.js"></script>
  <script src="js/jquery.ui.core.min.js"></script>
  <script src="js/jquery.ui.datepicker.min.js"></script>
  <script src="js/jquery.ui.datepicker-ja.min.js"></script>

  <script>
    // サムネイル表示関数
    function viewImage($timeStr) {
      $times = $timeStr.toString();
      document.getElementById("mainImg").src = "<?php echo "images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_"; ?>" + $times + ".jpg";
      document.getElementById("mainImg_large").href = "<?php echo "images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_"; ?>" + $times + ".jpg";
      var img = new Image();
      img.src = "<?php echo "images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_"; ?>" + $times + ".jpg";
      img.onerror = function() {
        document.getElementById("mainImg").src = "img/Noimage_image.png";
        document.getElementById("mainImg_large").href = "img/Noimage_image.png";
      }
      document.getElementById("mainImg").style.display = "block";
    }

    /**
     * ローディング画面表示関数
     *
     * @param msg
     * return void
     */
    function dispLoading(msg) {
      // 引数無し(メッセージなし)を許容
      if (msg == undefined) {
        msg = "";
      }
      // 画面表示メッセージ
      var dispMsg = "<div class='loadingMsg'>" + msg + "</div>";
      // ローディング画像が表示されていない場合のみ出力
      $("body").append("<div id='loading'>" + dispMsg + "</div>");
    }

    /**
     * ローディング画像表示関数
     *
     * @return void
     */
    function removeLoading() {
      $("#loading").remove();
    }
  </script>
  <!--単体フォーム用-->
  <script type="text/javascript">
    $(function() {
      $(".xxdate").datepicker({
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

    /**
     * 日付を変更して自画面遷移
     *
     * @return void
     */
    function goImage() {
      aForm.action = "farm_main_dev.php";
      aForm.submit();
    }

    /**
     *グラフ画面に遷移する処理
     */
    function onGraph() {
      aForm.action = "farm_graph.php";
      aForm.submit();
    }

    /**
     * 静止画データ結合処理を呼び出す関数
     *
     * @return void
     */
    var f_name = "";

    /**
     * 画像結合処理を呼び出す非同期処理
     */
    function image_merge() {
      dispLoading("結合処理中...");

      //meta情報を取得して、リフレッシュを書き換え
      var metaDiscre = document.head.children;
      var metaLength = metaDiscre.length;
      for (var i = 0; i < metaLength; i++) {
        // metaタグをすべてループ
        var proper = metaDiscre[i].getAttribute('name');
        if (proper === 'refTime') {
          //metaの名前がrefTimeの場合(リフレッシュのmeta)、書き換え処理
          var ref = metaDiscre[i];
          //contentに指定しているリフレッシュ秒数を空にする
          ref.setAttribute('content', '');
        }
      }

      var now = new Date();
      var n_year = now.getFullYear();
      var n_mon = now.getMonth() + 1
      if (n_mon < 10) {
        n_mon = "0" + n_mon.toString();
      }
      var n_date = now.getDate();
      // 現在の日付を取得
      var n_today = n_year.toString() + n_mon.toString() + n_date.toString();

      //入力された各種値の取得
      var s_date = document.getElementById("startdate").value;
      var e_date = document.getElementById("enddate").value;
      var s_time = $("#start_time").val();
      var e_time = $("#end_time").val();
      var d_speed = document.getElementById("disp_speed").value;

      // 日付文字列から区切り文字削除
      s_date = s_date.replace(/\//g, "");
      e_date = e_date.replace(/\//g, "");

      // 開始日と終了日が同一かつ、開始時間が終了時間以上の場合は取得範囲エラー
      if (s_date == e_date && s_time >= e_time) {
        alert("有効な開始・終了時間を設定してください");
        removeLoading();
        return;
      } else if (s_date > e_date) {
        // 開始日が終了日より後の場合は取得範囲エラー
        alert("有効な開始・終了時間を設定してください");
        removeLoading();
        return;
      } else if (s_date == "" || e_date == "") {
        // 開始日・終了日が空の場合エラー
        alert("開始・終了時間を入力してください");
        removeLoading();
        return;
      } else if (s_date > n_today || e_date > n_today) {
        // 開始日・終了日が現在日付より後の場合エラー
        alert("開始・終了日は現在の日付と同じまたは前の日付を設定してください");
        removeLoading();
        return;
      }

      // // 画像結合処理のURLを変数に格納
      // serv_url = "http://160.16.239.88/farm/img_merge.php"
      // // 画像連結処理のウィンドウを開く
      // window.open(serv_url + "?start_date=" + s_date + "&end_date=" + e_date + "&start_time=" + s_time + "&end_time=" + e_time + "&disp_speed=" + d_speed + "&camera=" + <?php echo $camera_id ?>)

      // //テストてきにいったんウィンドウが開いたらローディング画像を削除する
      // removeLoading();

      // 非同期処理
      $.ajax({
          url: 'img_merge.php',
          method: 'POST',
          timeout: 300000,
          data: {
            start_date: s_date,
            end_date: e_date,
            start_time: s_time,
            end_time: e_time,
            disp_speed: d_speed,
            camera: '<?php echo $camera_id ?>'
          }
        })
        //通信成功時
        .done(function(data) {
          f_name = '/var/www/html/farm/images/dl/' + s_date + "_" + s_time + "00-" + e_date + "_" + e_time + "00_cam" + <?php echo $camera_id ?> + ".mp4";
          alert('静止画データの結合に成功しました');
        })
        //失敗時
        .fail(function(jqXHR, textStatus, errorThrown) {
          // 通信失敗時の処理
          alert('ファイルの取得に失敗しました。');
          console.log("ajax通信に失敗しました");
          console.log("jqXHR          : " + jqXHR.status); // HTTPステータスが取得
          console.log("textStatus     : " + textStatus); // タイムアウト、パースエラー
          console.log("errorThrown    : " + errorThrown.message); // 例外情報
        })
        //処理終了時
        .always(function(data) {
          //Loading画像を消す
          removeLoading();
          //contentの再設定
          ref.setAttribute('content', '300');
        });
    }

    /**
     * 各種ボタンの切り替え処理
     */
    var playButton = function() {
      $.ajax('cmdbox.php', {
          type: 'get',
          data: {
            file: f_name
          },
          dataType: 'html'
        })
        .done(function(data) {
          document.getElementById("cmdBox").innerHTML = data;
          setTimeout(playButton, 1000);
        })
        // 検索失敗時には、その旨をダイアログ表示
        .fail(function() {
          document.getElementById("cmdBox").innerHTML = "";
        });
    }
    playButton();
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
  <div style=" background-color:#FFF;height: 40px;">
    <table>
      <td>
        <form action="farm_main_dev.php" method="post" name="aForm">
          <input type="button" value="　撮影画像　" onClick="goImage();"><input type="button" value="　グラフ　" onClick="onGraph();">
          <input type="hidden" name="camera" value="<?php echo $camera_id ?>" />
        </form>
      </td>
    </table>
  </div>
  <hr>
  <div>
    <form method='POST' action='farm_main_dev.php'>
      <table>
        <td>
          <input type="text" name="date" class="xxdate" readonly="readonly" value="<?php echo $org_date; ?>">
          <select name='camera'>
            <?php
            echo $camera_data; ?>
          </select>
          <input type='submit' value='送信' />
        </td>
      </table>
    </form>
    <hr>

    <?php echo substr($dateStr, 0, 4); ?>/<?php echo substr($dateStr, 4, 2); ?>/<?php echo substr($dateStr, 6, 2); ?>

    <br>
  </div>
  <div style="padding:20px 0px 0px 0px; width: 100%;">
    <table width="100%">
      <tr>
        <td algin="center" style="text-align:center;">
          <!-- ここに大きな画像を出力する -->
          <a href="<?php echo $mainImg; ?>" data-lightbox="image" target="_blank" rel="noopener noreferrer" id="mainImg_large">
            <img src="<?php echo $mainImg; ?>" width="640" height="360" border=1 style="margin-left:auto;margin-right:auto;display:block" id="mainImg">
          </a>
        </td>
      </tr>
    </table>

    <form action="farm_main_dev.php" method="POST" style="padding-top: 10px;" width="50%">
      <table align="center">
        <tr>
          <th>開始日</th>
          <td>
            <input name=" start_date" type="text" class="xxdate" id="startdate" readonly="readonly" style="width: 80px;">
          </td>
          <th>終了日</th>
          <td>
            <input name="end_date" type="text" class="xxdate" id="enddate" readonly="readonly" style="width: 80px;">
          </td>
          <th>表示速度</th>
          <td>
            <input type="number" name="disp_speed" id="disp_speed" value="0.5" step="0.1" min="0.5" max="5.0" style="width: 80px">
          </td>
        </tr>
        <tr>
          <th>開始時間</th>
          <td>
            <select name="start_time" id="start_time" style="width: 80px;">
              <option value="00" selected=select>00:00</option>
              <option value="01">01:00</option>
              <option value="02">02:00</option>
              <option value="03">03:00</option>
              <option value="04">04:00</option>
              <option value="05">05:00</option>
              <option value="06">06:00</option>
              <option value="07">07:00</option>
              <option value="08">08:00</option>
              <option value="09">09:00</option>
              <option value="10">10:00</option>
              <option value="11">11:00</option>
              <option value="12">12:00</option>
              <option value="13">13:00</option>
              <option value="14">14:00</option>
              <option value="15">15:00</option>
              <option value="16">16:00</option>
              <option value="17">17:00</option>
              <option value="18">18:00</option>
              <option value="19">19:00</option>
              <option value="20">20:00</option>
              <option value="21">21:00</option>
              <option value="22">22:00</option>
              <option value="23">23:00</option>
              <option value="24">24:00</option>
            </select>
          </td>
          <th>終了時間</th>
          <td>
            <select name="end_time" id="end_time" style="width: 80px;">
              <option value="00">00:00</option>
              <option value="01" selected=select>01:00</option>
              <option value="02">02:00</option>
              <option value="03">03:00</option>
              <option value="04">04:00</option>
              <option value="05">05:00</option>
              <option value="06">06:00</option>
              <option value="07">07:00</option>
              <option value="08">08:00</option>
              <option value="09">09:00</option>
              <option value="10">10:00</option>
              <option value="11">11:00</option>
              <option value="12">12:00</option>
              <option value="13">13:00</option>
              <option value="14">14:00</option>
              <option value="15">15:00</option>
              <option value="16">16:00</option>
              <option value="17">17:00</option>
              <option value="18">18:00</option>
              <option value="19">19:00</option>
              <option value="20">20:00</option>
              <option value="21">21:00</option>
              <option value="22">22:00</option>
              <option value="23">23:00</option>
              <option value="24">24:00</option>
            </select>
          </td>
          <th>結合開始</th>
          <td>
            <input type="hidden" name="camera" value="<?php echo $camera_id ?>" />
            <input type="button" value="結合開始" onclick="image_merge()">
          </td>
        </tr>
      </table>
    </form>
    <table align="center">
      <tr>
        <td>
          <!-- ↓ダウンロードボタンを表示する場所を確保 -->
          <label text-align="center" style=" padding-left: 10px;" id="cmdBox"></label>
          <!-- ↑cmdboxの処理でダウンロードボタンを表示する -->
        </td>
      </tr>
    </table>
  </div>
  <div>
    <tr>
      <?php
      $hh = substr($timeStr, 0, 2);
      $m0 = substr($timeStr, 2, 1);
      $min = substr($timeStr, 2, 2);
      if ($min > 50) {
        $min = 50;
      }

      for ($i = 0; $i < 10; $i++) {
        if ($min == 0) {
          $d_min = $m0 . $i;
        } else {
          $d_min = $min + $i;
        }

        // file_existsで検索する場合はIPアドレスから指定してあげる。
        // それ以外はエイリアスのパスで指定する
        $subImg = "img/Noimage_image.png";
        // カメラ毎の画像フォルダを参照するように修正
        // if (file_exists("images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $hh . $m0 . $i . "00_mini.jpg")) {
        //   $subImg = "images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $hh . $m0 . $i . "00_mini.jpg";
        // }
        if (file_exists("images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $hh . $d_min . "00_mini.jpg")) {
          $subImg = "images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $hh . $d_min . "00_mini.jpg";
        }

      ?>
        <td width="10%" algin="center" style="text-align:center;">
          <?php echo substr($timeStr, 0, 2); ?>:<?php echo sprintf('%02d', $min + $i); ?><br />
          <img src="<?php echo $subImg; ?>" width="85" height="48" border=1 style="cursor:pointer;margin-left:auto;margin-right:auto;" onClick="viewImage('<?php echo $hh . $d_min . "00"; ?>');">
        </td>
      <?php } ?>
    </tr>
    </table>

    <div style="text-align:center;width:100%;height:200px;">
      <table style="margin-left:auto;margin-right:auto;">
        <!--追加部分-->
        <tr>
          <td></td>
          <td>00分</td>
          <td>10分</td>
          <td>20分</td>
          <td>30分</td>
          <td>40分</td>
          <td>50分</td>
        </tr>
        <!--追加部分-->
        <?php for ($i = 0; $i < 24; $i++) { ?>
          <tr>
            <td align="right"><?php echo str_pad($i, 2, 0, STR_PAD_LEFT); ?>時</td>
            <?php
            $hh = str_pad($i, 2, 0, STR_PAD_LEFT);
            for ($j = 0; $j < 6; $j++) {
              $m0 = $j;

              // file_existsで検索する場合はIPアドレスから指定してあげる。
              // それ以外はエイリアスのパスで指定する
              $subImg = "img/Noimage_image.png";
              if (file_exists("images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $hh . $m0 . "000_mini.jpg")) {
                $subImg = "images/" . $camera_id . "/" . $dateStr . "/" . $dateStr . "_" . $hh . $m0 . "000_mini.jpg";
              }
            ?>
              <td>
                <a href="?date=<?php echo $dateStr; ?>&time=<?php echo $hh . $m0 ?>000&camera=<?php echo $camera_id ?>">
                  <img src="<?php echo $subImg; ?>" width="85" height="48" border=1 style="margin-left:auto;margin-right:auto;">
                </a>
              </td>
            <?php } ?>
          </tr>
        <?php } ?>
      </table>
    </div>
  </div>
  <script src="js/lightbox.js"></script>
</body>

</html>