package com.hqyj.serviceImpl;

import java.util.List;

import javax.annotation.Resource;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.hqyj.bean.Login;
import com.hqyj.dao.LoginDao;
import com.hqyj.service.LoginService;

@Service
@Transactional
public class LoginServiceImpl implements LoginService {
	@Resource
	private LoginDao dao;

	@Override
	public Login findByName(String name) {
		
		return dao.findByName(name);
	}
	@Override
	public List queryAll() {
		// TODO Auto-generated method stub
		return dao.queryAll();
	}
	
	
	
	
	
}
