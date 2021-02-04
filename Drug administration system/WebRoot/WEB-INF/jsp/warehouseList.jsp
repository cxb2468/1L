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
    
    <title>My JSP 'itemsList.jsp' starting page</title>
    
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
		$().ready(function(){
			$("#list4").addClass("bgclass");

		})
	</script>
  </head>
  
  <body >
  <div id="bigbox">
  <div id="title" style="background-image: url(pic/h1.jpg)"><div><%=loginName %>欢迎</div>
  <div id="exitbox"><a href="${pageContext.request.contextPath }/user/exitAll.do">退出</a></div>
  </div>
  	
  	<div id="list" style="background-image: url(pic/list.jpg)">
 		 <div id="list1"><a href="${pageContext.request.contextPath }/user/userList.do">人员列表</a></div>
   		 <div id="list2"> <a href="${pageContext.request.contextPath }/user/stockdrugList.do">进药列表</a></div>
  		 <div id="list3"><a href="${pageContext.request.contextPath }/user/querysaledrugAll.do">售药列表</a></div>
   		 <div id="list4"> <a href="${pageContext.request.contextPath }/user/querywarehouseAll.do">库存列表</a></div>
  	</div>
  	<dir id="midbox" style="background-image: url(pic/mid.jpg)">
  		<form name="warehouseForm" method="post" action="${pageContext.request.contextPath }/user/querywarehouse.do">
  			<table width="100%" border="1">
  				<tr>
  					<td>	
						药品编码<input type="text" name="drug_id">
						库存量<input type="text" name="stock_number">
						生产厂家<input type="text" name="manufacturer">
						<br>
						规格<input type="text" name="standard">
						零售价<input type="text" name="sale_price">
						<input type="submit" value="查询">
  					</td>
  				</tr>	
  			</table>
  	
  
  
	
		<table width="100%"border=1>
			<tr>
			<td>药品编码</td>
			<td>库存量</td>
			<td>生产厂家</td>
			<td>规格</td>
			<td>零售价</td>
			<td>操作</td>
			</tr>
			
			
			<c:forEach items="${warehoustList }" var="warehouse">
				<tr>
					<td>${warehouse.drug_id}</td>
					<td>${warehouse.stock_number}</td>
					<td>${warehouse.manufacturer}</td>
					<td>${warehouse.standard}</td>
					<td>${warehouse.sale_price}</td>
					
					<td>
					<a href="${pageContext.request.contextPath }/user/prewarehouseupdate.do?id=${warehouse.id}">修改</a>
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
