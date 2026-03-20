## 黄金价格监控系统
### 一、背景需求
随着这两年黄金价格大涨，大家想实时关注金价但是有时又不能不方便实时查看手机或电脑，需要一个价格提醒的需求，虽然现有很多app提供价格提醒，但是可能我接触的少，发现很多软件都不是自己需要的，所以基于自己想法和需求想弄一个价格提醒系统。此程序适合做短线黄金交易。投资有风险，购买请谨慎！
### 二、技术实现
#### PS：作为一个白剽党而言想办法节省或者免费才是王道！哈
服务器：本地运行或云服务器
域名：（可选）
开发语言：Python
主力开发：AI
消息推送：微信公众号（可申请微信公众平台的测试号-免费）

整个程序都是基于半吊子全栈开发"AI"训练而来，肯定有不尽人意的地方，但是还算满意（声明：本人对于python是大白，所以介意者可忽略本文及代码，自行实现）
### 三、开发思路整理
补充下一个重要说明，微信公众平台测试号有个坑，就是千万不要设置提醒过于频繁，每天最多100次左右吧，超过了他回缓存，递增给每天的配额，也就是说如果你一次性发1000条消息推送，那未来10天你都看不见新消息了，所以千万谨慎设置。
#### 功能特点
    
- 自动从多个数据源抓取实时黄金价格（每5分钟抓取一次）
- 支持京东金融、新浪财经等多个数据源
- 可配置的价格预警阈值
- 通过微信公众号模板消息向用户发送价格提醒
- 支持价格涨跌预警功能
- 可配置推送间隔时间和推送次数
- 支持定时推送（每小时的01分和31分）
- 预警推送与定时推送互不影响
- 动态更新基准价格
- 增强的日志记录和监控
- 优化的缓存机制，支持缓存过期和性能优化
- 支持缓存清除功能
- 支持生成HTML文件用于Web预览
- 当微信推送出现bug或无法推送时，仍能生成并显示价格数据
- 每天检查重置禁止推送文件push_blocked.txt防止推送被限制
- 多个账号推送配置，自动切换失败的账号
- 支持生成windows桌面软件
- 支持Web配置页面，可通过浏览器访问进行配置管理
- **管理员后台**：支持登录状态管理，登录后可直接访问配置页面
- **AI智能分析功能**：对接免费金融数据分析AI接口，分析黄金和贵金属行情并给出专业建议（控制在200字以内），显示在查看页面和微信推送消息中
- **系统健康监控**：实时监控系统各组件状态，包括数据抓取、JSON生成等
- **增强的JSON写入可靠性**：添加重试机制和状态监控，确保数据持久化

### 四、技术栈

- Python 3.8+
- Playwright（用于抓取黄金价格）
- Requests（用于HTTP请求）
- Flask（用于Web配置页面）
- Jinja2（模板引擎）
- PyInstaller（用于编译Windows可执行文件）
- python-dotenv（用于环境变量管理）
- pyyaml（用于配置管理）
- psutil（用于系统信息监控）
- 微信公众平台API

### 五、项目结构

