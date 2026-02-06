/*
Navicat MySQL Data Transfer


Date: 2019-01-25 15:58:31
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for tbl_airline_information_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airline_information_dat`;
CREATE TABLE `tbl_airline_information_dat` (
  `airline_id` int(3) NOT NULL AUTO_INCREMENT,
  `airline_code` varchar(50) DEFAULT NULL,
  `airline_name` varchar(50) DEFAULT NULL,
  `airline_logo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`airline_id`)
) ENGINE=InnoDB AUTO_INCREMENT=256 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_airport_message_temp_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_message_temp_dat`;
CREATE TABLE `tbl_airport_message_temp_dat` (
  `temp_id` varchar(32) NOT NULL COMMENT '模板id',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `temp_content` text COMMENT '模板内容',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`temp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机场消息模板表';

-- ----------------------------
-- Table structure for tbl_airport_recommend_goods
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_recommend_goods`;
CREATE TABLE `tbl_airport_recommend_goods` (
  `giid` varchar(50) NOT NULL DEFAULT '' COMMENT '商品id',
  `aiid` varchar(50) NOT NULL DEFAULT '' COMMENT '机场id',
  `goods_sort` int(10) NOT NULL DEFAULT '0',
  `is_delete` varchar(10) NOT NULL DEFAULT '98989802' COMMENT '是否删除',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `create_people` varchar(50) NOT NULL,
  `update_people` varchar(50) NOT NULL,
  PRIMARY KEY (`giid`,`aiid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_airport_service_configure_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_configure_dat`;
CREATE TABLE `tbl_airport_service_configure_dat` (
  `configure_id` varchar(32) NOT NULL COMMENT '配置id',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `service_id` varchar(32) DEFAULT NULL COMMENT '服务名称id',
  `type_id` varchar(32) DEFAULT NULL COMMENT '类型id',
  `service_phone` varchar(100) DEFAULT NULL COMMENT '服务电话',
  `service_url` varchar(255) DEFAULT NULL COMMENT '服务链接',
  `service_img_url` varchar(255) DEFAULT NULL COMMENT '服务图片链接',
  `service_content` longtext COMMENT '服务内容',
  `service_supplement` text COMMENT '服务规定',
  `contact` text COMMENT '联系方式',
  `setting_sort` varchar(8) DEFAULT NULL COMMENT '设置排序',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT '0' COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`configure_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机场服务配置表';

-- ----------------------------
-- Table structure for tbl_airport_service_flight_history_messages_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_flight_history_messages_dat`;
CREATE TABLE `tbl_airport_service_flight_history_messages_dat` (
  `history_id` varchar(32) NOT NULL COMMENT '历史提醒id',
  `flight_number` varchar(20) DEFAULT NULL COMMENT '航班号',
  `reservation_reminder` varchar(255) DEFAULT NULL COMMENT '提醒方式',
  `remind_people` text COMMENT '提醒人',
  `seat_number` varchar(20) DEFAULT NULL COMMENT '座位号',
  `auto_type` varchar(4) DEFAULT NULL COMMENT '发送状态',
  `messages_content` text COMMENT '消息内容',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`history_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机场航班历史提醒表';

-- ----------------------------
-- Table structure for tbl_airport_service_flight_reminder_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_flight_reminder_dic`;
CREATE TABLE `tbl_airport_service_flight_reminder_dic` (
  `reminder_id` varchar(32) NOT NULL COMMENT '提醒方式id',
  `reminder_name` varchar(50) DEFAULT NULL COMMENT '提醒方式名称',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`reminder_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机场航班提醒方式表';

-- ----------------------------
-- Table structure for tbl_airport_service_flight_reservation_reminder_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_flight_reservation_reminder_dat`;
CREATE TABLE `tbl_airport_service_flight_reservation_reminder_dat` (
  `reservation_id` varchar(32) NOT NULL COMMENT '预约提醒id',
  `user_id` varchar(50) DEFAULT NULL COMMENT '用户id',
  `flight_record_id` varchar(50) DEFAULT NULL COMMENT '航班信息id',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `flight_number` varchar(20) DEFAULT NULL COMMENT '航班号',
  `user_name` varchar(50) DEFAULT NULL COMMENT '乘机人名称',
  `seat_number` varchar(20) DEFAULT NULL COMMENT '座位号',
  `flight_date` datetime DEFAULT NULL COMMENT '航班出发日期',
  `reservation_name` varchar(50) DEFAULT NULL COMMENT '预约名称',
  `reservation_phone` varchar(50) DEFAULT NULL COMMENT '预约手机号',
  `reservation_reminder` varchar(255) DEFAULT NULL COMMENT '预约提醒方式（多个）',
  `reservation_date` datetime DEFAULT NULL COMMENT '预约时间',
  `reservation_type` varchar(4) DEFAULT NULL COMMENT '预约提醒类型1：普通旅客，2：针对特殊陪伴id',
  `special_service_type` varchar(255) DEFAULT NULL COMMENT '特殊陪伴id',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `scan_type` varchar(20) DEFAULT '',
  PRIMARY KEY (`reservation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机场航班预约提醒表';

-- ----------------------------
-- Table structure for tbl_airport_service_free_entry_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_free_entry_dat`;
CREATE TABLE `tbl_airport_service_free_entry_dat` (
  `unaccompanied_id` varchar(32) NOT NULL COMMENT '无忧畅行服务id',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `user_id` varchar(50) DEFAULT NULL COMMENT '用户id',
  `flight_number` varchar(20) DEFAULT NULL COMMENT '航班号',
  `seat_number` varchar(20) DEFAULT NULL COMMENT '座位号',
  `flight_date` datetime DEFAULT NULL COMMENT '航班日期',
  `flight_status` varchar(4) DEFAULT NULL COMMENT '航班状态',
  `children_name` varchar(50) DEFAULT NULL COMMENT '儿童姓名',
  `children_age` varchar(20) DEFAULT NULL COMMENT '儿童年龄',
  `guardian_name` varchar(50) DEFAULT NULL COMMENT '监护人姓名',
  `guardian_phone` varchar(20) DEFAULT NULL COMMENT '监护人联系方式',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`unaccompanied_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='无忧畅行服务表';

-- ----------------------------
-- Table structure for tbl_airport_service_lost_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_lost_dat`;
CREATE TABLE `tbl_airport_service_lost_dat` (
  `detailed_id` varchar(32) NOT NULL COMMENT '清单id',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `detailed_name` varchar(50) DEFAULT NULL COMMENT '清单名称',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`detailed_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='失物招领清单表';

-- ----------------------------
-- Table structure for tbl_airport_service_lost_detail_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_lost_detail_dat`;
CREATE TABLE `tbl_airport_service_lost_detail_dat` (
  `missing_id` varchar(32) NOT NULL COMMENT '失物id',
  `detailed_id` varchar(32) DEFAULT NULL COMMENT '清单id',
  `missing_code` varchar(50) DEFAULT NULL COMMENT '失物code',
  `things_name` varchar(50) DEFAULT NULL COMMENT '物品名称',
  `lost_region` varchar(50) DEFAULT NULL COMMENT '丢失区域',
  `lost_date` datetime DEFAULT NULL COMMENT '丢失时间',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`missing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='失物招领清单明细表';

-- ----------------------------
-- Table structure for tbl_airport_service_name_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_name_dic`;
CREATE TABLE `tbl_airport_service_name_dic` (
  `service_id` varchar(32) NOT NULL COMMENT '服务id',
  `service_name` varchar(50) DEFAULT NULL COMMENT '服务名称',
  `type_id` varchar(32) DEFAULT NULL COMMENT '类型id',
  `service_url` varchar(255) DEFAULT NULL COMMENT '服务url',
  `service_icon` varchar(255) DEFAULT NULL COMMENT '服务图片',
  `service_web_icon` varchar(255) DEFAULT NULL COMMENT '前端展示icon',
  `service_banner` varchar(255) DEFAULT NULL COMMENT '服务banner',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT '0' COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `service_web_icon2` varchar(255) DEFAULT '',
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机场服务名称表';

-- ----------------------------
-- Table structure for tbl_airport_service_type_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_type_dic`;
CREATE TABLE `tbl_airport_service_type_dic` (
  `type_id` varchar(32) NOT NULL COMMENT '类型id',
  `type_name` varchar(50) DEFAULT NULL COMMENT '类型名称',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='机场服务类型表';

-- ----------------------------
-- Table structure for tbl_airport_service_unaccompanied_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_service_unaccompanied_dat`;
CREATE TABLE `tbl_airport_service_unaccompanied_dat` (
  `unaccompanied_id` varchar(32) NOT NULL COMMENT '无人陪伴服务id',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `user_id` varchar(50) DEFAULT NULL COMMENT '用户id',
  `flight_number` varchar(20) DEFAULT NULL COMMENT '航班号',
  `flight_date` datetime DEFAULT NULL COMMENT '航班日期',
  `flight_status` varchar(4) DEFAULT NULL COMMENT '航班状态',
  `children_name` varchar(50) DEFAULT NULL COMMENT '儿童姓名',
  `children_age` varchar(20) DEFAULT NULL COMMENT '儿童年龄',
  `children_six` varchar(20) DEFAULT NULL COMMENT '儿童性别',
  `guardian_name` varchar(50) DEFAULT NULL COMMENT '监护人姓名',
  `guardian_phone` varchar(20) DEFAULT NULL COMMENT '监护人联系方式',
  `feeder_name` varchar(50) DEFAULT NULL COMMENT '送机人姓名',
  `feeder_phone` varchar(20) DEFAULT NULL COMMENT '送机人联系方式',
  `pick_up_name` varchar(50) DEFAULT NULL COMMENT '接机人姓名',
  `pick_up_phone` varchar(20) DEFAULT NULL COMMENT '接机人联系方式',
  `status` varchar(4) DEFAULT NULL COMMENT '状态（7001：待审核;7002：已审核;7003：审核不通过;7004：审核通过）',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`unaccompanied_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='无人陪伴服务表';

-- ----------------------------
-- Table structure for tbl_airport_terminal_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_terminal_dat`;
CREATE TABLE `tbl_airport_terminal_dat` (
  `airport_terminal_id` varchar(50) NOT NULL COMMENT 'id',
  `airport_id` varchar(50) NOT NULL COMMENT '机场id',
  `terminal_name` varchar(50) NOT NULL COMMENT '航站楼名称',
  `terminal_remark` varchar(50) DEFAULT NULL COMMENT '备注',
  `airport_terminal_sort` int(11) NOT NULL DEFAULT '0' COMMENT '排序',
  `update_people` varchar(50) DEFAULT NULL COMMENT '更新人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `is_delete` varchar(4) DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`airport_terminal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_airport_terminal_gate_business_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_terminal_gate_business_rlt`;
CREATE TABLE `tbl_airport_terminal_gate_business_rlt` (
  `airport_terminal_gate_id` varchar(50) NOT NULL COMMENT '登机口id',
  `business_id` varchar(50) NOT NULL COMMENT '店铺id',
  `gate_business_remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(50) DEFAULT NULL COMMENT '更新人',
  `is_delete` varchar(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`airport_terminal_gate_id`,`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_airport_terminal_gate_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_airport_terminal_gate_dat`;
CREATE TABLE `tbl_airport_terminal_gate_dat` (
  `airport_terminal_gate_id` varchar(50) NOT NULL COMMENT '主键',
  `airport_terminal_id` varchar(50) NOT NULL COMMENT '航站楼id',
  `gate_flag` varchar(4) DEFAULT '1' COMMENT '1:出发口1，2:到达口，3:登机口，',
  `gate_name` varchar(50) NOT NULL COMMENT '登机口名称',
  `gate_remark` varchar(50) DEFAULT NULL COMMENT '备注',
  `gate_sort` int(11) DEFAULT '0' COMMENT '排序',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_people` varchar(50) DEFAULT NULL,
  `is_delete` varchar(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`airport_terminal_gate_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_ams_user_airport_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_ams_user_airport_rlt`;
CREATE TABLE `tbl_ams_user_airport_rlt` (
  `rlt_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '关联ID',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '机场系统用户ID',
  `airport_id` varchar(50) NOT NULL DEFAULT '' COMMENT '机场ID',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COMMENT='用户机场关联表';

-- ----------------------------
-- Table structure for tbl_ams_user_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_ams_user_info_dat`;
CREATE TABLE `tbl_ams_user_info_dat` (
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `login_name` varchar(50) DEFAULT NULL COMMENT '用户登陆名称',
  `user_name` varchar(50) DEFAULT NULL COMMENT '用户昵称',
  `password` varchar(255) NOT NULL DEFAULT '' COMMENT '密码',
  `role` varchar(255) NOT NULL DEFAULT '' COMMENT '角色',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机场服务管理用户信息表';

-- ----------------------------
-- Table structure for tbl_app_advertising_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_app_advertising_dat`;
CREATE TABLE `tbl_app_advertising_dat` (
  `advertising_id` varchar(50) NOT NULL,
  `advertising_menu_name` varchar(50) DEFAULT '' COMMENT '广告菜单名称',
  `upper_advertising_id` varchar(50) DEFAULT '' COMMENT '上级菜单id',
  `advertising_menu_sort` int(11) DEFAULT '0' COMMENT '排序',
  `advertising_menu_remark` varchar(100) DEFAULT '' COMMENT '备注',
  `is_leaf` varchar(4) NOT NULL COMMENT '是否叶子节点',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_people` varchar(50) DEFAULT '',
  `is_delete` varchar(4) DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`advertising_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_article_airport_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_article_airport_rlt`;
CREATE TABLE `tbl_article_airport_rlt` (
  `article_airport_relation_id` varchar(50) NOT NULL COMMENT '文章机场关系表id',
  `article_id` varchar(50) DEFAULT NULL COMMENT '文章id',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`article_airport_relation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='文章机场对应关系';

-- ----------------------------
-- Table structure for tbl_article_information_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_article_information_dat`;
CREATE TABLE `tbl_article_information_dat` (
  `article_id` varchar(50) NOT NULL COMMENT '文章id',
  `article_name` varchar(50) DEFAULT '' COMMENT '文章名称',
  `article_introduce` varchar(200) CHARACTER SET utf8mb4 DEFAULT '' COMMENT '文章介绍',
  `article_content` longtext CHARACTER SET utf8mb4 COMMENT '文章内容',
  `article_pic_address` varchar(255) DEFAULT NULL COMMENT '文章主图片地址',
  `article_examine` varchar(4) DEFAULT '0' COMMENT '文章是否审核 0：未审核，1：审核通过，2：审核失败',
  `article_sort` varchar(8) DEFAULT NULL COMMENT '文章排序',
  `article_hot` varchar(8) DEFAULT NULL COMMENT '文章热度',
  `article_thumb_url` varchar(200) DEFAULT NULL COMMENT '文章缩略图',
  `article_pub_headimg` varchar(200) DEFAULT NULL COMMENT '发布人头像',
  `article_pub_nickname` varchar(200) DEFAULT NULL COMMENT '发布人昵称',
  `is_home` varchar(4) DEFAULT NULL COMMENT '是否显示在首页',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT '0' COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`article_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='文章表';

-- ----------------------------
-- Table structure for tbl_article_info_type_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_article_info_type_dat`;
CREATE TABLE `tbl_article_info_type_dat` (
  `article_type_relation_id` varchar(32) NOT NULL COMMENT '文章分类关系表id',
  `article_type_id` varchar(32) NOT NULL COMMENT '文章分类id',
  `article_id` varchar(32) NOT NULL COMMENT '文章id',
  `is_home` varchar(4) DEFAULT '0' COMMENT '是否展示在首页',
  `article_sort` int(11) DEFAULT '0' COMMENT '文章排序',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT '0' COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`article_type_relation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='文章分类对应文章表\r\n';

-- ----------------------------
-- Table structure for tbl_article_statistics_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_article_statistics_dat`;
CREATE TABLE `tbl_article_statistics_dat` (
  `article_relation_id` varchar(32) NOT NULL COMMENT '文章计数关系id',
  `article_id` varchar(32) NOT NULL COMMENT '文章id',
  `article_collection` varchar(20) DEFAULT '0' COMMENT '文章收藏',
  `article_praise_sum` varchar(20) DEFAULT '0' COMMENT '文章点赞数',
  `article_like` varchar(20) DEFAULT '0' COMMENT '文章喜爱数',
  `article_crux` varchar(255) DEFAULT NULL COMMENT '文章关键字',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT '0' COMMENT '是否删除',
  `remark` varchar(200) DEFAULT '' COMMENT '备注',
  PRIMARY KEY (`article_relation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='文章计数关系表';

-- ----------------------------
-- Table structure for tbl_article_type_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_article_type_dic`;
CREATE TABLE `tbl_article_type_dic` (
  `article_type_id` varchar(32) NOT NULL COMMENT '文章类型id',
  `type_name` varchar(50) DEFAULT NULL COMMENT '类型名称',
  `father_type_id` varchar(32) DEFAULT NULL COMMENT '父类型id',
  `num_config_code` varchar(255) DEFAULT NULL COMMENT '显示数量配置',
  `is_home` varchar(4) DEFAULT '0' COMMENT '是否展示在首页',
  `type_pic` varchar(200) DEFAULT '' COMMENT '类型图片',
  `type_pic_inside` varchar(200) DEFAULT '' COMMENT '分类二级图',
  `type_sort` int(11) DEFAULT '0' COMMENT '排序',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT '0' COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `type_ico` varchar(255) DEFAULT '' COMMENT 'icon',
  `type_url` varchar(255) DEFAULT '' COMMENT 'url跳转地址',
  PRIMARY KEY (`article_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='文章分类表';

-- ----------------------------
-- Table structure for tbl_benefit_function_model_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_benefit_function_model_dat`;
CREATE TABLE `tbl_benefit_function_model_dat` (
  `function_model_id` int(8) NOT NULL AUTO_INCREMENT COMMENT '功能模块id',
  `model_name` varchar(50) NOT NULL COMMENT '模块名称',
  `special_picture` varchar(255) NOT NULL COMMENT '特殊图片： 活动或火爆等其他图片',
  `common_picture` varchar(255) NOT NULL COMMENT '普通图片',
  `disable_picture` varchar(255) NOT NULL COMMENT '不可以点击的图片',
  `model_url` varchar(255) CHARACTER SET utf8 DEFAULT NULL COMMENT '模块跳转的url',
  `is_click` varchar(2) CHARACTER SET utf8 NOT NULL DEFAULT '0' COMMENT '是否可点击 ,  1:可点击  ；0：不可点击',
  `is_delete` varchar(2) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(50) CHARACTER SET utf8 DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`function_model_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_benefit_member_function_model_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_benefit_member_function_model_rlt`;
CREATE TABLE `tbl_benefit_member_function_model_rlt` (
  `rit_id` varchar(50) CHARACTER SET utf8 NOT NULL COMMENT '关联id',
  `mlid` varchar(50) CHARACTER SET utf8 NOT NULL COMMENT '等级id',
  `function_model_id` varchar(50) CHARACTER SET utf8 NOT NULL COMMENT '功能模块id',
  `model_sort` int(2) NOT NULL DEFAULT '0' COMMENT '模块排序',
  `is_delete` varchar(1) CHARACTER SET utf8 NOT NULL DEFAULT '0' COMMENT '是否删除',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_people` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`rit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_benefit_menu_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_benefit_menu_dat`;
CREATE TABLE `tbl_benefit_menu_dat` (
  `benefit_menu_id` int(10) NOT NULL AUTO_INCREMENT COMMENT '福利页功能菜单id',
  `menu_name` varchar(10) NOT NULL COMMENT '菜单名字',
  `menu_display_icon` varchar(255) NOT NULL COMMENT '菜单显示图标',
  `menu_disable_icon` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '菜单不可点击图标',
  `menu_page_url` varchar(255) DEFAULT NULL COMMENT '菜单跳转页面url',
  `is_display` varchar(2) NOT NULL DEFAULT '0' COMMENT '是否显示  1：显示；  0：不显示',
  `is_click` varchar(2) NOT NULL DEFAULT '0' COMMENT '是否可点击 ,  1:可点击  ；0：不可点击',
  `is_delete` varchar(2) NOT NULL DEFAULT '0' COMMENT '是否删除 ：  0：不删除；  1：删除',
  `menu_sort` int(11) NOT NULL DEFAULT '0' COMMENT '菜单功能排序',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(50) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`benefit_menu_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_bms_user_business_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_bms_user_business_rlt`;
CREATE TABLE `tbl_bms_user_business_rlt` (
  `rlt_id` varchar(50) NOT NULL COMMENT '关联ID',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '商户系统用户ID',
  `business_id` varchar(50) NOT NULL DEFAULT '' COMMENT '商户ID',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_delete` varchar(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户商户关联表';

-- ----------------------------
-- Table structure for tbl_bms_user_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_bms_user_info_dat`;
CREATE TABLE `tbl_bms_user_info_dat` (
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `user_code` varchar(50) NOT NULL COMMENT '用户编码，用于登机校验',
  `password` varchar(255) NOT NULL DEFAULT '' COMMENT '密码',
  `clear_password` varchar(50) DEFAULT NULL COMMENT '明文密码',
  `user_name` varchar(200) DEFAULT '' COMMENT '用户名',
  `user_headimg` varchar(200) DEFAULT NULL COMMENT '用户头像',
  `user_telphone` varchar(18) DEFAULT NULL COMMENT '手机号码',
  `user_sex` varchar(4) DEFAULT '0' COMMENT '性别 -0：女  1：男',
  `user_mail` varchar(50) DEFAULT NULL COMMENT '用户邮件',
  `is_activate` varchar(4) DEFAULT '0' COMMENT '是否激活，用于极光推送',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `last_login_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '最后登录时间',
  `update_people` varchar(100) DEFAULT NULL COMMENT '创建者',
  `role` varchar(255) NOT NULL DEFAULT '' COMMENT '角色',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_code` (`user_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户用户信息表';

-- ----------------------------
-- Table structure for tbl_business_brand
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_brand`;
CREATE TABLE `tbl_business_brand` (
  `brand_id` varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '店铺品牌id',
  `business_id` varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '店铺id',
  `brand_name` varchar(10) CHARACTER SET utf8 NOT NULL COMMENT '品牌名称',
  `brand_introduction` varchar(255) NOT NULL COMMENT '品牌介绍',
  `brand_picture` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '品牌图片',
  `brand_contractions` varchar(255) CHARACTER SET utf8 DEFAULT NULL COMMENT '品牌缩略图',
  `brand_sort` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `is_display` varchar(10) CHARACTER SET utf8 NOT NULL DEFAULT '98989804' COMMENT '是否显示    ',
  `is_delete` varchar(10) CHARACTER SET utf8 NOT NULL DEFAULT '98989802' COMMENT '是否删除    ',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_category_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_category_dic`;
CREATE TABLE `tbl_business_category_dic` (
  `business_category_id` varchar(50) NOT NULL,
  `business_category_name` varchar(100) NOT NULL COMMENT '店铺分类名称',
  `virtualBusinessMark` varchar(2) NOT NULL COMMENT '店铺标识   0:实体店铺  1:虚拟店铺  2:餐饮店铺',
  `business_category_sort` int(11) DEFAULT '0' COMMENT '店铺分类排序',
  `remark` varchar(200) DEFAULT '',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(50) DEFAULT '' COMMENT '修改人',
  `is_delete` varchar(4) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`business_category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_category_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_category_rlt`;
CREATE TABLE `tbl_business_category_rlt` (
  `business_category_rlt_id` varchar(50) NOT NULL COMMENT '主键id',
  `business_category_id` varchar(50) NOT NULL COMMENT '店铺分类id',
  `business_id` varchar(50) NOT NULL COMMENT '店铺id',
  `business_category_rlt_sort` int(11) NOT NULL DEFAULT '0' COMMENT '排序',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_delete` varchar(4) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_people` varchar(50) DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`business_category_rlt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_free_enjoy_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_free_enjoy_record_dat`;
CREATE TABLE `tbl_business_free_enjoy_record_dat` (
  `busi_en_free_id` varchar(50) NOT NULL,
  `order_id` varchar(50) NOT NULL COMMENT '订单id',
  `is_prize` varchar(4) NOT NULL DEFAULT '0' COMMENT '是否中奖，默认0',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`busi_en_free_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_free_setting_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_free_setting_dic`;
CREATE TABLE `tbl_business_free_setting_dic` (
  `business_id` varchar(50) NOT NULL COMMENT '店铺id',
  `free_unit_money_initial` decimal(10,0) NOT NULL DEFAULT '60' COMMENT '订单满足的初始价格',
  `free_month_money` decimal(10,2) NOT NULL DEFAULT '2000.00' COMMENT '每月免单总金额',
  `free_keyword` varchar(200) NOT NULL DEFAULT '8' COMMENT '中间关键字列如包含8',
  `free_index` varchar(50) NOT NULL DEFAULT '1' COMMENT '中奖索引号，目前表示第几位中奖',
  `free_limit_count_day` int(11) NOT NULL DEFAULT '3' COMMENT '每个用户限制单数 （参与免单）',
  `free_much_count_day` int(11) NOT NULL DEFAULT '1' COMMENT '该店每天最多中奖人数',
  `is_enable` varchar(4) NOT NULL DEFAULT '0' COMMENT '是否启用，0：不启用',
  `remark` varchar(200) DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `free_unit_moeny_limit` decimal(10,0) NOT NULL DEFAULT '100' COMMENT '单笔订单最高不超过的价格',
  PRIMARY KEY (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_goods_promotion_new
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_goods_promotion_new`;
CREATE TABLE `tbl_business_goods_promotion_new` (
  `gbpn_id` varchar(50) NOT NULL COMMENT '商品id',
  `giid` varchar(50) NOT NULL,
  `biid` varchar(50) NOT NULL COMMENT '店铺id',
  `goods_type` varchar(10) NOT NULL DEFAULT '60106002' COMMENT '商品类型，促销和上新',
  `goods_sort` int(10) NOT NULL DEFAULT '0' COMMENT '商品排序',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`gbpn_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_grade_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_grade_dat`;
CREATE TABLE `tbl_business_grade_dat` (
  `business_grade` int(2) NOT NULL AUTO_INCREMENT COMMENT '店铺等级',
  `grade_name` varchar(50) NOT NULL COMMENT '等级名称',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`business_grade`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_special
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_special`;
CREATE TABLE `tbl_business_special` (
  `special_id` varchar(50) CHARACTER SET utf8 NOT NULL COMMENT '专题id',
  `business_id` varchar(50) CHARACTER SET utf8 NOT NULL COMMENT '店铺id',
  `special_name` varchar(50) CHARACTER SET utf8 DEFAULT NULL COMMENT '专题名称',
  `special_description` varchar(255) DEFAULT '' COMMENT '专题描述',
  `special_picture` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '店铺专题图片',
  `special_sort` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `is_display` varchar(10) CHARACTER SET utf8 NOT NULL DEFAULT '98989804' COMMENT '是否显示    ',
  `is_delete` varchar(10) CHARACTER SET utf8 NOT NULL DEFAULT '98989802' COMMENT '是否删除   ',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`special_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_statistics_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_statistics_dat`;
CREATE TABLE `tbl_business_statistics_dat` (
  `business_id` varchar(50) NOT NULL COMMENT '店铺id',
  `business_sort` int(8) DEFAULT NULL COMMENT '店铺口碑',
  `business_evaluate` varchar(4) DEFAULT NULL COMMENT '店铺星级',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='店铺关系表';

-- ----------------------------
-- Table structure for tbl_business_table_num_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_table_num_dic`;
CREATE TABLE `tbl_business_table_num_dic` (
  `table_num_no` varchar(50) NOT NULL COMMENT '桌位号码',
  `table_label` varchar(50) DEFAULT NULL COMMENT '桌位标记',
  `is_delete` varchar(50) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`table_num_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_business_table_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_business_table_rlt`;
CREATE TABLE `tbl_business_table_rlt` (
  `biid_table_no` varchar(50) NOT NULL COMMENT '主键id',
  `biid` varchar(50) NOT NULL COMMENT '店铺id',
  `table_num_no` varchar(50) NOT NULL DEFAULT '' COMMENT '桌位编号',
  `is_delete` varchar(4) DEFAULT '0' COMMENT '是否删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`biid_table_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_configuration_bapp_api_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_configuration_bapp_api_dat`;
CREATE TABLE `tbl_configuration_bapp_api_dat` (
  `cfg_key` varchar(50) NOT NULL DEFAULT '' COMMENT '配置类型',
  `cfg_value` varchar(255) DEFAULT NULL COMMENT '配置内容',
  `remark` varchar(255) DEFAULT '' COMMENT '备注',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(20) NOT NULL DEFAULT '' COMMENT '修改人',
  PRIMARY KEY (`cfg_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商家版api配置';

-- ----------------------------
-- Table structure for tbl_configuration_bapp_development_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_configuration_bapp_development_dat`;
CREATE TABLE `tbl_configuration_bapp_development_dat` (
  `cfg_key` varchar(50) NOT NULL DEFAULT '' COMMENT '配置类型',
  `remark` varchar(255) DEFAULT '' COMMENT '备注',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(20) NOT NULL DEFAULT '' COMMENT '修改人',
  PRIMARY KEY (`cfg_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商家版开发者列表';

-- ----------------------------
-- Table structure for tbl_configuration_bapp_home_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_configuration_bapp_home_dat`;
CREATE TABLE `tbl_configuration_bapp_home_dat` (
  `cfg_key` int(11) NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `cfg_type` varchar(1) NOT NULL DEFAULT '' COMMENT '配置类型',
  `type_text` varchar(10) NOT NULL DEFAULT '' COMMENT '类型',
  `image_url` varchar(255) NOT NULL DEFAULT '' COMMENT '图片url',
  `title_text` varchar(255) DEFAULT '' COMMENT '标题',
  `goto_url` varchar(255) DEFAULT '' COMMENT '跳转url',
  `sort` varchar(2) NOT NULL DEFAULT '' COMMENT '顺序',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(20) NOT NULL DEFAULT '' COMMENT '修改人',
  PRIMARY KEY (`cfg_key`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COMMENT='商家版主页配置';

-- ----------------------------
-- Table structure for tbl_configuration_capp_home_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_configuration_capp_home_dat`;
CREATE TABLE `tbl_configuration_capp_home_dat` (
  `cfg_key` int(11) NOT NULL AUTO_INCREMENT,
  `airport_id` varchar(50) CHARACTER SET utf8 DEFAULT NULL COMMENT '机场id',
  `type_text` varchar(500) DEFAULT '',
  `title_text` varchar(500) DEFAULT '',
  `goto_url` varchar(500) DEFAULT '',
  `sort` varchar(2) NOT NULL DEFAULT '0',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `update_people` varchar(20) DEFAULT NULL,
  `is_delete` varchar(4) NOT NULL DEFAULT '0',
  `is_state` varchar(4) NOT NULL DEFAULT '1' COMMENT '(0:下架/1:未下架)',
  PRIMARY KEY (`cfg_key`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_configuration_common_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_configuration_common_dat`;
CREATE TABLE `tbl_configuration_common_dat` (
  `cfg_key` varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '配置类型',
  `cfg_value` text CHARACTER SET utf8 COMMENT '配置内容',
  `remark` varchar(255) CHARACTER SET utf8 DEFAULT NULL COMMENT '备注',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(20) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '修改人',
  PRIMARY KEY (`cfg_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_configuration_wechat_mp_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_configuration_wechat_mp_dat`;
CREATE TABLE `tbl_configuration_wechat_mp_dat` (
  `cfg_key` varchar(50) NOT NULL DEFAULT '' COMMENT '配置类型',
  `cfg_value` text COMMENT '配置内容',
  `remark` varchar(255) DEFAULT '' COMMENT '备注',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(20) NOT NULL DEFAULT '' COMMENT '修改人',
  PRIMARY KEY (`cfg_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信公众号配置';

-- ----------------------------
-- Table structure for tbl_coupon_apply_crowd_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_apply_crowd_dic`;
CREATE TABLE `tbl_coupon_apply_crowd_dic` (
  `coupon_apply_crowd_id` int(255) NOT NULL AUTO_INCREMENT COMMENT '适用人群id',
  `coupon_apply_crowd_desc` varchar(200) NOT NULL DEFAULT '' COMMENT '人群描述',
  `coupon_apply_crowd_sort` int(11) DEFAULT '0' COMMENT '排序',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  PRIMARY KEY (`coupon_apply_crowd_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_apply_platform_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_apply_platform_dic`;
CREATE TABLE `tbl_coupon_apply_platform_dic` (
  `coupon_apply_platform_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '适用平台id',
  `coupon_appy_platform_name` varchar(50) NOT NULL DEFAULT '' COMMENT '平台名称',
  `coupon_apply_platform_sort` int(11) DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`coupon_apply_platform_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_business_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_business_rlt`;
CREATE TABLE `tbl_coupon_business_rlt` (
  `coupon_id` varchar(50) NOT NULL COMMENT '优惠券id',
  `business_id` varchar(50) NOT NULL COMMENT '店铺id',
  `coupon_business_sort` int(11) DEFAULT '0' COMMENT '店铺优惠券排序',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_delete` varchar(4) DEFAULT '0',
  PRIMARY KEY (`coupon_id`,`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_goods_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_goods_rlt`;
CREATE TABLE `tbl_coupon_goods_rlt` (
  `coupon_id` varchar(50) NOT NULL COMMENT '优惠券id',
  `goods_id` varchar(50) NOT NULL COMMENT '商品id',
  `coupon_goods_sort` int(11) DEFAULT '0' COMMENT '商品优惠券排序',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`coupon_id`,`goods_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_goods_subclass_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_goods_subclass_rlt`;
CREATE TABLE `tbl_coupon_goods_subclass_rlt` (
  `coupon_id` varchar(50) NOT NULL COMMENT '优惠券id',
  `goods_subclass_id` varchar(50) NOT NULL COMMENT '商品子类id',
  `coupon_goods_subclass_sort` int(11) DEFAULT '0' COMMENT '平类券排序',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`coupon_id`,`goods_subclass_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_information_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_information_dat`;
CREATE TABLE `tbl_coupon_information_dat` (
  `coupon_id` varchar(50) NOT NULL COMMENT '优惠券id',
  `coupon_name` varchar(200) NOT NULL COMMENT '优惠券名称',
  `coupon_number` varchar(100) DEFAULT '' COMMENT '优惠券编号',
  `coupon_image_url` varchar(100) DEFAULT '/ptcent_file_upload/logo/16-16-logo-icon-01.jpg' COMMENT '优惠券图片地址url',
  `coupon_describe` varchar(500) NOT NULL DEFAULT '' COMMENT '优惠券描述',
  `coupon_amount` decimal(10,2) DEFAULT '0.00' COMMENT '优惠金额',
  `coupon_discount_rate` decimal(10,2) DEFAULT '0.00' COMMENT '折扣 （0~1）',
  `coupon_use_min_amount` decimal(10,2) DEFAULT '0.00' COMMENT '使用条件，满 XX 元使用 或 不限制',
  `coupon_start_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '优惠券生效时间',
  `coupon_end_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '优惠券失效时间',
  `coupon_type_id` int(11) NOT NULL COMMENT '券类型id 关联 tbl_coupon_type_dic',
  `coupon_property_id` int(11) NOT NULL DEFAULT '1' COMMENT '优惠券属性id 关联 tbl_coupon_property_dic',
  `coupon_usable_range_id` int(11) NOT NULL DEFAULT '2' COMMENT '适用范围-关联tbl_coupon_usable_range_dic',
  `coupon_apply_crowd_id` int(11) NOT NULL DEFAULT '1' COMMENT '适应人群id 关联 tbl_apply_crowd_id',
  `coupon_apply_platform_id` int(11) NOT NULL DEFAULT '1' COMMENT '适用平台id 关联 tbl_coupon_apply_platform_dic',
  `coupon_obtain_quantity_limit` int(11) DEFAULT '1' COMMENT '每人限制领取数量',
  `coupon_send_total_quantity` int(11) NOT NULL DEFAULT '0' COMMENT '派发总数',
  `coupon_send_subject` varchar(4) NOT NULL COMMENT '发放主体，1：平台优惠券，2：店铺优惠券',
  `coupon_send_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '优惠券投放时间',
  `coupon_send_auto_status` varchar(4) NOT NULL DEFAULT '0' COMMENT '自动投放状态 0：不自动，1：自动',
  `coupon_open_status` varchar(4) NOT NULL DEFAULT '0' COMMENT '优惠券是否已投放公开 0：不公开，1：公开',
  `coupon_remind_user_status` varchar(4) NOT NULL DEFAULT '0' COMMENT '是否提醒用户到期，0：不提醒，1：提醒',
  `coupon_return_setting_id` int(11) NOT NULL DEFAULT '1' COMMENT '退款设置id 关联 tbl_coupon_return_setting_dic',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `create_people` varchar(50) DEFAULT '',
  `update_people` varchar(50) DEFAULT '' COMMENT '更新人',
  `is_delete` varchar(4) DEFAULT '0' COMMENT '删除标记',
  PRIMARY KEY (`coupon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_property_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_property_dic`;
CREATE TABLE `tbl_coupon_property_dic` (
  `coupon_property_id` int(11) NOT NULL,
  `coupon_property_name` varchar(100) NOT NULL DEFAULT '',
  `coupon_property_sort` int(11) DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`coupon_property_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_return_setting_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_return_setting_dic`;
CREATE TABLE `tbl_coupon_return_setting_dic` (
  `coupon_return_setting_id` int(11) NOT NULL AUTO_INCREMENT,
  `coupon_return_setting_describe` varchar(200) NOT NULL DEFAULT '' COMMENT '退回描述',
  `coupon_return_setting_sort` int(11) DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`coupon_return_setting_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_send_method_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_send_method_dic`;
CREATE TABLE `tbl_coupon_send_method_dic` (
  `coupon_send_method_id` int(11) NOT NULL AUTO_INCREMENT,
  `coupon_send_method_name` varchar(100) NOT NULL DEFAULT '' COMMENT '优惠券发放方式',
  `coupon_send_method_sort` int(11) DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`coupon_send_method_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_type_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_type_dic`;
CREATE TABLE `tbl_coupon_type_dic` (
  `coupon_type_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `coupon_type_name` varchar(255) NOT NULL DEFAULT '' COMMENT '优惠券类型名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`coupon_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_usable_range_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_usable_range_dic`;
CREATE TABLE `tbl_coupon_usable_range_dic` (
  `coupon_usable_range_id` int(11) NOT NULL AUTO_INCREMENT,
  `coupon_usable_range_name` varchar(50) NOT NULL DEFAULT '' COMMENT '使用范围名称',
  `coupon_usable_range_sort` int(11) DEFAULT '0' COMMENT '使用范围排序',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '添加时间',
  PRIMARY KEY (`coupon_usable_range_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_user_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_user_rlt`;
CREATE TABLE `tbl_coupon_user_rlt` (
  `coupon_user_id` varchar(50) NOT NULL,
  `coupon_id` varchar(50) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `coupon_status` varchar(4) NOT NULL COMMENT '优惠券状态，1：未使用，2：已使用，3：已过期',
  `coupon_send_method_id` int(11) NOT NULL COMMENT '领取优惠券方式，关联 tbl_coupon_send_method_dic',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`coupon_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_coupon_use_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_coupon_use_record_dat`;
CREATE TABLE `tbl_coupon_use_record_dat` (
  `coupon_use_record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录id',
  `coupon_id` varchar(50) NOT NULL COMMENT '优惠券id',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户id',
  `coupon_record_status` varchar(4) NOT NULL COMMENT '记录状态，1：使用，2：获取',
  `coupon_record_quantity` int(11) NOT NULL DEFAULT '1' COMMENT '使用数量',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`coupon_use_record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_feedback_column_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_feedback_column_dic`;
CREATE TABLE `tbl_feedback_column_dic` (
  `feedback_column_id` varchar(50) NOT NULL COMMENT '栏目ID',
  `feedback_column_name` varchar(50) NOT NULL COMMENT '栏目名称',
  `feedback_column_type` varchar(50) DEFAULT NULL COMMENT '栏目类型',
  `feedback_column_url` varchar(255) DEFAULT NULL COMMENT '跳转url(针对客服)',
  `feedback_column_sort` varchar(8) DEFAULT NULL COMMENT '栏目排序',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`feedback_column_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='意见反馈栏目表';

-- ----------------------------
-- Table structure for tbl_feedback_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_feedback_info_dat`;
CREATE TABLE `tbl_feedback_info_dat` (
  `feedback_dat_id` varchar(50) NOT NULL COMMENT '意见反馈数据id',
  `feedback_dat_question` text COMMENT '意见反馈问题',
  `feedback_dat_contact_way` varchar(50) DEFAULT NULL COMMENT '意见反馈联系方式',
  `feedback_label_id` varchar(50) DEFAULT NULL COMMENT '标签id',
  `feedback_pic_x256` varchar(255) DEFAULT NULL COMMENT '反馈数据图1',
  `feedback_pic_x512` varchar(255) DEFAULT NULL COMMENT '反馈数据图2',
  `feedback_pic_x1024` varchar(255) DEFAULT NULL COMMENT '反馈数据图3',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`feedback_dat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='意见反馈数据表';

-- ----------------------------
-- Table structure for tbl_feedback_label_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_feedback_label_rlt`;
CREATE TABLE `tbl_feedback_label_rlt` (
  `feedback_label_id` varchar(50) NOT NULL COMMENT '标签id',
  `feedback_label_name` varchar(50) NOT NULL COMMENT '标签name',
  `feedback_column_id` varchar(50) DEFAULT NULL COMMENT '栏目id',
  `feedback_label_sort` varchar(8) DEFAULT NULL COMMENT '标签关系排序',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`feedback_label_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='意见反馈与标签关系表';

-- ----------------------------
-- Table structure for tbl_flight_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_flight_record_dat`;
CREATE TABLE `tbl_flight_record_dat` (
  `flight_record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '航班信息id',
  `flight_airport_id` varchar(50) NOT NULL DEFAULT '' COMMENT 'IMF平台FLID',
  `flight_airport_long_id` varchar(50) NOT NULL DEFAULT '' COMMENT 'IMF平台FFID',
  `flight_num` varchar(10) NOT NULL DEFAULT '' COMMENT '航班号',
  `airline_code` varchar(10) NOT NULL DEFAULT '' COMMENT '航空公司代码',
  `from_airport_code` varchar(10) NOT NULL DEFAULT '' COMMENT '出发机场代码',
  `arr_airport_code` varchar(10) NOT NULL DEFAULT '' COMMENT '到达机场代码',
  `flight_date` date DEFAULT NULL COMMENT '航班日期',
  `from_terminal` varchar(10) NOT NULL DEFAULT '' COMMENT '出发机场楼',
  `arr_terminal` varchar(10) NOT NULL DEFAULT '' COMMENT '到达机场楼',
  `accuracy_rate` varchar(10) NOT NULL DEFAULT '' COMMENT '准确率',
  `state_code` varchar(10) NOT NULL DEFAULT '' COMMENT '状态代码',
  `boarding_gate` varchar(10) NOT NULL DEFAULT '' COMMENT '登机口',
  `check_in_counter` varchar(20) NOT NULL DEFAULT '' COMMENT '值机柜台',
  `luggage_gate` varchar(10) NOT NULL DEFAULT '' COMMENT '行李闸口',
  `aircraft_number` varchar(10) NOT NULL DEFAULT '' COMMENT '飞机编号',
  `aircraft_model` varchar(10) NOT NULL DEFAULT '' COMMENT '飞机型号',
  `from_weather_code` varchar(10) NOT NULL DEFAULT '' COMMENT '起飞天气代码',
  `arr_weather_code` varchar(10) NOT NULL DEFAULT '' COMMENT '到达天气代码',
  `from_weather_temperature` varchar(10) NOT NULL DEFAULT '' COMMENT '起飞温度',
  `arr_weather_temperature` varchar(10) NOT NULL DEFAULT '' COMMENT '到达温度',
  `plan_from_time` datetime DEFAULT NULL COMMENT '计划起飞时间',
  `plan_arr_time` datetime DEFAULT NULL COMMENT '计划到达时间',
  `estimated_from_time` datetime DEFAULT NULL COMMENT '预计起飞时间',
  `estimated_arr_time` datetime DEFAULT NULL COMMENT '预计到达时间',
  `real_from_time` datetime DEFAULT NULL COMMENT '实际起飞时间',
  `real_arr_time` datetime DEFAULT NULL COMMENT '实际到达时间',
  `is_lock` varchar(1) NOT NULL DEFAULT '0' COMMENT '是否锁定不被删除',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`flight_record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='航班数据';

-- ----------------------------
-- Table structure for tbl_flight_route_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_flight_route_dat`;
CREATE TABLE `tbl_flight_route_dat` (
  `query_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '查询任务ID',
  `from_airport_code` varchar(5) NOT NULL DEFAULT '' COMMENT '起飞机场代码',
  `arr_airport_code` varchar(5) NOT NULL DEFAULT '' COMMENT '到达机场代码',
  PRIMARY KEY (`query_id`)
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8mb4 COMMENT='航显查询任务表';

-- ----------------------------
-- Table structure for tbl_flight_state_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_flight_state_dic`;
CREATE TABLE `tbl_flight_state_dic` (
  `state_code` varchar(2) NOT NULL DEFAULT '' COMMENT '状态代码',
  `state_name` varchar(10) NOT NULL DEFAULT '' COMMENT '状态名称',
  PRIMARY KEY (`state_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='航班状态字典表';

-- ----------------------------
-- Table structure for tbl_flight_weather_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_flight_weather_dic`;
CREATE TABLE `tbl_flight_weather_dic` (
  `weather_code` varchar(2) NOT NULL DEFAULT '' COMMENT '天气代码',
  `weather_name` varchar(10) NOT NULL DEFAULT '' COMMENT '天气名称',
  PRIMARY KEY (`weather_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='航班数据天气字典表';

-- ----------------------------
-- Table structure for tbl_goods_delivery_method_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_goods_delivery_method_rlt`;
CREATE TABLE `tbl_goods_delivery_method_rlt` (
  `Dmid` varchar(50) NOT NULL COMMENT '配送方式id',
  `giid` varchar(50) NOT NULL COMMENT '商品id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`Dmid`,`giid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_goods_extend_relate_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_goods_extend_relate_rlt`;
CREATE TABLE `tbl_goods_extend_relate_rlt` (
  `giid` varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '商品id',
  `supplier_id` varchar(50) NOT NULL DEFAULT '' COMMENT '供应商id',
  `brand_id` varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '品牌id',
  `business_category_id` varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '店铺分类id',
  `special_id` varchar(50) NOT NULL DEFAULT '' COMMENT '专题id',
  `brand_goods_sort` int(10) NOT NULL DEFAULT '0' COMMENT '店铺品牌商品排序排序',
  `category_goods_sort` int(10) NOT NULL DEFAULT '0' COMMENT '店铺分类商品排序',
  `special_goods_sort` int(10) NOT NULL DEFAULT '0' COMMENT '专题商品排序',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`giid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_goods_label_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_goods_label_dat`;
CREATE TABLE `tbl_goods_label_dat` (
  `label_id` int(2) NOT NULL AUTO_INCREMENT COMMENT '商品标签Id',
  `label_name` varchar(50) CHARACTER SET utf8 DEFAULT NULL COMMENT '商品标签名称',
  `label_introduce` varchar(255) CHARACTER SET utf8 DEFAULT NULL COMMENT '商品标签介绍',
  `label_sort` int(2) DEFAULT NULL COMMENT '商品标签排序',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '商品标签修改时间',
  PRIMARY KEY (`label_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_goods_label_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_goods_label_rlt`;
CREATE TABLE `tbl_goods_label_rlt` (
  `label_id` int(2) NOT NULL COMMENT '商品标签id',
  `giid` varchar(50) CHARACTER SET utf8 NOT NULL COMMENT '商品信息ID',
  `is_delete` varchar(2) CHARACTER SET utf8 NOT NULL DEFAULT '0' COMMENT '是否删除',
  `update_Time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`label_id`,`giid`,`is_delete`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_goods_statistics_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_goods_statistics_dat`;
CREATE TABLE `tbl_goods_statistics_dat` (
  `goods_id` varchar(50) NOT NULL COMMENT '商品id',
  `goods_month_sales` int(8) DEFAULT NULL COMMENT '商品销量',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT '0' COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`goods_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='商品销量关系表';

-- ----------------------------
-- Table structure for tbl_goods_supplier_info_recorde
-- ----------------------------
DROP TABLE IF EXISTS `tbl_goods_supplier_info_recorde`;
CREATE TABLE `tbl_goods_supplier_info_recorde` (
  `supplier_id` varchar(50) NOT NULL COMMENT '供应商id',
  `supplier_name` varchar(50) NOT NULL COMMENT '供应商名称',
  `platform_people_name` varchar(10) NOT NULL COMMENT '平台对接人名称',
  `supplier_people_name` varchar(10) NOT NULL COMMENT '供应商对接人名称',
  `supplier_people_phone` varchar(50) NOT NULL COMMENT '供应商对接人联系电话',
  `supplier_adress` varchar(100) NOT NULL COMMENT '供应商地址',
  `supplier_finance_name` varchar(10) NOT NULL COMMENT '供应商财务开户人名称',
  `supplier_bank_account` varchar(100) NOT NULL COMMENT '供应商银行账号',
  `supplier_bank_name` varchar(100) NOT NULL COMMENT '供应商银行名称',
  `is_delete` varchar(10) NOT NULL DEFAULT '98989802' COMMENT '是否删除',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_home_weather_message
-- ----------------------------
DROP TABLE IF EXISTS `tbl_home_weather_message`;
CREATE TABLE `tbl_home_weather_message` (
  `home_weather_message_id` varchar(50) NOT NULL,
  `home_weather_code` varchar(50) DEFAULT NULL COMMENT '天气code标识',
  `home_weather_content` varchar(255) DEFAULT NULL COMMENT '天气问候内容',
  `home_warther_sort` int(11) DEFAULT NULL COMMENT '排序',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_people` varchar(50) DEFAULT NULL,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_delete` varchar(2) DEFAULT '0',
  PRIMARY KEY (`home_weather_message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_index_airport_banner_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_index_airport_banner_rlt`;
CREATE TABLE `tbl_index_airport_banner_rlt` (
  `airport_banner_id` varchar(50) NOT NULL,
  `airport_id` varchar(50) NOT NULL DEFAULT '' COMMENT '机场id',
  `ibid` varchar(50) NOT NULL COMMENT '广告bannerID',
  `airport_banner_sort` int(11) DEFAULT '0' COMMENT '排序',
  `airport_banner_remark` varchar(500) DEFAULT '',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_people` varchar(50) DEFAULT NULL,
  `is_delete` varchar(4) DEFAULT '0',
  PRIMARY KEY (`airport_banner_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_invoice_address_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_invoice_address_dat`;
CREATE TABLE `tbl_invoice_address_dat` (
  `invoice_address_id` varchar(32) NOT NULL COMMENT '发票快递地址ID ',
  `invoice_id` varchar(32) DEFAULT NULL COMMENT ' 发票ID ',
  `direction_name` varchar(32) DEFAULT NULL COMMENT ' 收件人名称',
  `phone` varchar(18) DEFAULT NULL COMMENT ' 电话 ',
  `region` varchar(50) DEFAULT NULL COMMENT ' 地区 ',
  `address` varchar(255) DEFAULT NULL COMMENT '详细地址 ',
  `description` varchar(50) DEFAULT NULL COMMENT ' 描述 ',
  `create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',
  `update_time` datetime DEFAULT NULL COMMENT ' 修改时间 ',
  `update_people` varchar(20) DEFAULT NULL COMMENT ' 修改人 ',
  `is_delete` varchar(1) DEFAULT NULL COMMENT ' 是否删除 ',
  `remark` varchar(200) DEFAULT NULL COMMENT ' 备注 ',
  PRIMARY KEY (`invoice_address_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT=' 发票快递地址表 ';

-- ----------------------------
-- Table structure for tbl_invoice_information_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_invoice_information_dat`;
CREATE TABLE `tbl_invoice_information_dat` (
  `invoice_id` varchar(32) NOT NULL COMMENT ' 发票ID ',
  `shop_id` varchar(50) DEFAULT NULL COMMENT ' 店铺id ',
  `invoice_type` varchar(4) DEFAULT NULL COMMENT ' 发票类型 ',
  `invoice_head_name` varchar(200) DEFAULT NULL COMMENT ' 发票抬头名称 ',
  `taxpayer_num` varchar(20) DEFAULT NULL COMMENT ' 纳税人识别号 ',
  `value_add` varchar(4) DEFAULT NULL COMMENT ' 是否需要增值税专用发票 ',
  `corporation_address` varchar(255) DEFAULT NULL COMMENT ' 公司地址 ',
  `corporation_phone` varchar(18) DEFAULT NULL COMMENT ' 公司电话 ',
  `bank_num` varchar(20) DEFAULT NULL COMMENT ' 银行账号 ',
  `open_bank_name` varchar(50) DEFAULT NULL COMMENT '开户行 ',
  `description` varchar(50) DEFAULT NULL COMMENT ' 描述 ',
  `create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',
  `update_time` datetime DEFAULT NULL COMMENT ' 修改时间 ',
  `update_people` varchar(20) DEFAULT NULL COMMENT ' 修改人 ',
  `is_delete` varchar(1) DEFAULT NULL COMMENT ' 是否删除 ',
  `remark` varchar(200) DEFAULT NULL COMMENT ' 备注 ',
  PRIMARY KEY (`invoice_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT=' 发票表 ';

-- ----------------------------
-- Table structure for tbl_log_ams_user_access_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_log_ams_user_access_record_dat`;
CREATE TABLE `tbl_log_ams_user_access_record_dat` (
  `record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '手机号码',
  `request_time` int(10) NOT NULL DEFAULT '0' COMMENT '请求返回时间(ms)',
  `request_path` varchar(255) NOT NULL DEFAULT '' COMMENT '访问URI',
  `request_param` varchar(1000) NOT NULL DEFAULT '' COMMENT '访问参数',
  `response` varchar(1000) NOT NULL DEFAULT '' COMMENT '请求返回结果',
  `context_path` varchar(255) NOT NULL DEFAULT '' COMMENT '项目名称',
  `request_url` varchar(255) NOT NULL DEFAULT '' COMMENT '请求URL',
  `exception` varchar(1000) NOT NULL DEFAULT '' COMMENT '异常记录',
  `localAddr` varchar(50) NOT NULL DEFAULT '' COMMENT '访问服务器',
  `object_type` varchar(10) NOT NULL DEFAULT '' COMMENT '访问对象类型',
  `object_id` varchar(50) NOT NULL DEFAULT '' COMMENT '访问对象ID',
  `access_mode` varchar(10) NOT NULL DEFAULT '' COMMENT '访问来源--0:未知,1:iosapp,2:androidapp,8:android,9:iphone',
  `access_ip` varchar(50) NOT NULL DEFAULT '' COMMENT '访问IP',
  `referer` varchar(255) NOT NULL DEFAULT '' COMMENT 'referer',
  `um_distinctid` varchar(100) NOT NULL DEFAULT '' COMMENT 'cookie id',
  `session_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户session ID',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ams用户访问日志表';

-- ----------------------------
-- Table structure for tbl_log_bapp_user_access_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_log_bapp_user_access_record_dat`;
CREATE TABLE `tbl_log_bapp_user_access_record_dat` (
  `record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '手机号码',
  `request_time` int(10) NOT NULL DEFAULT '0' COMMENT '请求返回时间(ms)',
  `request_path` varchar(255) NOT NULL DEFAULT '' COMMENT '访问URI',
  `request_param` varchar(1000) NOT NULL DEFAULT '' COMMENT '访问参数',
  `response` varchar(1000) NOT NULL DEFAULT '' COMMENT '请求返回结果',
  `context_path` varchar(255) NOT NULL DEFAULT '' COMMENT '项目名称',
  `request_url` varchar(255) NOT NULL DEFAULT '' COMMENT '请求URL',
  `exception` varchar(1000) NOT NULL DEFAULT '' COMMENT '异常记录',
  `localAddr` varchar(50) NOT NULL DEFAULT '' COMMENT '访问服务器',
  `object_type` varchar(10) NOT NULL DEFAULT '' COMMENT '访问对象类型',
  `object_id` varchar(50) NOT NULL DEFAULT '' COMMENT '访问对象ID',
  `access_mode` varchar(10) NOT NULL DEFAULT '' COMMENT '访问来源--0:未知,1:iosapp,2:androidapp,8:android,9:iphone',
  `access_ip` varchar(50) NOT NULL DEFAULT '' COMMENT '访问IP',
  `referer` varchar(255) NOT NULL DEFAULT '' COMMENT 'referer',
  `um_distinctid` varchar(100) NOT NULL DEFAULT '' COMMENT 'cookie id',
  `session_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户session ID',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='b端app用户访问日志表';

-- ----------------------------
-- Table structure for tbl_log_bms_user_access_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_log_bms_user_access_record_dat`;
CREATE TABLE `tbl_log_bms_user_access_record_dat` (
  `record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '手机号码',
  `request_time` int(10) NOT NULL DEFAULT '0' COMMENT '请求返回时间(ms)',
  `request_path` varchar(255) NOT NULL DEFAULT '' COMMENT '访问URI',
  `request_param` varchar(1000) NOT NULL DEFAULT '' COMMENT '访问参数',
  `response` varchar(1000) NOT NULL DEFAULT '' COMMENT '请求返回结果',
  `context_path` varchar(255) NOT NULL DEFAULT '' COMMENT '项目名称',
  `request_url` varchar(255) NOT NULL DEFAULT '' COMMENT '请求URL',
  `exception` varchar(1000) NOT NULL DEFAULT '' COMMENT '异常记录',
  `localAddr` varchar(50) NOT NULL DEFAULT '' COMMENT '访问服务器',
  `object_type` varchar(10) NOT NULL DEFAULT '' COMMENT '访问对象类型',
  `object_id` varchar(50) NOT NULL DEFAULT '' COMMENT '访问对象ID',
  `access_mode` varchar(10) NOT NULL DEFAULT '' COMMENT '访问来源--0:未知,1:iosapp,2:androidapp,8:android,9:iphone',
  `access_ip` varchar(50) NOT NULL DEFAULT '' COMMENT '访问IP',
  `referer` varchar(255) NOT NULL DEFAULT '' COMMENT 'referer',
  `um_distinctid` varchar(100) NOT NULL DEFAULT '' COMMENT 'cookie id',
  `session_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户session ID',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='bms用户访问日志表';

-- ----------------------------
-- Table structure for tbl_log_capp_referer_access_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_log_capp_referer_access_record_dat`;
CREATE TABLE `tbl_log_capp_referer_access_record_dat` (
  `record_id` int(50) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `record_date` date DEFAULT NULL COMMENT '创建时间',
  `record_referer` varchar(1000) NOT NULL DEFAULT '' COMMENT '页面地址',
  `record_pv` int(11) NOT NULL DEFAULT '0' COMMENT 'pv数',
  `record_uv` int(11) NOT NULL DEFAULT '0' COMMENT 'uv数',
  `record_ip` int(11) NOT NULL DEFAULT '0' COMMENT 'ip数',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=619 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_log_capp_user_access_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_log_capp_user_access_record_dat`;
CREATE TABLE `tbl_log_capp_user_access_record_dat` (
  `record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '手机号码',
  `request_time` int(10) NOT NULL DEFAULT '0' COMMENT '请求返回时间(ms)',
  `request_path` varchar(255) NOT NULL DEFAULT '' COMMENT '访问URI',
  `request_param` varchar(1000) NOT NULL COMMENT '访问参数',
  `response` varchar(1000) NOT NULL DEFAULT '' COMMENT '请求返回结果',
  `context_path` varchar(255) NOT NULL DEFAULT '' COMMENT '项目名称',
  `request_url` varchar(255) NOT NULL DEFAULT '' COMMENT '请求URL',
  `exception` varchar(1000) NOT NULL DEFAULT '' COMMENT '异常记录',
  `localAddr` varchar(50) NOT NULL DEFAULT '' COMMENT '访问服务器',
  `object_type` varchar(10) NOT NULL DEFAULT '' COMMENT '访问对象类型',
  `object_id` varchar(50) NOT NULL DEFAULT '' COMMENT '访问对象ID',
  `access_mode` varchar(10) NOT NULL DEFAULT '' COMMENT '访问来源--0:未知,1:iosapp,2:androidapp,8:android,9:iphone',
  `access_ip` varchar(50) NOT NULL DEFAULT '' COMMENT '访问IP',
  `referer` varchar(255) NOT NULL DEFAULT '' COMMENT 'referer',
  `um_distinctid` varchar(100) NOT NULL DEFAULT '' COMMENT 'cookie id',
  `session_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户session ID',
  PRIMARY KEY (`record_id`),
  KEY `index_referer` (`referer`(191)),
  KEY `index_create_time` (`create_time`),
  KEY `index_um_distinct` (`um_distinctid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='C端app用户访问日志表';

-- ----------------------------
-- Table structure for tbl_log_cms_user_access_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_log_cms_user_access_record_dat`;
CREATE TABLE `tbl_log_cms_user_access_record_dat` (
  `record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '手机号码',
  `request_time` int(10) NOT NULL DEFAULT '0' COMMENT '请求返回时间(ms)',
  `request_path` varchar(255) NOT NULL DEFAULT '' COMMENT '访问URI',
  `request_param` longtext NOT NULL COMMENT '访问参数',
  `response` varchar(1000) NOT NULL DEFAULT '' COMMENT '请求返回结果',
  `context_path` varchar(255) NOT NULL DEFAULT '' COMMENT '项目名称',
  `request_url` varchar(255) NOT NULL DEFAULT '' COMMENT '请求URL',
  `exception` varchar(1000) NOT NULL DEFAULT '' COMMENT '异常记录',
  `localAddr` varchar(50) NOT NULL DEFAULT '' COMMENT '访问服务器',
  `object_type` varchar(10) NOT NULL DEFAULT '' COMMENT '访问对象类型',
  `object_id` varchar(50) NOT NULL DEFAULT '' COMMENT '访问对象ID',
  `access_mode` varchar(10) NOT NULL DEFAULT '' COMMENT '访问来源--0:未知,1:iosapp,2:androidapp,8:android,9:iphone',
  `access_ip` varchar(50) NOT NULL DEFAULT '' COMMENT '访问IP',
  `referer` varchar(255) NOT NULL DEFAULT '' COMMENT 'referer',
  `um_distinctid` varchar(100) NOT NULL DEFAULT '' COMMENT 'cookie id',
  `session_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户session ID',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='cms用户访问日志表';

-- ----------------------------
-- Table structure for tbl_my_message_type
-- ----------------------------
DROP TABLE IF EXISTS `tbl_my_message_type`;
CREATE TABLE `tbl_my_message_type` (
  `MsgType` varchar(50) NOT NULL COMMENT '消息类型id',
  `MsgIcon` varchar(200) DEFAULT NULL COMMENT '类型图片icon',
  `CreateTime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `MsgName` varchar(100) DEFAULT '' COMMENT '类型名称',
  PRIMARY KEY (`MsgType`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_num_config_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_num_config_dic`;
CREATE TABLE `tbl_num_config_dic` (
  `num_config_id` int(11) NOT NULL,
  `num_config_code` varchar(100) NOT NULL COMMENT '配置项关键字',
  `number` int(11) DEFAULT '0' COMMENT '配置项显示数量',
  `num_cofig_sort` int(11) DEFAULT '0' COMMENT '配置项排序',
  `num_config_name` varchar(200) NOT NULL DEFAULT '' COMMENT '配置项名称',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(100) DEFAULT '' COMMENT '修改人',
  PRIMARY KEY (`num_config_id`),
  UNIQUE KEY `config_code` (`num_config_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_operate_classify_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_operate_classify_rlt`;
CREATE TABLE `tbl_operate_classify_rlt` (
  `commodity_id` varchar(50) NOT NULL COMMENT '商品对应关系ID',
  `goods_id` varchar(50) DEFAULT NULL COMMENT '商品id',
  `classify_id` varchar(50) DEFAULT NULL COMMENT '专题分类id',
  `is_home` varchar(4) DEFAULT NULL COMMENT '是否显示在首页',
  `is_shooping_mall` varchar(4) DEFAULT NULL COMMENT '是否显示在商城',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `theme_sort` varchar(8) DEFAULT NULL COMMENT '商品排序',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`commodity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='分类与商品的对应关系表';

-- ----------------------------
-- Table structure for tbl_operate_special_column_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_operate_special_column_dat`;
CREATE TABLE `tbl_operate_special_column_dat` (
  `special_column_id` varchar(50) NOT NULL COMMENT '栏目ID',
  `special_column_name` varchar(50) NOT NULL COMMENT '栏目名称',
  `special_column_introduce` varchar(200) DEFAULT NULL COMMENT '栏目介绍',
  `column_sort` varchar(8) DEFAULT NULL COMMENT '栏目排序',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `is_home` varchar(4) DEFAULT NULL COMMENT '是否显示在首页',
  `is_shooping_mall` varchar(4) DEFAULT NULL COMMENT '是否显示在商城',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`special_column_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='专栏表';

-- ----------------------------
-- Table structure for tbl_operate_theme_classify_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_operate_theme_classify_dic`;
CREATE TABLE `tbl_operate_theme_classify_dic` (
  `classify_id` varchar(50) NOT NULL COMMENT '专题分类id',
  `classify_name` varchar(50) DEFAULT NULL COMMENT '专题分类名称',
  `theme_id` varchar(50) DEFAULT NULL COMMENT '专题id',
  `num_config_code` varchar(100) DEFAULT NULL COMMENT '显示数量配置',
  `is_home` varchar(4) DEFAULT NULL COMMENT '是否显示在首页',
  `is_shooping_mall` varchar(4) DEFAULT NULL COMMENT '是否显示在商城',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `theme_sort` varchar(8) DEFAULT NULL COMMENT '商品排序',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`classify_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='专题分类表';

-- ----------------------------
-- Table structure for tbl_operate_theme_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_operate_theme_dat`;
CREATE TABLE `tbl_operate_theme_dat` (
  `theme_id` varchar(50) NOT NULL COMMENT '专题ID',
  `special_column_id` varchar(50) DEFAULT NULL COMMENT '专栏id',
  `theme_name` varchar(50) DEFAULT NULL COMMENT '专题名称',
  `theme_pic_x64` varchar(255) DEFAULT NULL COMMENT '专题64图片',
  `theme_pic_x128` varchar(255) DEFAULT NULL COMMENT '专题128图片',
  `theme_pic_x256` varchar(255) DEFAULT NULL COMMENT '专题256图片',
  `theme_sort` varchar(8) DEFAULT NULL COMMENT '专题排序',
  `is_home` varchar(4) DEFAULT NULL COMMENT '是否显示在首页',
  `is_shooping_mall` varchar(4) DEFAULT NULL COMMENT '是否显示在商城',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`theme_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='专题表';

-- ----------------------------
-- Table structure for tbl_operate_theme_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_operate_theme_rlt`;
CREATE TABLE `tbl_operate_theme_rlt` (
  `commodity_id` varchar(50) NOT NULL COMMENT '商品对应关系ID',
  `goods_id` varchar(50) DEFAULT NULL COMMENT '商品id',
  `theme_id` varchar(50) DEFAULT NULL COMMENT '专题id',
  `is_home` varchar(4) DEFAULT NULL COMMENT '是否显示在首页',
  `is_shooping_mall` varchar(4) DEFAULT NULL COMMENT '是否显示在商城',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`commodity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='商品与专题对应关系表';

-- ----------------------------
-- Table structure for tbl_order_information_change_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_order_information_change_record_dat`;
CREATE TABLE `tbl_order_information_change_record_dat` (
  `order_record_id` bigint(11) NOT NULL AUTO_INCREMENT COMMENT '主键序号',
  `order_id` varchar(100) NOT NULL DEFAULT '' COMMENT '订单id',
  `master_order_id` varchar(100) NOT NULL COMMENT '主单id',
  `order_record_content` varchar(500) DEFAULT '' COMMENT '记录内容',
  `order_record_sub_content` varchar(500) DEFAULT '' COMMENT '二级内容',
  `order_record_money` decimal(18,2) DEFAULT '0.00' COMMENT '记录金额',
  `order_record_request_url` text COMMENT '请求参数连接',
  `order_change_type` varchar(50) DEFAULT '' COMMENT '订单变更类型，create，pay，refund，close，end，other',
  `order_create_callback_data` text,
  `order_record_type` varchar(100) NOT NULL DEFAULT '' COMMENT '记录类型，user，business，system，other',
  `order_operator_id` varchar(100) NOT NULL COMMENT '操作人id',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_delete` varchar(4) NOT NULL DEFAULT '0' COMMENT '删除标识',
  PRIMARY KEY (`order_record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=882 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_order_logistical_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_order_logistical_dat`;
CREATE TABLE `tbl_order_logistical_dat` (
  `logistical_id` varchar(32) NOT NULL COMMENT '物流单id',
  `logistical_name` varchar(255) DEFAULT NULL COMMENT '物流名称',
  `logistical_remark` varchar(255) DEFAULT NULL COMMENT '物流备注',
  `logistical_type` varchar(8) DEFAULT NULL COMMENT '物流类型',
  `logistical_state` varchar(8) DEFAULT NULL COMMENT '物流状态',
  `create_date` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`logistical_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='物流表';

-- ----------------------------
-- Table structure for tbl_order_master_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_order_master_dat`;
CREATE TABLE `tbl_order_master_dat` (
  `master_order_id` varchar(32) NOT NULL COMMENT '主订单id',
  `pay_time` varchar(32) DEFAULT NULL COMMENT '订单发起支付时间（用于第三方支付查询）',
  `service_id` varchar(32) DEFAULT NULL COMMENT '服务id',
  `user_id` varchar(50) DEFAULT NULL COMMENT '用户id',
  `total_price` decimal(18,2) DEFAULT '0.00' COMMENT '订单总金额',
  `freight_price` decimal(18,2) DEFAULT '0.00' COMMENT '订单总邮费',
  `coupon_price` decimal(18,2) DEFAULT '0.00' COMMENT '优惠券抵扣总金额',
  `integral_price` decimal(18,2) DEFAULT '0.00' COMMENT '积分抵扣总金额',
  `activity_price` decimal(18,2) DEFAULT '0.00' COMMENT '活动抵扣总金额',
  `pay_price` decimal(18,2) DEFAULT '0.00' COMMENT '支付总金额',
  `refund_price` decimal(18,2) DEFAULT '0.00' COMMENT '退款总金额',
  `refundable_amount` decimal(18,2) DEFAULT '0.00' COMMENT '可退款总金额',
  `refundable_integral` varchar(20) DEFAULT NULL COMMENT '可退款总积分',
  `integral_amt` varchar(20) DEFAULT NULL COMMENT '总使用积分',
  `order_status` varchar(8) DEFAULT NULL COMMENT '订单状态',
  `address_id` varchar(50) DEFAULT NULL COMMENT '收货地址id',
  `order_source` varchar(8) DEFAULT NULL COMMENT '订单来源',
  `order_label` varchar(32) DEFAULT NULL COMMENT '订单类型(同系统餐饮或其他订单类型)',
  `order_create_time` datetime DEFAULT NULL COMMENT '订单创建时间',
  `order_close_time` datetime DEFAULT NULL COMMENT '订单关闭时间',
  `order_refund_time` datetime DEFAULT NULL COMMENT '订单退款发起时间(采用最后一次退款时间更新)',
  `order_pay_time` datetime DEFAULT NULL COMMENT '订单支付时间',
  `order_sett_time` datetime DEFAULT NULL COMMENT '订单结算时间',
  `order_account_time` datetime DEFAULT NULL COMMENT '订单对账时间',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`master_order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='主订单表';

-- ----------------------------
-- Table structure for tbl_order_refund_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_order_refund_dat`;
CREATE TABLE `tbl_order_refund_dat` (
  `refund_record_id` varchar(32) NOT NULL COMMENT '退款记录id',
  `master_order_id` varchar(32) DEFAULT NULL COMMENT '主订单号',
  `order_id` varchar(32) DEFAULT NULL COMMENT '子订单号',
  `channel_order_id` varchar(32) DEFAULT NULL COMMENT '支付渠道订单号',
  `channel_flow_id` varchar(32) DEFAULT NULL COMMENT '支付渠道流水号',
  `payment_method` varchar(32) DEFAULT NULL COMMENT '支付渠道',
  `user_id` varchar(50) DEFAULT NULL COMMENT '用户id',
  `order_price` decimal(18,2) DEFAULT NULL COMMENT '主订单金额',
  `refund_price` decimal(18,2) DEFAULT NULL COMMENT '退款金额',
  `refund_state` varchar(8) DEFAULT NULL COMMENT '退款状态',
  `refund_type` varchar(8) DEFAULT NULL COMMENT '申请类型',
  `order_type` varchar(8) DEFAULT NULL COMMENT '订单类型',
  `application_description` varchar(255) DEFAULT NULL COMMENT '申请理由',
  `refuse_description` varchar(255) DEFAULT NULL COMMENT '拒绝理由',
  `refund_date` datetime DEFAULT NULL COMMENT '退款时间',
  `create_date` datetime DEFAULT NULL COMMENT '创建时间',
  `remark` varchar(2000) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`refund_record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='退款记录表';

-- ----------------------------
-- Table structure for tbl_pay_order_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_pay_order_dat`;
CREATE TABLE `tbl_pay_order_dat` (
  `order_number` varchar(32) NOT NULL COMMENT '支付订单号',
  `sorder_number` varchar(32) NOT NULL COMMENT '交易订单号',
  `unique_order_no` varchar(50) DEFAULT NULL COMMENT '银行订单号',
  `token` varchar(255) DEFAULT NULL COMMENT '支付后token',
  `order_time` varchar(32) DEFAULT NULL COMMENT '下单时间',
  `service_id` varchar(32) DEFAULT NULL COMMENT '服务ID',
  `goods_name` varchar(255) DEFAULT NULL COMMENT '商品名',
  `coupon_code` varchar(255) DEFAULT NULL COMMENT '优惠券码（多个用，隔开）',
  `final_money` decimal(18,2) DEFAULT '0.00' COMMENT '应付金额',
  `refund_amount` decimal(18,2) DEFAULT '0.00' COMMENT '可退金额',
  `order_state` varchar(8) DEFAULT NULL COMMENT '订单状态（待支付，已支付，已关闭）',
  `pay_flag` varchar(8) DEFAULT NULL COMMENT '支付方式',
  `pay_time` datetime DEFAULT NULL COMMENT '支付时间',
  `user_id` varchar(50) DEFAULT NULL COMMENT '客户id',
  `tel` varchar(20) DEFAULT NULL COMMENT '电话号码',
  `notifyUrl` varchar(1000) DEFAULT NULL COMMENT '异步通知第三方接口',
  `front_url` varchar(1000) DEFAULT NULL COMMENT '前端通知页面',
  `request_url` varchar(1000) DEFAULT NULL COMMENT '请求url',
  `response_param` varchar(1000) DEFAULT '' COMMENT '第三方创建支付返回信息',
  PRIMARY KEY (`order_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='支付订单表';

-- ----------------------------
-- Table structure for tbl_platform_busness_category_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_platform_busness_category_rlt`;
CREATE TABLE `tbl_platform_busness_category_rlt` (
  `paltform_category_id` varchar(50) NOT NULL COMMENT '平台分类id',
  `business_category_id` varchar(50) NOT NULL COMMENT '店铺分类id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_platform_category_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_platform_category_dat`;
CREATE TABLE `tbl_platform_category_dat` (
  `platform_category_id` varchar(50) NOT NULL COMMENT '平台分类id',
  `category_name` varchar(10) NOT NULL COMMENT '分类名称',
  `is_display` varchar(1) NOT NULL DEFAULT '0' COMMENT '是否显示 ，1：显示；   0：不显示',
  `sort` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_people` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`platform_category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_qrcode_wechat_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_qrcode_wechat_info_dat`;
CREATE TABLE `tbl_qrcode_wechat_info_dat` (
  `qrcode_id` varchar(64) NOT NULL DEFAULT '' COMMENT '二维码ID',
  `url` varchar(255) NOT NULL DEFAULT '' COMMENT '二维码图片解析后的地址',
  `goto_url` varchar(255) NOT NULL DEFAULT '' COMMENT '跳转地址',
  `type` varchar(255) NOT NULL DEFAULT '' COMMENT '二维码分类',
  `owner` varchar(255) NOT NULL DEFAULT '' COMMENT '二维码所属',
  `ticket` varchar(255) NOT NULL DEFAULT '' COMMENT '获取的二维码ticket',
  `expire_seconds` int(11) NOT NULL DEFAULT '0' COMMENT '二维码有效时间',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`qrcode_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信二维码信息表';

-- ----------------------------
-- Table structure for tbl_sms_mobile_code_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_sms_mobile_code_dat`;
CREATE TABLE `tbl_sms_mobile_code_dat` (
  `sms_code_id` varchar(50) NOT NULL COMMENT '主键id',
  `sms_mobile` varchar(15) NOT NULL DEFAULT '' COMMENT '''发送验证码的手机号''',
  `sms_mobile_encrypt` varchar(100) NOT NULL COMMENT '手机号密文',
  `sms_code` varchar(6) NOT NULL DEFAULT '' COMMENT '''验证码''',
  `sms_type` varchar(10) NOT NULL DEFAULT '' COMMENT '''验证码类型''',
  `invalid_time` datetime NOT NULL COMMENT '失效时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  PRIMARY KEY (`sms_code_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_special_column_airport_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_special_column_airport_rlt`;
CREATE TABLE `tbl_special_column_airport_rlt` (
  `special_column_airport_relation_id` varchar(50) NOT NULL COMMENT '专栏机场关系表id',
  `special_column_id` varchar(50) DEFAULT NULL COMMENT '栏目ID',
  `airport_id` varchar(50) DEFAULT NULL COMMENT '机场id',
  `description` varchar(50) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `update_people` varchar(20) DEFAULT NULL COMMENT '修改人',
  `is_delete` varchar(1) DEFAULT NULL COMMENT '是否删除',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`special_column_airport_relation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='专栏机场对应关系';

-- ----------------------------
-- Table structure for tbl_special_topic_airport_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_special_topic_airport_rlt`;
CREATE TABLE `tbl_special_topic_airport_rlt` (
  `goods_and_article_id` varchar(32) NOT NULL COMMENT ' 专题对应机场关系ID ',
  `special_topic_id` varchar(32) DEFAULT NULL COMMENT ' 专题id ',
  `airport_id` varchar(50) DEFAULT NULL COMMENT ' 机场id ',
  `description` varchar(50) DEFAULT NULL COMMENT ' 描述 ',
  `create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',
  `update_time` datetime DEFAULT NULL COMMENT ' 修改时间 ',
  `update_people` varchar(20) DEFAULT NULL COMMENT ' 修改人 ',
  `is_delete` varchar(1) DEFAULT NULL COMMENT ' 是否删除 ',
  `remark` varchar(200) DEFAULT NULL COMMENT ' 备注 ',
  PRIMARY KEY (`goods_and_article_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT=' 专题与机场关系 ';

-- ----------------------------
-- Table structure for tbl_special_topic_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_special_topic_dat`;
CREATE TABLE `tbl_special_topic_dat` (
  `special_topic_id` varchar(32) NOT NULL COMMENT '专题id',
  `special_topic_father_id` varchar(32) DEFAULT NULL COMMENT '专题父id',
  `special_topic_type` varchar(32) DEFAULT NULL COMMENT '专题类型',
  `special_topic_label` varchar(200) DEFAULT NULL COMMENT '专题标签',
  `special_topic_code` varchar(32) DEFAULT NULL COMMENT '专题编号',
  `special_topic_name` varchar(50) DEFAULT NULL COMMENT '专题名称',
  `special_topic_shelves` varchar(8) DEFAULT NULL COMMENT '专题上下架',
  `special_topic_pic_x64` varchar(255) DEFAULT NULL COMMENT '专题64图片',
  `special_topic_pic_x128` varchar(255) DEFAULT NULL COMMENT '专题128图片',
  `special_topic_pic_x256` varchar(255) DEFAULT NULL COMMENT '专题256图片',
  `special_topic_sort` varchar(8) DEFAULT NULL COMMENT '专题排序',
  `special_topic_external_style` varchar(32) DEFAULT NULL COMMENT '内部样式 ',
  `special_topic_inside_style` varchar(32) DEFAULT NULL COMMENT ' 外部样式 ',
  `description` varchar(50) DEFAULT NULL COMMENT ' 描述 ',
  `create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',
  `update_time` datetime DEFAULT NULL COMMENT ' 修改时间 ',
  `update_people` varchar(20) DEFAULT NULL COMMENT ' 修改人 ',
  `is_delete` varchar(1) DEFAULT NULL COMMENT ' 是否删除 ',
  `remark` varchar(200) DEFAULT NULL COMMENT ' 备注 ',
  PRIMARY KEY (`special_topic_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT=' 专题表 ';

-- ----------------------------
-- Table structure for tbl_special_topic_goods_and_article_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_special_topic_goods_and_article_rlt`;
CREATE TABLE `tbl_special_topic_goods_and_article_rlt` (
  `goods_and_article_id` varchar(32) NOT NULL COMMENT ' 专题对应商品或者文章关系ID ',
  `special_topic_id` varchar(32) DEFAULT NULL COMMENT ' 专题id ',
  `goods_id` varchar(50) DEFAULT NULL COMMENT ' 商品id ',
  `article_id` varchar(50) DEFAULT NULL COMMENT ' 文章id ',
  `topic_sort` varchar(8) DEFAULT NULL COMMENT ' 商品或文章排序 ',
  `description` varchar(50) DEFAULT NULL COMMENT ' 描述 ',
  `create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',
  `update_time` datetime DEFAULT NULL COMMENT ' 修改时间 ',
  `update_people` varchar(20) DEFAULT NULL COMMENT ' 修改人 ',
  `is_delete` varchar(1) DEFAULT NULL COMMENT ' 是否删除 ',
  `remark` varchar(200) DEFAULT NULL COMMENT ' 备注 ',
  PRIMARY KEY (`goods_and_article_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT=' 专题商品或者文章挂靠关系 ';

-- ----------------------------
-- Table structure for tbl_statistics_global_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_statistics_global_dat`;
CREATE TABLE `tbl_statistics_global_dat` (
  `statistics_id` varchar(50) NOT NULL DEFAULT '' COMMENT '统计ID',
  `statistics_date` date DEFAULT NULL COMMENT '统计日期',
  `global_pv` int(11) NOT NULL DEFAULT '0' COMMENT '全部pv数',
  `global_uv` int(11) NOT NULL DEFAULT '0' COMMENT '全部uv数',
  `global_ip` int(11) NOT NULL DEFAULT '0' COMMENT '全部ip数',
  `order_total` int(11) NOT NULL DEFAULT '0' COMMENT '全部订单数',
  `order_valid` int(11) NOT NULL DEFAULT '0' COMMENT '有效订单数',
  `order_return` int(11) NOT NULL DEFAULT '0' COMMENT '退款订单数',
  `order_arrearage` int(11) NOT NULL DEFAULT '0' COMMENT '未支付订单数',
  `user_new` int(11) NOT NULL DEFAULT '0' COMMENT '新增用户数',
  `user_bind` int(11) NOT NULL DEFAULT '0' COMMENT '绑定手机用户数',
  `business_access` int(11) NOT NULL DEFAULT '0' COMMENT '店铺访问数',
  `goods_access` int(11) NOT NULL DEFAULT '0' COMMENT '商品访问数',
  `article_access` int(11) NOT NULL DEFAULT '0' COMMENT '文章访问数',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `new_visitors` int(11) NOT NULL DEFAULT '0' COMMENT '新访客数',
  `new_visitorsPages` int(11) NOT NULL DEFAULT '0' COMMENT '新访客访问页数',
  `scan_airCount` int(11) NOT NULL DEFAULT '0' COMMENT '航班提醒二维码扫码数',
  PRIMARY KEY (`statistics_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='全局统计表';

-- ----------------------------
-- Table structure for tbl_statistics_user_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_statistics_user_dat`;
CREATE TABLE `tbl_statistics_user_dat` (
  `stat_id` varchar(50) NOT NULL COMMENT '统计id',
  `stat_date` date NOT NULL COMMENT '统计日期',
  `new_user_day` int(12) NOT NULL DEFAULT '0' COMMENT '昨日新增用户数',
  `active_user_day` int(12) NOT NULL DEFAULT '0' COMMENT '昨日活跃用户数',
  `old_user_day` int(12) NOT NULL DEFAULT '0' COMMENT '日忠实用户',
  `old_user_week` int(12) NOT NULL DEFAULT '0' COMMENT '周忠实用户',
  `old_user_month` int(12) NOT NULL DEFAULT '0' COMMENT '月忠实用户',
  `old_user_year` int(12) NOT NULL DEFAULT '0' COMMENT '年忠实用户',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`stat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_store_page_banner_type_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_store_page_banner_type_dat`;
CREATE TABLE `tbl_store_page_banner_type_dat` (
  `banner_type_id` varchar(2) CHARACTER SET utf8 NOT NULL COMMENT 'banner类型id',
  `type_name` varchar(50) CHARACTER SET utf8 DEFAULT NULL COMMENT '类型名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `parameter` varchar(10) NOT NULL DEFAULT '' COMMENT '参数名',
  `link_uri` varchar(150) NOT NULL DEFAULT '' COMMENT '跳转地址',
  `type_status` varchar(2) NOT NULL DEFAULT '0' COMMENT '类型状态  0：无  1：输入框  ；  2：下拉框',
  PRIMARY KEY (`banner_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_sys_traffic_count_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_sys_traffic_count_dic`;
CREATE TABLE `tbl_sys_traffic_count_dic` (
  `sys_traffic_count_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '平台流量人数id',
  `sys_traffic_count_sum` int(11) DEFAULT NULL COMMENT '平台流量人数总计',
  `ran_out_of` varchar(4) DEFAULT '0' COMMENT '是否剩余 1：耗尽，0：还有剩余',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  PRIMARY KEY (`sys_traffic_count_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_traffic_package_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_traffic_package_dic`;
CREATE TABLE `tbl_traffic_package_dic` (
  `traffic_id` int(11) NOT NULL COMMENT '流量主键id',
  `traffic_size` int(11) NOT NULL COMMENT '流量大小',
  `traffic_remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `type` varchar(4) DEFAULT '1' COMMENT '此次活动流量包类型1:流量，2:积分',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(50) DEFAULT NULL COMMENT '修改人',
  PRIMARY KEY (`traffic_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_traffic_rule_dic
-- ----------------------------
DROP TABLE IF EXISTS `tbl_traffic_rule_dic`;
CREATE TABLE `tbl_traffic_rule_dic` (
  `rule_id` int(11) NOT NULL COMMENT '流量规则id',
  `rule_name` varchar(200) DEFAULT NULL COMMENT '获取流量操作',
  `rule_remark` varchar(200) DEFAULT '' COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_upms_app_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_app_info_dat`;
CREATE TABLE `tbl_upms_app_info_dat` (
  `app_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '应用ID',
  `app_name` varchar(255) NOT NULL DEFAULT '' COMMENT '应用名称',
  `app_key` varchar(255) NOT NULL DEFAULT '' COMMENT '应用key',
  `app_secret` varchar(255) NOT NULL DEFAULT '' COMMENT '应用密钥',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COMMENT='upms应用信息表';

-- ----------------------------
-- Table structure for tbl_upms_group_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_group_info_dat`;
CREATE TABLE `tbl_upms_group_info_dat` (
  `group_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '组ID',
  `parent_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '父级组ID',
  `parent_path` varchar(255) NOT NULL DEFAULT '' COMMENT '父级路径',
  `group_name` varchar(255) NOT NULL DEFAULT '' COMMENT '组名称',
  `priority` int(11) NOT NULL DEFAULT '0' COMMENT '优先级',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COMMENT='upms组信息表';

-- ----------------------------
-- Table structure for tbl_upms_group_resource_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_group_resource_rlt`;
CREATE TABLE `tbl_upms_group_resource_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '组资源关联ID',
  `group_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '组ID',
  `resource_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '资源ID',
  `permissions` varchar(255) NOT NULL DEFAULT '' COMMENT '权限',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=146 DEFAULT CHARSET=utf8mb4 COMMENT='upms组权限关联表';

-- ----------------------------
-- Table structure for tbl_upms_organization_airport_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_organization_airport_rlt`;
CREATE TABLE `tbl_upms_organization_airport_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '关联ID',
  `organization_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '组织ID',
  `airport_id` varchar(50) NOT NULL DEFAULT '0' COMMENT '机场ID',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9387 DEFAULT CHARSET=utf8mb4 COMMENT='upms组织机场关联表';

-- ----------------------------
-- Table structure for tbl_upms_organization_business_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_organization_business_rlt`;
CREATE TABLE `tbl_upms_organization_business_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '关联ID',
  `organization_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '组织ID',
  `business_id` varchar(50) NOT NULL DEFAULT '0' COMMENT '商户ID',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2135563 DEFAULT CHARSET=utf8mb4 COMMENT='upms组织商户关联表';

-- ----------------------------
-- Table structure for tbl_upms_organization_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_organization_info_dat`;
CREATE TABLE `tbl_upms_organization_info_dat` (
  `organization_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '组织ID',
  `parent_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '父级组织',
  `parent_path` varchar(255) NOT NULL DEFAULT '' COMMENT '父级路径',
  `organization_name` varchar(255) NOT NULL DEFAULT '' COMMENT '组织名称',
  `priority` int(11) NOT NULL DEFAULT '0' COMMENT '优先级',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COMMENT='upms组织信息表';

-- ----------------------------
-- Table structure for tbl_upms_organization_resource_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_organization_resource_rlt`;
CREATE TABLE `tbl_upms_organization_resource_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '组织资源关联表',
  `organization_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '组织ID',
  `resource_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '资源ID',
  `permissions` varchar(255) NOT NULL DEFAULT '' COMMENT '权限',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2162 DEFAULT CHARSET=utf8mb4 COMMENT='upms组织权限关联表';

-- ----------------------------
-- Table structure for tbl_upms_resource_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_resource_info_dat`;
CREATE TABLE `tbl_upms_resource_info_dat` (
  `resource_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '资源ID',
  `parent_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '父级资源ID',
  `parent_path` varchar(255) NOT NULL DEFAULT '' COMMENT '父级路径',
  `permissions_code` varchar(255) NOT NULL DEFAULT '' COMMENT '权限标识',
  `resource_name` varchar(255) NOT NULL DEFAULT '' COMMENT '资源名称',
  `resource_type` varchar(255) NOT NULL DEFAULT '' COMMENT '资源类型',
  `resource_request_uri` varchar(255) NOT NULL DEFAULT '' COMMENT '资源请求URL',
  `resource_image_uri` varchar(255) NOT NULL DEFAULT '' COMMENT '资源图片URL',
  `priority` int(11) NOT NULL DEFAULT '0' COMMENT '优先级',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`resource_id`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COMMENT='upms权限信息表';

-- ----------------------------
-- Table structure for tbl_upms_role_group_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_role_group_rlt`;
CREATE TABLE `tbl_upms_role_group_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '角色组关联ID',
  `role_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '角色ID',
  `group_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '组ID',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='upms角色组关联表';

-- ----------------------------
-- Table structure for tbl_upms_role_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_role_info_dat`;
CREATE TABLE `tbl_upms_role_info_dat` (
  `role_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `parent_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '父级角色ID',
  `parent_path` varchar(255) NOT NULL DEFAULT '' COMMENT '父级路径',
  `role_name` varchar(255) NOT NULL DEFAULT '' COMMENT '角色名称',
  `priority` int(11) NOT NULL DEFAULT '0' COMMENT '优先级',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COMMENT='upms角色信息表';

-- ----------------------------
-- Table structure for tbl_upms_role_resource_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_role_resource_rlt`;
CREATE TABLE `tbl_upms_role_resource_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '角色资源关联ID',
  `role_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '角色ID',
  `resource_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '资源ID',
  `permissions` varchar(255) NOT NULL DEFAULT '' COMMENT '权限',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=utf8mb4 COMMENT='upms角色权限表';

-- ----------------------------
-- Table structure for tbl_upms_session_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_session_record_dat`;
CREATE TABLE `tbl_upms_session_record_dat` (
  `session_id` varchar(50) NOT NULL DEFAULT '' COMMENT '会话ID',
  `session_object` tinytext NOT NULL COMMENT '会话内容',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='upms会话记录表';

-- ----------------------------
-- Table structure for tbl_upms_user_group_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_user_group_rlt`;
CREATE TABLE `tbl_upms_user_group_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户组关联ID',
  `user_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '用户ID',
  `app_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '应用ID',
  `group_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '组ID',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8mb4 COMMENT='upms用户组关联表';

-- ----------------------------
-- Table structure for tbl_upms_user_info_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_user_info_dat`;
CREATE TABLE `tbl_upms_user_info_dat` (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `user_name` varchar(255) NOT NULL DEFAULT '' COMMENT '登录帐号',
  `password` varchar(255) NOT NULL DEFAULT '' COMMENT '用户密码',
  `salt` varchar(255) NOT NULL DEFAULT '' COMMENT '加密密码的盐',
  `locked` tinyint(1) NOT NULL DEFAULT '0' COMMENT '用户被锁',
  `real_name` varchar(255) NOT NULL DEFAULT '' COMMENT '用户姓名',
  `nick_name` varchar(255) NOT NULL DEFAULT '' COMMENT '用户昵称',
  `head_portrait` varchar(500) CHARACTER SET utf8 DEFAULT '' COMMENT '用户头像',
  `mobile` varchar(255) NOT NULL DEFAULT '' COMMENT '手机号',
  `email` varchar(255) NOT NULL DEFAULT '' COMMENT '电子邮箱',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COMMENT='upms用户信息表';

-- ----------------------------
-- Table structure for tbl_upms_user_organization_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_user_organization_rlt`;
CREATE TABLE `tbl_upms_user_organization_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户组织关联ID',
  `user_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '用户ID',
  `app_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '应用ID',
  `organization_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '组织ID',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=212 DEFAULT CHARSET=utf8mb4 COMMENT='upms用户组织关联表';

-- ----------------------------
-- Table structure for tbl_upms_user_resource_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_user_resource_rlt`;
CREATE TABLE `tbl_upms_user_resource_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户资源关联ID',
  `user_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '用户ID',
  `app_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '应用ID',
  `resource_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '资源ID',
  `permissions` varchar(255) NOT NULL DEFAULT '' COMMENT '权限',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=768 DEFAULT CHARSET=utf8mb4 COMMENT='upms用户权限关联表';

-- ----------------------------
-- Table structure for tbl_upms_user_role_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_user_role_rlt`;
CREATE TABLE `tbl_upms_user_role_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户角色ID',
  `user_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '用户ID',
  `app_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '应用ID',
  `role_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '角色ID',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=utf8mb4 COMMENT='upms用户角色关联表';

-- ----------------------------
-- Table structure for tbl_upms_user_runas_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_upms_user_runas_rlt`;
CREATE TABLE `tbl_upms_user_runas_rlt` (
  `rlt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '关联ID',
  `from_user_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '授权用户',
  `to_user_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '授权到该用户',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `description` varchar(255) NOT NULL DEFAULT '' COMMENT '描述',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(255) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (`rlt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='upms用户切换身份关联表';

-- ----------------------------
-- Table structure for tbl_user_access_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_access_record_dat`;
CREATE TABLE `tbl_user_access_record_dat` (
  `record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '手机号码',
  `request_time` int(10) NOT NULL DEFAULT '0' COMMENT '请求返回时间(ms)',
  `request_path` varchar(255) NOT NULL DEFAULT '' COMMENT '访问URI',
  `request_param` varchar(1000) NOT NULL DEFAULT '' COMMENT '访问参数',
  `response` varchar(1000) NOT NULL DEFAULT '' COMMENT '请求返回结果',
  `exception` varchar(1000) NOT NULL DEFAULT '' COMMENT '异常记录',
  `localAddr` varchar(50) NOT NULL DEFAULT '' COMMENT '访问服务器',
  `object_type` varchar(10) NOT NULL DEFAULT '' COMMENT '访问对象类型',
  `object_id` varchar(50) NOT NULL DEFAULT '' COMMENT '访问对象ID',
  `access_mode` varchar(10) NOT NULL DEFAULT '' COMMENT '访问来源--0:未知,1:iosapp,2:androidapp,8:android,9:iphone',
  `access_ip` varchar(50) NOT NULL DEFAULT '' COMMENT '访问IP',
  `referer` varchar(255) NOT NULL DEFAULT '' COMMENT 'referer',
  `um_distinctid` varchar(100) NOT NULL DEFAULT '' COMMENT 'cookie',
  `session_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户session ID',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户访问记录表';

-- ----------------------------
-- Table structure for tbl_user_account_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_account_dat`;
CREATE TABLE `tbl_user_account_dat` (
  `user_id` varchar(50) NOT NULL,
  `net_traffic` int(11) DEFAULT '0' COMMENT '用户数据流量',
  `user_source` varchar(4) DEFAULT '' COMMENT '用户来源 1：wifi活动来源，2：扫码来源，3：公众号主动关注',
  `scan_qrcode` varchar(50) DEFAULT '' COMMENT '扫描二维码',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_subscribe` varchar(4) NOT NULL DEFAULT '0' COMMENT '是否订阅',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_user_browse_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_browse_record_dat`;
CREATE TABLE `tbl_user_browse_record_dat` (
  `record_id` varchar(50) NOT NULL DEFAULT '' COMMENT '记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `object_type` varchar(10) NOT NULL DEFAULT '' COMMENT '访问对象类型',
  `object_id` varchar(50) NOT NULL DEFAULT '' COMMENT '访问对象ID',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户浏览记录表';

-- ----------------------------
-- Table structure for tbl_user_collection_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_collection_rlt`;
CREATE TABLE `tbl_user_collection_rlt` (
  `user_collection_relation_id` varchar(50) NOT NULL COMMENT '用户收藏表id',
  `user_id` varchar(50) NOT NULL COMMENT '用户id',
  `collection_content_id` varchar(50) NOT NULL COMMENT '用户收藏内容id',
  `collection_type` varchar(4) NOT NULL COMMENT '收藏类型 1：文章，2：店铺，3：商品',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(2) NOT NULL DEFAULT '1' COMMENT '是否取消收藏  1 ：收藏 ，0：取消收藏',
  PRIMARY KEY (`user_collection_relation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_user_flight_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_flight_record_dat`;
CREATE TABLE `tbl_user_flight_record_dat` (
  `user_flight_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户航班记录ID',
  `user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `flight_record_id` varchar(255) NOT NULL DEFAULT '' COMMENT '航班记录ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`user_flight_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户航程记录表';

-- ----------------------------
-- Table structure for tbl_user_follow_rit
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_follow_rit`;
CREATE TABLE `tbl_user_follow_rit` (
  `user_follow_relation_id` varchar(50) NOT NULL COMMENT '用户关注表id',
  `user_id` varchar(50) NOT NULL COMMENT '用户id',
  `follow_content_id` varchar(50) NOT NULL COMMENT '关注内容id',
  `follow_type` varchar(4) NOT NULL COMMENT '关注类型  1：店铺',
  `status` varchar(2) NOT NULL DEFAULT '1' COMMENT '关注状态  1：已关注，0：取消关注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`user_follow_relation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_user_merge_rlt
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_merge_rlt`;
CREATE TABLE `tbl_user_merge_rlt` (
  `user_merge_id` varchar(50) NOT NULL COMMENT '主键id',
  `to_user_id` varchar(50) NOT NULL COMMENT '目标用户',
  `from_user_id` varchar(50) NOT NULL DEFAULT '' COMMENT '来源用户',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_merge_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_user_opinion_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_opinion_record_dat`;
CREATE TABLE `tbl_user_opinion_record_dat` (
  `OpinionID` int(50) NOT NULL AUTO_INCREMENT COMMENT '意见id',
  `OpinionType` varchar(50) CHARACTER SET utf8 NOT NULL COMMENT '意见类型',
  `UserID` varchar(500) CHARACTER SET utf8 NOT NULL COMMENT '当前登录人的id',
  `Content` varchar(500) CHARACTER SET utf8 DEFAULT NULL COMMENT '意见内容',
  `Contact` varchar(60) CHARACTER SET utf8 NOT NULL COMMENT '联系方式',
  `Level` int(2) DEFAULT '0' COMMENT '"0"为父类型',
  `CreateTime` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`OpinionID`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_user_signin_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_signin_dat`;
CREATE TABLE `tbl_user_signin_dat` (
  `user_signin_id` varchar(50) NOT NULL COMMENT '用户签到id',
  `user_id` varchar(50) DEFAULT NULL COMMENT '用户id',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `lntegral` int(11) DEFAULT '0' COMMENT '签到所得积分数',
  `is_signin` varchar(4) DEFAULT '0' COMMENT '是否签到，0：未签到，1：签到',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`user_signin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tbl_user_traffic_record_dat
-- ----------------------------
DROP TABLE IF EXISTS `tbl_user_traffic_record_dat`;
CREATE TABLE `tbl_user_traffic_record_dat` (
  `record_id` varchar(50) NOT NULL COMMENT 'gprs用户领取记录',
  `traffic_id` int(11) DEFAULT NULL COMMENT 'gprs_dic外键id',
  `rule_id` int(11) DEFAULT '0' COMMENT 'gprs_rule外键id',
  `user_id` varchar(50) DEFAULT NULL COMMENT '用户id',
  `user_traffic_direction` varchar(2) NOT NULL DEFAULT '' COMMENT 'gprs变动方向 + 进  - 出',
  `extract_phone` varchar(18) NOT NULL COMMENT '流量到账手机号码',
  `encrypt_phone` varchar(18) NOT NULL COMMENT '加密手机号',
  `remark` varchar(200) DEFAULT NULL COMMENT '用户记录备注',
  `is_delete` varchar(1) NOT NULL DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
  `request_id` varchar(50) DEFAULT '' COMMENT '充值请求id',
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_account_change_reason
-- ----------------------------
DROP TABLE IF EXISTS `tb_account_change_reason`;
CREATE TABLE `tb_account_change_reason` (
  `ACRID` int(2) NOT NULL,
  `ACReason` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ACRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_account_change_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_account_change_record`;
CREATE TABLE `tb_account_change_record` (
  `ACRID` varchar(50) NOT NULL,
  `CCRID` varchar(50) NOT NULL,
  `Direction` varchar(1) NOT NULL,
  `ChangeAmount` decimal(12,2) NOT NULL,
  `UserType` varchar(1) NOT NULL,
  `UserID` varchar(50) NOT NULL,
  `AccountType` varchar(1) NOT NULL,
  `CreateTime` datetime DEFAULT NULL,
  PRIMARY KEY (`ACRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_activity_share_receive_record_data
-- ----------------------------
DROP TABLE IF EXISTS `tb_activity_share_receive_record_data`;
CREATE TABLE `tb_activity_share_receive_record_data` (
  `activity_receive_id` varchar(50) NOT NULL,
  `activity_share_id` varchar(50) NOT NULL,
  `receive_userid` varchar(50) NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`activity_receive_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_activity_share_record_data
-- ----------------------------
DROP TABLE IF EXISTS `tb_activity_share_record_data`;
CREATE TABLE `tb_activity_share_record_data` (
  `activity_share_id` varchar(50) NOT NULL,
  `userid` varchar(50) NOT NULL,
  `share_url` varchar(200) DEFAULT NULL,
  `qiid` varchar(50) DEFAULT NULL,
  `is_new` varchar(2) NOT NULL COMMENT '0：老用户，1：新用户',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`activity_share_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_activity_stimulate
-- ----------------------------
DROP TABLE IF EXISTS `tb_activity_stimulate`;
CREATE TABLE `tb_activity_stimulate` (
  `asid` varchar(50) NOT NULL,
  `btiid` varchar(50) DEFAULT NULL,
  `orderid` varchar(255) DEFAULT NULL,
  `stimulate_amount` decimal(10,0) DEFAULT NULL,
  `activity_feedback` varchar(500) DEFAULT NULL,
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
  `donate` varchar(2) DEFAULT '0',
  `evaluate` varchar(2) DEFAULT '0',
  PRIMARY KEY (`asid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_activity_stimulate_feedback
-- ----------------------------
DROP TABLE IF EXISTS `tb_activity_stimulate_feedback`;
CREATE TABLE `tb_activity_stimulate_feedback` (
  `asfid` int(11) NOT NULL AUTO_INCREMENT,
  `asfname` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`asfid`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_activity_stimulate_feedback_order
-- ----------------------------
DROP TABLE IF EXISTS `tb_activity_stimulate_feedback_order`;
CREATE TABLE `tb_activity_stimulate_feedback_order` (
  `orderid` varchar(50) NOT NULL,
  `asfid` varchar(50) DEFAULT NULL,
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_airline_astyle
-- ----------------------------
DROP TABLE IF EXISTS `tb_airline_astyle`;
CREATE TABLE `tb_airline_astyle` (
  `AStyleID` int(2) NOT NULL,
  `AStyleName` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`AStyleID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airline_info
-- ----------------------------
DROP TABLE IF EXISTS `tb_airline_info`;
CREATE TABLE `tb_airline_info` (
  `AID` varchar(50) NOT NULL,
  `Aname` varchar(255) DEFAULT NULL,
  `Alogo` varchar(255) DEFAULT NULL,
  `AMain` varchar(255) DEFAULT NULL,
  `Serviceline` varchar(50) DEFAULT NULL,
  `Introduction` mediumtext,
  PRIMARY KEY (`AID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airline_service_items
-- ----------------------------
DROP TABLE IF EXISTS `tb_airline_service_items`;
CREATE TABLE `tb_airline_service_items` (
  `ASIID` varchar(50) NOT NULL,
  `AID` varchar(50) NOT NULL,
  `AStyleID` int(2) DEFAULT NULL,
  `ServiceDescription` mediumtext NOT NULL,
  `LastRevisionsTime` datetime NOT NULL,
  PRIMARY KEY (`ASIID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airline_service_items_picture
-- ----------------------------
DROP TABLE IF EXISTS `tb_airline_service_items_picture`;
CREATE TABLE `tb_airline_service_items_picture` (
  `ASIPID` varchar(50) NOT NULL,
  `ASIID` varchar(50) NOT NULL,
  `Picture` varchar(100) NOT NULL,
  PRIMARY KEY (`ASIPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airportinfo_hot
-- ----------------------------
DROP TABLE IF EXISTS `tb_airportinfo_hot`;
CREATE TABLE `tb_airportinfo_hot` (
  `hotairportid` varchar(50) NOT NULL,
  `aiid` varchar(50) NOT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `sort` int(11) DEFAULT '0',
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
  `lastmodifiedtime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hotairportid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_announcement
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_announcement`;
CREATE TABLE `tb_airport_announcement` (
  `AAID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `Atitle` varchar(200) NOT NULL,
  `Announce` mediumtext NOT NULL,
  `AnnounceTime` datetime NOT NULL,
  PRIMARY KEY (`AAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_board
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_board`;
CREATE TABLE `tb_airport_board` (
  `abid` varchar(50) NOT NULL,
  `aiid` varchar(50) NOT NULL,
  `boardname` varchar(100) NOT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`abid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_airport_board_businessinformation
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_board_businessinformation`;
CREATE TABLE `tb_airport_board_businessinformation` (
  `abid` varchar(50) NOT NULL,
  `biid` varchar(50) NOT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`abid`,`biid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_airport_board_service
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_board_service`;
CREATE TABLE `tb_airport_board_service` (
  `abid` varchar(50) NOT NULL,
  `astid` varchar(50) NOT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`abid`,`astid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_airport_checkin_service
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_checkin_service`;
CREATE TABLE `tb_airport_checkin_service` (
  `ACSID` varchar(50) NOT NULL,
  `AIID` varchar(5) NOT NULL,
  `UserID` varchar(50) NOT NULL,
  `ProcessTime` datetime NOT NULL,
  `CredentialsType` varchar(50) NOT NULL DEFAULT '1',
  `CredentialsNum` varchar(20) NOT NULL,
  PRIMARY KEY (`ACSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_code
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_code`;
CREATE TABLE `tb_airport_code` (
  `airportCodeID` int(11) NOT NULL,
  `airportCode` varchar(50) DEFAULT NULL,
  `airportName` varchar(50) DEFAULT NULL,
  `airportCity` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`airportCodeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_contacts
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_contacts`;
CREATE TABLE `tb_airport_contacts` (
  `ACID` varchar(50) DEFAULT NULL,
  `AIID` varchar(50) NOT NULL,
  `ACName` varchar(20) NOT NULL,
  `Position` varchar(20) NOT NULL,
  `ContactNum` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_delivery_point
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_delivery_point`;
CREATE TABLE `tb_airport_delivery_point` (
  `ADPID` varchar(50) DEFAULT NULL,
  `ADPIDs` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `DPNo` varchar(20) NOT NULL,
  `DPName` varchar(20) NOT NULL,
  `Address` varchar(100) NOT NULL,
  `PUserID` varchar(50) NOT NULL,
  PRIMARY KEY (`ADPIDs`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_delivery_point_logistics
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_delivery_point_logistics`;
CREATE TABLE `tb_airport_delivery_point_logistics` (
  `DPOID` varchar(50) NOT NULL,
  `ADPID` varchar(50) NOT NULL,
  `OrderID` varchar(50) NOT NULL,
  `OLStatus` varchar(50) DEFAULT NULL,
  `ConfirmReceiptTime` datetime DEFAULT NULL,
  `ReturnTime` datetime DEFAULT NULL,
  PRIMARY KEY (`DPOID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_delivery_point_logistics_change_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_delivery_point_logistics_change_record`;
CREATE TABLE `tb_airport_delivery_point_logistics_change_record` (
  `ADPLCRID` varchar(50) NOT NULL,
  `ADPID` varchar(50) NOT NULL,
  `StorageDirection` varchar(50) NOT NULL,
  `ProductSKUID` varchar(50) NOT NULL,
  `ProductNum` varchar(8) NOT NULL,
  `Operattime` datetime NOT NULL,
  `StorageReason` varchar(50) NOT NULL,
  `PUserID` varchar(50) NOT NULL,
  PRIMARY KEY (`ADPLCRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_delivery_point_products
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_delivery_point_products`;
CREATE TABLE `tb_airport_delivery_point_products` (
  `ADPPID` varchar(50) NOT NULL,
  `ADPID` varchar(50) NOT NULL,
  `ProductSKUID` varchar(50) NOT NULL,
  `Inventory` varchar(8) NOT NULL,
  PRIMARY KEY (`ADPPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_home
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_home`;
CREATE TABLE `tb_airport_home` (
  `AHID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `ARID` varchar(50) NOT NULL,
  `MainPicture` varchar(100) DEFAULT NULL,
  `LinkType` varchar(50) DEFAULT NULL,
  `LinkPath` varchar(100) DEFAULT NULL,
  `ReleaseTime` datetime NOT NULL,
  `AHStatus` varchar(2) DEFAULT '2',
  `Publisher` varchar(50) NOT NULL,
  `PubPicture` varchar(100) DEFAULT NULL,
  `AhitsOn` int(20) DEFAULT '0',
  PRIMARY KEY (`AHID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_info
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_info`;
CREATE TABLE `tb_airport_info` (
  `AIID` varchar(50) NOT NULL,
  `Anum` varchar(20) DEFAULT NULL,
  `AIName` varchar(50) DEFAULT NULL,
  `AINameShort` varchar(50) DEFAULT NULL,
  `GMapAIName` varchar(50) DEFAULT NULL,
  `AreaID` varchar(50) DEFAULT NULL,
  `Adress` varchar(100) DEFAULT NULL,
  `AIMainPic` varchar(100) DEFAULT NULL,
  `Introduction` text,
  `ServiceLine` varchar(15) DEFAULT NULL,
  `AIZfbNo` varchar(20) DEFAULT NULL,
  `AIAccountNo` varchar(20) DEFAULT NULL,
  `CashAccount` decimal(15,2) DEFAULT '0.00',
  `lockCashAccount` decimal(12,2) DEFAULT '0.00',
  `CISAgreement` varchar(2000) DEFAULT NULL,
  `ContractStatus` varchar(10) DEFAULT '0',
  `AiCardNo` varchar(10) DEFAULT NULL,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_people` varchar(50) DEFAULT '100' COMMENT '修改人',
  `is_delete` varchar(50) NOT NULL DEFAULT '0' COMMENT '是否删除',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `CityID` varchar(200) DEFAULT '',
  PRIMARY KEY (`AIID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_recourse_phone
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_recourse_phone`;
CREATE TABLE `tb_airport_recourse_phone` (
  `ARPID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `RPName` varchar(40) NOT NULL,
  `Rphone` varchar(15) NOT NULL,
  `ServiceDescr` varchar(100) NOT NULL,
  PRIMARY KEY (`ARPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_service_type
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_service_type`;
CREATE TABLE `tb_airport_service_type` (
  `ASTID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `ASIntroduction` mediumtext NOT NULL,
  `BusinessMark` char(1) DEFAULT '0',
  `RelatedBusiness` varchar(50) DEFAULT NULL,
  `LastChangeTime` datetime NOT NULL,
  `ASSID` int(5) DEFAULT NULL,
  `sort` int(11) DEFAULT NULL,
  `ToUrl` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`ASTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_service_type_picture
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_service_type_picture`;
CREATE TABLE `tb_airport_service_type_picture` (
  `ASTPID` varchar(50) NOT NULL,
  `ASTID` varchar(50) NOT NULL,
  `Picture` varchar(100) NOT NULL,
  PRIMARY KEY (`ASTPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_service_type_type
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_service_type_type`;
CREATE TABLE `tb_airport_service_type_type` (
  `ASSID` int(5) NOT NULL AUTO_INCREMENT,
  `ASName` varchar(50) NOT NULL COMMENT '类型名称',
  `ASIcon` varchar(500) DEFAULT NULL COMMENT '类型icon',
  `ASType` varchar(4) DEFAULT NULL COMMENT '1：机场维护，2：平台维护，3：航空公司服务维护',
  `AsBanner` varchar(200) CHARACTER SET utf8mb4 DEFAULT '' COMMENT '服务类型头图banner',
  PRIMARY KEY (`ASSID`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_wifi
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_wifi`;
CREATE TABLE `tb_airport_wifi` (
  `AWID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `Introduction` mediumtext NOT NULL,
  PRIMARY KEY (`AWID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_wifi_pic
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_wifi_pic`;
CREATE TABLE `tb_airport_wifi_pic` (
  `AWPID` varchar(50) NOT NULL,
  `AWID` varchar(50) NOT NULL,
  `AWPic` varchar(100) NOT NULL,
  PRIMARY KEY (`AWPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_airport_withdrawals_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_airport_withdrawals_record`;
CREATE TABLE `tb_airport_withdrawals_record` (
  `AWRID` varchar(50) NOT NULL DEFAULT '',
  `AIID` varchar(50) NOT NULL,
  `Wamt` decimal(12,2) NOT NULL,
  `ApplicationTime` datetime(6) NOT NULL,
  `ReceptionTime` datetime(6) NOT NULL,
  `CompleteTime` datetime(6) NOT NULL,
  `Status` varchar(1) NOT NULL,
  `RefuseReason` varchar(100) NOT NULL,
  PRIMARY KEY (`AWRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_amall_page_banner
-- ----------------------------
DROP TABLE IF EXISTS `tb_amall_page_banner`;
CREATE TABLE `tb_amall_page_banner` (
  `APBID` varchar(50) NOT NULL,
  `Picture` varchar(100) NOT NULL,
  PRIMARY KEY (`APBID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_amall_page_display_business
-- ----------------------------
DROP TABLE IF EXISTS `tb_amall_page_display_business`;
CREATE TABLE `tb_amall_page_display_business` (
  `APDBID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `APnum` varchar(8) DEFAULT '0',
  PRIMARY KEY (`APDBID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_amall_page_display_coupons_commodities
-- ----------------------------
DROP TABLE IF EXISTS `tb_amall_page_display_coupons_commodities`;
CREATE TABLE `tb_amall_page_display_coupons_commodities` (
  `APDCCID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `APnum` int(8) DEFAULT '0',
  PRIMARY KEY (`APDCCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_amall_page_display_physical_commodities
-- ----------------------------
DROP TABLE IF EXISTS `tb_amall_page_display_physical_commodities`;
CREATE TABLE `tb_amall_page_display_physical_commodities` (
  `APDPCID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `APnum` int(8) DEFAULT '0',
  PRIMARY KEY (`APDPCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_area_info
-- ----------------------------
DROP TABLE IF EXISTS `tb_area_info`;
CREATE TABLE `tb_area_info` (
  `AreaID` varchar(50) NOT NULL,
  `AreaName` varchar(80) NOT NULL,
  `UpperLevelID` varchar(50) DEFAULT NULL,
  `CodingStandards` varchar(50) DEFAULT NULL,
  `Level` int(50) DEFAULT NULL,
  `IfLeaf` varchar(50) DEFAULT '1',
  `ping` varchar(50) DEFAULT NULL,
  `area_sort` int(11) DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `popcity` varchar(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`AreaID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_article
-- ----------------------------
DROP TABLE IF EXISTS `tb_article`;
CREATE TABLE `tb_article` (
  `ARID` varchar(50) NOT NULL,
  `ArticleTitle` varchar(50) NOT NULL,
  `ArticleContext` mediumtext NOT NULL,
  `ArticleCreatTime` datetime NOT NULL,
  `Artflag` varchar(2) DEFAULT '0',
  `ArticleSubinfo` varchar(200) DEFAULT NULL,
  `Acid` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ARID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_article_classify
-- ----------------------------
DROP TABLE IF EXISTS `tb_article_classify`;
CREATE TABLE `tb_article_classify` (
  `acid` varchar(50) NOT NULL,
  `acname` varchar(50) DEFAULT NULL,
  `sort` int(11) DEFAULT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`acid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_account_change_reason
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_account_change_reason`;
CREATE TABLE `tb_business_account_change_reason` (
  `BACRID` int(2) NOT NULL AUTO_INCREMENT COMMENT '商户资金账户变动原因ID',
  `BACReason` varchar(40) NOT NULL COMMENT '商户资金账户变动原因',
  PRIMARY KEY (`BACRID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_account_change_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_account_change_record`;
CREATE TABLE `tb_business_account_change_record` (
  `BACRDID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `CashAccountType` varchar(50) NOT NULL,
  `Direction` varchar(50) NOT NULL,
  `ChangeAmount` decimal(12,2) NOT NULL,
  `BACRID` varchar(50) NOT NULL,
  `AccountTypes` varchar(50) NOT NULL,
  `OtherID` varchar(50) NOT NULL,
  `OtherCAT` varchar(50) NOT NULL,
  `ChangeTime` datetime NOT NULL,
  PRIMARY KEY (`BACRDID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_information
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_information`;
CREATE TABLE `tb_business_information` (
  `BIID` varchar(50) NOT NULL COMMENT '商户信息ID',
  `BILogo` varchar(255) DEFAULT NULL COMMENT '商户Logo',
  `BNum` varchar(20) DEFAULT NULL COMMENT '商户编号',
  `BIName` varchar(100) NOT NULL COMMENT '商户名称',
  `LoginPassword` varchar(50) DEFAULT NULL COMMENT '登录密码',
  `SelfSign` varchar(20) NOT NULL DEFAULT '0' COMMENT '平台自营标识',
  `AttributionType` varchar(5) DEFAULT NULL COMMENT '归属类型',
  `ASType` varchar(5) DEFAULT NULL COMMENT '机场服务类型',
  `PositionRange` varchar(10) DEFAULT NULL COMMENT '位置范围',
  `Adress` varchar(100) DEFAULT NULL COMMENT '具体地址',
  `address_curt` varchar(100) DEFAULT NULL COMMENT '简短地址',
  `AIID` varchar(50) NOT NULL COMMENT '所属机场ID',
  `BCID` varchar(50) NOT NULL COMMENT '商户分类ID',
  `MainPic` varchar(255) DEFAULT NULL COMMENT '主图',
  `CardPic` varchar(255) DEFAULT NULL COMMENT '卡片缩略图',
  `Introduction` longtext COMMENT '介绍',
  `AllowMorePic` varchar(10) DEFAULT NULL COMMENT '允许更多图片',
  `CashAccount` decimal(15,2) DEFAULT '0.00' COMMENT '资金账户',
  `LockCashAccount` decimal(15,2) DEFAULT NULL COMMENT '锁定资金账户',
  `RAID` varchar(50) DEFAULT NULL COMMENT '缺省退货地址',
  `QRCode` varchar(255) DEFAULT NULL COMMENT '商户二维码',
  `ShippingFee` decimal(8,2) DEFAULT '0.00' COMMENT '运费',
  `ContactNum` varchar(50) DEFAULT NULL COMMENT '联系电话',
  `FContactNum` varchar(15) DEFAULT NULL COMMENT '财务联系电话',
  `WeChatNo` varchar(40) DEFAULT NULL COMMENT '微信账号',
  `BankAccNo` varchar(30) DEFAULT NULL COMMENT '银行账号',
  `AlipayNo` varchar(40) DEFAULT NULL COMMENT '支付宝账号',
  `eMail` varchar(50) DEFAULT NULL COMMENT '邮箱',
  `BusinesslicensePic` varchar(100) DEFAULT NULL COMMENT '营业执照图片',
  `ConfirmReceiptDays` int(11) DEFAULT NULL COMMENT '确认收货天数',
  `CashRaisedDays` int(11) DEFAULT '15' COMMENT '商家结算提现天数',
  `SMFID` int(11) DEFAULT NULL COMMENT '管理费标准ID',
  `Remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `ContractStatus` varchar(2) NOT NULL COMMENT '签约状态',
  `BAccountName` varchar(50) DEFAULT NULL,
  `ReturnableDays` int(11) DEFAULT NULL,
  `flag` varchar(2) DEFAULT '0',
  `kongPic` varchar(200) DEFAULT NULL,
  `talbeware_cost` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '餐具费用 (每份)',
  `tableware_flag` varchar(4) NOT NULL DEFAULT '0' COMMENT '餐具是否免费，1:免费',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `Grade` int(2) NOT NULL DEFAULT '1' COMMENT '店铺等级',
  `virtualBusinessMark` varchar(2) NOT NULL COMMENT '店铺标识   0:实体店铺  1:虚拟店铺  2:餐饮店铺',
  PRIMARY KEY (`BIID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_introduction_pic
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_introduction_pic`;
CREATE TABLE `tb_business_introduction_pic` (
  `BIPID` varchar(50) NOT NULL COMMENT '商户介绍图片ID',
  `BIID` varchar(50) NOT NULL COMMENT '商户信息ID',
  `BIPic` varchar(100) NOT NULL COMMENT '商户介绍图片',
  PRIMARY KEY (`BIPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_parameter_settings
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_parameter_settings`;
CREATE TABLE `tb_business_parameter_settings` (
  `BPSID` varchar(50) NOT NULL COMMENT '商户参数设置ID',
  `BIID` varchar(50) NOT NULL COMMENT '商户信息ID',
  `ConfirmReceiptDays` varchar(50) NOT NULL COMMENT '确认收货天数(最低）',
  `BillingCycle` varchar(50) NOT NULL COMMENT '结算周期（天数）',
  `SMFID` varchar(50) DEFAULT NULL COMMENT '管理费标准ID',
  `Percent` decimal(2,2) NOT NULL,
  `HighestPercent` decimal(2,2) NOT NULL COMMENT '积分每单抵用最高比例',
  PRIMARY KEY (`BPSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_return_address
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_return_address`;
CREATE TABLE `tb_business_return_address` (
  `BRAID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `AreaID` varchar(50) NOT NULL,
  `Address` varchar(100) NOT NULL,
  `Mphone` varchar(15) NOT NULL,
  `ContactName` varchar(40) NOT NULL,
  PRIMARY KEY (`BRAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_trade_information
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_trade_information`;
CREATE TABLE `tb_business_trade_information` (
  `btiid` varchar(255) NOT NULL,
  `aiid` varchar(255) DEFAULT NULL,
  `biid` varchar(255) DEFAULT NULL,
  `tradeNo` varchar(255) DEFAULT NULL,
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
  `lastmodifiedtime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`btiid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_business_withdrawals_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_business_withdrawals_record`;
CREATE TABLE `tb_business_withdrawals_record` (
  `BWRID` varchar(50) NOT NULL,
  `BIID` varchar(50) DEFAULT NULL,
  `Wamt` decimal(12,2) DEFAULT NULL,
  `ApplicationTime` datetime(6) DEFAULT NULL,
  `ReceptionTime` datetime DEFAULT NULL,
  `CompleteTime` datetime DEFAULT NULL,
  `Status` varchar(1) NOT NULL,
  `RefuseReason` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`BWRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_buyed_voucher
-- ----------------------------
DROP TABLE IF EXISTS `tb_buyed_voucher`;
CREATE TABLE `tb_buyed_voucher` (
  `BWID` varchar(50) NOT NULL COMMENT '购买的电子券ID',
  `OrderID` varchar(50) NOT NULL COMMENT '订单ID',
  `UserID` varchar(50) NOT NULL COMMENT '用户ID',
  `GSKUID` varchar(50) NOT NULL COMMENT '商品SKUID',
  `Status` char(1) DEFAULT NULL COMMENT '状态',
  `Quantity` int(10) DEFAULT NULL,
  `BuyTime` datetime DEFAULT NULL,
  `UseTime` datetime DEFAULT NULL,
  `ReturnTime` datetime DEFAULT NULL,
  `UserWay` varchar(5) DEFAULT NULL,
  `ReturnStatus` varchar(5) DEFAULT NULL,
  `SKUIntegral` int(10) DEFAULT NULL,
  `SKUIntegralValue` decimal(7,2) DEFAULT NULL,
  `RetailPrice` decimal(7,2) DEFAULT NULL,
  `ActualPrice` decimal(7,2) DEFAULT NULL,
  `ReturnCause` varchar(500) DEFAULT NULL,
  `ActualPayment` decimal(10,2) DEFAULT NULL,
  `ReturnPrice` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`BWID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_cash_change_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_cash_change_record`;
CREATE TABLE `tb_cash_change_record` (
  `CCRID` varchar(50) NOT NULL DEFAULT '',
  `PACRID` int(2) DEFAULT NULL,
  `RelateID` varchar(50) DEFAULT NULL,
  `CCTime` datetime(6) DEFAULT NULL,
  `OperatorType` varchar(1) DEFAULT NULL,
  `OperatorID` varchar(50) DEFAULT NULL,
  `CreateTime` datetime DEFAULT NULL,
  PRIMARY KEY (`CCRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_commodity_comment
-- ----------------------------
DROP TABLE IF EXISTS `tb_commodity_comment`;
CREATE TABLE `tb_commodity_comment` (
  `CCID` varchar(50) NOT NULL COMMENT '商品评论ID',
  `GIID` varchar(50) NOT NULL COMMENT '商品信息ID',
  `OrderID` varchar(50) DEFAULT NULL COMMENT '订单ID',
  `Content` varchar(255) DEFAULT NULL COMMENT '评论内容',
  `IndexEvaluation` varchar(50) NOT NULL DEFAULT '0' COMMENT '指标评价',
  `CommentTime` datetime NOT NULL COMMENT '评论时间',
  `UserID` varchar(50) NOT NULL COMMENT '用户ID（发布者）',
  `GSKUID` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`CCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_custom_categories
-- ----------------------------
DROP TABLE IF EXISTS `tb_custom_categories`;
CREATE TABLE `tb_custom_categories` (
  `CCID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `CCName` varchar(20) NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `cust_cate_sort` int(11) DEFAULT '0' COMMENT '自定义分类排序',
  `is_delete` varchar(4) DEFAULT '0' COMMENT '是否删除：0-不删除，1-删除',
  `CCPicture` varchar(255) NOT NULL DEFAULT '' COMMENT '店铺分类图片',
  `is_display` varchar(10) NOT NULL DEFAULT '98989804' COMMENT '是否展示 ',
  `category_description` varchar(150) NOT NULL DEFAULT '' COMMENT '店铺分类描述',
  PRIMARY KEY (`CCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_delivery_address
-- ----------------------------
DROP TABLE IF EXISTS `tb_delivery_address`;
CREATE TABLE `tb_delivery_address` (
  `DAID` varchar(50) NOT NULL,
  `UserID` varchar(50) NOT NULL,
  `PCC` varchar(50) DEFAULT NULL,
  `Adress` varchar(100) NOT NULL,
  `Mphone` varchar(15) NOT NULL,
  `ContactName` varchar(20) NOT NULL,
  `DefaultAddress` char(1) DEFAULT '1' COMMENT '0：默认地址  1：收货地址',
  `PC` varchar(10) DEFAULT NULL,
  `Status` char(1) DEFAULT '1' COMMENT '逻辑删除1：使用中 2：已删除',
  `province` varchar(20) DEFAULT '' COMMENT '省',
  `city` varchar(20) DEFAULT '' COMMENT '市',
  `district` varchar(20) DEFAULT '' COMMENT '行政区',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`DAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_delivery_method
-- ----------------------------
DROP TABLE IF EXISTS `tb_delivery_method`;
CREATE TABLE `tb_delivery_method` (
  `DMID` varchar(50) NOT NULL,
  `DMName` varchar(50) NOT NULL,
  `is_delete` varchar(1) NOT NULL DEFAULT '0' COMMENT '是否删除  1:删除；  0：不删除',
  PRIMARY KEY (`DMID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_delivery_points_storage_reasons
-- ----------------------------
DROP TABLE IF EXISTS `tb_delivery_points_storage_reasons`;
CREATE TABLE `tb_delivery_points_storage_reasons` (
  `DPSRID` varchar(50) NOT NULL,
  `StorageReasons` varchar(20) NOT NULL,
  `StorageMark` varchar(50) NOT NULL,
  PRIMARY KEY (`DPSRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_faqlist_answers
-- ----------------------------
DROP TABLE IF EXISTS `tb_faqlist_answers`;
CREATE TABLE `tb_faqlist_answers` (
  `FLAID` varchar(50) NOT NULL,
  `Problem` varchar(200) NOT NULL,
  `Answer` varchar(500) NOT NULL,
  PRIMARY KEY (`FLAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_flight_information
-- ----------------------------
DROP TABLE IF EXISTS `tb_flight_information`;
CREATE TABLE `tb_flight_information` (
  `FIID` int(8) NOT NULL AUTO_INCREMENT COMMENT '航班信息ID',
  `FlightNo` varchar(20) DEFAULT NULL COMMENT '航班号',
  `AID` varchar(50) DEFAULT NULL COMMENT '航空公司ID',
  PRIMARY KEY (`FIID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_flight_path
-- ----------------------------
DROP TABLE IF EXISTS `tb_flight_path`;
CREATE TABLE `tb_flight_path` (
  `FPID` varchar(50) NOT NULL,
  `FIID` varchar(50) NOT NULL,
  `leaveAIID` varchar(50) NOT NULL,
  `leaveAreaID` varchar(50) NOT NULL,
  `leaveTime` datetime NOT NULL,
  `ArrivalsAIID` varchar(50) NOT NULL,
  `ArrivalsAreaID` varchar(50) NOT NULL,
  `ArrivalsTime` datetime NOT NULL,
  PRIMARY KEY (`FPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_function_and_structure
-- ----------------------------
DROP TABLE IF EXISTS `tb_function_and_structure`;
CREATE TABLE `tb_function_and_structure` (
  `FunID` varchar(50) NOT NULL COMMENT '功能ID',
  `FunName` varchar(20) NOT NULL COMMENT '功能名称',
  `LinkResources` varchar(100) NOT NULL COMMENT '链接资源',
  `ULFunID` varchar(10) NOT NULL COMMENT '上一级功能ID',
  `Level` varchar(10) NOT NULL COMMENT '层级',
  `IfLeaf` varchar(10) NOT NULL DEFAULT '1' COMMENT '是否叶子',
  PRIMARY KEY (`FunID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goodssku_inventory_changes_recorded
-- ----------------------------
DROP TABLE IF EXISTS `tb_goodssku_inventory_changes_recorded`;
CREATE TABLE `tb_goodssku_inventory_changes_recorded` (
  `GSKUICRID` varchar(50) NOT NULL,
  `GSKUID` varchar(50) NOT NULL,
  `GCDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `GCDirection` varchar(50) NOT NULL,
  `SKUSCRID` varchar(50) NOT NULL,
  `GCQuantity` int(11) DEFAULT '0',
  PRIMARY KEY (`GSKUICRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_categories
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_categories`;
CREATE TABLE `tb_goods_categories` (
  `GCID` varchar(50) NOT NULL COMMENT '商品大类ID',
  `GCName` varchar(20) NOT NULL COMMENT '商品大类名称',
  `VirtualGoodsMark` varchar(50) NOT NULL COMMENT '虚拟商品标识',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `gc_sort` int(11) NOT NULL DEFAULT '0' COMMENT '分类排序',
  `gc_picture` varchar(100) NOT NULL COMMENT '商品大类图片',
  `gc_description` varchar(255) NOT NULL DEFAULT '' COMMENT '商品大类描述',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`GCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_information
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_information`;
CREATE TABLE `tb_goods_information` (
  `GIID` varchar(50) NOT NULL COMMENT '商品信息ID',
  `BIID` varchar(50) NOT NULL DEFAULT '' COMMENT '商户信息ID',
  `GSID` varchar(50) NOT NULL DEFAULT '' COMMENT '商品类型ID',
  `CCID` varchar(50) NOT NULL DEFAULT '' COMMENT '自定义商品分类ID',
  `GDescription` varchar(500) NOT NULL DEFAULT '' COMMENT '商品描述',
  `GIntroduction` text NOT NULL COMMENT '商品介绍',
  `GMainPic` varchar(255) DEFAULT NULL COMMENT '商品主图',
  `CardPic` varchar(255) NOT NULL DEFAULT '' COMMENT '卡片缩略图',
  `VirtualGoodsMark` char(1) NOT NULL DEFAULT '0' COMMENT '是否虚拟商品',
  `GStartDate` datetime(6) DEFAULT NULL COMMENT '有效起始日',
  `GEndDate` datetime(6) DEFAULT NULL COMMENT '有效结束日',
  `GQRCode` varchar(255) NOT NULL DEFAULT '' COMMENT '商品二维码',
  `Unit` varchar(10) NOT NULL DEFAULT '' COMMENT '计量单位',
  `AgentsMark` varchar(50) NOT NULL DEFAULT '' COMMENT '可代理标识',
  `Brands` varchar(50) NOT NULL DEFAULT '' COMMENT '品牌',
  `InevitablyPost` varchar(50) NOT NULL DEFAULT '' COMMENT '不免邮标识',
  `AddedMark` varchar(50) NOT NULL DEFAULT '' COMMENT '上架标识',
  `PRStatus` varchar(50) NOT NULL DEFAULT '' COMMENT '商品审核状态',
  `ApplicableDP` varchar(50) NOT NULL DEFAULT '' COMMENT '适用提货点',
  `PremiumsMark` varchar(50) NOT NULL DEFAULT '' COMMENT '赠品标识',
  `GoodsName` varchar(500) DEFAULT NULL,
  `MonthlySales` int(20) DEFAULT '0',
  `TimeOnShelves` datetime DEFAULT CURRENT_TIMESTAMP,
  `SinglePieceWeight` varchar(50) DEFAULT '0',
  `RetailPrice` decimal(7,2) DEFAULT NULL,
  `WithTimestamps` varchar(50) DEFAULT NULL,
  `WithWay` varchar(200) DEFAULT NULL,
  `AppointmentPrompt` varchar(100) DEFAULT NULL,
  `flag` varchar(2) DEFAULT '0',
  `MarkPrice` decimal(10,0) DEFAULT NULL,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_people` varchar(100) CHARACTER SET utf8mb4 NOT NULL DEFAULT '' COMMENT '修改人',
  `GoodsSlogan` varchar(50) NOT NULL DEFAULT '' COMMENT '商品广告语',
  PRIMARY KEY (`GIID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_picture
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_picture`;
CREATE TABLE `tb_goods_picture` (
  `GPID` varchar(50) NOT NULL COMMENT '商品图片ID',
  `GIID` varchar(50) NOT NULL COMMENT '商品信息ID',
  `Gpicture` varchar(100) NOT NULL COMMENT '商品图片',
  PRIMARY KEY (`GPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_sales
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_sales`;
CREATE TABLE `tb_goods_sales` (
  `gsid` varchar(50) NOT NULL,
  `giid` varchar(50) NOT NULL,
  `salestotal` int(200) DEFAULT NULL,
  `expanddesc` varchar(500) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`gsid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_sku
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_sku`;
CREATE TABLE `tb_goods_sku` (
  `GSKUID` varchar(50) NOT NULL COMMENT '商品SKUID',
  `SpecificationsID` varchar(500) DEFAULT NULL,
  `GIID` varchar(50) DEFAULT NULL COMMENT '商品信息ID',
  `SKUPic` varchar(255) NOT NULL DEFAULT '' COMMENT 'SKU图片',
  `FaceValue` decimal(18,2) DEFAULT NULL COMMENT '面值',
  `MarketPrice` decimal(18,2) DEFAULT NULL COMMENT '市场价',
  `RetailPrice` decimal(18,2) DEFAULT '0.00' COMMENT '零售原价',
  `AgreementPrice` decimal(18,2) DEFAULT NULL COMMENT '协议价',
  `InitialInventory` int(50) DEFAULT '0' COMMENT '初始库存量',
  `AvailableInventory` int(50) NOT NULL DEFAULT '0' COMMENT '可用库存量',
  `OnWayInventory` int(50) NOT NULL DEFAULT '0' COMMENT '在途库存量',
  `AddedStatus` varchar(255) NOT NULL DEFAULT '0' COMMENT '上架状态',
  `QRCode` varchar(255) NOT NULL DEFAULT '' COMMENT '上架状态',
  `SKUDescription` varchar(255) NOT NULL DEFAULT '' COMMENT 'SKU描述',
  `CommissionRate` decimal(18,2) NOT NULL DEFAULT '0.00' COMMENT '佣金比例',
  `AgentsMark` varchar(10) NOT NULL DEFAULT '0' COMMENT '可代理标识',
  `PremiumsMark` varchar(10) NOT NULL DEFAULT '' COMMENT '赠品标识',
  `Barcode` varchar(50) DEFAULT '' COMMENT 'sku条形码',
  `BarcodeDesc` varchar(200) DEFAULT '' COMMENT 'sku条形码描述',
  `flag` varchar(2) DEFAULT '0',
  `CreateTime` datetime DEFAULT CURRENT_TIMESTAMP,
  `sku_name` varchar(100) NOT NULL DEFAULT '' COMMENT 'sku名称',
  PRIMARY KEY (`GSKUID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_specification
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_specification`;
CREATE TABLE `tb_goods_specification` (
  `GSID` varchar(50) NOT NULL COMMENT '商品规格ID',
  `GIID` varchar(50) NOT NULL COMMENT '商品信息ID',
  `SGSID` varchar(50) NOT NULL COMMENT '标准商品规格ID',
  `ImpactPriceMark` varchar(1) NOT NULL COMMENT '影响价格标识',
  `flag` varchar(2) DEFAULT '0',
  PRIMARY KEY (`GSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_specification_option
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_specification_option`;
CREATE TABLE `tb_goods_specification_option` (
  `GSOID` varchar(50) NOT NULL COMMENT '商品规格选项ID',
  `GSID` varchar(50) NOT NULL COMMENT '商品规格ID',
  `GSKUID` varchar(50) NOT NULL COMMENT '商品SKUID',
  `SGSOID` varchar(50) NOT NULL COMMENT '标准商品规格选项ID',
  `flag` varchar(2) DEFAULT '0',
  PRIMARY KEY (`GSOID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_goods_subclass
-- ----------------------------
DROP TABLE IF EXISTS `tb_goods_subclass`;
CREATE TABLE `tb_goods_subclass` (
  `GSID` varchar(50) NOT NULL,
  `GCID` varchar(50) NOT NULL,
  `GSName` varchar(50) NOT NULL,
  `gs_description` varchar(255) NOT NULL DEFAULT '' COMMENT '商品小类描述',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `gs_sort` int(10) NOT NULL DEFAULT '0' COMMENT '分类排序',
  PRIMARY KEY (`GSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_groups_info
-- ----------------------------
DROP TABLE IF EXISTS `tb_groups_info`;
CREATE TABLE `tb_groups_info` (
  `GIID` varchar(50) NOT NULL,
  `GroupsName` varchar(100) NOT NULL,
  `UserID` varchar(50) NOT NULL,
  `CreatedTime` datetime NOT NULL,
  PRIMARY KEY (`GIID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_groups_member
-- ----------------------------
DROP TABLE IF EXISTS `tb_groups_member`;
CREATE TABLE `tb_groups_member` (
  `GMID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `UserID` varchar(50) NOT NULL,
  `JoinedTime` datetime NOT NULL,
  PRIMARY KEY (`GMID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_group_chat
-- ----------------------------
DROP TABLE IF EXISTS `tb_group_chat`;
CREATE TABLE `tb_group_chat` (
  `GCID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `BubbleContentType` varchar(50) NOT NULL,
  `BubbleText` varchar(500) DEFAULT NULL,
  `UserID` varchar(50) NOT NULL,
  `SendTime` datetime NOT NULL,
  PRIMARY KEY (`GCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_index_banner
-- ----------------------------
DROP TABLE IF EXISTS `tb_index_banner`;
CREATE TABLE `tb_index_banner` (
  `ibid` varchar(50) NOT NULL,
  `advertising_id` varchar(50) NOT NULL DEFAULT '',
  `bannerimg` varchar(200) DEFAULT '',
  `sort` int(11) DEFAULT '0',
  `expanddesc` varchar(500) DEFAULT '',
  `bannerurl` varchar(500) DEFAULT '',
  `banner_type` varchar(4) DEFAULT '1' COMMENT 'banner连接类型，1：图文，2：外链',
  `introduction` longtext COMMENT '广告图文介绍',
  `is_show` varchar(255) NOT NULL DEFAULT '0' COMMENT '是否显示，1：显示，0：不显示',
  `is_home` varchar(4) NOT NULL DEFAULT '1' COMMENT '显示位置，1：商城首页，2：福利首页（该字段不使用，已废弃）',
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
  `lastmodifiedtime` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_delete` varchar(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ibid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_information_irregularities_cause
-- ----------------------------
DROP TABLE IF EXISTS `tb_information_irregularities_cause`;
CREATE TABLE `tb_information_irregularities_cause` (
  `IICID` int(4) NOT NULL AUTO_INCREMENT COMMENT '信息不合规反馈原因ID',
  `ICAUSE` varchar(200) NOT NULL COMMENT '信息不合规反馈原因',
  PRIMARY KEY (`IICID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_integral_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_integral_record`;
CREATE TABLE `tb_integral_record` (
  `IRDID` varchar(50) NOT NULL,
  `IRID` varchar(50) NOT NULL,
  `Lntegral` int(50) NOT NULL DEFAULT '0',
  `OperatingTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `GIID` varchar(50) DEFAULT NULL,
  `UserID` varchar(50) DEFAULT NULL,
  `qiid` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`IRDID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_integral_record_del
-- ----------------------------
DROP TABLE IF EXISTS `tb_integral_record_del`;
CREATE TABLE `tb_integral_record_del` (
  `IRDID` varchar(50) NOT NULL,
  `IRID` varchar(50) NOT NULL,
  `Lntegral` int(50) NOT NULL DEFAULT '0',
  `OperatingTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `GIID` varchar(50) DEFAULT NULL,
  `UserID` varchar(50) DEFAULT NULL,
  `qiid` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`IRDID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_integral_rules
-- ----------------------------
DROP TABLE IF EXISTS `tb_integral_rules`;
CREATE TABLE `tb_integral_rules` (
  `IRID` int(4) NOT NULL AUTO_INCREMENT,
  `Operating` varchar(30) DEFAULT NULL,
  `IRMB` int(8) NOT NULL,
  `Lntegral` varchar(50) NOT NULL,
  `EnableMark` varchar(50) NOT NULL,
  `CreateTime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IRID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_invite_your_friends_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_invite_your_friends_record`;
CREATE TABLE `tb_invite_your_friends_record` (
  `IYFRID` varchar(50) NOT NULL,
  `CommunityType` varchar(50) NOT NULL,
  `RINo` varchar(40) NOT NULL,
  `OperatingTime` datetime NOT NULL,
  `UserID` varchar(50) NOT NULL,
  PRIMARY KEY (`IYFRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_invoice_information
-- ----------------------------
DROP TABLE IF EXISTS `tb_invoice_information`;
CREATE TABLE `tb_invoice_information` (
  `IIID` varchar(50) DEFAULT NULL COMMENT '发票信息ID',
  `UserId` varchar(50) DEFAULT NULL COMMENT '用户ID',
  `Invoice` varchar(100) DEFAULT NULL COMMENT '发票抬头',
  `InvoiceType` varchar(50) DEFAULT NULL COMMENT '发票类型',
  `InvoiceContent` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_logistics_companies
-- ----------------------------
DROP TABLE IF EXISTS `tb_logistics_companies`;
CREATE TABLE `tb_logistics_companies` (
  `LCID` varchar(50) NOT NULL COMMENT '物流公司ID',
  `LCName` varchar(40) NOT NULL COMMENT '物流公司名称',
  `LCIntroduction` varchar(500) NOT NULL COMMENT '物流公司介绍',
  `ServiceLine` varchar(15) NOT NULL COMMENT '服务电话',
  PRIMARY KEY (`LCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_lost_and_found
-- ----------------------------
DROP TABLE IF EXISTS `tb_lost_and_found`;
CREATE TABLE `tb_lost_and_found` (
  `LAFID` varchar(50) NOT NULL COMMENT '失物招领ID',
  `BIID` varchar(50) DEFAULT NULL COMMENT '商户信息ID',
  `LAFTitle` varchar(100) DEFAULT NULL,
  `RegisterTime` datetime(6) NOT NULL COMMENT '登记时间',
  `LostLocation` varchar(100) NOT NULL COMMENT '遗失地点',
  `Characterization` varchar(200) NOT NULL COMMENT '特征描述',
  `LostStatus` varchar(50) NOT NULL DEFAULT '1' COMMENT '失物状态',
  `ClaimTime` datetime(6) NOT NULL COMMENT '认领时间',
  `UserID` varchar(50) DEFAULT NULL COMMENT '认领用户ID',
  `ClaimantName` varchar(20) NOT NULL COMMENT '认领人姓名',
  `ClaimantMPhone` varchar(15) NOT NULL COMMENT '认领人手机',
  `ClaimantDocType` varchar(50) NOT NULL DEFAULT '1' COMMENT '认领人证件类型',
  `ClaimantDocNum` varchar(50) NOT NULL COMMENT '认领人证件号码',
  `DetailsInfo` varchar(200) NOT NULL COMMENT '招领详情信息',
  PRIMARY KEY (`LAFID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_lost_and_found_photo
-- ----------------------------
DROP TABLE IF EXISTS `tb_lost_and_found_photo`;
CREATE TABLE `tb_lost_and_found_photo` (
  `LAFPID` varchar(50) NOT NULL COMMENT '失物招领照片ID',
  `LAFID` varchar(50) NOT NULL COMMENT '失物招领ID',
  `LAFPhoto` varchar(100) NOT NULL COMMENT '失物招领照片',
  PRIMARY KEY (`LAFPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_lost_registration
-- ----------------------------
DROP TABLE IF EXISTS `tb_lost_registration`;
CREATE TABLE `tb_lost_registration` (
  `LRID` varchar(50) NOT NULL COMMENT '失物登记ID',
  `BIID` varchar(50) DEFAULT NULL COMMENT '商户信息ID',
  `UserID` varchar(50) DEFAULT NULL COMMENT '登记用户ID',
  `RPersonName` varchar(20) NOT NULL COMMENT '登记人姓名',
  `RPersonMPhone` varchar(15) NOT NULL COMMENT '登记人手机',
  `RPersonDocType` varchar(50) NOT NULL DEFAULT '1' COMMENT '登记人证件类型',
  `RPersonDocNum` varchar(30) NOT NULL COMMENT '登记人证件号码',
  `RegisterTime` datetime(6) NOT NULL COMMENT '登记时间',
  `LostLocation` varchar(100) NOT NULL COMMENT '遗失地点',
  `Characterization` varchar(200) NOT NULL COMMENT '特征描述',
  `LostStatus` varchar(50) NOT NULL DEFAULT '1' COMMENT '失物状态',
  `ClaimTime` datetime(6) DEFAULT NULL COMMENT '认领时间',
  `Title` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_lost_registration_photo
-- ----------------------------
DROP TABLE IF EXISTS `tb_lost_registration_photo`;
CREATE TABLE `tb_lost_registration_photo` (
  `LRPID` varchar(50) NOT NULL COMMENT '失物登记照片ID',
  `LRID` varchar(50) NOT NULL COMMENT '失物登记ID',
  `LRPhoto` varchar(100) NOT NULL COMMENT '失物登记照片',
  PRIMARY KEY (`LRPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_lounge_appointment
-- ----------------------------
DROP TABLE IF EXISTS `tb_lounge_appointment`;
CREATE TABLE `tb_lounge_appointment` (
  `LAID` varchar(50) NOT NULL COMMENT '贵宾厅预约ID',
  `UserID` varchar(50) NOT NULL COMMENT '用户ID',
  `Instructions` varchar(200) NOT NULL DEFAULT '' COMMENT '预约说明',
  `ArrivalTime` datetime(6) NOT NULL COMMENT '预约到达时间',
  `AHours` varchar(50) NOT NULL COMMENT '预约小时数',
  `SubmitTime` datetime(6) NOT NULL COMMENT '预约提交',
  `OrderID` varchar(50) NOT NULL DEFAULT '' COMMENT '订单ID',
  `AStatus` varchar(50) NOT NULL COMMENT '预约状态',
  `AppointNumber` int(11) DEFAULT NULL,
  `AirportNO` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`LAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_management_fee_billing_business
-- ----------------------------
DROP TABLE IF EXISTS `tb_management_fee_billing_business`;
CREATE TABLE `tb_management_fee_billing_business` (
  `MFBBID` varchar(50) NOT NULL,
  `PMFBRID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `BillingTime` datetime NOT NULL,
  `BillingAmt` decimal(10,2) NOT NULL DEFAULT '0.00',
  `PUserID` varchar(50) NOT NULL,
  PRIMARY KEY (`MFBBID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_membership_level
-- ----------------------------
DROP TABLE IF EXISTS `tb_membership_level`;
CREATE TABLE `tb_membership_level` (
  `MLID` int(2) NOT NULL AUTO_INCREMENT COMMENT '会员等级ID',
  `MLName` varchar(20) NOT NULL,
  `LevelIcons` varchar(255) NOT NULL COMMENT '等级图标',
  `Expense` decimal(10,2) NOT NULL COMMENT '满消费额',
  `Level` varchar(50) NOT NULL DEFAULT '1' COMMENT '会员等级',
  `is_display` varchar(1) NOT NULL DEFAULT '0' COMMENT '是否展示  : 1:展示；  0：不展示',
  PRIMARY KEY (`MLID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_member_label
-- ----------------------------
DROP TABLE IF EXISTS `tb_member_label`;
CREATE TABLE `tb_member_label` (
  `MLAID` int(4) NOT NULL,
  `MLAName` varchar(255) NOT NULL,
  PRIMARY KEY (`MLAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_my_flights
-- ----------------------------
DROP TABLE IF EXISTS `tb_my_flights`;
CREATE TABLE `tb_my_flights` (
  `MFID` varchar(50) NOT NULL COMMENT '我的航班ID',
  `FIID` varchar(50) DEFAULT NULL COMMENT '航班信息ID',
  `FlightNo` varchar(20) NOT NULL COMMENT '航班号',
  `FlightDate` datetime(6) NOT NULL,
  `leaveAIID` varchar(50) NOT NULL COMMENT '出发机场ID',
  `leaveAreaID` varchar(50) NOT NULL COMMENT '出发城市ID',
  `BoardingPort` varchar(50) DEFAULT NULL COMMENT '登机口',
  `HandleCounter` varchar(50) DEFAULT NULL COMMENT '办理柜台',
  `ArrivalsAIID` varchar(50) NOT NULL COMMENT '到达机场ID',
  `ArrivalsAreaID` varchar(50) NOT NULL COMMENT '到达城市ID',
  `ArrivalsTime` datetime(6) NOT NULL,
  `BaggageBelts` varchar(50) DEFAULT NULL COMMENT '行李带',
  `ReserveTicketNo` varchar(20) DEFAULT NULL COMMENT '预订机票号',
  `ArrivalsTerminal` varchar(20) NOT NULL,
  `leaveTerminal` varchar(20) NOT NULL,
  `leaveTime` datetime(6) NOT NULL,
  `UserID` varchar(50) NOT NULL,
  `AirlineID` varchar(50) DEFAULT NULL,
  `isAttention` varchar(2) DEFAULT '0',
  PRIMARY KEY (`MFID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_my_message
-- ----------------------------
DROP TABLE IF EXISTS `tb_my_message`;
CREATE TABLE `tb_my_message` (
  `MMID` varchar(50) NOT NULL,
  `MsgType` varchar(50) DEFAULT NULL,
  `RelatedInforID` varchar(50) DEFAULT NULL,
  `ArrivalTime` datetime DEFAULT NULL,
  `UserID` varchar(50) DEFAULT NULL,
  `ArrTitle` varchar(100) DEFAULT '通知' COMMENT '消息标题',
  `ArrContent` varchar(500) DEFAULT NULL,
  `State` int(2) DEFAULT '0',
  PRIMARY KEY (`MMID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_my_message_details
-- ----------------------------
DROP TABLE IF EXISTS `tb_my_message_details`;
CREATE TABLE `tb_my_message_details` (
  `RelatedInforID` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` varchar(1000) NOT NULL,
  PRIMARY KEY (`RelatedInforID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_action_definition
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_action_definition`;
CREATE TABLE `tb_order_action_definition` (
  `OADID` varchar(50) NOT NULL COMMENT '订单操作定义ID',
  `OADName` varchar(20) NOT NULL COMMENT '订单操作名称',
  PRIMARY KEY (`OADID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_goods_sku
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_goods_sku`;
CREATE TABLE `tb_order_goods_sku` (
  `OGSKUID` varchar(50) NOT NULL COMMENT '订单商品SKUID',
  `master_id` varchar(32) DEFAULT NULL COMMENT '主单id',
  `logistical_id` varchar(32) DEFAULT NULL COMMENT '物流单id',
  `refund_record_id` varchar(32) DEFAULT NULL COMMENT '退款单id',
  `OrderID` varchar(50) NOT NULL COMMENT '订单ID',
  `integral_price` decimal(18,2) DEFAULT NULL COMMENT '积分优惠券金额',
  `refundable_amount` decimal(18,2) DEFAULT NULL COMMENT '可退款总金额',
  `refundable_integral` varchar(200) DEFAULT NULL COMMENT '可退款总积分',
  `is_refund` varchar(8) DEFAULT NULL COMMENT '是否已发生退款',
  `discount_price` decimal(18,2) DEFAULT NULL COMMENT '优惠金额',
  `SCGID` varchar(50) NOT NULL COMMENT '购物车商品ID',
  `Quantity` varchar(50) NOT NULL COMMENT '数量',
  `RetailPrice` decimal(18,2) NOT NULL COMMENT '零售原价',
  `ActualPrice` decimal(18,2) NOT NULL COMMENT '实际价格',
  `ActualPayment` decimal(18,2) DEFAULT NULL COMMENT '实付款',
  `SKUIntegral` int(10) DEFAULT '0',
  `SKUIntegralValue` decimal(18,2) DEFAULT '0.00',
  PRIMARY KEY (`OGSKUID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_information
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_information`;
CREATE TABLE `tb_order_information` (
  `OrderID` varchar(250) NOT NULL COMMENT '订单ID',
  `OrderNumber` varchar(250) DEFAULT NULL COMMENT '订单编号',
  `master_order_id` varchar(32) DEFAULT NULL COMMENT '主订单id',
  `service_id` varchar(32) DEFAULT NULL COMMENT '服务类型id',
  `refundable_amount` decimal(18,2) DEFAULT NULL COMMENT '可退款总金额',
  `refundable_integral` varchar(20) DEFAULT NULL COMMENT '可退款总积分',
  `UserID` varchar(50) DEFAULT NULL,
  `BIID` varchar(50) DEFAULT NULL COMMENT '商户信息ID',
  `PPSKUID` varchar(50) DEFAULT NULL COMMENT '商品套餐SKUID',
  `PMID` int(2) DEFAULT NULL COMMENT '支付方式ID',
  `paymentmeans` char(255) DEFAULT NULL,
  `shop_address` varchar(255) DEFAULT NULL COMMENT '店铺地址',
  `shop_name` varchar(50) DEFAULT NULL COMMENT '店铺名称',
  `DMID` varchar(8) DEFAULT NULL COMMENT '配送方式ID',
  `DAID` varchar(50) DEFAULT NULL COMMENT '送货地址ID',
  `DLCID` varchar(50) DEFAULT NULL,
  `LCName` varchar(50) DEFAULT NULL,
  `DeliveryNo` varchar(20) DEFAULT NULL COMMENT '送货单号',
  `SwapNo` varchar(20) DEFAULT NULL COMMENT '换货送货单号',
  `RAID` varchar(50) DEFAULT NULL COMMENT '退货地址ID',
  `RLCID` int(2) DEFAULT NULL COMMENT '物流公司（退货）ID',
  `ReturnNo` int(20) DEFAULT NULL COMMENT '退货单号',
  `VirtualGoodsMark` varchar(8) DEFAULT '0' COMMENT '是否虚拟商品 0：实物商品，1：虚拟商品，2：餐饮',
  `Status` varchar(8) DEFAULT '1' COMMENT '订单状态',
  `TradingResults` char(1) DEFAULT '0' COMMENT '交易结果',
  `TotalPrice` decimal(18,2) DEFAULT '0.00' COMMENT '订单总价',
  `DiscountPrice` decimal(18,2) DEFAULT '0.00' COMMENT '折扣后总价',
  `GoodsPrice` decimal(18,2) DEFAULT NULL,
  `CouponOffsetAmt` decimal(18,2) DEFAULT '0.00' COMMENT '优惠券抵用额',
  `VoucherOffsetAmt` decimal(18,2) DEFAULT '0.00' COMMENT '抵用券使用额',
  `IntegralOffsetAmt` decimal(18,2) DEFAULT '0.00' COMMENT '积分抵用额',
  `IntegralAmt` int(10) DEFAULT '0' COMMENT '使用积分数',
  `ActualpaidAmount` decimal(18,2) DEFAULT '0.00' COMMENT '实际支付金额',
  `NeedInvoice` varchar(8) DEFAULT '0' COMMENT '是否需要发票',
  `IFInvoiced` varchar(8) DEFAULT '0' COMMENT '是否已开票',
  `IIID` varchar(50) DEFAULT NULL COMMENT '发票信息ID',
  `RSRID` int(2) DEFAULT NULL COMMENT '退换货标准原因ID',
  `Postage` decimal(18,2) DEFAULT '0.00' COMMENT '运费',
  `SPAID` varchar(50) DEFAULT NULL COMMENT '优惠策略活动ID',
  `BillingStatus` varchar(8) DEFAULT '0' COMMENT '结算状态',
  `CommissionAmount` decimal(18,2) DEFAULT '0.00' COMMENT '平台提成金额',
  `PlatformIncome` decimal(18,2) DEFAULT '0.00' COMMENT '平台收入',
  `PlatformPayables` decimal(18,2) DEFAULT '0.00' COMMENT '平台应付款',
  `CreateTime` datetime(6) DEFAULT NULL COMMENT '生成时间',
  `UpdateTime` datetime(6) DEFAULT NULL,
  `PaymentTime` datetime(6) DEFAULT NULL COMMENT '付款时间',
  `ShipTime` datetime(6) DEFAULT NULL COMMENT '发货时间',
  `ReceiptTime` datetime(6) DEFAULT NULL COMMENT '收货时间',
  `ReturnTime` datetime(6) DEFAULT NULL COMMENT '退货时间',
  `RefundTime` datetime(6) DEFAULT NULL COMMENT '退款时间',
  `SwapShipTime` datetime(6) DEFAULT NULL COMMENT '换货发货时间',
  `SwapReceiptTime` datetime(6) DEFAULT NULL COMMENT '换货收货时间',
  `BillingTime` datetime(6) DEFAULT NULL COMMENT '结算时间',
  `EndTime` datetime(6) DEFAULT NULL COMMENT '完结时间',
  `CloseTime` datetime(6) DEFAULT NULL COMMENT '关闭时间',
  `flag` varchar(8) DEFAULT '0',
  `ratedFlag` varchar(8) DEFAULT '1' COMMENT '1、待评价(默认)  2、已评价  3、已修改',
  `OrderSource` varchar(50) DEFAULT '0' COMMENT '1：app，2：微信公众号，3：微信小程序',
  `OrderRemark` varchar(500) DEFAULT NULL,
  `ReturnPrice` decimal(18,2) DEFAULT NULL,
  `order_diners_count` int(11) DEFAULT '0' COMMENT '餐饮订单用餐人数',
  `order_table_no` varchar(255) NOT NULL DEFAULT '' COMMENT '餐饮店铺订单桌号',
  `tableware_fee` decimal(18,2) NOT NULL DEFAULT '0.00' COMMENT '餐具费',
  `amount_free` decimal(18,2) NOT NULL DEFAULT '0.00' COMMENT '免单金额不包括积分减免，单对霸王餐减免',
  PRIMARY KEY (`OrderID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_information_del
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_information_del`;
CREATE TABLE `tb_order_information_del` (
  `OrderID` varchar(250) NOT NULL COMMENT '订单ID',
  `OrderNumber` varchar(250) DEFAULT NULL COMMENT '订单编号',
  `master_order_id` varchar(32) DEFAULT NULL COMMENT '主订单id',
  `service_id` varchar(32) DEFAULT NULL COMMENT '服务类型id',
  `refundable_amount` decimal(18,2) DEFAULT '0.00' COMMENT '可退款总金额',
  `refundable_integral` varchar(20) DEFAULT '' COMMENT '可退款总积分',
  `UserID` varchar(50) DEFAULT NULL,
  `BIID` varchar(50) DEFAULT NULL COMMENT '商户信息ID',
  `PPSKUID` varchar(50) DEFAULT NULL COMMENT '商品套餐SKUID',
  `PMID` int(20) DEFAULT NULL COMMENT '支付方式ID',
  `paymentmeans` char(255) DEFAULT NULL,
  `shop_address` varchar(255) DEFAULT NULL COMMENT '店铺地址',
  `shop_name` varchar(50) DEFAULT NULL COMMENT '店铺名称',
  `DMID` int(20) DEFAULT NULL COMMENT '配送方式ID',
  `DAID` varchar(50) DEFAULT NULL COMMENT '送货地址ID',
  `DLCID` varchar(50) DEFAULT NULL,
  `LCName` varchar(50) DEFAULT NULL,
  `DeliveryNo` varchar(20) DEFAULT NULL COMMENT '送货单号',
  `SwapNo` varchar(20) DEFAULT NULL COMMENT '换货送货单号',
  `RAID` varchar(50) DEFAULT NULL COMMENT '退货地址ID',
  `RLCID` int(20) DEFAULT NULL COMMENT '物流公司（退货）ID',
  `ReturnNo` int(20) DEFAULT NULL COMMENT '退货单号',
  `VirtualGoodsMark` varchar(50) DEFAULT '0' COMMENT '是否虚拟商品 0：实物商品，1：虚拟商品，2：餐饮',
  `Status` varchar(50) DEFAULT '1' COMMENT '订单状态',
  `TradingResults` varchar(50) DEFAULT '0' COMMENT '交易结果',
  `TotalPrice` decimal(18,2) DEFAULT '0.00' COMMENT '订单总价',
  `DiscountPrice` decimal(18,2) DEFAULT '0.00' COMMENT '折扣后总价',
  `GoodsPrice` decimal(18,2) DEFAULT NULL,
  `CouponOffsetAmt` decimal(18,2) DEFAULT '0.00' COMMENT '优惠券抵用额',
  `VoucherOffsetAmt` decimal(18,2) DEFAULT '0.00' COMMENT '抵用券使用额',
  `IntegralOffsetAmt` decimal(18,2) DEFAULT '0.00' COMMENT '积分抵用额',
  `IntegralAmt` int(10) DEFAULT '0' COMMENT '使用积分数',
  `ActualpaidAmount` decimal(18,2) DEFAULT '0.00' COMMENT '实际支付金额',
  `NeedInvoice` varchar(50) DEFAULT '0' COMMENT '是否需要发票',
  `IFInvoiced` varchar(50) DEFAULT '0' COMMENT '是否已开票',
  `IIID` varchar(50) DEFAULT NULL COMMENT '发票信息ID',
  `RSRID` int(20) DEFAULT NULL COMMENT '退换货标准原因ID',
  `Postage` decimal(18,2) DEFAULT '0.00' COMMENT '运费',
  `SPAID` varchar(50) DEFAULT NULL COMMENT '优惠策略活动ID',
  `BillingStatus` varchar(50) DEFAULT '0' COMMENT '结算状态',
  `CommissionAmount` decimal(18,2) DEFAULT '0.00' COMMENT '平台提成金额',
  `PlatformIncome` decimal(18,2) DEFAULT '0.00' COMMENT '平台收入',
  `PlatformPayables` decimal(18,2) DEFAULT '0.00' COMMENT '平台应付款',
  `CreateTime` datetime(6) DEFAULT NULL COMMENT '生成时间',
  `UpdateTime` datetime(6) DEFAULT NULL COMMENT '更新时间',
  `PaymentTime` datetime(6) DEFAULT NULL COMMENT '付款时间',
  `ShipTime` datetime(6) DEFAULT NULL COMMENT '发货时间',
  `ReceiptTime` datetime(6) DEFAULT NULL COMMENT '收货时间',
  `ReturnTime` datetime(6) DEFAULT NULL COMMENT '退货时间',
  `RefundTime` datetime(6) DEFAULT NULL COMMENT '退款时间',
  `SwapShipTime` datetime(6) DEFAULT NULL COMMENT '换货发货时间',
  `SwapReceiptTime` datetime(6) DEFAULT NULL COMMENT '换货收货时间',
  `BillingTime` datetime(6) DEFAULT NULL COMMENT '结算时间',
  `EndTime` datetime(6) DEFAULT NULL COMMENT '完结时间',
  `CloseTime` datetime(6) DEFAULT NULL COMMENT '关闭时间',
  `flag` varchar(50) DEFAULT '0',
  `ratedFlag` varchar(50) DEFAULT '1' COMMENT '1、待评价(默认)  2、已评价  3、已修改',
  `OrderSource` varchar(50) DEFAULT '0' COMMENT '1：app，2：微信公众号，3：微信小程序',
  `OrderRemark` varchar(500) DEFAULT NULL,
  `ReturnPrice` decimal(18,2) DEFAULT NULL,
  `order_diners_count` int(11) DEFAULT '0' COMMENT '餐饮订单用餐人数',
  `order_table_no` varchar(255) NOT NULL DEFAULT '' COMMENT '餐饮店铺订单桌号',
  `tableware_fee` decimal(18,2) NOT NULL DEFAULT '0.00' COMMENT '餐具费',
  `amount_free` decimal(18,2) NOT NULL DEFAULT '0.00' COMMENT '免单金额不包括积分减免，单对霸王餐减免',
  PRIMARY KEY (`OrderID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_operation_log
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_operation_log`;
CREATE TABLE `tb_order_operation_log` (
  `OOLID` varchar(50) NOT NULL COMMENT '订单操作日志ID',
  `OrderID` varchar(50) NOT NULL COMMENT '订单ID',
  `OADID` varchar(50) NOT NULL COMMENT '订单操作定义ID',
  `OperateTime` datetime(6) NOT NULL COMMENT '订单操作时间',
  `OperatorType` varchar(50) NOT NULL COMMENT '操作人类型',
  `OperatorID` varchar(50) NOT NULL COMMENT '操作人ID',
  PRIMARY KEY (`OOLID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_preferential_activity
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_preferential_activity`;
CREATE TABLE `tb_order_preferential_activity` (
  `OPAID` varchar(50) NOT NULL COMMENT '订单优惠活动ID',
  `PTAID` varchar(50) NOT NULL COMMENT '优惠策略活动ID',
  PRIMARY KEY (`OPAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_premiums
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_premiums`;
CREATE TABLE `tb_order_premiums` (
  `OPID` varchar(50) NOT NULL COMMENT '订单赠品ID',
  `OrderID` varchar(50) NOT NULL COMMENT '订单ID',
  `PTAPCID` varchar(50) NOT NULL COMMENT '优惠策略活动参与商品ID',
  `GSKUID` varchar(50) NOT NULL COMMENT '商品(赠品)SKUID',
  `GetNum` varchar(50) NOT NULL COMMENT '赠送数量'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_return_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_return_record`;
CREATE TABLE `tb_order_return_record` (
  `OGSKUID` varchar(50) NOT NULL COMMENT '订单商品SKUID',
  `Quantity` int(5) DEFAULT NULL,
  `ActionType` varchar(8) NOT NULL DEFAULT '0' COMMENT '1：退货，2：换货，3：退款',
  `ReturnStatus` varchar(8) NOT NULL COMMENT '0：无状态，1：发起退款，2：退款成功，3：退款失败',
  `CShipmentNum` varchar(20) NOT NULL DEFAULT '',
  `ReplacementStatus` varchar(8) NOT NULL COMMENT '0：无状态，1：发起换货，2：商家已发货，3：换货成功，4：换货失败',
  `BShipmentNum` varchar(20) DEFAULT NULL,
  `BReplacementLogistical` varchar(50) DEFAULT NULL,
  `ReturnTime` datetime(6) DEFAULT NULL,
  `ConfirmTime` datetime(6) DEFAULT NULL,
  `ReturnWhy` varchar(255) DEFAULT NULL,
  `ReturnLogistical` varchar(20) DEFAULT '' COMMENT '退货物流公司',
  `GSKUID` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`OGSKUID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_use_coupon
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_use_coupon`;
CREATE TABLE `tb_order_use_coupon` (
  `OUCID` varchar(50) NOT NULL COMMENT '订单使用优惠券ID',
  `OrderID` varchar(50) NOT NULL COMMENT '订单ID',
  `RCID` varchar(50) NOT NULL COMMENT '领用优惠券ID',
  PRIMARY KEY (`OUCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_order_use_voucher
-- ----------------------------
DROP TABLE IF EXISTS `tb_order_use_voucher`;
CREATE TABLE `tb_order_use_voucher` (
  `OUVID` varchar(50) NOT NULL COMMENT '订单使用优惠券ID',
  `OrderID` varchar(50) NOT NULL,
  `BWID` varchar(50) NOT NULL,
  PRIMARY KEY (`OUVID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_partook
-- ----------------------------
DROP TABLE IF EXISTS `tb_partook`;
CREATE TABLE `tb_partook` (
  `PID` varchar(50) NOT NULL,
  `Imgs` varchar(255) NOT NULL,
  `Title` varchar(50) NOT NULL,
  `Url` varchar(255) NOT NULL,
  `Description` varchar(255) NOT NULL,
  PRIMARY KEY (`PID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_payment_method
-- ----------------------------
DROP TABLE IF EXISTS `tb_payment_method`;
CREATE TABLE `tb_payment_method` (
  `PMID` varchar(10) NOT NULL COMMENT '支付方式ID',
  `PMName` varchar(20) NOT NULL COMMENT '支付方式名称',
  PRIMARY KEY (`PMID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_pay_ordernumber
-- ----------------------------
DROP TABLE IF EXISTS `tb_pay_ordernumber`;
CREATE TABLE `tb_pay_ordernumber` (
  `ponid` varchar(50) NOT NULL,
  `ordernumber` varchar(50) DEFAULT NULL,
  `upperordernumber` varchar(50) DEFAULT NULL,
  `islast` varchar(2) DEFAULT '0',
  `outtradeno_gzh` varchar(100) DEFAULT '',
  `createtime` datetime DEFAULT NULL,
  PRIMARY KEY (`ponid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_platform
-- ----------------------------
DROP TABLE IF EXISTS `tb_platform`;
CREATE TABLE `tb_platform` (
  `PID` varchar(50) NOT NULL,
  `CashAccount` decimal(20,2) NOT NULL DEFAULT '0.00',
  `CashLockAccount` decimal(20,2) NOT NULL DEFAULT '0.00',
  `FirstMessage` varchar(200) NOT NULL,
  `CustomerWaitTimeSet` int(3) NOT NULL,
  `NoFeedbackEndTime` int(3) NOT NULL,
  `MostReceiveCustomers` int(3) NOT NULL,
  `WaitMsg` varchar(200) NOT NULL,
  `PointsValue` int(4) NOT NULL,
  `HighestPercent` decimal(2,2) NOT NULL,
  `PayPalAccount` varchar(20) DEFAULT NULL,
  `WeChatAccount` varchar(20) DEFAULT NULL,
  `ApplePay` varchar(20) DEFAULT NULL,
  `OrderRoyaltyRate` decimal(2,2) DEFAULT NULL,
  `LogisticsDMEnable` char(1) NOT NULL DEFAULT '1',
  `SelfDMEnable` char(1) NOT NULL DEFAULT '1',
  `DeliveryPointEnable` char(1) NOT NULL DEFAULT '1',
  `OrderStorageTime` int(2) DEFAULT '36',
  `ReportFormTime` int(2) DEFAULT '6',
  `CustomerQ` int(2) DEFAULT '6',
  PRIMARY KEY (`PID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_platform_account_change_reason
-- ----------------------------
DROP TABLE IF EXISTS `tb_platform_account_change_reason`;
CREATE TABLE `tb_platform_account_change_reason` (
  `PACRID` varchar(50) NOT NULL COMMENT '平台资金账户变动原因ID',
  `PACReason` varchar(40) NOT NULL COMMENT '平台资金账户变动原因',
  PRIMARY KEY (`PACRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_platform_account_change_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_platform_account_change_record`;
CREATE TABLE `tb_platform_account_change_record` (
  `PACRTID` varchar(50) NOT NULL,
  `CashAccountType` varchar(5) NOT NULL,
  `Direction` varchar(5) NOT NULL,
  `ChangeAmount` decimal(12,2) NOT NULL,
  `PACRID` varchar(10) NOT NULL,
  `AccountTypes` varchar(50) NOT NULL,
  `OtherID` varchar(50) NOT NULL,
  `OtherCAT` varchar(50) NOT NULL,
  `ChangeTime` datetime NOT NULL,
  PRIMARY KEY (`PACRTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_platform_copywriter
-- ----------------------------
DROP TABLE IF EXISTS `tb_platform_copywriter`;
CREATE TABLE `tb_platform_copywriter` (
  `PCID` int(4) NOT NULL AUTO_INCREMENT,
  `PCName` varchar(50) NOT NULL,
  `PCContent` varchar(1000) NOT NULL,
  PRIMARY KEY (`PCID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_platform_management_feebilling_records
-- ----------------------------
DROP TABLE IF EXISTS `tb_platform_management_feebilling_records`;
CREATE TABLE `tb_platform_management_feebilling_records` (
  `PMFBRID` varchar(50) NOT NULL,
  `BillingMonth` datetime NOT NULL,
  `MFBTotal` decimal(22,2) NOT NULL,
  PRIMARY KEY (`PMFBRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_platform_user
-- ----------------------------
DROP TABLE IF EXISTS `tb_platform_user`;
CREATE TABLE `tb_platform_user` (
  `PUserID` varchar(50) NOT NULL,
  `Username` varchar(40) DEFAULT NULL,
  `HeadPortrait` varchar(255) DEFAULT NULL,
  `NickName` varchar(100) DEFAULT NULL,
  `Mphone` varchar(15) NOT NULL,
  `LoginPassword` varchar(50) DEFAULT NULL,
  `RTID` varchar(20) DEFAULT NULL,
  `FullName` varchar(40) NOT NULL,
  `JobNum` varchar(20) DEFAULT NULL,
  `Position` varchar(20) DEFAULT NULL,
  `eMail` varchar(60) DEFAULT NULL,
  `Remark` varchar(500) DEFAULT NULL,
  `ASTID` varchar(50) DEFAULT NULL,
  `AIID` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`PUserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_postage_application_scope
-- ----------------------------
DROP TABLE IF EXISTS `tb_postage_application_scope`;
CREATE TABLE `tb_postage_application_scope` (
  `PASID` varchar(50) NOT NULL DEFAULT '',
  `PSID` varchar(50) DEFAULT NULL,
  `AreaID` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`PASID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_postage_settings
-- ----------------------------
DROP TABLE IF EXISTS `tb_postage_settings`;
CREATE TABLE `tb_postage_settings` (
  `PSID` varchar(50) NOT NULL DEFAULT '',
  `BIID` varchar(50) DEFAULT NULL,
  `SetType` int(1) DEFAULT NULL,
  `Postage` double(5,2) DEFAULT NULL,
  PRIMARY KEY (`PSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_preferential_coupon
-- ----------------------------
DROP TABLE IF EXISTS `tb_preferential_coupon`;
CREATE TABLE `tb_preferential_coupon` (
  `PCID` varchar(50) NOT NULL,
  `PTAID` varchar(50) NOT NULL,
  `PCName` varchar(40) NOT NULL,
  `PCPicture` varchar(255) NOT NULL,
  `FaceValue` decimal(7,2) NOT NULL DEFAULT '0.00',
  `Description` varchar(500) DEFAULT NULL,
  `UseMode` varchar(1) NOT NULL DEFAULT '1',
  `OrderFullAmt` decimal(7,2) DEFAULT NULL,
  `Unit` varchar(20) NOT NULL,
  `PerLimitNum` varchar(2) DEFAULT NULL,
  `LimitNum` varchar(8) NOT NULL DEFAULT '0',
  `BIID` varchar(50) NOT NULL,
  `EffectiveStartDate` datetime NOT NULL,
  `EffectiveEndDate` datetime NOT NULL,
  `IssueNum` varchar(8) DEFAULT NULL,
  `ReceivedNum` varchar(8) NOT NULL DEFAULT '0',
  PRIMARY KEY (`PCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_preferential_coupon_numbering
-- ----------------------------
DROP TABLE IF EXISTS `tb_preferential_coupon_numbering`;
CREATE TABLE `tb_preferential_coupon_numbering` (
  `PCNID` varchar(50) NOT NULL,
  `PCID` varchar(50) DEFAULT NULL,
  `CouponCode` int(50) DEFAULT NULL,
  `CouponStatus` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`PCNID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_preferential_strategic_activities_to_participate_in_commodity
-- ----------------------------
DROP TABLE IF EXISTS `tb_preferential_strategic_activities_to_participate_in_commodity`;
CREATE TABLE `tb_preferential_strategic_activities_to_participate_in_commodity` (
  `PTAPCID` varchar(50) NOT NULL,
  `PTAID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `UnitNum` varchar(10) NOT NULL DEFAULT '1',
  PRIMARY KEY (`PTAPCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_preferential_tactics_activity
-- ----------------------------
DROP TABLE IF EXISTS `tb_preferential_tactics_activity`;
CREATE TABLE `tb_preferential_tactics_activity` (
  `PTAID` varchar(50) NOT NULL,
  `BIID` varchar(50) DEFAULT NULL,
  `Atitle` varchar(50) DEFAULT NULL,
  `Description` varchar(1000) DEFAULT NULL,
  `Status` varchar(10) DEFAULT '0',
  `StartTime` datetime NOT NULL,
  `EndTime` datetime DEFAULT NULL,
  `CreatedTime` datetime DEFAULT NULL,
  `ReleaseTime` datetime DEFAULT NULL,
  `GoodsRange` varchar(10) DEFAULT NULL,
  `SPID` varchar(50) DEFAULT NULL,
  `GBDiscount` decimal(2,2) DEFAULT '0.00',
  `StartConsumerNum` varchar(20) DEFAULT '0',
  `BoughtNum` varchar(20) DEFAULT '0',
  `LTDiscount` decimal(2,2) DEFAULT '0.00',
  `OrderFullAmt` decimal(7,2) DEFAULT '0.00',
  PRIMARY KEY (`PTAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_product_packagessku
-- ----------------------------
DROP TABLE IF EXISTS `tb_product_packagessku`;
CREATE TABLE `tb_product_packagessku` (
  `PPSKUID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `PPName` varchar(50) NOT NULL,
  `PPPicture` varchar(255) NOT NULL,
  `PPPrice` decimal(7,2) NOT NULL,
  `ReleaseTime` datetime NOT NULL,
  `AddedStatus` varchar(20) NOT NULL DEFAULT '1',
  PRIMARY KEY (`PPSKUID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_product_packages_selcet_goodssku
-- ----------------------------
DROP TABLE IF EXISTS `tb_product_packages_selcet_goodssku`;
CREATE TABLE `tb_product_packages_selcet_goodssku` (
  `PPSGID` varchar(50) NOT NULL,
  `PPSKUID` varchar(50) NOT NULL,
  `GSKUID` varchar(50) NOT NULL,
  PRIMARY KEY (`PPSGID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_pta_member_exclusive_discount
-- ----------------------------
DROP TABLE IF EXISTS `tb_pta_member_exclusive_discount`;
CREATE TABLE `tb_pta_member_exclusive_discount` (
  `PTAMEDID` varchar(50) NOT NULL,
  `MLID` varchar(50) NOT NULL,
  `Mdiscount` decimal(2,2) NOT NULL,
  `PTAID` varchar(50) NOT NULL,
  PRIMARY KEY (`PTAMEDID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_pta_participate_packages
-- ----------------------------
DROP TABLE IF EXISTS `tb_pta_participate_packages`;
CREATE TABLE `tb_pta_participate_packages` (
  `PPAPPID` varchar(50) NOT NULL,
  `PTAID` varchar(50) NOT NULL,
  `PPSKUID` varchar(50) NOT NULL,
  PRIMARY KEY (`PPAPPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_qrcode_images
-- ----------------------------
DROP TABLE IF EXISTS `tb_qrcode_images`;
CREATE TABLE `tb_qrcode_images` (
  `qiid` varchar(64) NOT NULL DEFAULT '0',
  `qiname` varchar(100) DEFAULT NULL,
  `qtid` int(11) DEFAULT NULL,
  `qiidentification` varchar(500) DEFAULT NULL,
  `qiurl` varchar(500) DEFAULT NULL,
  `qiimages` varchar(100) DEFAULT NULL,
  `qiwechaturl` varchar(1000) DEFAULT NULL,
  `qiexpiredate` datetime DEFAULT NULL,
  `qiscantimes` int(11) DEFAULT NULL,
  `qiscanvalidtimes` int(11) DEFAULT NULL,
  `expanddesc` varchar(500) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT CURRENT_TIMESTAMP,
  `wechat_url` varchar(255) NOT NULL DEFAULT '' COMMENT '微信二维码地址',
  `wechat_ticket` varchar(255) NOT NULL DEFAULT '' COMMENT '微信二维码ticket',
  `wechat_expire_seconds` int(11) NOT NULL DEFAULT '0' COMMENT '微信二维码有效时间',
  `is_used` varchar(4) DEFAULT '0' COMMENT '是否使用，1：在使用，0：未使用',
  PRIMARY KEY (`qiid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_qrcode_type
-- ----------------------------
DROP TABLE IF EXISTS `tb_qrcode_type`;
CREATE TABLE `tb_qrcode_type` (
  `qtid` int(11) NOT NULL,
  `qtname` varchar(500) DEFAULT NULL,
  `expanddesc` varchar(500) DEFAULT NULL,
  `isdonate` varchar(2) DEFAULT NULL,
  `irid` int(11) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`qtid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_qrcode_user_scan
-- ----------------------------
DROP TABLE IF EXISTS `tb_qrcode_user_scan`;
CREATE TABLE `tb_qrcode_user_scan` (
  `qusid` varchar(50) NOT NULL,
  `qiid` varchar(50) DEFAULT NULL,
  `irid` varchar(50) DEFAULT NULL,
  `userid` varchar(50) DEFAULT NULL,
  `scanintegral` int(11) DEFAULT NULL,
  `scantimes` int(11) DEFAULT NULL,
  `scantime` datetime DEFAULT NULL,
  PRIMARY KEY (`qusid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_recipients_coupon
-- ----------------------------
DROP TABLE IF EXISTS `tb_recipients_coupon`;
CREATE TABLE `tb_recipients_coupon` (
  `RCID` varchar(50) NOT NULL DEFAULT '0' COMMENT '领用优惠券ID',
  `UserID` varchar(50) NOT NULL COMMENT '用户ID',
  `PCNID` varchar(50) NOT NULL COMMENT '优惠券编号ID',
  `UseTime` datetime(6) DEFAULT NULL COMMENT '消费使用时间',
  `Status` varchar(10) NOT NULL DEFAULT '1' COMMENT '状态',
  PRIMARY KEY (`RCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_return_address_information
-- ----------------------------
DROP TABLE IF EXISTS `tb_return_address_information`;
CREATE TABLE `tb_return_address_information` (
  `RAID` varchar(50) NOT NULL COMMENT '退货地址ID',
  `BIID` varchar(50) NOT NULL COMMENT '商户信息ID',
  `AreaID` varchar(50) NOT NULL COMMENT '地区编码',
  `Adress` varchar(100) NOT NULL COMMENT '详细地址',
  `Mphone` varchar(15) NOT NULL COMMENT '联系手机',
  `ContactName` varchar(20) NOT NULL COMMENT '联系人姓名',
  PRIMARY KEY (`RAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_return_standard_reason
-- ----------------------------
DROP TABLE IF EXISTS `tb_return_standard_reason`;
CREATE TABLE `tb_return_standard_reason` (
  `RSRID` varchar(50) NOT NULL,
  `RSRName` varchar(20) NOT NULL,
  PRIMARY KEY (`RSRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_rolefunction_authority
-- ----------------------------
DROP TABLE IF EXISTS `tb_rolefunction_authority`;
CREATE TABLE `tb_rolefunction_authority` (
  `RFAID` varchar(50) NOT NULL COMMENT '角色功能权限ID',
  `RTID` varchar(50) NOT NULL COMMENT '角色类型ID',
  `FunID` varchar(50) NOT NULL COMMENT '功能ID',
  `AuthorityMark` varchar(50) NOT NULL DEFAULT '1' COMMENT '权限标识',
  PRIMARY KEY (`RFAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_role_types
-- ----------------------------
DROP TABLE IF EXISTS `tb_role_types`;
CREATE TABLE `tb_role_types` (
  `RTID` varchar(50) NOT NULL COMMENT '角色类型ID',
  `RTName` varchar(50) NOT NULL COMMENT '角色类型名称',
  PRIMARY KEY (`RTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_settled_airlines
-- ----------------------------
DROP TABLE IF EXISTS `tb_settled_airlines`;
CREATE TABLE `tb_settled_airlines` (
  `SAID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `AID` varchar(50) NOT NULL,
  PRIMARY KEY (`SAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_shipping_policy
-- ----------------------------
DROP TABLE IF EXISTS `tb_shipping_policy`;
CREATE TABLE `tb_shipping_policy` (
  `SPID` varchar(50) NOT NULL COMMENT '优惠策略ID',
  `SPName` varchar(50) NOT NULL COMMENT '优惠策略名称',
  PRIMARY KEY (`SPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_shopping_cart_goods
-- ----------------------------
DROP TABLE IF EXISTS `tb_shopping_cart_goods`;
CREATE TABLE `tb_shopping_cart_goods` (
  `SCGID` varchar(50) NOT NULL COMMENT '购物车商品ID',
  `GSKUID` varchar(50) NOT NULL COMMENT '商品SKUID',
  `Quantity` int(50) NOT NULL DEFAULT '1' COMMENT '数量',
  `delivery_method_type` varchar(8) DEFAULT '4' COMMENT '商品配送方式  1:物流到家  ； 3：门店自提    ；  4：物流到家和门店自提',
  `AddTime` datetime NOT NULL COMMENT '加入购车时间',
  `BIID` varchar(50) NOT NULL COMMENT '商户信息ID',
  `UserID` varchar(50) NOT NULL COMMENT '用户ID',
  `TransferOrder` datetime DEFAULT NULL COMMENT '转订单时间',
  `Status` char(1) NOT NULL DEFAULT '1' COMMENT '状态',
  PRIMARY KEY (`SCGID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_shops_page_banner
-- ----------------------------
DROP TABLE IF EXISTS `tb_shops_page_banner`;
CREATE TABLE `tb_shops_page_banner` (
  `SPBID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `Picture` varchar(100) NOT NULL,
  `APnum` varchar(8) DEFAULT '0',
  PRIMARY KEY (`SPBID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_shops_page_display_business
-- ----------------------------
DROP TABLE IF EXISTS `tb_shops_page_display_business`;
CREATE TABLE `tb_shops_page_display_business` (
  `SPDBID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `APnum` varchar(8) DEFAULT '0',
  PRIMARY KEY (`SPDBID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_shops_page_display_coupons_commodities
-- ----------------------------
DROP TABLE IF EXISTS `tb_shops_page_display_coupons_commodities`;
CREATE TABLE `tb_shops_page_display_coupons_commodities` (
  `SPDCCID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `APnum` varchar(8) DEFAULT '0',
  `StoreType` char(1) DEFAULT '0',
  PRIMARY KEY (`SPDCCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_shops_page_display_physical_commodities
-- ----------------------------
DROP TABLE IF EXISTS `tb_shops_page_display_physical_commodities`;
CREATE TABLE `tb_shops_page_display_physical_commodities` (
  `SPDPCID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `APnum` int(11) DEFAULT '0',
  `StoreType` char(1) DEFAULT '0',
  PRIMARY KEY (`SPDPCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_sku_stock_change_reasons
-- ----------------------------
DROP TABLE IF EXISTS `tb_sku_stock_change_reasons`;
CREATE TABLE `tb_sku_stock_change_reasons` (
  `SKUSCRID` int(2) NOT NULL AUTO_INCREMENT COMMENT '商品SKU库存变动原因ID',
  `Reasons` varchar(50) NOT NULL COMMENT 'SKU库存变动原因',
  PRIMARY KEY (`SKUSCRID`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_specical_subject_classify
-- ----------------------------
DROP TABLE IF EXISTS `tb_specical_subject_classify`;
CREATE TABLE `tb_specical_subject_classify` (
  `ssccid` varchar(100) NOT NULL,
  `sfpid` varchar(50) DEFAULT NULL,
  `ssptitle` varchar(100) DEFAULT NULL,
  `sscimage` varchar(200) DEFAULT NULL,
  `sort` int(3) DEFAULT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`ssccid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_standard_goods_specification
-- ----------------------------
DROP TABLE IF EXISTS `tb_standard_goods_specification`;
CREATE TABLE `tb_standard_goods_specification` (
  `SGSID` varchar(50) NOT NULL COMMENT '标准商品规格ID',
  `GSID` varchar(50) NOT NULL COMMENT '商品子类ID',
  `SGSName` varchar(30) NOT NULL COMMENT '标准商品规格名称',
  PRIMARY KEY (`SGSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_standard_goods_specification_options
-- ----------------------------
DROP TABLE IF EXISTS `tb_standard_goods_specification_options`;
CREATE TABLE `tb_standard_goods_specification_options` (
  `SGSOID` varchar(50) NOT NULL COMMENT '标准商品规格选项ID',
  `SGSID` varchar(50) NOT NULL COMMENT '标准商品规格ID',
  `GSOptions` varchar(50) NOT NULL COMMENT '标准商品规格选项名称',
  `gsoptions_desc` varchar(100) NOT NULL DEFAULT '' COMMENT '描述，老字段',
  PRIMARY KEY (`SGSOID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_standard_management_fee
-- ----------------------------
DROP TABLE IF EXISTS `tb_standard_management_fee`;
CREATE TABLE `tb_standard_management_fee` (
  `SMFID` varchar(50) NOT NULL,
  `Priod` varchar(50) NOT NULL,
  `FixedPayDate` varchar(50) NOT NULL DEFAULT '8',
  `MFee` decimal(10,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`SMFID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_store_fixed_program
-- ----------------------------
DROP TABLE IF EXISTS `tb_store_fixed_program`;
CREATE TABLE `tb_store_fixed_program` (
  `sfpid` varchar(50) NOT NULL,
  `aiid` varchar(100) NOT NULL,
  `sfptitle` varchar(200) DEFAULT NULL,
  `sfpimage` varchar(200) DEFAULT NULL,
  `recommend_url` varchar(255) DEFAULT NULL COMMENT '推荐url',
  `inner_pic` varchar(255) DEFAULT NULL COMMENT '内图',
  `sort` int(3) DEFAULT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`sfpid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_store_page_banner
-- ----------------------------
DROP TABLE IF EXISTS `tb_store_page_banner`;
CREATE TABLE `tb_store_page_banner` (
  `SPBID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `Picture` varchar(100) NOT NULL,
  `APnum` varchar(8) DEFAULT '0',
  `skip_type` varchar(50) NOT NULL DEFAULT '' COMMENT 'banner跳转类型',
  `skip_type_id` varchar(255) NOT NULL DEFAULT '' COMMENT 'banner跳转类型内容id',
  `link_uri` varchar(150) NOT NULL DEFAULT '' COMMENT '链接地址',
  `is_display` varchar(10) NOT NULL DEFAULT '98989804' COMMENT '是否展示：1：显示，0：不显示',
  `banner_information` varchar(50) NOT NULL DEFAULT '' COMMENT 'banner基本信息',
  `banner_description` varchar(100) NOT NULL DEFAULT '' COMMENT 'banner描述',
  `banner_thumb` varchar(100) NOT NULL DEFAULT '' COMMENT 'banner缩略图',
  `is_delete` varchar(10) NOT NULL DEFAULT '98989802' COMMENT '是否删除',
  PRIMARY KEY (`SPBID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_store_page_display_coupons_commodities
-- ----------------------------
DROP TABLE IF EXISTS `tb_store_page_display_coupons_commodities`;
CREATE TABLE `tb_store_page_display_coupons_commodities` (
  `SPDCCID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `APnum` int(8) DEFAULT '0',
  `StoreType` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`SPDCCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_store_page_display_physical_commodities
-- ----------------------------
DROP TABLE IF EXISTS `tb_store_page_display_physical_commodities`;
CREATE TABLE `tb_store_page_display_physical_commodities` (
  `SPDPCID` varchar(50) NOT NULL,
  `BIID` varchar(50) NOT NULL,
  `GIID` varchar(50) NOT NULL,
  `APnum` int(11) DEFAULT '0',
  `StoreType` varchar(10) DEFAULT '0' COMMENT '0-上新，1-促销，2-普通',
  PRIMARY KEY (`SPDPCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_store_spread_program
-- ----------------------------
DROP TABLE IF EXISTS `tb_store_spread_program`;
CREATE TABLE `tb_store_spread_program` (
  `sspid` varchar(200) NOT NULL,
  `aiid` varchar(100) NOT NULL,
  `ssptitle` varchar(100) DEFAULT NULL,
  `sspimage` varchar(200) DEFAULT NULL,
  `sspdescribe` varchar(200) DEFAULT NULL,
  `sspsort` int(3) DEFAULT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`sspid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_subject_good
-- ----------------------------
DROP TABLE IF EXISTS `tb_subject_good`;
CREATE TABLE `tb_subject_good` (
  `sgid` varchar(100) NOT NULL,
  `aiid` varchar(100) DEFAULT NULL,
  `giid` varchar(100) DEFAULT NULL,
  `ssccid` varchar(100) DEFAULT NULL,
  `sgimage` varchar(200) DEFAULT NULL,
  `sort` int(3) DEFAULT NULL,
  `expanddesc` varchar(200) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`sgid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_system_operation_log
-- ----------------------------
DROP TABLE IF EXISTS `tb_system_operation_log`;
CREATE TABLE `tb_system_operation_log` (
  `SOLID` varchar(50) NOT NULL,
  `FunID` varchar(50) NOT NULL,
  `PUserID` varchar(50) NOT NULL,
  `OperatingTime` datetime NOT NULL,
  PRIMARY KEY (`SOLID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_sys_business_group_info
-- ----------------------------
DROP TABLE IF EXISTS `tb_sys_business_group_info`;
CREATE TABLE `tb_sys_business_group_info` (
  `group_id` varchar(50) NOT NULL DEFAULT '' COMMENT '商户群组标识',
  `group_name` varchar(50) NOT NULL DEFAULT '' COMMENT '商户群组名称',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户群组信息';

-- ----------------------------
-- Table structure for tb_sys_business_store_relate_goup_map
-- ----------------------------
DROP TABLE IF EXISTS `tb_sys_business_store_relate_goup_map`;
CREATE TABLE `tb_sys_business_store_relate_goup_map` (
  `BSRGM_ID` varchar(50) NOT NULL DEFAULT '' COMMENT '关联标识',
  `BIID` varchar(50) NOT NULL DEFAULT '' COMMENT '商户门店标识',
  `group_id` varchar(50) NOT NULL DEFAULT '' COMMENT '商户群组标识',
  PRIMARY KEY (`BSRGM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户门店与群组关联';

-- ----------------------------
-- Table structure for tb_sys_business_user_info
-- ----------------------------
DROP TABLE IF EXISTS `tb_sys_business_user_info`;
CREATE TABLE `tb_sys_business_user_info` (
  `user_code` varchar(50) NOT NULL DEFAULT '' COMMENT '商户会员标识',
  `user_name` varchar(50) NOT NULL DEFAULT '' COMMENT '会员名称',
  `user_number` varchar(50) NOT NULL DEFAULT '' COMMENT '会员编号',
  `user_post` varchar(50) NOT NULL DEFAULT '' COMMENT '会员职位',
  `user_pwd` varchar(100) NOT NULL DEFAULT '' COMMENT '会员密码',
  `user_sex` varchar(10) NOT NULL DEFAULT '' COMMENT '会员性别',
  `user_mail` varchar(50) NOT NULL DEFAULT '' COMMENT '会员邮箱',
  `user_telphone` varchar(20) NOT NULL DEFAULT '' COMMENT '会员电话',
  `user_mobile` varchar(20) NOT NULL DEFAULT '' COMMENT '会员手机号码',
  `user_sys_pwd` varchar(20) NOT NULL DEFAULT '' COMMENT '会员系统密码',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户用户信息';

-- ----------------------------
-- Table structure for tb_sys_business_user_relate_group_map
-- ----------------------------
DROP TABLE IF EXISTS `tb_sys_business_user_relate_group_map`;
CREATE TABLE `tb_sys_business_user_relate_group_map` (
  `BURGM_ID` varchar(50) NOT NULL DEFAULT '' COMMENT '关联标识',
  `user_code` varchar(50) NOT NULL DEFAULT '' COMMENT '商户会员标识',
  `group_id` varchar(50) NOT NULL DEFAULT '' COMMENT '商户群组标识',
  PRIMARY KEY (`BURGM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户用户与群组关联';

-- ----------------------------
-- Table structure for tb_task
-- ----------------------------
DROP TABLE IF EXISTS `tb_task`;
CREATE TABLE `tb_task` (
  `taskid` varchar(50) DEFAULT NULL,
  `taskname` varchar(255) DEFAULT NULL,
  `taskday` int(11) DEFAULT NULL,
  `remark` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_timelyfights
-- ----------------------------
DROP TABLE IF EXISTS `tb_timelyfights`;
CREATE TABLE `tb_timelyfights` (
  `FIID` varchar(50) NOT NULL,
  `FlightNo` varchar(50) NOT NULL,
  `FlightCompany` varchar(50) NOT NULL,
  `FlightDepcode` varchar(50) NOT NULL,
  `FlightArrcode` varchar(50) NOT NULL,
  `FlightDeptimePlanDate` datetime NOT NULL,
  `FlightArrtimePlanDate` datetime NOT NULL,
  `FlightDeptimeReadyDate` datetime NOT NULL,
  `FlightArrtimeReadyDate` datetime NOT NULL,
  `FlightDeptimeDate` datetime NOT NULL,
  `FlightArrtimeDate` datetime NOT NULL,
  `FlightIngateTime` datetime NOT NULL,
  `FlightOutgateTime` datetime NOT NULL,
  `stopFlag` char(1) NOT NULL,
  `shareFlag` char(1) NOT NULL,
  `LegFlag` char(1) NOT NULL,
  `ShareFlightNo` int(8) NOT NULL,
  `BoardGate` varchar(50) NOT NULL,
  `BaggageID` varchar(50) NOT NULL,
  `FlightState` char(1) NOT NULL,
  `FlightHTerminal` varchar(50) NOT NULL,
  `FlightTerminal` varchar(50) NOT NULL,
  `FlightDep` varchar(50) NOT NULL,
  `FlightArr` varchar(50) NOT NULL,
  `FlightDepAirport` varchar(50) NOT NULL,
  `FlightArrAirport` varchar(50) NOT NULL,
  `org_timezone` varchar(50) NOT NULL,
  `dst_timezone` varchar(50) NOT NULL,
  `fcategory` char(1) NOT NULL,
  `fid` varchar(50) NOT NULL,
  `DepWeather` varchar(200) NOT NULL,
  `ArrWeather` varchar(200) NOT NULL,
  PRIMARY KEY (`FIID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_today_classify
-- ----------------------------
DROP TABLE IF EXISTS `tb_today_classify`;
CREATE TABLE `tb_today_classify` (
  `classifyid` varchar(50) NOT NULL DEFAULT '',
  `aiid` varchar(50) DEFAULT NULL,
  `classifyname` varchar(50) DEFAULT NULL,
  `expanddesc` varchar(200) DEFAULT '',
  `sort` int(11) DEFAULT '0',
  `createtime` datetime(6) DEFAULT NULL,
  `lastmodifiedtime` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`classifyid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_today_classify_coupon_goods
-- ----------------------------
DROP TABLE IF EXISTS `tb_today_classify_coupon_goods`;
CREATE TABLE `tb_today_classify_coupon_goods` (
  `tccgid` varchar(50) NOT NULL,
  `classifyid` varchar(50) DEFAULT NULL,
  `biid` varchar(50) DEFAULT NULL,
  `gskuid` varchar(50) DEFAULT NULL,
  `couponinfo` varchar(200) DEFAULT NULL,
  `sort` int(11) DEFAULT NULL,
  `tccgimage` varchar(500) DEFAULT NULL,
  `createtime` datetime(6) DEFAULT NULL,
  `lastmodifiedtime` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`tccgid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_traffic_near_airport
-- ----------------------------
DROP TABLE IF EXISTS `tb_traffic_near_airport`;
CREATE TABLE `tb_traffic_near_airport` (
  `TNAID` varchar(50) NOT NULL,
  `AIID` varchar(50) NOT NULL,
  `LineName` varchar(50) NOT NULL,
  `LineNo` varchar(50) NOT NULL,
  `Traffic` varchar(50) NOT NULL DEFAULT '1',
  `MapPhotos` varchar(100) NOT NULL,
  PRIMARY KEY (`TNAID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_usertbl
-- ----------------------------
DROP TABLE IF EXISTS `tb_usertbl`;
CREATE TABLE `tb_usertbl` (
  `UserId` varchar(50) NOT NULL DEFAULT '' COMMENT '用户ID',
  `HeadPortrait` varchar(500) DEFAULT '/ptcent_file_upload/headFiles/grl.png' COMMENT '用户头像',
  `Nickname` varchar(200) CHARACTER SET utf8mb4 DEFAULT '' COMMENT '昵称',
  `MobilePhoneNo` varchar(20) DEFAULT '' COMMENT '手机号(登录号)',
  `loginPassword` varchar(200) DEFAULT NULL COMMENT '登录密码',
  `DocNum` varchar(30) DEFAULT '' COMMENT '证件号码',
  `DocType` char(1) DEFAULT '1' COMMENT '证件类别',
  `PlateNum` varchar(15) DEFAULT NULL COMMENT '车牌号',
  `MemberMark` char(1) DEFAULT '0' COMMENT '会员标识',
  `MLID` int(2) DEFAULT '1' COMMENT '会员等级ID',
  `FullName` varchar(200) CHARACTER SET utf8mb4 DEFAULT '' COMMENT '姓名',
  `Sex` varchar(20) DEFAULT '0' COMMENT '性别1:男，2：女，0：未知，',
  `Age` int(3) DEFAULT NULL COMMENT '年龄',
  `CashAccount` decimal(12,2) DEFAULT '0.00' COMMENT '资金账户',
  `LockCashAccount` decimal(10,2) DEFAULT '0.00' COMMENT '锁定资金账户',
  `PointsBaLance` int(12) DEFAULT '0' COMMENT '积分账户',
  `CurFlights` varchar(50) DEFAULT NULL COMMENT '选择当前航班',
  `DAID` varchar(50) DEFAULT NULL COMMENT '缺省送货地址',
  `IIID` varchar(50) DEFAULT NULL COMMENT '缺省发票ID',
  `QRCode` varchar(255) DEFAULT NULL COMMENT '用户二维码',
  `ClearCache` char(1) DEFAULT '0' COMMENT '清除缓存',
  `AutoUpdate` char(1) DEFAULT '1' COMMENT 'Wifi环境下自动升级客户端',
  `Uid` int(20) DEFAULT NULL,
  `WeixinId` varchar(50) DEFAULT NULL,
  `LoginType` varchar(2) DEFAULT '0' COMMENT '登录类型 0:app 1:微信公众号授权登录 2:app微信登录',
  `RegisterType` varchar(2) DEFAULT '0' COMMENT '登录类型 0:app 1:微信公众号授权登录 2:app微信登录',
  `OpenId` varchar(50) DEFAULT NULL,
  `openId_app` varchar(50) DEFAULT '' COMMENT 'app应用的openId',
  `UnionId` varchar(50) DEFAULT NULL,
  `RegisterTime` datetime DEFAULT CURRENT_TIMESTAMP,
  `LoginTime` datetime DEFAULT CURRENT_TIMESTAMP,
  `email` varchar(100) DEFAULT '' COMMENT '邮箱',
  `user_status` varchar(4) DEFAULT NULL COMMENT '用户状态，0：正常，1：删除，2：合并过的账户',
  PRIMARY KEY (`UserId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_user_access_service
-- ----------------------------
DROP TABLE IF EXISTS `tb_user_access_service`;
CREATE TABLE `tb_user_access_service` (
  `UASID` varchar(50) NOT NULL,
  `AccessTime` datetime NOT NULL,
  `UserID` varchar(50) NOT NULL,
  `PUserID` varchar(50) DEFAULT NULL,
  `ReceptionTime` datetime DEFAULT NULL,
  `ServiceEndTime` datetime DEFAULT NULL,
  `Status` varchar(50) NOT NULL,
  PRIMARY KEY (`UASID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_user_account_change_reason
-- ----------------------------
DROP TABLE IF EXISTS `tb_user_account_change_reason`;
CREATE TABLE `tb_user_account_change_reason` (
  `UACRID` int(2) NOT NULL AUTO_INCREMENT COMMENT '用户资金账户变动原因ID',
  `UACReason` varchar(50) NOT NULL COMMENT '用户资金账户变动原因',
  PRIMARY KEY (`UACRID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_user_account_change_record
-- ----------------------------
DROP TABLE IF EXISTS `tb_user_account_change_record`;
CREATE TABLE `tb_user_account_change_record` (
  `UACRID` varchar(50) NOT NULL COMMENT '用户资金账户变动记录ID',
  `CashAccountType` varchar(50) NOT NULL COMMENT '资金账户类型',
  `Direction` varchar(50) NOT NULL COMMENT '变动方向',
  `ChangeAmount` decimal(12,2) NOT NULL COMMENT '变动金额',
  `UACRIDT` varchar(50) NOT NULL COMMENT '用户资金账户变动原因ID',
  `AccountTypes` varchar(10) NOT NULL COMMENT '对方类型',
  `OtherID` varchar(50) NOT NULL COMMENT '对方账户',
  `OtherCAT` varchar(10) NOT NULL COMMENT '对方资金账户类型',
  `ChangeTime` datetime(6) NOT NULL COMMENT '变动时间',
  PRIMARY KEY (`UACRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_user_service_communication
-- ----------------------------
DROP TABLE IF EXISTS `tb_user_service_communication`;
CREATE TABLE `tb_user_service_communication` (
  `USCID` varchar(50) NOT NULL,
  `UASID` varchar(50) NOT NULL,
  `SendMsgType` varchar(50) NOT NULL,
  `TextOrPath` varchar(500) NOT NULL,
  `SendTime` datetime NOT NULL,
  `ComplianceStatus` varchar(10) NOT NULL DEFAULT '0',
  `IICID` varchar(15) NOT NULL,
  `SenderID` varchar(50) NOT NULL,
  `SenderType` varchar(5) NOT NULL,
  PRIMARY KEY (`USCID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_user_statistics
-- ----------------------------
DROP TABLE IF EXISTS `tb_user_statistics`;
CREATE TABLE `tb_user_statistics` (
  `userid` varchar(50) NOT NULL,
  `totalfee` decimal(10,2) DEFAULT '0.00' COMMENT '消费总数',
  `totalscan` int(11) DEFAULT '0' COMMENT '扫码总数',
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
  `total_signin` int(11) DEFAULT '0',
  `total_keep_signin` int(11) DEFAULT '0',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`userid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for tb_verification_code
-- ----------------------------
DROP TABLE IF EXISTS `tb_verification_code`;
CREATE TABLE `tb_verification_code` (
  `VID` varchar(50) NOT NULL,
  `VNumber` varchar(10) DEFAULT NULL,
  `VTime` datetime(6) DEFAULT NULL,
  `VPhoneNumber` varchar(11) DEFAULT NULL,
  PRIMARY KEY (`VID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_vip_enjoy_detail
-- ----------------------------
DROP TABLE IF EXISTS `tb_vip_enjoy_detail`;
CREATE TABLE `tb_vip_enjoy_detail` (
  `vedid` varchar(50) NOT NULL,
  `aiid` varchar(50) DEFAULT NULL,
  `vipcabin` longtext,
  `vipservice` longtext,
  `vipcard` longtext,
  `createtime` datetime DEFAULT NULL,
  `lastmodifiedtime` datetime DEFAULT NULL,
  PRIMARY KEY (`vedid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_whisper_detail
-- ----------------------------
DROP TABLE IF EXISTS `tb_whisper_detail`;
CREATE TABLE `tb_whisper_detail` (
  `WBID` varchar(50) NOT NULL,
  `WRID` varchar(50) NOT NULL,
  `BubbleContentType` varchar(50) NOT NULL,
  `BubbleText` varchar(500) DEFAULT NULL,
  `UserID` varchar(50) NOT NULL,
  `SendTime` datetime NOT NULL,
  PRIMARY KEY (`WBID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_whisper_relations
-- ----------------------------
DROP TABLE IF EXISTS `tb_whisper_relations`;
CREATE TABLE `tb_whisper_relations` (
  `WRID` varchar(50) NOT NULL,
  `User1ID` varchar(50) NOT NULL,
  `User2ID` varchar(50) NOT NULL,
  PRIMARY KEY (`WRID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_wx_sys_param
-- ----------------------------
DROP TABLE IF EXISTS `tb_wx_sys_param`;
CREATE TABLE `tb_wx_sys_param` (
  `sys_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sys_code` varchar(50) DEFAULT NULL,
  `sys_name` varchar(200) DEFAULT NULL,
  `sys_value` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`sys_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tb_wx_userinfo
-- ----------------------------
DROP TABLE IF EXISTS `tb_wx_userinfo`;
CREATE TABLE `tb_wx_userinfo` (
  `wxrandomId` varchar(50) DEFAULT NULL,
  `openId` varchar(50) DEFAULT NULL,
  `unionId` varchar(100) DEFAULT NULL,
  `nickname` varchar(50) CHARACTER SET utf8mb4 DEFAULT NULL,
  `sex` varchar(2) CHARACTER SET utf8mb4 DEFAULT '1',
  `country` varchar(50) CHARACTER SET utf8mb4 DEFAULT '',
  `province` varchar(50) CHARACTER SET utf8mb4 DEFAULT '',
  `city` varchar(50) CHARACTER SET utf8mb4 DEFAULT '',
  `headImgUrl` varchar(500) CHARACTER SET utf8mb4 DEFAULT '',
  `accessToken` varchar(500) DEFAULT NULL,
  `refreshToken` varchar(500) DEFAULT NULL,
  `privilegeList` varchar(500) DEFAULT NULL,
  `scope` varchar(500) DEFAULT NULL,
  `openIdType` varchar(4) DEFAULT '' COMMENT 'openId类型，1：公众号，2：app',
  `createdate` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for token
-- ----------------------------
DROP TABLE IF EXISTS `token`;
CREATE TABLE `token` (
  `userId` varchar(50) NOT NULL,
  `access_token` varchar(50) DEFAULT NULL,
  `expire` bigint(20) DEFAULT NULL,
  `ip` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_app_version
-- ----------------------------
DROP TABLE IF EXISTS `tsys_app_version`;
CREATE TABLE `tsys_app_version` (
  `version` varchar(50) NOT NULL DEFAULT '',
  `release_date` datetime DEFAULT NULL COMMENT '发布时间',
  `update_info` varchar(500) DEFAULT NULL COMMENT '更新内容',
  `file_size` varchar(50) DEFAULT NULL COMMENT '大小',
  `type` varchar(2) NOT NULL COMMENT '1：安卓，2：ios',
  `need` varchar(2) DEFAULT NULL COMMENT '0：否，1：是',
  `app_platform` varchar(2) DEFAULT NULL COMMENT 'app类型--1:用户端，2： 商家端',
  `download_url` varchar(200) DEFAULT NULL COMMENT '下载地址',
  `open` varchar(2) DEFAULT '0' COMMENT '开启状态，0：不开启，1：开启',
  `version_code` varchar(10) NOT NULL DEFAULT '' COMMENT '版本序号',
  `app_name` varchar(200) NOT NULL DEFAULT '' COMMENT '包名'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_department
-- ----------------------------
DROP TABLE IF EXISTS `tsys_department`;
CREATE TABLE `tsys_department` (
  `department_code` varchar(50) NOT NULL,
  `department_name` varchar(50) DEFAULT NULL,
  `department_parentcode` varchar(50) DEFAULT NULL,
  `department_fullpath` varchar(500) DEFAULT NULL,
  `department_islast` int(11) DEFAULT NULL,
  `department_sort` int(11) DEFAULT NULL,
  PRIMARY KEY (`department_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_integral
-- ----------------------------
DROP TABLE IF EXISTS `tsys_integral`;
CREATE TABLE `tsys_integral` (
  `id` varchar(50) DEFAULT NULL,
  `userid` varchar(50) DEFAULT NULL,
  `integral` int(11) DEFAULT NULL,
  `createdate` datetime DEFAULT NULL,
  `description` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_interface
-- ----------------------------
DROP TABLE IF EXISTS `tsys_interface`;
CREATE TABLE `tsys_interface` (
  `id` varchar(50) NOT NULL,
  `title` varchar(500) DEFAULT NULL,
  `describle` varchar(2000) DEFAULT NULL,
  `posturl` text,
  `moduleid` varchar(50) DEFAULT NULL,
  `createdate` datetime DEFAULT NULL,
  `sqlserviceid` varchar(50) DEFAULT NULL,
  `sqlcode` varchar(200) DEFAULT NULL,
  `flag` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_log
-- ----------------------------
DROP TABLE IF EXISTS `tsys_log`;
CREATE TABLE `tsys_log` (
  `id` varchar(50) NOT NULL,
  `method` varchar(50) DEFAULT NULL,
  `userid` varchar(50) DEFAULT NULL,
  `createdate` datetime DEFAULT NULL,
  `describle` text,
  `sqlcode` varchar(500) DEFAULT NULL,
  `errormsg` text,
  `requesturl` varchar(500) DEFAULT NULL,
  `logtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_menu
-- ----------------------------
DROP TABLE IF EXISTS `tsys_menu`;
CREATE TABLE `tsys_menu` (
  `menu_code` varchar(200) NOT NULL,
  `menu_name` varchar(200) DEFAULT NULL,
  `menu_displayname` varchar(200) DEFAULT NULL,
  `menu_fullpath` varchar(200) DEFAULT NULL,
  `menu_parentcode` varchar(200) DEFAULT NULL,
  `menu_rightFrame` varchar(200) DEFAULT NULL,
  `menu_islast` int(11) DEFAULT NULL,
  `menu_sort` int(11) NOT NULL,
  `menu_prower_code` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`menu_code`),
  KEY `parentcode` (`menu_parentcode`) USING HASH
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_module
-- ----------------------------
DROP TABLE IF EXISTS `tsys_module`;
CREATE TABLE `tsys_module` (
  `id` varchar(50) NOT NULL,
  `title` varchar(200) DEFAULT NULL,
  `describle` varchar(200) DEFAULT NULL,
  `createdate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_parameter
-- ----------------------------
DROP TABLE IF EXISTS `tsys_parameter`;
CREATE TABLE `tsys_parameter` (
  `id` varchar(50) NOT NULL,
  `title` varchar(500) DEFAULT NULL,
  `code` varchar(50) NOT NULL,
  `value` varchar(500) DEFAULT NULL,
  `lastmodifieddate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_power
-- ----------------------------
DROP TABLE IF EXISTS `tsys_power`;
CREATE TABLE `tsys_power` (
  `power_code` varchar(200) NOT NULL,
  `power_name` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`power_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_role
-- ----------------------------
DROP TABLE IF EXISTS `tsys_role`;
CREATE TABLE `tsys_role` (
  `role_code` varchar(200) NOT NULL,
  `role_name` varchar(200) NOT NULL,
  PRIMARY KEY (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_rolepower
-- ----------------------------
DROP TABLE IF EXISTS `tsys_rolepower`;
CREATE TABLE `tsys_rolepower` (
  `role_code` varchar(200) NOT NULL,
  `power_code` varchar(200) NOT NULL,
  PRIMARY KEY (`role_code`,`power_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_sqldetail
-- ----------------------------
DROP TABLE IF EXISTS `tsys_sqldetail`;
CREATE TABLE `tsys_sqldetail` (
  `id` varchar(50) NOT NULL,
  `sqltextid` varchar(50) DEFAULT NULL,
  `sqltext` text,
  `createdate` datetime DEFAULT NULL,
  `sqlresultcode` varchar(50) DEFAULT NULL,
  `ispage` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_sqlparam
-- ----------------------------
DROP TABLE IF EXISTS `tsys_sqlparam`;
CREATE TABLE `tsys_sqlparam` (
  `id` varchar(50) NOT NULL,
  `title` varchar(500) DEFAULT NULL,
  `value` varchar(500) DEFAULT NULL,
  `sqltextid` varchar(50) DEFAULT NULL,
  `sqldetailid` varchar(50) DEFAULT NULL,
  `param` varchar(500) DEFAULT NULL,
  `createruserid` varchar(50) DEFAULT NULL,
  `createdate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_sqlservice
-- ----------------------------
DROP TABLE IF EXISTS `tsys_sqlservice`;
CREATE TABLE `tsys_sqlservice` (
  `id` varchar(50) NOT NULL,
  `title` varchar(500) DEFAULT NULL,
  `sqltext` varchar(2000) DEFAULT NULL,
  `describle` varchar(500) DEFAULT NULL,
  `sqltype` varchar(50) DEFAULT NULL,
  `moduleid` varchar(50) DEFAULT NULL,
  `sqlcode` varchar(200) DEFAULT NULL,
  `createruserid` varchar(50) DEFAULT NULL,
  `updateuserid` varchar(50) DEFAULT NULL,
  `createdate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sqlcode` (`sqlcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_staff
-- ----------------------------
DROP TABLE IF EXISTS `tsys_staff`;
CREATE TABLE `tsys_staff` (
  `staff_code` varchar(50) NOT NULL,
  `staff_name` varchar(50) DEFAULT NULL,
  `staff_number` varchar(50) DEFAULT NULL,
  `staff_post` varchar(50) DEFAULT NULL,
  `staff_pwd` varchar(100) DEFAULT NULL,
  `staff_sex` varchar(11) DEFAULT NULL,
  `staff_mail` varchar(50) DEFAULT NULL,
  `staff_sort` varchar(11) DEFAULT NULL,
  `department_code` varchar(50) DEFAULT NULL,
  `staff_telphone` varchar(50) DEFAULT NULL,
  `staff_mobile` varchar(50) DEFAULT NULL,
  `staff_id` varchar(50) DEFAULT NULL,
  `staff_menu_data` text,
  `AIID` varchar(50) DEFAULT NULL,
  `tsyspwd` varchar(100) DEFAULT NULL,
  `isregister` varchar(5) DEFAULT '0',
  `register_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `login_time` datetime DEFAULT NULL,
  PRIMARY KEY (`staff_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_staffrole
-- ----------------------------
DROP TABLE IF EXISTS `tsys_staffrole`;
CREATE TABLE `tsys_staffrole` (
  `staff_code` varchar(50) NOT NULL DEFAULT '',
  `role_code` varchar(200) NOT NULL DEFAULT '',
  PRIMARY KEY (`staff_code`,`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tsys_user
-- ----------------------------
DROP TABLE IF EXISTS `tsys_user`;
CREATE TABLE `tsys_user` (
  `id` varchar(50) NOT NULL DEFAULT '',
  `username` varchar(50) DEFAULT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  `realname` varchar(50) DEFAULT NULL,
  `createdate` datetime DEFAULT NULL,
  `avatar` varchar(100) DEFAULT NULL,
  `sex` int(11) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `birthday` varchar(255) DEFAULT NULL,
  `mail` varchar(50) DEFAULT NULL,
  `ismarry` int(11) DEFAULT NULL,
  `integral` int(11) DEFAULT NULL,
  `fans` float DEFAULT NULL,
  `usertype` int(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `flag` int(11) DEFAULT NULL,
  `qq` varchar(50) DEFAULT NULL,
  `wechat` varchar(50) DEFAULT NULL,
  `microblog` varchar(50) DEFAULT NULL,
  `aplipay` varchar(50) DEFAULT NULL,
  `unionpay` varchar(50) DEFAULT NULL,
  `lastmodifieddate` datetime DEFAULT NULL,
  `lastlogindate` datetime DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for zite_weixin_active
-- ----------------------------
DROP TABLE IF EXISTS `zite_weixin_active`;
CREATE TABLE `zite_weixin_active` (
  `id` int(50) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `flag` varchar(50) DEFAULT NULL,
  `cardType` varchar(50) DEFAULT NULL,
  `visitant` varchar(50) DEFAULT NULL,
  `visitantType` varchar(50) DEFAULT NULL,
  `address` varchar(50) DEFAULT NULL,
  `number` varchar(50) DEFAULT NULL,
  `price` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for zite_weixin_count_page
-- ----------------------------
DROP TABLE IF EXISTS `zite_weixin_count_page`;
CREATE TABLE `zite_weixin_count_page` (
  `id` int(7) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `type` varchar(50) NOT NULL,
  `address` varchar(50) NOT NULL,
  `count` int(10) NOT NULL,
  `updateOfTime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;

-- ----------------------------
-- View structure for order_phy_return_goods_sub_view
-- ----------------------------
DROP VIEW IF EXISTS `order_phy_return_goods_sub_view`;
