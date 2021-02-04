package com.hqyj.dao;

import java.util.List;

import com.hqyj.bean.Saledrug;

public interface SaledrugDao {
	public List querysaledrugAll();
	public void saledrugadd(Saledrug saledrug);
	public void saledrugdelete(int id);
	public Saledrug querysaledrugById(int id);
	public List querysaledrug(Saledrug saledrug);
	public void saledrugupdate(Saledrug saledrug);
}
