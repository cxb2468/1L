# AI服务API密钥获取指南

## 🚀 推荐的AI服务平台

### 1. 阿里云百炼 (DashScope)
**官网**: https://dashscope.console.aliyun.com/
**文档**: https://help.aliyun.com/document_detail/2214717.html

**获取步骤**:
1. 访问阿里云官网注册账号
2. 搜索"DashScope"或"百炼"
3. 开通服务并进入控制台
4. 在API密钥管理中创建AccessKey
5. 复制API密钥填入配置文件

### 2. 百度千帆大模型平台
**官网**: https://qianfan.cloud.baidu.com/
**文档**: https://cloud.baidu.com/doc/WENXINWORKSHOP/s/jlil56u11

**获取步骤**:
1. 访问百度智能云注册账号
2. 进入千帆大模型平台
3. 创建应用获取API Key和Secret Key
4. 将两个密钥分别填入配置文件

### 3. 讯飞星火认知大模型
**官网**: https://xinghuo.xfyun.cn/
**文档**: https://www.xfyun.cn/doc/spark/Web.html

**获取步骤**:
1. 访问讯飞开放平台注册开发者账号
2. 进入星火认知大模型控制台
3. 创建应用获取API密钥
4. 填入配置文件

## 💡 免费额度说明

| 平台 | 免费额度 | 适用场景 |
|------|----------|----------|
| 阿里云百炼 | 每月一定额度免费调用 | 个人学习、小规模应用 |
| 百度千帆 | 新用户赠送额度 + 每日免费额度 | 个人项目、测试使用 |
| 讯飞星火 | 新用户试用额度 | 学习研究、简单应用 |

## ⚙️ 配置示例

### .env 文件配置模板
```env
# 阿里云百炼API密钥
ALIYUN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 百度千帆API密钥
BAIDU_API_KEY=xxxxxxxxxxxxxxxxxxxxxx
BAIDU_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxx

# 讯飞星火API密钥  
XUNFEI_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## 🔧 故障排除

### 常见问题及解决方案

1. **链接无法访问**
   - 尝试使用不同的网络环境
   - 检查是否被防火墙拦截
   - 使用手机热点测试访问

2. **注册账号问题**
   - 确保邮箱/手机号未被注册
   - 检查验证码是否正确输入
   - 查看垃圾邮件箱中的验证邮件

3. **API密钥获取失败**
   - 确认已开通对应服务
   - 检查账户余额是否充足
   - 联系平台客服寻求帮助

## 🎯 推荐配置策略

**初学者建议**:
- 选择一个平台开始（推荐百度千帆，文档相对完善）
- 先用免费额度测试功能
- 熟悉后再考虑多平台配置

**生产环境建议**:
- 配置2-3个平台实现冗余
- 监控各平台的使用额度
- 建立密钥轮换机制

## 📞 技术支持

如遇到具体技术问题，可以：
1. 查阅各平台官方文档
2. 在开发者社区提问
3. 联系平台技术支持
4. 参考GitHub上的开源项目示例

---
*注：以上链接和信息可能会随时间变化，请以各平台官方最新信息为准*