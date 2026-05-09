<?php require_once 'common.php'; check_login(); ?>
<div style="background:#2c6e9e; color:white; padding:10px;">
  <span style="float:right;">欢迎 <?=htmlspecialchars($_SESSION['username'])?> | <a href="logout.php" style="color:white;">退出</a></span>
  <h2 style="margin:0;">校务管理系统</h2>
</div>