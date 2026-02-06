from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 用户模型
class User(db.Model):
    __tablename__ = 'tbl_upms_user_info_dat'
    user_id = db.Column(db.BigInteger, primary_key=True)
    user_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    salt = db.Column(db.String(255))
    locked = db.Column(db.Integer)
    real_name = db.Column(db.String(255))
    nick_name = db.Column(db.String(255))
    head_portrait = db.Column(db.String(500))
    mobile = db.Column(db.String(255))
    email = db.Column(db.String(255))
    is_delete = db.Column(db.Integer)
    description = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    update_people = db.Column(db.String(255))

# 商品信息模型
class GoodsInformation(db.Model):
    __tablename__ = 'tb_goods_information'
    giid = db.Column(db.String(50), primary_key=True)  # 商品信息ID
    biid = db.Column(db.String(50))  # 商户信息ID
    gsid = db.Column(db.String(50))  # 商品类型ID
    ccid = db.Column(db.String(50))  # 自定义商品分类ID
    g_description = db.Column('GDescription', db.String(500))  # 商品描述
    g_introduction = db.Column('GIntroduction', db.Text)  # 商品介绍
    g_main_pic = db.Column('GMainPic', db.String(255))  # 商品主图
    card_pic = db.Column('CardPic', db.String(255))  # 卡片缩略图
    virtual_goods_mark = db.Column('VirtualGoodsMark', db.String(1))  # 是否虚拟商品
    g_start_date = db.Column('GStartDate', db.DateTime)  # 有效起始日
    g_end_date = db.Column('GEndDate', db.DateTime)  # 有效结束日
    g_qr_code = db.Column('GQRCode', db.String(255))  # 商品二维码
    unit = db.Column('Unit', db.String(10))  # 计量单位
    agents_mark = db.Column('AgentsMark', db.String(50))  # 可代理标识
    brands = db.Column('Brands', db.String(50))  # 品牌
    inevitably_post = db.Column('InevitablyPost', db.String(50))  # 不免邮标识
    added_mark = db.Column('AddedMark', db.String(50))  # 上架标识
    pr_status = db.Column('PRStatus', db.String(50))  # 商品审核状态
    applicable_dp = db.Column('ApplicableDP', db.String(50))  # 适用提货点
    premiums_mark = db.Column('PremiumsMark', db.String(50))  # 赠品标识
    goods_name = db.Column('GoodsName', db.String(500))  # 商品名称
    monthly_sales = db.Column('MonthlySales', db.Integer)  # 月销量
    time_on_shelves = db.Column('TimeOnShelves', db.DateTime)  # 上架时间
    single_piece_weight = db.Column('SinglePieceWeight', db.String(50))  # 单件重量
    retail_price = db.Column('RetailPrice', db.Numeric(precision=7, scale=2))  # 零售价格
    with_timestamps = db.Column('WithTimestamps', db.String(50))  # 预约时间
    with_way = db.Column('WithWay', db.String(200))  # 预约方式
    appointment_prompt = db.Column('AppointmentPrompt', db.String(100))  # 预约提示
    flag = db.Column('flag', db.String(2))  # 标志
    mark_price = db.Column('MarkPrice', db.Numeric(precision=10, scale=0))  # 市场价
    update_time = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now)
    update_people = db.Column('update_people', db.String(100))
    goods_slogan = db.Column('GoodsSlogan', db.String(50))  # 商品广告语

# 商品SKU模型
class GoodsSku(db.Model):
    __tablename__ = 'tb_goods_sku'
    gskuid = db.Column('GSKUID', db.String(50), primary_key=True)  # 商品SKUID
    specifications_id = db.Column('SpecificationsID', db.String(500))  # 规格ID
    giid = db.Column('GIID', db.String(50))  # 商品信息ID
    sku_pic = db.Column('SKUPic', db.String(255))  # SKU图片
    face_value = db.Column('FaceValue', db.Numeric(precision=18, scale=2))  # 面值
    market_price = db.Column('MarketPrice', db.Numeric(precision=18, scale=2))  # 市场价
    retail_price = db.Column('RetailPrice', db.Numeric(precision=18, scale=2))  # 零售原价
    agreement_price = db.Column('AgreementPrice', db.Numeric(precision=18, scale=2))  # 协议价
    initial_inventory = db.Column('InitialInventory', db.Integer)  # 初始库存量
    available_inventory = db.Column('AvailableInventory', db.Integer)  # 可用库存量
    on_way_inventory = db.Column('OnWayInventory', db.Integer)  # 在途库存量
    added_status = db.Column('AddedStatus', db.String(255))  # 上架状态
    qr_code = db.Column('QRCode', db.String(255))  # 二维码
    sku_description = db.Column('SKUDescription', db.String(255))  # SKU描述
    commission_rate = db.Column('CommissionRate', db.Numeric(precision=18, scale=2))  # 佣金比例
    agents_mark = db.Column('AgentsMark', db.String(10))  # 可代理标识
    premiums_mark = db.Column('PremiumsMark', db.String(10))  # 赠品标识
    barcode = db.Column('Barcode', db.String(50))  # 条形码
    barcode_desc = db.Column('BarcodeDesc', db.String(200))  # 条形码描述
    flag = db.Column('flag', db.String(2))  # 标志
    create_time = db.Column('CreateTime', db.DateTime, default=datetime.now)
    sku_name = db.Column('sku_name', db.String(100))  # SKU名称