```
.
├── README.md                  # 项目说明文档
├── .env.example              # 环境变量配置示例文件
├── .gitignore                # Git忽略文件配置
├── LICENSE                   # 项目许可证
├── gold_alert.py             # 黄金价格预警模块（负责处理黄金价格预警逻辑）
├── generate_html.py          # 生成HTML文件功能（负责生成黄金价格监控HTML文件）
├── main.py                   # 主程序（黄金价格监控主循环）
├── main.spec                 # PyInstaller打包配置文件
├── requirements.txt          # 项目依赖列表
├── 部署到宝塔面板.md          # 宝塔面板部署指南
├── templates/                # HTML模板目录
│   ├── admin/                # 管理员后台模板
│   │   ├── config.html       # 配置页面
│   │   ├── dashboard.html    # 仪表盘页面
│   │   ├── login.html        # 登录页面
│   │   └── price-monitor.html # 价格监控页面
│   ├── config_template.html  # 配置页面模板（包含数据源配置和优先级设置）
│   └── gold_price_template.html  # 黄金价格监控HTML模板
├── favicon/                  # 网站图标目录
│   ├── android-chrome-192x192.png
│   ├── android-chrome-512x512.png
│   ├── apple-touch-icon.png
│   ├── favicon-16x16.png
│   ├── favicon-32x32.png
│   ├── favicon.ico           # 网站favicon图标
│   └── site.webmanifest
├── app/                      # Flask应用目录
│   ├── __init__.py           # 应用初始化文件
│   └── routes.py             # 应用路由定义
├── admin/                    # 管理员后台模块
│   ├── __init__.py           # 后台模块初始化文件
│   ├── routes.py             # 后台路由定义
│   └── README.md             # 后台模块说明
├── config/                   # 配置模块目录
│   ├── __init__.py           # 配置包初始化文件
│   ├── config.py             # 核心配置文件
│   └── config_web.py         # Web配置页面处理模块
├── sources/                  # 数据源模块目录
│   ├── __init__.py           # 数据源包初始化文件
│   └── data_source.py        # 黄金价格数据源模块（支持API和页面爬虫）
├── logger/                   # 日志模块目录
│   ├── __init__.py           # 日志包初始化文件
│   └── logger_config.py      # 日志配置模块
├── monitor/                  # 监控模块目录
│   ├── __init__.py           # 监控包初始化文件
│   └── monitor.py            # 监控逻辑实现
├── utils/                    # 工具模块目录
│   ├── __init__.py           # 工具包初始化文件
│   ├── gold_monitor_single.py # 单文件版本的黄金价格监控系统
│   ├── clear_cache.py        # 缓存清理功能
│   ├── cross_platform_utils.py # 跨平台工具函数
│   ├── json_scheduler.py     # JSON数据调度器
│   ├── utils.py              # 核心工具函数
│   └── windows_compile.py    # Windows可执行文件编译功能
├── wechat/                   # 微信模块目录
│   ├── __init__.py           # 微信包初始化文件
│   ├── access_token.py       # 微信 Access Token 管理
│   └── message.py            # 微信消息发送功能
├── ai/                       # AI分析模块目录
│   ├── __init__.py           # AI包初始化文件
│   ├── ai_analyzer.py        # AI价格分析器
│   ├── ai_service_navigator.py # AI服务导航器
│   ├── check_ai_config.py    # AI配置检查工具
│   └── API_KEY_GUIDE.md      # AI API密钥配置指南
├── gui/                      # GUI窗口模块
│   ├── __init__.py           # GUI模块初始化文件
│   └── window.py             # GUI窗口实现
├── static/                   # 静态文件目录
│   └── vendor/               # 第三方库
│       ├── element-plus/     # Element Plus UI库
│       └── vue/              # Vue.js框架
```

### 六、配置说明

#### 方式一：通过环境变量配置（推荐）

复制 `.env.example` 文件为 `.env`，然后填入实际配置值：

```bash
cp .env.example .env
```

在 `.env` 文件中配置以下信息：

##### 微信公众号配置
- `WECHAT_APP_ID_1`: 第一个公众号AppID
- `WECHAT_APP_SECRET_1`: 第一个公众号AppSecret
- `WECHAT_TEMPLATE_ID_1`: 第一个公众号模板消息ID
- `WECHAT_WEB_URL_1`: 第一个公众号跳转URL
- `WECHAT_ACCOUNT_NAME_1`: 第一个公众号名称

- `WECHAT_APP_ID_2`: 第二个公众号AppID（可选）
- `WECHAT_APP_SECRET_2`: 第二个公众号AppSecret（可选）
- `WECHAT_TEMPLATE_ID_2`: 第二个公众号模板消息ID（可选）
- `WECHAT_WEB_URL_2`: 第二个公众号跳转URL（可选）
- `WECHAT_ACCOUNT_NAME_2`: 第二个公众号名称（可选）

##### AI服务API密钥配置
- `ALIYUN_API_KEY`: 阿里云百炼API密钥
- `BAIDU_API_KEY`: 百度文心一言API Key
- `BAIDU_SECRET_KEY`: 百度文心一言Secret Key
- `XUNFEI_API_KEY`: 讯飞星火API密钥

##### 其他配置项
详见 `.env.example` 文件中的详细说明

#### 方式二：通过Web配置页面（推荐）

1. 启动项目后，在浏览器中访问 `http://localhost:5000/admin/`
2. 输入默认密码 `admin888` 登录（登录后建议修改密码）
3. 在配置页面中修改各项配置
4. 点击保存按钮应用更改

#### 方式三：直接修改 config.py 文件

