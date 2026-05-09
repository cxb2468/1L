# Everything搜索助手

基于Everything SDK的增强型搜索工具，支持Everything 1.4和1.5版本，提供更强大的搜索功能和友好的用户界面。

## 功能特性

- ✅ 支持Everything 1.4和1.5版本的自动检测和适配
- ✅ 提供直观的图形用户界面
- ✅ 支持高级搜索语法
- ✅ 实时搜索结果显示
- ✅ 支持多种排序方式
- ✅ 快速启动Everything服务
- ✅ 配置持久化保存
- ✅ 多语言支持

## 系统要求

- Windows 7或更高版本
- Python 3.7或更高版本
- Everything 1.4或1.5版本

## 安装说明

### 1. 安装Python

如果您还没有安装Python，请从[Python官方网站](https://www.python.org/downloads/)下载并安装Python 3.7或更高版本。

### 2. 安装依赖

打开命令提示符，进入项目目录，执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### 3. 安装Everything

确保您已经安装了Everything 1.4或1.5版本。您可以从[Everything官方网站](https://www.voidtools.com/)下载并安装。

### 4. 配置SDK文件

项目已经包含了必要的SDK文件，位于`resources/dll/`目录下：
- `Everything64.dll`：Everything 1.4 SDK
- `Everything3_x64.dll`：Everything 1.5 SDK

## 使用方法

### 启动应用

双击`main.py`文件或在命令提示符中执行以下命令：

```bash
python main.py
```

### 基本操作

1. **搜索**：在搜索框中输入搜索关键词，按Enter键或点击搜索按钮开始搜索
2. **排序**：点击结果列表的列标题可以按该列排序
3. **打开文件**：双击搜索结果可以打开文件或文件夹
4. **复制路径**：右键点击搜索结果可以复制文件路径

### 高级搜索语法

支持Everything的高级搜索语法，例如：
- `ext:pdf`：搜索PDF文件
- `size:>10mb`：搜索大于10MB的文件
- `dm:lastweek`：搜索上周修改的文件
- `name:"test"`：搜索名称包含test的文件

## 项目结构

```
EverythingHelper/
├── config/             # 配置文件目录
│   └── config.json     # 应用配置
├── resources/          # 资源文件目录
│   └── dll/            # SDK DLL文件
│       ├── Everything64.dll       # Everything 1.4 SDK
│       └── Everything3_x64.dll    # Everything 1.5 SDK
├── src/                # 源代码目录
│   ├── config_manager.py        # 配置管理
│   ├── resource_manager.py      # 资源管理
│   ├── sdk_adapter.py           # SDK适配器
│   ├── ui_main.py               # 用户界面
│   ├── user_interaction.py      # 用户交互
│   └── version_detector.py      # 版本检测
├── main.py             # 应用主入口
├── requirements.txt    # 依赖文件
└── README.md           # 项目说明
```

## 核心模块

### version_detector.py

负责检测系统中安装的Everything版本，支持从注册表和正在运行的进程中检测版本信息。

### sdk_adapter.py

SDK适配器，支持同时加载和使用Everything 1.4和1.5版本的SDK，根据检测结果选择合适的版本进行通信。

### config_manager.py

配置管理器，负责加载和保存应用配置，包括窗口大小、位置等设置。

### ui_main.py

用户界面模块，构建应用的图形界面，包括搜索框、结果列表、工具栏等。

### resource_manager.py

资源管理器，负责管理SDK文件的路径和加载。

## 常见问题

### Q: 应用无法启动，提示找不到Everything

A: 请确保您已经安装了Everything，并且Everything服务正在运行。您可以在应用启动时选择手动指定Everything版本。

### Q: 搜索结果为空

A: 请检查Everything服务是否正在运行，以及您的搜索语法是否正确。

### Q: 应用崩溃或无响应

A: 请检查您的Python版本是否符合要求，以及是否安装了所有依赖。如果问题仍然存在，请查看日志文件获取更多信息。

## 日志文件

应用会生成以下日志文件：
- `sdk_adapter.log`：SDK适配器日志
- `ui_main.log`：用户界面日志
- `config_manager.log`：配置管理日志
- `version_detector.log`：版本检测日志

## 开发说明

### 运行测试

项目包含多个测试文件，用于测试各个模块的功能：

```bash
python test_version_detector.py
python test_sdk_adapter.py
python test_config_manager.py
python test_integration.py
```

### 代码风格

项目使用PEP 8代码风格，建议使用以下工具进行代码检查：

```bash
pip install flake8
flake8 src/
```

## 许可证

本项目采用MIT许可证。

## 致谢

- [Everything](https://www.voidtools.com/)：强大的文件搜索工具
- [Python](https://www.python.org/)：优秀的编程语言
- [Tkinter](https://docs.python.org/3/library/tkinter.html)：Python的标准GUI库

## 联系方式

如果您有任何问题或建议，欢迎联系我们。

---

**Everything搜索助手** - 让文件搜索更简单、更高效！