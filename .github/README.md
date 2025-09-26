# GitHub Actions 构建说明

本项目使用GitHub Actions自动构建Windows可执行文件，支持多种触发方式和平台。

## 工作流文件说明

### 1. `build-windows.yml` - Windows专用构建
- **触发条件**: 推送到main/master/Cookie分支，标签推送，手动触发
- **功能**: 专门为Windows平台构建可执行文件
- **特点**: 简单高效，适合日常开发

### 2. `build-multiplatform.yml` - 多平台构建
- **触发条件**: 推送到main/master/Cookie分支，标签推送，手动触发
- **功能**: 同时构建Windows、Linux、macOS版本
- **特点**: 支持手动选择平台，适合正式发布

### 3. `test-build.yml` - 测试构建
- **触发条件**: 推送到Cookie/test分支，PR到Cookie分支
- **功能**: 快速测试构建流程
- **特点**: 包含基础测试，适合开发调试

## 使用方法

### 自动触发
1. **推送代码**: 推送到指定分支会自动触发构建
2. **创建标签**: 创建`v*`格式的标签会自动发布Release
3. **Pull Request**: 向Cookie分支提交PR会触发测试构建

### 手动触发
1. 进入GitHub仓库的Actions页面
2. 选择对应的工作流
3. 点击"Run workflow"按钮
4. 选择分支和参数（多平台构建可选择平台）

### 标签发布
创建标签时会自动发布Release：
```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

## 构建产物

### Windows版本
- `PD-Signal.exe` - 主程序
- `启动PD-Signal.bat` - 启动脚本
- `使用说明.txt` - 使用说明
- `版本信息.txt` - 版本信息

### 多平台版本
- Windows: `PD-Signal.exe`
- Linux: `PD-Signal` (需要添加执行权限)
- macOS: `PD-Signal` (需要添加执行权限)

## 构建环境

- **Python版本**: 3.11
- **操作系统**: Windows Server 2022, Ubuntu 22.04, macOS 12
- **构建工具**: PyInstaller
- **依赖管理**: pip + requirements.txt

## 缓存策略

- **pip缓存**: 自动缓存pip依赖，加速构建
- **Python环境**: 使用actions/setup-python缓存
- **构建产物**: 保留30天（测试版本7天）

## 故障排除

### 常见问题

1. **构建失败**
   - 检查requirements.txt中的依赖版本
   - 确认Python代码语法正确
   - 查看Actions日志中的详细错误信息

2. **依赖安装失败**
   - 检查网络连接
   - 确认依赖包名称正确
   - 尝试更新pip版本

3. **PyInstaller打包失败**
   - 检查隐藏导入设置
   - 确认所有依赖都已安装
   - 查看PyInstaller错误日志

### 调试方法

1. **查看构建日志**
   - 进入Actions页面
   - 点击失败的构建任务
   - 查看详细日志输出

2. **本地测试**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   pip install pyinstaller
   
   # 本地构建
   python build.py
   ```

3. **验证环境**
   ```bash
   # 检查Python版本
   python --version
   
   # 检查依赖
   python -c "import flet, requests, plyer"
   
   # 检查PyInstaller
   pyinstaller --version
   ```

## 自定义配置

### 修改Python版本
在`.github/workflows/*.yml`文件中修改：
```yaml
env:
  PYTHON_VERSION: '3.12'  # 修改为需要的版本
```

### 添加新的触发条件
```yaml
on:
  push:
    branches: [ main, develop ]  # 添加新分支
  schedule:
    - cron: '0 0 * * 1'  # 每周一自动构建
```

### 修改构建参数
在PyInstaller命令中添加参数：
```yaml
- name: 构建可执行文件
  run: |
    pyinstaller --onefile --windowed --name=MyApp main.py
```

## 最佳实践

1. **版本管理**: 使用语义化版本标签
2. **分支策略**: 主分支用于发布，开发分支用于测试
3. **依赖管理**: 定期更新requirements.txt
4. **测试覆盖**: 在PR中运行测试构建
5. **文档更新**: 及时更新README和说明文档

## 联系支持

如有问题，请：
1. 查看GitHub Issues
2. 检查Actions构建日志
3. 提交新的Issue描述问题