在 `config.py` 文件中配置以下信息：

##### 微信公众号配置
- `MULTI_ACCOUNT_CONFIG`: 多账号配置数组，包含多个公众号账号的配置信息
  - `APP_ID`: 公众号AppID
  - `APP_SECRET`: 公众号AppSecret
  - `TEMPLATE_ID`: 模板消息ID
  - `WEB_URL`: 公众号跳转URL
  - `NAME`: 账号名称

##### 推送时间配置
- `PUSH_START_TIME`: 每天推送开始时间（24小时制）
- `PUSH_END_TIME`: 每天推送结束时间（24小时制）
- `REGULAR_PUSH_MINUTES`: 定期推送的分钟点（每小时的01分和31分）
- `REGULAR_PUSH_WINDOW`: 定期推送的时间窗口（分钟）

##### 推送频率限制配置
- `MAX_PUSH_COUNT`: 每次触发推送的最大次数
- `BATCH_PUSH_INTERVAL`: 批量推送最小间隔（秒）
- `GLOBAL_PUSH_INTERVAL`: 全局推送最小间隔（秒）

##### 黄金价格配置
- `DATA_FETCH_INTERVAL`: 数据抓取间隔（秒）
- `PRICE_CACHE_EXPIRATION`: 价格缓存过期时间（秒）

##### 黄金价格预警配置
- `DEFAULT_GOLD_PRICE`: 默认黄金价格（人民币/克）
- `DEFAULT_PRICE_GAP_HIGH`: 默认价格上涨浮动差额（人民币/克）
- `DEFAULT_PRICE_GAP_LOW`: 默认价格下跌浮动差额（人民币/克）
- `PRICE_CHANGE_THRESHOLD`: 价格变化阈值（元），用于防止重复推送

##### 系统健康监控配置
- `HEALTH_CHECK_INTERVAL`: 健康检查间隔（秒）
- `JSON_WRITE_RETRY_COUNT`: JSON写入重试次数
- `JSON_WRITE_RETRY_DELAY`: JSON写入重试延迟（秒）

##### 日志配置
- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `LOG_FILE`: 日志文件路径

##### 测试模式配置
- `TEST_MODE`: 测试模式开关，设为 True 时启用测试模式，False 时启用正式模式

##### 功能控制配置
- `ENABLE_WECHAT_PUSH`: 控制是否启用微信推送（包括预警推送和定期推送）
  - `True`: 启用微信推送
  - `False`: 禁用微信推送
- `ENABLE_HTML_GENERATION`: 控制是否生成HTML文件
  - `True`: 启用HTML文件生成
  - `False`: 禁用HTML文件生成
- `ENABLE_GUI_WINDOW`: 控制是否显示GUI窗口
  - `True`: 启用GUI窗口显示
  - `False`: 禁用GUI窗口显示
- `ENABLE_COMPILE`: 控制是否编译Windows可执行文件
  - `True`: 启用Windows可执行文件编译
  - `False`: 禁用Windows可执行文件编译
- `ENABLE_RUN_EXE`: 控制是否运行生成的Windows可执行文件
  - `True`: 启用Windows可执行文件运行
  - `False`: 禁用Windows可执行文件运行

##### 数据源配置
- `DATA_SOURCE_TYPES`: 数据源类型配置，包含API和页面爬虫两种类型
  - `api`: API接口获取数据
  - `drissionpage`: 页面爬虫获取数据
- `DATA_SOURCE_MODES`: 数据源获取模式配置
  - `single`: 单一获取模式（按排序和启用状态获取第一个可用数据源）
  - `cycle`: 循环获取模式（按排序遍历所有启用数据源，获取到即停止）
- `GOLD_PRICE_SOURCES`: 黄金价格数据源配置，包含多个数据源的详细信息
  - 每个数据源包含以下字段：
    - `name`: 数据源名称
    - `type`: 数据源类型（api或drissionpage）
    - `url`: 数据源URL
    - `enabled`: 是否启用（true/false）
    - `sort_order`: 排序序号（数字，越小优先级越高）

