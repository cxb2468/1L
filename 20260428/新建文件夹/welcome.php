<?php
// welcome.php - 系统欢迎页（仪表盘）
require_once 'common.php';
check_login();
$conn = db_connect();

// 获取学校名称（从配置读取，若无则默认）
$school_name = "校务管理系统";
$res = $conn->query("SELECT 学校名称 FROM 系统设置表 LIMIT 1");
if ($res && $row = $res->fetch_assoc()) {
    $school_name = $row['学校名称'];
}

// 统计在校学生数
$stu_res = $conn->query("SELECT COUNT(*) as cnt FROM 学籍表");
$student_count = $stu_res ? $stu_res->fetch_assoc()['cnt'] : 0;

// 统计在职教员数
$tea_res = $conn->query("SELECT COUNT(*) as cnt FROM 教员表");
$teacher_count = $tea_res ? $tea_res->fetch_assoc()['cnt'] : 0;

// 统计离校人员数
$left_res = $conn->query("SELECT COUNT(*) as cnt FROM 离校人员名单");
$left_count = $left_res ? $left_res->fetch_assoc()['cnt'] : 0;

// 统计班级数
$class_res = $conn->query("SELECT COUNT(*) as cnt FROM 班级表");
$class_count = $class_res ? $class_res->fetch_assoc()['cnt'] : 0;
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>系统首页</title>
<style>
body { font-family: 微软雅黑,宋体; margin:0; padding:20px; background:#f0f2f5; }
.container { max-width:1000px; margin:0 auto; }
.welcome-box { background:white; border-radius:8px; padding:20px; margin-bottom:20px; box-shadow:0 2px 5px rgba(0,0,0,0.1); }
.stats { display:flex; flex-wrap:wrap; gap:15px; margin-bottom:20px; }
.stat-card { background:white; border-radius:8px; padding:15px; flex:1; min-width:120px; text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.1); }
.stat-number { font-size:32px; font-weight:bold; color:#2c6e9e; }
.stat-label { color:#666; margin-top:8px; }
.shortcuts { background:white; border-radius:8px; padding:15px; box-shadow:0 2px 5px rgba(0,0,0,0.1); }
.shortcuts h3 { margin-top:0; color:#2c6e9e; }
.shortcuts a { display:inline-block; margin:5px 10px; padding:8px 15px; background:#2c6e9e; color:white; text-decoration:none; border-radius:4px; }
.shortcuts a:hover { background:#1e5a7a; }
.footer { margin-top:20px; text-align:center; color:#999; font-size:12px; }
/* IE8 兼容 Flex 使用表格替代 */
.ie8-stats { width:100%; border-collapse:collapse; margin-bottom:20px; }
.ie8-stats td { border:1px solid #ddd; padding:15px; text-align:center; background:white; vertical-align:top; width:25%; }
</style>
</head>
<body>
<div class="container">
    <div class="welcome-box">
        <h2>欢迎使用 <?php echo htmlspecialchars($school_name); ?></h2>
        <p>当前登录用户：<?php echo htmlspecialchars($_SESSION['username']); ?></p>
        <p>系统时间：<?php echo date("Y-m-d H:i:s"); ?></p>
    </div>

    <!-- 统计卡片（兼容 IE8 使用表格布局） -->
    <table class="ie8-stats" cellpadding="0" cellspacing="0">
        <tr>
            <td><div class="stat-number"><?php echo $student_count; ?></div><div class="stat-label">在校学生</div></td>
            <td><div class="stat-number"><?php echo $teacher_count; ?></div><div class="stat-label">在职教员</div></td>
            <td><div class="stat-number"><?php echo $left_count; ?></div><div class="stat-label">离校人员</div></td>
            <td><div class="stat-number"><?php echo $class_count; ?></div><div class="stat-label">教学班级</div></td>
        </tr>
    </table>

    <!-- 快捷入口 -->
    <div class="shortcuts">
        <h3>常用功能</h3>
        <p>
            <a href="student.php?action=list" target="main">学生列表</a>
            <a href="student.php?action=add" target="main">添加学生</a>
            <a href="teacher.php?action=list" target="main">教员列表</a>
            <a href="score.php?action=input" target="main">成绩录入</a>
            <a href="wage.php?action=list&table=1" target="main">工资管理</a>
            <a href="left_student.php" target="main">离校人员</a>
            <?php if(has_perm(3)): ?>
                <a href="admin_user.php" target="main">管理员设置</a>
                <a href="class_manage.php" target="main">班级管理</a>
            <?php endif; ?>
        </p>
    </div>

    <div class="footer">
        校务管理系统 v1.2.0.1073 RELEASE &Copyright; 2010-2026
    </div>
</div>
</body>
</html>