# 商户信息模型
class BusinessInformation(db.Model):
    __tablename__ = 'tb_business_information'
    biid = db.Column('BIID', db.String(50), primary_key=True)  # 商户信息ID
    bi_logo = db.Column('BILogo', db.String(255))  # 商户Logo
    b_num = db.Column('BNum', db.String(20))  # 商户编号
    bi_name = db.Column('BIName', db.String(100))  # 商户名称
    login_password = db.Column('LoginPassword', db.String(50))  # 登录密码
    self_sign = db.Column('SelfSign', db.String(20))  # 平台自营标识
    attribution_type = db.Column('AttributionType', db.String(5))  # 归属类型
    as_type = db.Column('ASType', db.String(5))  # 机场服务类型
    position_range = db.Column('PositionRange', db.String(10))  # 位置范围
    adress = db.Column('Adress', db.String(100))  # 具体地址
    address_curt = db.Column('address_curt', db.String(100))  # 简短地址
    aiid = db.Column('AIID', db.String(50))  # 所属机场ID
    bcid = db.Column('BCID', db.String(50))  # 商户分类ID
    main_pic = db.Column('MainPic', db.String(255))  # 主图
    card_pic = db.Column('CardPic', db.String(255))  # 卡片缩略图
    introduction = db.Column('Introduction', db.Text)  # 介绍
    allow_more_pic = db.Column('AllowMorePic', db.String(10))  # 允许更多图片
    cash_account = db.Column('CashAccount', db.Numeric(precision=15, scale=2))  # 资金账户
    lock_cash_account = db.Column('LockCashAccount', db.Numeric(precision=15, scale=2))  # 锁定资金账户
    raid = db.Column('RAID', db.String(50))  # 缺省退货地址
    qr_code = db.Column('QRCode', db.String(255))  # 商户二维码
    shipping_fee = db.Column('ShippingFee', db.Numeric(precision=8, scale=2))  # 运费
    contact_num = db.Column('ContactNum', db.String(50))  # 联系电话
    f_contact_num = db.Column('FContactNum', db.String(15))  # 财务联系电话
    we_chat_no = db.Column('WeChatNo', db.String(40))  # 微信账号
    bank_acc_no = db.Column('BankAccNo', db.String(30))  # 银行账号
    alipay_no = db.Column('AlipayNo', db.String(40))  # 支付宝账号
    e_mail = db.Column('eMail', db.String(50))  # 邮箱
    businesslicense_pic = db.Column('BusinesslicensePic', db.String(100))  # 营业执照图片
    confirm_receipt_days = db.Column('ConfirmReceiptDays', db.Integer)  # 确认收货天数
    cash_raised_days = db.Column('CashRaisedDays', db.Integer)  # 商家结算提现天数
    smfid = db.Column('SMFID', db.Integer)  # 管理费标准ID
    remark = db.Column('Remark', db.String(500))  # 备注
    contract_status = db.Column('ContractStatus', db.String(2))  # 签约状态
    b_account_name = db.Column('BAccountName', db.String(50))  # 银行账户名
    returnable_days = db.Column('ReturnableDays', db.Integer)  # 可退货天数
    flag = db.Column('flag', db.String(2))  # 标志
    kong_pic = db.Column('kongPic', db.String(200))  # 空图片
    talbeware_cost = db.Column('talbeware_cost', db.Numeric(precision=10, scale=2))  # 餐具费用
    tableware_flag = db.Column('tableware_flag', db.String(4))  # 餐具是否免费
    update_time = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now)
    grade = db.Column('Grade', db.Integer)  # 店铺等级
    virtual_business_mark = db.Column('virtualBusinessMark', db.String(2))  # 店铺标识

