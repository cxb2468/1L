<%@ page language="java" import="java.util.*" pageEncoding="UTF-8"%>
<%@taglib uri = "http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@taglib uri = "http://java.sun.com/jsp/jstl/fmt" prefix="fmt" %>
<%
String path = request.getContextPath();
String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+path+"/";
%>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <base href="<%=basePath%>">
    
    <title>My JSP 'itemsList.jsp' starting page</title>
    
	<meta http-equiv="pragma" content="no-cache">
	<meta http-equiv="cache-control" content="no-cache">
	<meta http-equiv="expires" content="0">    
	<meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
	<meta http-equiv="description" content="This is my page">
	<!--
	<link rel="stylesheet" type="text/css" href="styles.css">
	-->
	<link rel="stylesheet" type="text/css" href="css/my.css">
	
	<script src="js/jquery-3.2.0.min.js"></script>
	<script src="js/jquery.cookie.js"></script>
	<script src="js/my.js"></script>
	<script type="text/javascript">
		 $().ready(function(){
			$("#list1").addClass("bgclass");

		});
	</script>
  </head>
  
  <body >
  <div id="bigbox">
  	<div id="title" style="background-image: url(pic/h1.jpg)">
  	<div id="exitbox"><a href="${pageContext.request.contextPath }/user/exitAll.do">退出</a>
  	<input type="button" value="重新填写" onclick="javascript:history.back(-1);"/>
  	</div>
  	</div>
  	
  	<div id="list" style="background-image: url(pic/list.jpg)">
  		 <div id="list1"><a href="${pageContext.request.contextPath }/user/userList.do">人员列表</a></div>
   		 <div id="list2"> <a href="${pageContext.request.contextPath }/user/stockdrugList.do">进药列表</a></div>
   		 <div id="list3"><a href="${pageContext.request.contextPath }/user/querysaledrugAll.do">售药列表</a></div>
   		 <div id="list4"> <a href="${pageContext.request.contextPath }/user/querywarehouseAll.do">库存列表</a></div>
  	</div>
  	<dir id="midbox" style="background-image: url(pic/mid.jpg)">
  		<form name="userForm" method="post" action="${pageContext.request.contextPath }/user/add.do">
  			<table width="100%" border="1">
  				<tr>
  					<td>
						用户名<input type="text" name="username"/>
						密码<input type="text" name="password">
						权限<select name="usertype" >
							<option value="0">管理</option>
							<option value="1">销售</option>
							<option value="2">库管</option>
						</select>
						<input type="submit" value="增加">
  					</td>
  				</tr>	
  			</table>
		
		</form>	
  	</dir>
  </div>
  	 <div id="footbox">&nbsp;© mi.com 京ICP证110507号 京ICP备10046444号 京公网安备11010802020134号 京网文[2017]1530-131号 
						<br>（京）网械平台备字（2018）第00005号 互联网药品信息服务资格证 (京)  
  </div>	
  </body>
</html>
