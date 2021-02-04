package com.hqyj.controller;

import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import com.hqyj.bean.Warehouse;
import com.hqyj.service.WarehouseService;


@Controller
@RequestMapping("/user")
public class WarehouseController {
	@Autowired
	private WarehouseService warehouseService;

	public WarehouseService getWarehouseService() {
		return warehouseService;
	}

	public void setWarehouseService(WarehouseService warehouseService) {
		this.warehouseService = warehouseService;
	}
	
	@RequestMapping("/querywarehouseAll")
	public String querywarehouseAll(HttpServletRequest request){
		
		List<Warehouse> list = warehouseService.querywarehouseAll();
		request.setAttribute("warehoustList", list);
		return "warehouseList";
	}
	
	@RequestMapping("/querywarehouse")
	public String querywarehouse(Warehouse warehouse,HttpServletRequest request){
	    List<Warehouse> list = warehouseService.querywarehouse(warehouse);
		request.setAttribute("warehoustList", list);
		return "warehouseList";
	}
	@RequestMapping("/prewarehouseupdate")
	public String prewarehouseupdate(Warehouse warehouse,HttpServletRequest request){
		 List<Warehouse> list =  warehouseService.queryWarehouseById(warehouse.getId());
		request.setAttribute("warehoustList", list);
		return "warehouseupdate";
	}
	
	@RequestMapping("/warehouseupdate")
	public String warehouseupdate(Warehouse warehouse){
		warehouseService.updateWarehouseById(warehouse);
		return "redirect:/user/querywarehouseAll.do";
		
	}
	
	
}
