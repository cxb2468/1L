<?php require_once 'common.php'; check_login(); ?>
<style> a { display:block; padding:6px; text-decoration:none; } a:hover{background:#ddd;} </style>
<div style="background:#f0f0f0; height:100%;">
  <a href="welcome.php" target="main">系统首页</a>
  <b>学生管理</b>
  <a href="student.php?action=list" target="main">在校学生列表</a>
  <a href="left_student.php" target="main">离校人员列表</a>
  <a href="student.php?action=add" target="main">添加学生</a>
  <a href="student.php?action=graduate" target="main">毕业升级</a>
  <a href="student.php?action=transfer" target="main">转学/退学</a>
  <b>教员管理</b>
  <a href="teacher.php?action=list" target="main">教员列表</a>
  <a href="teacher.php?action=add" target="main">添加教员</a>
  <b>成绩管理</b>
  <a href="score.php?action=input" target="main">成绩录入</a>
  <a href="score.php?action=stats" target="main">各班级平均分</a>
  <b>工资管理</b>
  <a href="wage.php?action=list&table=1" target="main">工资表一</a>
  <b>系统设置</b>
  <?php if(has_perm(3)) echo '<a href="class_manage.php" target="main">班级管理</a>'; ?>
  <?php if(has_perm(3)) echo '<a href="class_setup.php" target="main">班级/科目设置</a>'; ?>
  <?php if(has_perm(3)) echo '<a href="admin_user.php" target="main">管理员设置</a>'; ?>
</div>