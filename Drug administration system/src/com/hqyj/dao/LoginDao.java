package com.hqyj.dao;

import java.util.List;

import com.hqyj.bean.Login;


public interface LoginDao {
	public Login findByName(String name);
	public List queryAll();
}
