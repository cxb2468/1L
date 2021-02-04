package com.hqyj.serviceImpl;

import java.util.List;

import javax.annotation.Resource;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.hqyj.bean.Warehouse;
import com.hqyj.dao.WarehouseDao;
import com.hqyj.service.WarehouseService;
@Service
@Transactional
public class WarehouseServiceImpl implements WarehouseService {
	@Resource
	private WarehouseDao warehouseDao;

	public WarehouseDao getWarehouseDao() {
		return warehouseDao;
	}

	public void setWarehouseDao(WarehouseDao warehouseDao) {
		this.warehouseDao = warehouseDao;
	}

	@Override
	public Warehouse queryWarehouseBydrug_id(Warehouse warehouse) {
		
		return warehouseDao.queryWarehouseBydrug_id(warehouse);
	}

	@Override
	public void updateWarehouseBydrug_id(Warehouse warehouse) {
		warehouseDao.updateWarehouseBydrug_id(warehouse);
	}

	@Override
	public void addWarehouseBydrug_id(Warehouse warehouse) {
		warehouseDao.addWarehouseBydrug_id(warehouse);
		
	}

	@Override
	public List querywarehouse(Warehouse warehouse) {
		return warehouseDao.querywarehouse(warehouse);
	}

	@Override
	public List querywarehouseAll() {
		return warehouseDao.querywarehouseAll();
	}

	@Override
	public List queryWarehouseById(int id) {
		return warehouseDao.queryWarehouseById(id);
	}
	@Override
	public void updateWarehouseById(Warehouse warehouse) {
		
		warehouseDao.updateWarehouseById(warehouse);
	}
	
	
}