##### 数据持久化配置
- **JSON数据文件生成**：无论功能控制配置如何，系统都会自动生成包含黄金价格和推送消息的JSON数据文件
  - 文件位置：项目根目录下的 `data/` 文件夹
  - 文件命名：按日期命名，格式为 `YYYYMMDD.json`
  - 数据结构：包含时间戳、价格数据、消息数据等完整信息
  - **防重复机制**：
    - 时间戳和价格双重校验，避免重复记录
    - 最小写入间隔1秒，防止高频写入
    - 自动检测并跳过相同时间戳和相似价格的数据
  - **安全机制**：采用临时文件+原子移动的方式写入，避免文件损坏
  - **文件管理**：自动限制文件大小（5MB）和记录数量（2000条），防止无限增长
  - **死循环防护**：内置频率控制和延迟机制，确保系统稳定运行

##### 配置页面密码
- `CONFIG_PASSWORD`: 配置页面访问密码，默认为 'admin888'

##### 管理员后台配置
- 管理员后台默认路径：`http://localhost:5000/admin/`
- 默认登录密码：`admin888`
- 登录后可直接访问配置页面，无需重复输入密码



### 七、使用方法

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果使用Playwright获取数据方式，请额外安装浏览器驱动：

```bash
# DrissionPage 不需要安装浏览器
```

**依赖说明**：
- `pyyaml`：用于配置管理，提供更多配置选项
- `psutil`：用于系统信息监控，显示CPU和内存使用率

#### 2. 配置环境变量（推荐方式）

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑 .env 文件，填入实际配置值
# 包括微信公众号配置、AI服务密钥等
```

或者使用配置检查工具验证配置：

```bash
python ai/check_ai_config.py
```

#### 3. 运行监控程序

```bash
python main.py
```

程序将：
1. 持续监控黄金价格（每5分钟抓取一次）
2. 根据 `ENABLE_WECHAT_PUSH` 配置决定是否发送微信推送消息
3. 在每天09:00-23:00期间的每小时01分和31分发送定期价格更新（仅当 `ENABLE_WECHAT_PUSH=True` 时）
4. 如果配置了 `ENABLE_HTML_GENERATION=True`，会每5分钟生成一次HTML文件
5. 如果配置了 `ENABLE_GUI_WINDOW=True`，会显示GUI窗口
6. 如果配置了 `ENABLE_COMPILE=True`，会编译Windows运行文件
7. 如果配置了 `ENABLE_RUN_EXE=True`，会运行生成的Windows可执行文件
8. 启动Flask服务器，提供Web配置页面

#### 4. 访问管理员后台

在浏览器中访问 `http://localhost:5000/admin/` 使用默认密码 `admin888` 登录（登录后建议修改密码）。

管理员后台提供以下功能：
- **仪表盘**：查看系统信息、运行状态和实时黄金价格
- **价格监控**：查看详细的价格监控数据和历史趋势
  - 基于当日JSON文件数据显示价格监控列表
  - 支持分页器显示，每页20条数据
  - 显示系统状态信息，包括数据抓取状态、JSON生成状态等
  - 实时价格显示与日志中缓存的金价数据保持一致
- **配置管理**：修改推送时间、频率、预警阈值等配置
  - 添加、修改或删除微信公众号账号配置
  - 修改配置页面访问密码
  - 配置数据源获取模式（单一获取或循环获取）
  - 管理数据源的启用/禁用状态
  - 设置数据源的排序序号
  - 通过标签页管理不同类型的数据源配置

**注意**：登录后可直接访问配置页面，无需重复输入密码。

#### 5. 生成HTML文件

在 `config.py` 中设置 `ENABLE_HTML_GENERATION=True`，然后运行 `main.py`，程序会在当前目录生成 `index.html` 文件，可直接用浏览器打开查看实时黄金价格信息。

**注意**：当 `ENABLE_HTML_GENERATION=True` 时，程序会每5分钟生成一次HTML文件，其他功能由相应的配置项控制。

#### 6. 编译Windows运行文件

在 `config.py` 中设置 `ENABLE_COMPILE=True`，然后运行 `main.py`，程序会在 `dist` 目录生成可执行文件，可直接在Windows系统上运行，无需安装Python环境。

或者直接运行编译脚本：

```bash
python windows_compile.py -y
```

#### 7. 清除缓存

项目支持缓存清除功能，可通过以下方式使用：

##### 6.1 运行缓存清除脚本

```bash
python -m utils.clear_cache
```

或者直接运行：

```bash
python utils/clear_cache.py
```

这将运行缓存清除功能，自动清理过期的JSON数据文件。

