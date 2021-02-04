package com.hqyj.service;

import java.util.List;

import com.hqyj.bean.Warehouse;

public interface WarehouseService {
	public Warehouse queryWarehouseBydrug_id(Warehouse warehouse);
	public void updateWarehouseBydrug_id(Warehouse warehouse);
	public void addWarehouseBydrug_id(Warehouse warehouse);
	public List querywarehouse(Warehouse warehouse);
	public List querywarehouseAll();
	public List queryWarehouseById(int id);
	public void updateWarehouseById(Warehouse warehouse);
}
