package com.hqyj.serviceImpl;

import java.util.List;

import javax.annotation.Resource;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.hqyj.bean.Saledrug;
import com.hqyj.dao.SaledrugDao;
import com.hqyj.service.SaledrugService;
@Service
@Transactional
public class SaledrugServiceImpl implements SaledrugService {
	@Resource
	private SaledrugDao saledrugDao;

	public SaledrugDao getSaledrugDao() {
		return saledrugDao;
	}

	public void setSaledrugDao(SaledrugDao saledrugDao) {
		this.saledrugDao = saledrugDao;
	}

	@Override
	public List querysaledrugAll() {
		// TODO Auto-generated method stub
		return saledrugDao.querysaledrugAll();
	}

	@Override
	public void saledrugadd(Saledrug saledrug) {
		saledrugDao.saledrugadd(saledrug);
	}

	@Override
	public void saledrugdelete(int id) {
		saledrugDao.saledrugdelete(id);
		
	}

	@Override
	public Saledrug querysaledrugById(int id) {
		// TODO Auto-generated method stub
		return saledrugDao.querysaledrugById(id);
	}

	@Override
	public List querysaledrug(Saledrug saledrug) {
		// TODO Auto-generated method stub
		return saledrugDao.querysaledrug(saledrug);
	}

	@Override
	public void saledrugupdate(Saledrug saledrug) {
		saledrugDao.saledrugupdate(saledrug);
	}
	
	
	
	
	
}
