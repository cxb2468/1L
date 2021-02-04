package com.hqyj.controller;

import java.util.ArrayList;
import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import com.hqyj.bean.User;
import com.hqyj.service.UserService;

@Controller
@RequestMapping("/user")
public class UserController {
	@Autowired
	private UserService userService;
	
	
	@RequestMapping("/queryAll")
	public String queryAll(HttpServletRequest request){
		 List<User> list = userService.queryAll();
		 request.setAttribute("userList", list);
		return "userList";
	}
	
	
	
	
	@RequestMapping("/preadd")
	public String preadd(){
		return "useradd";
	}
	
	@RequestMapping("/add")
	public String add(User user,HttpServletRequest request){
		
		
		
		if (userService.queryByName(user.getUsername())==null) {
			userService.add(user);
		} else {
			request.setAttribute("errorMessage","用户已存在");
		}
		return queryAll(request);
	}
	
	@RequestMapping("/delete")
	public String delete(User user){
		userService.delete(user.getId());
		return "redirect:/user/queryAll.do";
	}
	
	@RequestMapping("/preupdate")
	public String update(User user,HttpServletRequest request){
	 	user =	userService.queryById(user.getId());
	 	List<User> list = new ArrayList<User>();
	 	list.add(user);
		request.setAttribute("userList", list);
		return "userupdate";
	}
	
	@RequestMapping("/update")
	
	public String update(User user){
		userService.update(user);
		return "redirect:/user/queryAll.do";
	}
	
	@RequestMapping("/queryByUsernameUserType")
	
	public String queryByUsernameUserType(User user,HttpServletRequest request){
		 List<User> list = userService.queryByUsernameUserType(user);
		 request.setAttribute("userList", list);
		return "userList";
	}
	

	
	
	
	public UserService getUserService() {
		return userService;
	}
	public void setUserService(UserService userService) {
		this.userService = userService;
	}
	
	
	
	
	
	
	
	
	
	
}
