# PD Signal 项目总览

## 项目简介
基于Python和Flet框架重写的PandaLive主播监控工具，将原Node.js版本改造为本地GUI应用。

## 核心功能实现

### 1. 数据库管理 (database_manager.py)
- ✅ SQLite数据库管理
- ✅ 主播信息存储 (vtbs表)
- ✅ 监控列表管理 (watch表)  
- ✅ 配置持久化 (config表)
- ✅ CRUD操作接口

### 2. 通知系统 (notification_manager.py)
- ✅ Windows系统通知集成
- ✅ 开播/下播通知
- ✅ 状态变化通知
- ✅ 错误和信息通知
- ✅ 跨平台通知支持

### 3. 监控核心 (panda_monitor.py)
- ✅ PandaLive API集成
- ✅ Cookie认证支持
- ✅ 批量数据获取
- ✅ 实时状态检查
- ✅ 异步监控循环
- ✅ 主播添加/移除
- ✅ 状态回调机制

### 4. GUI界面 (main.py)
- ✅ Flet现代化界面
- ✅ Cookie配置面板
- ✅ 监控设置面板
- ✅ 主播管理面板
- ✅ 实时状态显示
- ✅ 运行日志显示
- ✅ 响应式布局

### 5. 配置管理 (config.py)
- ✅ JSON配置文件
- ✅ 默认配置管理
- ✅ 配置导入/导出
- ✅ 配置重置功能

### 6. 构建打包
- ✅ PyInstaller打包配置
- ✅ 依赖自动安装脚本
- ✅ 一键构建脚本
- ✅ 发布包生成

## 文件结构

```
pd-signal/
├── main.py                    # 🎯 主程序入口和GUI界面
├── database_manager.py        # 💾 数据库管理模块
├── notification_manager.py    # 🔔 通知管理模块
├── panda_monitor.py          # 🔍 监控核心逻辑
├── config.py                 # ⚙️ 配置管理模块
├── requirements.txt          # 📦 Python依赖列表
├── build.py                  # 🔨 构建脚本
├── build_release.bat         # 🚀 一键构建发布
├── install_dependencies.bat  # 📥 依赖安装脚本
├── run.bat                   # ▶️ 快速启动脚本
├── README_CN.md             # 📖 中文说明文档
└── project_overview.md      # 📋 项目总览
```

## 技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| GUI框架 | Flet | 0.28.3 | 现代化用户界面 |
| HTTP请求 | Requests | 2.31.0 | API调用 |
| 系统通知 | Plyer | 2.1.0 | 跨平台通知 |
| 数据库 | SQLite | 内置 | 本地数据存储 |
| 打包工具 | PyInstaller | 最新 | 可执行文件生成 |

## 与原项目对比

| 功能 | 原Node.js版本 | 新Python版本 |
|------|---------------|---------------|
| 通知方式 | Telegram Bot | Windows系统通知 ✅ |
| 用户界面 | 命令行 | GUI界面 ✅ |
| 数据存储 | SQLite | SQLite ✅ |
| 配置管理 | 命令行参数 | 可视化配置 ✅ |
| 部署方式 | Node.js运行时 | 独立可执行文件 ✅ |
| Cookie支持 | 支持 | 支持 ✅ |
| 监控功能 | 完整 | 完整 ✅ |

## 使用流程

1. **环境准备**
   ```bash
   # 方式1: 直接运行
   install_dependencies.bat
   python main.py
   
   # 方式2: 构建exe
   build_release.bat
   ```

2. **配置设置**
   - 获取PandaLive Cookie
   - 设置监控间隔
   - 保存配置

3. **添加主播**
   - 输入主播ID
   - 点击添加按钮
   - 确认添加成功

4. **开始监控**
   - 点击开始监控
   - 查看实时状态
   - 接收系统通知

## 核心优势

1. **本地化**: 无需Telegram，使用系统通知
2. **可视化**: 直观的GUI界面操作
3. **独立性**: 可打包为独立exe文件
4. **持久化**: 配置和数据自动保存
5. **现代化**: 基于现代Python技术栈
6. **易用性**: 一键安装和构建脚本

## 开发状态

✅ **已完成**: 核心功能全部实现  
✅ **已测试**: 基础功能测试通过  
✅ **可部署**: 支持源码运行和exe打包  
✅ **文档完整**: 包含详细使用说明  

## 后续优化

- [ ] 添加主播搜索功能
- [ ] 支持更多通知样式
- [ ] 添加统计数据面板
- [ ] 支持主播分组管理
- [ ] 添加自动更新功能

---

**项目状态**: ✅ 完成  
**最后更新**: 2025-01-26  
**版本**: v1.0.0
