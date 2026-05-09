<?php require_once 'common.php'; check_login(); ?>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>校务管理系统主界面</title></head>
<frameset rows="80,*" frameborder="0">
  <frame src="top.php" name="topFrame" scrolling="no">
  <frameset cols="180,*" frameborder="0">
    <frame src="menu.php" name="menu">
    <frame src="welcome.php" name="main">
  </frameset>
</frameset>
</html>