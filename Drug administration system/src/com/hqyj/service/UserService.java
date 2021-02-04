package com.hqyj.service;

import java.util.List;

import com.hqyj.bean.User;

public interface UserService {
	public void add(User user);
	public List queryAll();
	public boolean delete(int id);
	public User queryById(int id);
	public void update(User user);
	public List queryByUsernameUserType(User user);
	public User queryByName(String string);
}
