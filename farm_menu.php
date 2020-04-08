<?php
session_start();
if (!isset($_SESSION['USER'])) {
    header('Location: farm_index.php');
    exit;
}

if (isset($_POST['logout'])) {
    session_destroy();
    header('Location: farm_index.php');
    exit;
}
?>

<!DOCTYPE html>
<html>

<head>
    <title>メニュー</title>
    <meta name="viewport" content="width=device-width">
    <link rel="stylesheet" href="css/jquery-ui.min.css" />

    <script src="js/jquery-1.11.0.min.js"></script>
    <script src="js/jquery.ui.core.min.js"></script>
    <script src="js/jquery.ui.datepicker.min.js"></script>
    <script src="js/jquery.ui.datepicker-ja.min.js"></script>
    <!--単体フォーム用-->
    <script type="text/javascript">
        $(function() {
            $('#date').datepicker({
                dateFormat: 'yy/mm/dd', //年月日の並びを変更
            });
        });

        function goMovie() {
            aForm.action = "farm_main.php ";
            aForm.submit();
        }

        function onGraph() {
            aForm.action = "farm_graph.php";
            aForm.submit();
        }
    </script>

</head>

<body>
    <form action="main.php" method="post" target="main" name="aForm">
        <input type="text" name="date" id="date" readonly="readonly"><br>
        <input type="button" value="　撮影画像　" onClick="goMovie();"><input type="button" value="　グラフ　" onClick="onGraph();">
    </form>
    <!--hr>
<form method="post" action="setting.php" target="main">
    <input type="submit" name="logout" value="設定">
</form-->
    <hr>
    <form method="post" action="top.php" target="_top">
        <input type="submit" name="logout" value="ログアウト">
    </form>

</body>

</html>