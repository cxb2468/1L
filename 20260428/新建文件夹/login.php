<?php
session_start();
require_once 'common.php';
if ($_POST) {
    $user = trim($_POST['username']);
    $pwd = trim($_POST['password']);
    $conn = db_connect();
    $stmt = $conn->prepare("SELECT 用户名,密码,权限 FROM 管理员表 WHERE 用户名=?");
    $stmt->bind_param("s", $user);
    $stmt->execute();
    $res = $stmt->get_result();
    if ($row = $res->fetch_assoc()) {
        if ($pwd == $row['密码']) {
            $_SESSION['username'] = $row['用户名'];
            $_SESSION['perm'] = $row['权限'];
            header("Location: main.php");
            exit;
        }
    }
    show_msg("用户名或密码错误", "login.php");
}
?>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>校务管理系统登录</title></head>
<body style="font-family:微软雅黑;">
<form method="post">
<table align="center" border="0" cellpadding="8" bgcolor="#eee" style="margin-top:100px;">
<tr><td colspan="2" align="center"><b>校务管理系统登录</b></td></tr>
<tr><td>用户名：</td><td><input type="text" name="username" style="width:150px;"></td></tr>
<tr><td>密 码：</td><td><input type="password" name="password" style="width:150px;"></td></tr>
<tr><td>系统提示：<td></tr>
<tr><td>默认用户名：“admin”</td></tr>
<tr><td>密码：“123456”</td></tr>
<tr><td>请在进入系统后及时修改密码</td></tr>
<tr><td colspan="2" align="center"><input type="submit" value="登录"> <input type="reset" value="重置"></td></tr>
</table>
</form>
</body>
</html>