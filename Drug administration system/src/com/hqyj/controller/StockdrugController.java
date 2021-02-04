package com.hqyj.controller;

import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import com.hqyj.bean.Stockdrug;
import com.hqyj.bean.Warehouse;
import com.hqyj.service.StockdrugService;
import com.hqyj.service.WarehouseService;

@Controller
@RequestMapping("/user")
public class StockdrugController {
	@Autowired
	private StockdrugService stockdrugService;
	@Autowired
	private WarehouseService warehouseService;
	
	@RequestMapping("/stockdrugList")
	public String stockdrugList(HttpServletRequest request){
		return	querystockdrugAll(request);
	}
	@RequestMapping("/querystockdrugAll")
	public String querystockdrugAll(HttpServletRequest request){
		List<Stockdrug> list = stockdrugService.querystockdrugAll();
		request.setAttribute("stokdrugList", list);
		return "stockdrugList";
	}
	@RequestMapping("/prestockdrugadd")
	public String prestockdrugadd(){
		return "stockdrugadd";
	}
	
	@RequestMapping("/stockdrugadd")
	public String stockdrugadd(Stockdrug stockdrug,Warehouse warehouse){
		
		warehouse.setDrug_id(stockdrug.getDrug_id());
		warehouse.setStock_number(stockdrug.getBuy_num());
		if (warehouseService.queryWarehouseBydrug_id(warehouse)!=null) {
			warehouse.setStock_number((warehouse.getStock_number())+((warehouseService.queryWarehouseBydrug_id(warehouse)).getStock_number()));
			warehouseService.updateWarehouseBydrug_id(warehouse);
			stockdrugService.addStockdrugBydrug_id(stockdrug);
		} else {
			stockdrugService.addStockdrugBydrug_id(stockdrug);
			warehouseService.addWarehouseBydrug_id(warehouse);
		}
		
		return "redirect:/user/querystockdrugAll.do";
		
	}
	@RequestMapping("/stockdrugdelete")
	public String stockdrugdelete(Stockdrug stockdrug){
		stockdrugService.stockdrugdelete(stockdrug.getId());
		return "redirect:/user/querystockdrugAll.do";
	}
	@RequestMapping("/prestockdrugupdate")
	public String prestockdrugupdate(Stockdrug stockdrug,HttpServletRequest request){
		List<Stockdrug> list = stockdrugService.stockdrugQueryById(stockdrug.getId());
		
		request.setAttribute("stokdrugList", list);
		return "stockdrugupdate";
	}
	@RequestMapping("/stockdrugupdate")
	public String stockdrugupdate(Stockdrug stockdrug,Warehouse warehouse){
		String temp="" ;
		int te = 0;
		List<Stockdrug> list = stockdrugService.stockdrugQueryById(stockdrug.getId());
		for (Stockdrug stockdrug2 : list) {
			temp = stockdrug2.getDrug_id();
			te = stockdrug2.getBuy_num();
		}
		
		if ((stockdrug.getDrug_id()).equals(temp)) {
			warehouse.setDrug_id(stockdrug.getDrug_id());
			int a =	warehouseService.queryWarehouseBydrug_id(warehouse).getStock_number();
			a=a-te+stockdrug.getBuy_num();
			warehouse.setStock_number(a);
			warehouseService.updateWarehouseBydrug_id(warehouse);
		} else {
			warehouse.setDrug_id(temp);
			int a = warehouseService.queryWarehouseBydrug_id(warehouse).getStock_number();
			warehouse.setStock_number(a-te);
			warehouseService.updateWarehouseBydrug_id(warehouse);
			
			warehouse.setDrug_id(stockdrug.getDrug_id());
			if (warehouseService.queryWarehouseBydrug_id(warehouse)!=null) {
				warehouse.setStock_number(warehouseService.queryWarehouseBydrug_id(warehouse).getStock_number()+stockdrug.getBuy_num());
				warehouseService.updateWarehouseBydrug_id(warehouse);
			} else {
				warehouse.setStock_number(stockdrug.getBuy_num());
				warehouseService.addWarehouseBydrug_id(warehouse);
			}
		}
		
		stockdrugService.stockdrugupdate(stockdrug);
		
		return "redirect:/user/querystockdrugAll.do";
	}
	
	@RequestMapping("/querystockdrug")
	public String querystockdrug(Stockdrug stockdrug,HttpServletRequest request){
		List<Stockdrug> list =  stockdrugService.querystockdrug(stockdrug);
		request.setAttribute("stokdrugList", list);
		return "stockdrugList";
	}
	
	
	
	
	
	
	
	
	
}