##### 6.2 在代码中使用缓存清除功能

```python
from sources.data_source import price_cache

# 清除所有缓存
def clear_all_cache():
    price_cache.clear()
    print("所有缓存已清除")

# 清除指定键的缓存
def clear_specific_cache():
    price_cache.clear_key('gold_price')
    print("指定键的缓存已清除")
```

##### 6.3 缓存清除功能说明

- **`price_cache.clear()`**: 清除所有缓存数据，返回清除的记录数量
- **`price_cache.clear_key(key)`**: 清除指定键的缓存数据，返回清除结果
- **自动清理**: `clear_cache.py` 脚本会自动清理超过7天的JSON文件
- **文件截断**: 自动截断过大的JSON文件（超过10MB），保留最新的数据

### 八、项目逻辑说明

#### 1. 项目推送开始和结束时间
- 由 `PUSH_START_TIME` 和 `PUSH_END_TIME` 配置项控制
- 默认为 09:00-23:00
- 在推送时间范围外，程序会等待并定期检查
- 生成HTML文件功能不受此限制

#### 2. 项目推送的时间
- 定时推送：每小时的01分和31分
- 预警推送：当价格达到阈值时立即推送
- 生成HTML文件：每5分钟生成一次

#### 3. 项目推送的次数限制
- 每个预警条件（高价或低价）最多推送 `MAX_PUSH_COUNT` 次
- 添加了全局推送限制，防止短时间内推送过多消息
- 生成HTML文件功能不受此限制

#### 4. 数据抓取逻辑
- 每5分钟抓取一次数据
- 支持两种数据获取方式：API接口和页面爬虫（Playwright）
- 根据数据源获取模式设置（DATA_SOURCE_MODE）决定数据获取策略
- 支持数据源启用/禁用控制和排序功能
- 实现了简单的缓存机制以提高性能
- 采用工厂模式和基类/子类架构管理不同类型的数据源
- **单一获取模式**：严格按排序序号和启用状态，只使用第一个可用数据源
- **循环获取模式**：按排序序号遍历所有启用的数据源，获取到数据即停止
- 支持动态配置管理，可通过Web配置页面实时调整数据源设置

#### 5. 预警推送规则
- 当价格达到 `默认黄金价格+上涨浮动差额` 或 `默认黄金价格-下跌浮动差额` 时立即推送
- 预警推送不影响定时推送的时间规则
- 预警后自动更新默认黄金价格为预警价格

#### 6. 推送失败处理机制

系统实现了智能的推送失败处理机制：

- **失败计数**: 当推送失败时，系统会记录失败次数，而不是立即设置全天阻止
- **分类统计**: 分别统计定期推送、高价预警推送和低价预警推送的失败次数
- **阈值控制**: 只有当某类推送连续失败达到设定阈值（默认3次）时，才会设置当天禁止推送
- **灵活恢复**: 每天凌晨会自动清除失败计数和推送阻止状态

### 九、消息模板格式

为了确保消息能正确显示，微信模板消息应具有以下字段：

```
黄金价格
消息类型：{{type.DATA}}
当前价格：{{price.DATA}}
行情走势：{{trend.DATA}}
数据来源：{{source.DATA}}
基价：{{base.DATA}}
上浮价：{{high.DATA}}
下浮价：{{low.DATA}}
动态基准价：{{dynamic_base.DATA}}
AI分析建议：{{analysis.DATA}}
推送时间：{{time.DATA}}
```

字段说明：
- `type`：消息类型（定时消息/预警消息）
- `price`：当前价格信息
- `trend`：价格趋势（上涨/下跌/持平）
- `source`：数据来源（新浪财经）
- `base`：基准价格
- `high`：上涨阈值
- `low`：下跌阈值
- `dynamic_base`：动态基准价格
- `analysis`：AI分析建议（新增）
- `time`：推送时间

### 十、部署到宝塔面板

1. 在宝塔面板中创建新的Python项目
2. 上传所有代码文件到项目目录
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 如果使用Playwright获取数据方式，请额外安装浏览器驱动：
   ```bash
   # DrissionPage 不需要安装浏览器
   ```
5. 配置环境变量和定时任务（根据需要）
6. 启动项目并设置开机自启

### 十一、注意事项

- 需要安装 Playwright 并下载浏览器驱动：
  ```bash
  # DrissionPage 不需要安装浏览器
  ```
