<?php
// common.php - 公共函数
session_start();
require_once 'mysql_cfg.php';

function db_connect() {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
    if ($conn->connect_error) die("数据库连接失败: " . $conn->connect_error);
    $conn->set_charset("utf8");
    return $conn;
}

function check_login() {
    if (!isset($_SESSION['username'])) {
        header("Location: login.php");
        exit;
    }
}

function has_perm($perm_bit) {
    // 权限字符串如 "1111" 四位分别对应 学生、教员、工资、系统
    return isset($_SESSION['perm']) && substr($_SESSION['perm'], $perm_bit, 1) == '1';
}

function show_msg($msg, $url = '') {
    echo "<script>alert('".addslashes($msg)."');";
    if ($url) echo "location.href='$url';";
    echo "</script>";
    exit;
}

function get_class_list($conn) {
    $res = $conn->query("SELECT 所在班级 FROM 班级表 ORDER BY 所在班级");
    $list = [];
    while($row = $res->fetch_assoc()) $list[] = $row['所在班级'];
    return $list;
}
?>