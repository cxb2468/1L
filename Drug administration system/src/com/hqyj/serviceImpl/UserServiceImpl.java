package com.hqyj.serviceImpl;

import java.util.List;

import javax.annotation.Resource;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.hqyj.bean.User;
import com.hqyj.dao.UserDao;
import com.hqyj.service.UserService;
@Service
@Transactional
public class UserServiceImpl implements UserService {
	@Resource
	private UserDao dao;

	@Override
	public void add(User user) {
		dao.add(user);
		
	}

	@Override
	public List queryAll() {
		return dao.queryAll();
	}

	@Override
	public boolean delete(int id) {
		// TODO Auto-generated method stub
		return dao.delete(id);
	}

	@Override
	public User queryById(int id) {
		// TODO Auto-generated method stub
		return dao.queryById(id);
	}

	@Override
	public void update(User user) {
		dao.update(user);
		
	}

	@Override
	public List queryByUsernameUserType(User user) {
		return dao.queryByUsernameUserType(user);
	}

	@Override
	public User queryByName(String string) {
		return dao.queryByName(string);
	}
}
