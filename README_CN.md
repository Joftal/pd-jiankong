# PD Signal - PandaLive监控工具

基于Python和Flet框架开发的PandaLive主播监控工具，支持本地监控和Windows系统通知。

## 功能特点

- ✅ **多主播监控**: 同时监控多个PandaLive主播
- ✅ **实时通知**: 开播/下播/状态变化实时通知
- ✅ **系统通知**: 使用Windows原生通知系统
- ✅ **数据持久化**: 自动保存配置和监控列表
- ✅ **现代GUI**: 基于Flet的现代化界面
- ✅ **Cookie支持**: 支持登录状态监控，减少API请求
- ✅ **可执行文件**: 可打包为独立的exe文件

## 环境要求

- Windows 10/11
- Python 3.8+
- 网络连接

## 快速开始

### 方法1: 使用源码运行

1. **安装依赖**
   ```bash
   # 运行批处理文件安装依赖
   install_dependencies.bat
   
   # 或手动安装
   pip install -r requirements.txt
   ```

2. **运行程序**
   ```bash
   python main.py
   ```

### 方法2: 构建可执行文件

1. **安装依赖** (包含PyInstaller)
   ```bash
   install_dependencies.bat
   ```

2. **构建可执行文件**
   ```bash
   python build.py
   ```

3. **运行程序**
   - 在`dist`目录中找到`PD-Signal.exe`
   - 双击运行或使用`启动PD-Signal.bat`

## 使用说明

### 1. 设置Cookie

首次使用需要设置PandaLive的Cookie：

1. 打开浏览器，访问并登录 [PandaLive](https://www.pandalive.co.kr)
2. 按`F12`打开开发者工具
3. 切换到`Network`标签
4. 刷新页面，找到任意请求
5. 在请求头中找到`Cookie`值并复制
6. 在程序中粘贴到"Cookie设置"区域并保存

### 2. 添加监控主播

1. 在"主播ID"输入框中输入要监控的主播ID
2. 点击"添加"按钮
3. 主播将出现在监控列表中

### 3. 开始监控

1. 确保已设置有效的Cookie
2. 点击"开始监控"按钮
3. 程序会自动检查主播状态
4. 开播/下播时会收到系统通知

### 4. 配置设置

- **检测间隔**: 每个主播检测的间隔时间（秒）
- **更新间隔**: 获取在线主播列表的间隔时间（秒）
- 配置会自动保存

## 项目结构

```
pd-signal/
├── main.py                 # 主程序入口
├── database_manager.py     # 数据库管理
├── notification_manager.py # 通知管理
├── panda_monitor.py        # 监控核心逻辑
├── config.py              # 配置管理
├── requirements.txt       # Python依赖
├── build.py              # 构建脚本
├── install_dependencies.bat # 依赖安装脚本
└── README_CN.md          # 说明文档
```

## 与原项目的差异

相比原Node.js版本的主要改进：

1. **本地化**: 移除Telegram Bot依赖，使用Windows系统通知
2. **GUI界面**: 提供直观的图形用户界面
3. **数据持久化**: 配置和监控列表自动保存
4. **可执行文件**: 可打包为独立exe，无需安装运行时
5. **现代化**: 使用Python和Flet现代技术栈

## 技术栈

- **Python 3.8+**: 主要编程语言
- **Flet 0.28.3**: 现代GUI框架
- **SQLite**: 本地数据库
- **Requests**: HTTP请求库
- **Plyer**: 跨平台通知库
- **PyInstaller**: 可执行文件打包

## 故障排除

### 常见问题

1. **Cookie无效**
   - 重新获取Cookie
   - 确保Cookie包含完整的认证信息

2. **网络连接失败**
   - 检查网络连接
   - 确认PandaLive网站可访问

3. **通知不显示**
   - 检查Windows通知设置
   - 确保应用有通知权限

4. **主播添加失败**
   - 确认主播ID正确
   - 检查Cookie是否有效

### 调试模式

运行时可以查看控制台输出获取详细错误信息：
```bash
python main.py
```

## 开发

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd pd-signal

# 安装开发依赖
pip install -r requirements.txt
pip install pyinstaller

# 运行开发版本
python main.py
```

### 构建流程

```bash
# 清理并构建
python build.py
```

## 许可证

MIT License

## 致谢

本项目基于原始的 [pd-signal](https://github.com/nbtu/pd-signal) Node.js项目进行Python重写和功能增强。

## 更新日志

### v1.0.0
- 初始版本发布
- 基础监控功能
- Windows系统通知
- Flet GUI界面
- 数据持久化
- 可执行文件打包
