package com.hqyj.controller;

import java.util.ArrayList;
import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import com.hqyj.bean.Saledrug;
import com.hqyj.bean.Warehouse;
import com.hqyj.dao.WarehouseDao;
import com.hqyj.service.SaledrugService;
import com.hqyj.service.WarehouseService;

@Controller
@RequestMapping("/user")
public class SaledrugController {
	@Autowired
	private SaledrugService saledrugService;
	@Autowired
	private WarehouseService warehouseService;

	@RequestMapping("/querysaledrugAll")
	public String querysaledrugAll(HttpServletRequest request) {
		List<Warehouse> list = saledrugService.querysaledrugAll();
		request.setAttribute("saledrugList", list);
		return "saledrugList";
	}

	@RequestMapping("/presaledrugadd")
	public String presaledrugadd() {
		return "saledrugadd";
	}

	@RequestMapping("/saledrugadd")
	public String saledrugadd(Saledrug Saledrug, Warehouse warehouse,
			HttpServletRequest request) {
		warehouse.setDrug_id(Saledrug.getDrug_id());
		if (warehouseService.queryWarehouseBydrug_id(warehouse) == null) {
			request.setAttribute("errorMessage", "¿â´æ²»×ã");
			return "saledrugadd";
		} else {
			if (warehouseService.queryWarehouseBydrug_id(warehouse)
					.getStock_number() > Saledrug.getSale_number()) {
				saledrugService.saledrugadd(Saledrug);
				warehouse.setStock_number(warehouseService
						.queryWarehouseBydrug_id(warehouse).getStock_number()
						- Saledrug.getSale_number());
				warehouseService.updateWarehouseBydrug_id(warehouse);
				return "redirect:/user/querysaledrugAll.do";
			} else {
				request.setAttribute("errorMessage", "¿â´æ²»×ã");
				return "saledrugadd";
			}
		}

	}

	@RequestMapping("/saledrugdelete")
	public String saledrugdelete(Saledrug saledrug, Warehouse warehouse) {
		warehouse.setDrug_id(saledrugService
				.querysaledrugById(saledrug.getId()).getDrug_id());
		warehouse.setStock_number(warehouseService.queryWarehouseBydrug_id(
				warehouse).getStock_number()
				+ saledrugService.querysaledrugById(saledrug.getId())
						.getSale_number());
		warehouseService.updateWarehouseBydrug_id(warehouse);

		saledrugService.saledrugdelete(saledrug.getId());
		return "redirect:/user/querysaledrugAll.do";
	}

	@RequestMapping("/querysaledrug")
	public String querysaledrug(Saledrug saledrug, HttpServletRequest request) {
		List<Saledrug> list = saledrugService.querysaledrug(saledrug);
		request.setAttribute("saledrugList", list);
		return "saledrugList";
	}

	@RequestMapping("/presaledrugupdate")
	public String presaledrugupdate(Saledrug saledrug,
			HttpServletRequest request) {
		List<Saledrug> list = new ArrayList<Saledrug>();
		list.add(saledrugService.querysaledrugById(saledrug.getId()));
		request.setAttribute("saledrugList", list);

		return "saledrugupdate";
	}

	@RequestMapping("/saledrugupdate")
	public String saledrugupdate(Saledrug saledrug, Warehouse warehouse,
			HttpServletRequest request) {

		if ((saledrug.getDrug_id()).equals(saledrugService.querysaledrugById(
				saledrug.getId()).getDrug_id())) {
			warehouse.setDrug_id(saledrug.getDrug_id());
			warehouse.setStock_number(warehouseService.queryWarehouseBydrug_id(
					warehouse).getStock_number()
					+ saledrugService.querysaledrugById(saledrug.getId())
							.getSale_number() - saledrug.getSale_number());
			warehouseService.updateWarehouseBydrug_id(warehouse);
			saledrugService.saledrugupdate(saledrug);
		} else {
			warehouse.setDrug_id(saledrugService.querysaledrugById(
					saledrug.getId()).getDrug_id());
			warehouse.setStock_number(warehouseService.queryWarehouseBydrug_id(
					warehouse).getStock_number()
					+ saledrugService.querysaledrugById(saledrug.getId())
							.getSale_number());
			warehouseService.updateWarehouseBydrug_id(warehouse);
			warehouse.setDrug_id(saledrug.getDrug_id());
			if (warehouseService.queryWarehouseBydrug_id(warehouse) == null) {
				request.setAttribute("errorMessage", "¿â´æ²»×ã");
				return querysaledrugAll(request);
			} else {
				if (warehouseService.queryWarehouseBydrug_id(warehouse)
						.getStock_number() > saledrug.getSale_number()) {
					warehouse.setStock_number(warehouseService
							.queryWarehouseBydrug_id(warehouse)
							.getStock_number()
							- saledrug.getSale_number());
					warehouseService.updateWarehouseBydrug_id(warehouse);
					saledrugService.saledrugupdate(saledrug);
				} else {
					request.setAttribute("errorMessage", "¿â´æ²»×ã");
					return querysaledrugAll(request);
				}
			}
		}
		return "redirect:/user/querysaledrugAll.do";
	}

	public WarehouseService getWarehouseService() {
		return warehouseService;
	}

	public void setWarehouseService(WarehouseService warehouseService) {
		this.warehouseService = warehouseService;
	}

	public SaledrugService getSaledrugService() {
		return saledrugService;
	}

	public void setSaledrugService(SaledrugService saledrugService) {
		this.saledrugService = saledrugService;
	}

}
