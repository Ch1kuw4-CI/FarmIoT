<?php

/**
 * 共通ログイン画面
 */

session_start();
$message = '';
if (isset($_POST['login'])) {

    if ($_POST['user'] == 'user' && $_POST['pass'] == 'password') {
        //マルキンユーザの場合、マルキンの画面に遷移する
        $_SESSION["USER"] = 'user';
        header("Location: http://160.16.239.88/main.php");
        exit;
    } elseif ($_POST['user'] == 'kurozemu' && $_POST['pass'] == 'miura0313') {
        //くろぜむ農園の画面へ遷移
        $_SESSION["USER"] = 'kurozemu';
        header("Location: http://160.16.239.88/farm/farm_main.php");
        exit;
    } else {
        $message = 'IDかPWが間違っています。';
    }
}

?>

<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>ログイン</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open+Sans:400,700">
    <link rel="stylesheet" href="css/index.css" />
</head>

<body>
    <div id="login">
        <form name='form-login' method="post" action="common_index.php">
            <span class="fontawesome-user"></span>
            <input type="text" id="user" placeholder="Username">

            <span class="fontawesome-lock"></span>
            <input type="password" id="pass" placeholder="Password">

            <input type="submit" name="login" value="Login">
    </div>

    <!-- <h1>ログイン</h1>
    <p style="color: red"><?php //echo $message 
                            ?></p>
    <form method="post" action="index.php">
        <label for="email">ユーザーID</label>
        <input id="id" type="id" name="id">
        <br>
        <label for="password">パスワード</label>
        <input id="password" type="password" name="password">
        <br>
        <input type="submit" name="login" value="ログイン">
    </form> -->

</body>

</html>