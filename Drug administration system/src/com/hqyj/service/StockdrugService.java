package com.hqyj.service;

import java.util.List;

import com.hqyj.bean.Stockdrug;

public interface StockdrugService {
	public List querystockdrugAll();
	public Stockdrug queryStockdrugBydrug_id(String string);
	public void updateStockdrugBydrug_id(Stockdrug stockdrug);
	public void addStockdrugBydrug_id(Stockdrug stockdrug);
	public void stockdrugdelete(int id);
	public List stockdrugQueryById(int id);
	public void stockdrugupdate(Stockdrug stockdrug);
	public List querystockdrug(Stockdrug stockdrug);
}