- 确保网络连接正常
- 避免过于频繁的请求导致被反爬虫机制拦截
- 微信公众号需通过认证并开启相关接口权限
- 微信公众平台测试号每天有消息推送次数限制（约100次），请合理设置推送频率
- 生成的HTML文件可直接用浏览器打开查看
- 编译的Windows可执行文件会保存在 `dist` 目录
- 配置页面默认密码为 'admin888'，登录后请立即修改

### 十二、常见问题

#### 1. 为什么无法获取黄金价格？

- 检查网络连接是否正常
- 检查Playwright是否正确安装
- 检查新浪财经网站是否可以正常访问

#### 2. 为什么没有发送微信消息？

- 检查微信公众号配置是否正确
- 检查是否在推送时间范围内
- 检查是否被禁止推送（查看 `push_blocked.txt` 文件）
- 检查微信公众号是否已认证并开启相关接口权限

#### 3. 如何修改推送时间？

在 `config.py` 文件中修改 `PUSH_START_TIME` 和 `PUSH_END_TIME` 配置项。

#### 4. 如何修改预警阈值？

在 `config.py` 文件中修改 `DEFAULT_PRICE_GAP_HIGH` 和 `DEFAULT_PRICE_GAP_LOW` 配置项。

#### 5. 如何生成HTML文件？

在 `config.py` 文件中设置 `ENABLE_HTML_GENERATION=True`，然后运行 `main.py`。

#### 6. 如何编译Windows运行文件？

在 `config.py` 文件中设置 `ENABLE_COMPILE=True`，然后运行 `main.py`，或者直接运行：

```bash
python -m utils.windows_compile -y
```

或者：

```bash
python utils/windows_compile.py -y
```

#### 7. 如何修改配置页面密码？

在 `config.py` 文件中修改 `CONFIG_PASSWORD` 配置项，或者通过Web配置页面修改。

### 十三、错误处理机制

此项目已优化，在出现错误时会继续运行并尝试恢复，不会立即停止程序运行。

- 当无法获取金价数据时，程序会继续运行并在下次尝试时重试获取数据
- 当推送被禁止时，程序会继续运行但暂停推送功能
- 当HTML生成失败时，程序会继续运行并在下次尝试时重新生成
- 当Windows编译失败时，程序会继续运行并记录错误
- 当遇到严重异常时，程序会捕获异常并尝试恢复运行
- 配置模块加载失败时，会使用默认值并记录错误，确保系统可以继续运行

### 十四、更新日志

#### v1.0.0
- 初始版本发布
- 实现基本的黄金价格获取功能
- 实现微信模板消息推送功能

#### v1.1.0
- 添加多账号支持
- 添加价格预警功能
- 添加定时推送功能

#### v1.2.0
- 添加HTML页面生成功能
- 添加Windows可执行文件编译功能
- 优化错误处理机制

#### v1.3.0
- 添加推送失败重试机制
- 优化推送频率控制
- 改进日志输出格式

#### v1.4.0
- 优化推送失败处理机制
- 实现失败计数功能
- 实现按推送类型分类的失败阈值控制

#### v1.5.0
- 添加Web配置页面
- 实现配置的可视化管理
- 将配置处理逻辑从main.py分离到config_web.py
- 使用config.py中的CONFIG_PASSWORD作为配置页面访问密码

#### v1.6.0
- 重构数据源模块，采用工厂模式和基类/子类架构
- 添加数据源配置功能，支持API和页面爬虫两种数据获取方式
- 实现数据源优先级设置，可通过Web配置页面的单选按钮控制
- 优化配置页面，添加标签页管理不同类型的数据源

#### v1.7.0
- 移除数据源优先级相关功能，采用新的数据源管理模式
- 为每个数据源添加enabled（是否启用）和sort_order（排序序号）字段
- 实现单一获取和循环获取两种数据源获取模式
- 增强Web配置页面，支持数据源启用状态和排序序号的配置
- 完善数据源动态管理功能，支持实时配置更新

#### v1.8.0
- 优化当微信推送出现bug或无法推送时，不生成错误页而是把抓取或api返回的数据生成显示html内容
- 解决推送成功后出现死循环错误bug