# 订单主表模型
class OrderMaster(db.Model):
    __tablename__ = 'tbl_order_master_dat'
    master_order_id = db.Column(db.String(32), primary_key=True)  # 主订单id
    pay_time = db.Column(db.String(32))  # 订单发起支付时间
    service_id = db.Column(db.String(32))  # 服务id
    user_id = db.Column(db.String(50))  # 用户id
    total_price = db.Column(db.Numeric(precision=18, scale=2))  # 订单总金额
    freight_price = db.Column(db.Numeric(precision=18, scale=2))  # 订单总邮费
    coupon_price = db.Column(db.Numeric(precision=18, scale=2))  # 优惠券抵扣总金额
    integral_price = db.Column(db.Numeric(precision=18, scale=2))  # 积分抵扣总金额
    activity_price = db.Column(db.Numeric(precision=18, scale=2))  # 活动抵扣总金额
    pay_price = db.Column(db.Numeric(precision=18, scale=2))  # 支付总金额
    refund_price = db.Column(db.Numeric(precision=18, scale=2))  # 退款总金额
    refundable_amount = db.Column(db.Numeric(precision=18, scale=2))  # 可退款总金额
    refundable_integral = db.Column(db.String(20))  # 可退款总积分
    integral_amt = db.Column(db.String(20))  # 总使用积分
    order_status = db.Column(db.String(8))  # 订单状态
    address_id = db.Column(db.String(50))  # 收货地址id
    order_source = db.Column(db.String(8))  # 订单来源
    order_label = db.Column(db.String(32))  # 订单类型
    order_create_time = db.Column(db.DateTime)  # 订单创建时间
    order_close_time = db.Column(db.DateTime)  # 订单关闭时间
    order_refund_time = db.Column(db.DateTime)  # 订单退款发起时间
    order_pay_time = db.Column(db.DateTime)  # 订单支付时间
    order_sett_time = db.Column(db.DateTime)  # 订单结算时间
    order_account_time = db.Column(db.DateTime)  # 订单对账时间
    description = db.Column(db.String(50))  # 描述
    create_time = db.Column(db.DateTime)  # 创建时间
    update_time = db.Column(db.DateTime)  # 修改时间
    update_people = db.Column(db.String(20))  # 修改人
    is_delete = db.Column(db.String(1))  # 是否删除
    remark = db.Column(db.String(200))  # 备注

# 订单商品SKU模型
class OrderGoodsSku(db.Model):
    __tablename__ = 'tb_order_goods_sku'
    ogskuid = db.Column('OGSKUID', db.String(50), primary_key=True)  # 订单商品SKUID
    master_id = db.Column(db.String(32))  # 主单id
    logistical_id = db.Column(db.String(32))  # 物流单id
    refund_record_id = db.Column(db.String(32))  # 退款单id
    order_id = db.Column('OrderID', db.String(50))  # 订单ID
    integral_price = db.Column(db.Numeric(precision=18, scale=2))  # 积分优惠券金额
    refundable_amount = db.Column(db.Numeric(precision=18, scale=2))  # 可退款总金额
    refundable_integral = db.Column(db.String(200))  # 可退款总积分
    is_refund = db.Column(db.String(8))  # 是否已发生退款
    discount_price = db.Column(db.Numeric(precision=18, scale=2))  # 优惠金额
    scgid = db.Column('SCGID', db.String(50))  # 购物车商品ID
    quantity = db.Column('Quantity', db.String(50))  # 数量
    retail_price = db.Column('RetailPrice', db.Numeric(precision=18, scale=2))  # 零售原价
    actual_price = db.Column('ActualPrice', db.Numeric(precision=18, scale=2))  # 实际价格
    actual_payment = db.Column('ActualPayment', db.Numeric(precision=18, scale=2))  # 实付款
    sku_integral = db.Column('SKUIntegral', db.Integer)  # SKU积分
    sku_integral_value = db.Column('SKUIntegralValue', db.Numeric(precision=18, scale=2))  # SKU积分价值

# 购物车商品模型
class ShoppingCartGoods(db.Model):
    __tablename__ = 'tbl_shopping_cart_goods_dat'
    shopping_cart_goods_id = db.Column(db.String(50), primary_key=True)  # 购物车商品ID
    user_id = db.Column(db.String(50))  # 用户ID
    giid = db.Column(db.String(50))  # 商品信息ID
    gskuid = db.Column(db.String(50))  # 商品SKUID
    shopping_cart_goods_num = db.Column(db.Integer)  # 商品数量
    shopping_cart_goods_status = db.Column(db.String(4))  # 商品状态
    create_time = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

# 收货地址模型
class DeliveryAddress(db.Model):
    __tablename__ = 'tb_delivery_address'
    daid = db.Column('DAID', db.String(50), primary_key=True)  # 地址ID
    user_id = db.Column('UserID', db.String(50))  # 用户ID
    pcc = db.Column('PCC', db.String(50))  # 省市区代码
    adress = db.Column('Adress', db.String(100))  # 详细地址
    mphone = db.Column('Mphone', db.String(15))  # 手机号
    contact_name = db.Column('ContactName', db.String(20))  # 联系人姓名
    default_address = db.Column('DefaultAddress', db.String(1))  # 默认地址标识
    pc = db.Column('PC', db.String(10))  # 邮政编码
    status = db.Column('Status', db.String(1))  # 状态
    province = db.Column('province', db.String(20))  # 省
    city = db.Column('city', db.String(20))  # 市
    district = db.Column('district', db.String(20))  # 行政区
    create_time = db.Column('create_time', db.DateTime, default=datetime.now)
    update_time = db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now)