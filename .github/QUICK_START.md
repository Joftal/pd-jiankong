# GitHub Actions 使用指南

## 快速开始

### 1. 启用GitHub Actions
- 确保您的仓库已启用GitHub Actions
- 将工作流文件推送到`.github/workflows/`目录

### 2. 触发构建
```bash
# 推送到Cookie分支触发构建
git push origin Cookie

# 创建标签触发发布
git tag v1.0.0
git push origin v1.0.0
```

### 3. 查看构建结果
- 进入GitHub仓库的Actions页面
- 查看构建状态和日志
- 下载构建产物

## 工作流选择

| 工作流 | 用途 | 触发条件 | 输出 |
|--------|------|----------|------|
| `build-windows.yml` | Windows构建 | 推送/标签/手动 | Windows exe |
| `build-multiplatform.yml` | 多平台构建 | 推送/标签/手动 | Windows/Linux/macOS |
| `test-build.yml` | 测试构建 | PR/推送test分支 | 测试版本 |

## 手动触发

1. 进入Actions页面
2. 选择工作流
3. 点击"Run workflow"
4. 选择分支和参数

## 标签发布

创建`v*`格式的标签会自动发布Release：
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 故障排除

- 查看Actions日志
- 检查依赖版本
- 验证Python代码
- 本地测试构建

## 支持

- GitHub Issues
- Actions日志
- 构建产物下载
