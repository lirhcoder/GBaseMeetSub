# 贡献指南

感谢您对GBaseMeetSub项目的关注！

## 开发环境设置

1. Fork并克隆仓库
```bash
git clone https://github.com/YOUR_USERNAME/GBaseMeetSub.git
cd GBaseMeetSub
```

2. 设置虚拟环境
```bash
# Linux/MacOS
./setup_env.sh

# Windows
setup_env.bat
```

3. 安装开发依赖
```bash
pip install -r requirements-dev.txt
```

4. 安装pre-commit hooks
```bash
pre-commit install
```

## 开发流程

1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

2. 编写代码并测试
```bash
# 运行测试
python -m pytest tests/

# 检查代码风格
black src/ tests/
flake8 src/ tests/
mypy src/
```

3. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能"
```

提交信息格式：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 添加测试
- `chore:` 构建过程或辅助工具的变动

4. 推送并创建Pull Request
```bash
git push origin feature/your-feature-name
```

## 代码规范

- 使用Black进行代码格式化
- 遵循PEP 8规范
- 添加类型注解
- 编写单元测试
- 保持代码覆盖率在80%以上

## 测试要求

- 所有新功能必须包含测试
- 测试文件放在`tests/`目录
- 使用pytest框架
- 模拟外部依赖

## 文档要求

- 更新README.md（如需要）
- 添加代码注释
- 更新API文档

## 提交Pull Request

1. 确保所有测试通过
2. 更新相关文档
3. 描述清楚改动内容
4. 关联相关Issue

感谢您的贡献！