#### v1.9.0
- 完善管理员后台功能，实现登录状态管理
- 拆分admin/index页面为独立的dashboard、price-monitor和config页面
- 实现admin根路由重定向功能，未登录时跳转到登录页
- 优化config页面的登录状态处理，已登录用户跳过密码验证
- 修复配置模块加载失败时的错误处理，添加默认值和错误记录

#### v1.10.0
- 实现admin页面的动态数据获取，仪表盘和价格监控数据实时更新
- 修复系统信息显示"未知"的问题，确保psutil模块正常工作
- 优化项目结构，提高代码可维护性
- 清理临时文件，提升项目整洁度
- 更新README.md文档，移除无效说明并更新项目信息

#### v1.11.0
- 添加系统健康监控功能，实时监控系统各组件状态
- 增强JSON写入可靠性，添加重试机制和状态监控
- 实现admin/price-monitor页面分页显示，每页20条数据
- 优化默认黄金价格处理，直接读取配置文件中的值
- 移除HTTP请求日志，减少日志文件大小
- 修复JSON调度器中的日志初始化问题
- 移除BASE_PRICE_ADJUST_STEP相关逻辑，简化代码
- 确保admin/price-monitor页面显示的当前金价与日志中缓存的金价一致
- 基于当日JSON文件数据显示价格监控列表，保持实时数据显示逻辑不变
- 优化数据抓取和缓存机制，提高系统性能和可靠性

#### v1.12.0
- 修复utils/utils.py中的代码重复问题，提高代码质量
- 添加配置验证和变更日志功能，增强配置管理
- 增强错误处理机制，提高系统稳定性
- 优化预警推送时间检查逻辑，确保预警推送遵循推送时间配置
- 改进推送时间窗口计算，处理分钟值超过59的边界情况
- 添加配置变更日志记录功能，便于审计和追踪配置修改


### 十五、项目架构说明

本项目采用模块化设计，各功能模块职责分明：

#### 核心模块
- **main.py**: 程序入口和主循环控制
- **gold_alert.py**: 黄金价格预警逻辑处理
- **generate_html.py**: HTML页面生成功能
- **gold_monitor_single.py**: 单文件版本的黄金价格监控系统

#### 功能模块目录
- **admin/**: 管理员后台模块
  - `routes.py`: 后台路由定义

- **app/**: Flask应用模块
  - `routes.py`: 应用路由定义

- **config/**: 配置管理模块
  - `config.py`: 核心配置参数
  - `config_web.py`: Web配置界面

- **sources/**: 数据源管理模块
  - `data_source.py`: 黄金价格数据获取和处理

- **logger/**: 日志管理模块
  - `logger_config.py`: 日志配置和管理

- **monitor/**: 监控模块
  - `monitor.py`: 监控逻辑实现

- **utils/**: 工具函数模块
  - `utils.py`: 核心工具函数
  - `windows_compile.py`: Windows可执行文件编译
  - `clear_cache.py`: 缓存清理功能
  - `json_scheduler.py`: JSON数据调度器
  - `clean_temp_files.py`: 清理临时文件

- **wechat/**: 微信推送模块
  - `access_token.py`: 微信Access Token管理
  - `message.py`: 微信消息发送功能

- **ai/**: AI分析模块
  - `ai_analyzer.py`: AI价格分析功能
  - `ai_service_navigator.py`: AI服务管理
  - `check_ai_config.py`: AI配置检查工具

- **gui/**: GUI窗口模块
  - `window.py`: GUI窗口实现

- **templates/**: HTML模板目录
  - `admin/`: 管理员后台模板
  - `config_template.html`: 配置页面模板
  - `gold_price_template.html`: 黄金价格监控模板

- **static/**: 静态文件目录
  - `vendor/`: 第三方库（Element Plus、Vue.js）

这种模块化结构使得：
- 代码组织更加清晰，便于维护
- 功能模块间耦合度降低
- 支持按需导入，提高运行效率
- 便于团队协作开发
- 有利于功能扩展和重构

### 十六、贡献指南

欢迎提交Issue和Pull Request。在贡献代码时请注意：

1. 遵循现有的代码风格和项目结构
2. 新功能请添加相应的文档说明
3. 重要修改请提供测试验证
4. 保持向后兼容性

### 十七、许可证

MIT License

---

**项目状态**: 稳定运行 ✅
**最新版本**: v1.12.0
**更新时间**: 2026年2月
**开发语言**: Python 3.8+
