<%@ page language="java" import="java.util.*,java.net.URLDecoder" pageEncoding="UTF-8"%>
<%@taglib uri = "http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@taglib uri = "http://java.sun.com/jsp/jstl/fmt" prefix="fmt" %>
<%
String path = request.getContextPath();
String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+path+"/";
String loginName="";
Cookie[] cookArr = request.getCookies();
if(cookArr!=null){

	for(Cookie c:cookArr){
		if(c.getName().equals("username")){
			loginName = URLDecoder.decode(c.getValue(),"UTF-8");
		}
		
		c.getValue();
	}
}
%>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <base href="<%=basePath%>">
    
    <title>人员列表</title>
    
	<meta http-equiv="pragma" content="no-cache">
	<meta http-equiv="cache-control" content="no-cache">
	<meta http-equiv="expires" content="0">    
	<meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
	<meta http-equiv="description" content="This is my page">
	<!--
	<link rel="stylesheet" type="text/css" href="styles.css">
	-->
	<script src="js/jquery-3.2.0.min.js"></script>
	<script src="js/jquery.cookie.js"></script>
	<script src="js/my.js"></script>
	<link rel="stylesheet" type="text/css" href="css/my.css">
	<script type="text/javascript">
		function preadd(){
			document.userForm.action = "${pageContext.request.contextPath }/user/preadd.do";
			document.userForm.submit();
		}
		
	    var errorMsg="${requestScope.errorMessage}"; 
	    if(errorMsg!=""){ 
	    	alert(errorMsg);
	     }
	     
	     
	     $().ready(function(){
			$("#list1").addClass("bgclass");

		});
	</script>
	
  </head>
  
  <body >
  <div id="bigbox">
  <div id="title" style="background-image: url(pic/h1.jpg)">
  <div><%=loginName %>欢迎</div>
  <div id="exitbox"><a href="${pageContext.request.contextPath }/user/exitAll.do">退出</a></div>
  </div>
  	
  	<div id="list" style="background-image: url(pic/list.jpg)">
  		 <div id="list1"><a href="${pageContext.request.contextPath }/user/userList.do">人员列表</a></div>
   		 <div id="list2"> <a href="${pageContext.request.contextPath }/user/stockdrugList.do">进药列表</a></div>
   		 <div id="list3"><a href="${pageContext.request.contextPath }/user/querysaledrugAll.do">售药列表</a></div>
   		 <div id="list4"> <a href="${pageContext.request.contextPath }/user/querywarehouseAll.do">库存列表</a></div>
  	</div>
  	<dir id="midbox" style="background-image: url(pic/mid.jpg);">
  
  		<form name="userForm" method="post" action="${pageContext.request.contextPath }/user/queryByUsernameUserType.do">
  			<table width="100%" border="1">
  				<tr>
  					<td>
						用户名<input type="text" name="username"/>
						权限<select name="usertype" >
							<option value="3">所有</option>
							<option value="0">管理</option>
							<option value="1">销售</option>
							<option value="2">库管</option>
							
						</select>
						<input type="submit" value="查询">
						<input type="button" value="增加" onclick="preadd()">
  					</td>
  				</tr>	
  			</table>
  	
  
  
	
		<table width="100%"border=1>
			<tr>
			<td>用户</td>
			<td>权限</td>
			<td>操作</td>
			</tr>
			
			
			<c:forEach items="${userList }" var="user">
				<tr>
					<td>${user.username}</td>
					
					<td>
					<c:choose>
						<c:when test="${user.usertype eq 0}">管理员</c:when>
						<c:when test="${user.usertype eq 1}">销售</c:when>
						<c:when test="${user.usertype eq 2}">库管</c:when>
					</c:choose>
					
					
					</td>
					
					<td>
					<a href="${pageContext.request.contextPath }/user/preupdate.do?id=${user.id}">修改</a>
					<a href="${pageContext.request.contextPath }/user/delete.do?id=${user.id}">删除</a>
					</td>
				</tr>
			</c:forEach>
			
		</table>
		</form>	
	</dir>
	</div>
	 <div id="footbox">&nbsp;© mi.com 京ICP证110507号 京ICP备10046444号 京公网安备11010802020134号 京网文[2017]1530-131号 
						<br>（京）网械平台备字（2018）第00005号 互联网药品信息服务资格证 (京)  
  </div>
  </body>
</html>
