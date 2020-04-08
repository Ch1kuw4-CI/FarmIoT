<?php

session_start();
$message = '';
if (isset($_POST['login'])) {
    if ($_POST['id'] == 'kurozemu' && $_POST['password'] == 'miura0313') {
        $_SESSION["USER"] = 'kurozemu';
        header("Location: farm_graph.php");
        exit;
    } else {
        $message = 'IDかPWが間違っています。';
    }
}

?>

<!DOCTYPE html>
<html>

<head>
    <title>ログイン</title>
</head>

<body>
    <h1>ログイン</h1>
    <p style="color: red"><?php echo $message ?></p>
    <form method="post" action="farm_index.php">
        <label for="email">ユーザーID</label>
        <input id="id" type="id" name="id">
        <br>
        <label for="password">パスワード</label>
        <input id="password" type="password" name="password">
        <br>
        <input type="submit" name="login" value="ログイン">
    </form>

</body>

</html>