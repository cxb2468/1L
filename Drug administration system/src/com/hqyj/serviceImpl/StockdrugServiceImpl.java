package com.hqyj.serviceImpl;

import java.util.List;

import javax.annotation.Resource;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.hqyj.bean.Stockdrug;
import com.hqyj.dao.StockdrugDao;
import com.hqyj.dao.WarehouseDao;
import com.hqyj.service.StockdrugService;
@Service
@Transactional
public class StockdrugServiceImpl implements StockdrugService {
	@Resource
	private StockdrugDao stockdrugDao;
	@Resource
	private WarehouseDao warehouseDao;
	
	
	@Override
	public List querystockdrugAll() {
		// TODO Auto-generated method stub
		return stockdrugDao.querystockdrugAll();
	}

	@Override
	public Stockdrug queryStockdrugBydrug_id(String string) {
		
		return stockdrugDao.queryStockdrugBydrug_id(string);
		
	}

	@Override
	public void updateStockdrugBydrug_id(Stockdrug stockdrug) {
		
		
		 stockdrugDao.updateStockdrugBydrug_id(stockdrug);
		
	}

	@Override
	public void addStockdrugBydrug_id(Stockdrug stockdrug) {
		stockdrugDao.addStockdrugBydrug_id(stockdrug);
		
	}

	@Override
	public void stockdrugdelete(int id) {
		stockdrugDao.stockdrugdelete(id);
		
	}

	@Override
	public List stockdrugQueryById(int id) {
		return stockdrugDao.stockdrugQueryById(id);
	}

	@Override
	public void stockdrugupdate(Stockdrug stockdrug) {
		stockdrugDao.stockdrugupdate(stockdrug);
		
	}

	@Override
	public List querystockdrug(Stockdrug stockdrug) {
		return stockdrugDao.querystockdrug(stockdrug);
	}
}
