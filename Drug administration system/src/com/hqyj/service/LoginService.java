package com.hqyj.service;

import java.util.List;

import com.hqyj.bean.Login;

public interface LoginService {
	public Login findByName(String name);
	public List queryAll();
}
