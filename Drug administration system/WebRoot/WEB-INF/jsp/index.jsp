<%@ page language="java" import="java.util.*" pageEncoding="UTF-8"%>
<%
String path = request.getContextPath();
String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+path+"/";
%>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <base href="<%=basePath%>">
    
    <title>My JSP 'index.jsp' starting page</title>
	<meta http-equiv="pragma" content="no-cache">
	<meta http-equiv="cache-control" content="no-cache">
	<meta http-equiv="expires" content="0">    
	<meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
	<meta http-equiv="description" content="This is my page">
	<!--
	<link rel="stylesheet" type="text/css" href="styles.css">
	-->
	<style type="text/css">
	
		*{
			margin: 0px;
			padding: 0px;
		}
		input{
		outline: none;
		cursor: pointer;
		}
	
		#biggestbox{
			width: 100%;
			height:100%;
			background-image:url(pic/qqq.jpg);
		}
		
		#userbox{
			position: absolute;
			width: 300px;
			height: 200px;
			background-image:url(pic/525252.jpg);
			left: 50%;
			top: 50%;
			margin-left: -150px;
			margin-top: -100px;
		}
		
		#user{
			width: 200px;
			height: 30px;
			position: absolute;
			left: 50px;
			top: 45px
			
		}
		#password{
			width: 200px;
			height: 30px;
			position: absolute;
			left: 50px;
			top: 95px
		}
		
		#loginbuttom{
			width: 100px;
			height: 30px;
			position: absolute;
			left: 90px;
			top: 140px;
			
		}
		
		#title{
			font-size: 70px;
			position: absolute;
			width: 500px;
			height: 50px;
			left: 100px;
			top: 20px;
			color: white;
		}
		
	</style>
	
	<script type="text/javascript">
	</script>
  </head>
  
  <body>
  <form action="${pageContext.request.contextPath }/user/login.do" method="post">
  
    <div id="biggestbox">
    	<div id="title">药品管理系统</div>
    	<div id="userbox">
    		<input id="user" type="text" placeholder="请输入用户名" name="username">
    		<input id="password" type="password" placeholder="请输入密码" name="password">
    		<input id="loginbuttom" type="submit" value="登录">
    		
    	</div>
    </div>
   </form>
  </body>
</html>
