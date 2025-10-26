# 测试修复和改进策略

## 🎯 测试现状分析

### 当前问题
1. **测试文件引用错误**
   - [`tests/test_core.py`](tests/test_core.py:2) 引用不存在的 `example_pkg.core` 模块
   - [`tests/test_proxy.py`](tests/test_proxy.py:11) 引用不存在的 `run_geminicli` 函数

2. **测试覆盖率不足**
   - 缺少关键功能的单元测试
   - 没有集成测试
   - 缺少错误场景测试

3. **测试结构不合理**
   - 测试组织不清晰
   - 缺少测试配置
   - 测试依赖管理不完善

## 🛠️ 测试修复计划

### 阶段一：基础修复（立即执行）

#### 1.1 修复测试引用
```python
# 修复 tests/test_core.py
# 删除对 example_pkg.core 的引用
# 或者创建对应的测试模块

# 修复 tests/test_proxy.py  
# 更新函数引用为正确的函数名
# 确保所有mock对象正确设置
```

#### 1.2 验证测试可运行
```bash
# 运行所有测试验证修复
python -m unittest discover -v

# 检查测试输出
# 确保没有导入错误
# 验证测试执行
```

### 阶段二：测试增强（第一阶段）

#### 2.1 添加核心功能测试
```python
# 健康检查端点测试
def test_health_endpoint():
    # 测试 /health 端点
    # 验证响应格式和状态码

# 模型列表端点测试  
def test_models_endpoint():
    # 测试 /v1/models 端点
    # 验证模型列表格式

# 聊天补全端点测试
def test_chat_completions_endpoint():
    # 测试 /v1/chat/completions 端点
    # 验证请求处理和响应格式
```

#### 2.2 添加错误场景测试
```python
# 无效请求测试
def test_invalid_request():
    # 测试缺少必需参数
    # 测试无效JSON格式
    # 测试超时场景

# Gemini CLI错误测试
def test_gemini_cli_errors():
    # 测试CLI不存在的情况
    # 测试CLI执行失败
    # 测试超时情况
```

### 阶段三：测试架构优化（第二阶段）

#### 3.1 测试配置优化
```python
# 创建 tests/conftest.py
# 配置测试环境
# 设置测试夹具
# 管理测试依赖
```

#### 3.2 测试工具完善
```python
# 创建测试工具函数
# 测试数据生成器
# 断言辅助函数
# 模拟数据工具
```

## 📊 测试覆盖目标

### 单元测试覆盖
- [ ] 路由层测试覆盖 > 90%
- [ ] 服务层测试覆盖 > 85%  
- [ ] 工具类测试覆盖 > 95%
- [ ] 配置管理测试覆盖 > 80%

### 集成测试覆盖
- [ ] API端点集成测试
- [ ] 端到端功能测试
- [ ] 错误场景集成测试

### 性能测试
- [ ] 响应时间测试
- [ ] 并发处理测试
- [ ] 资源使用测试

## 🔧 具体实施步骤

### 步骤1：修复现有测试
```python
# 1. 分析测试失败原因
# 2. 更新模块和函数引用
# 3. 修复mock对象设置
# 4. 验证测试通过
```

### 步骤2：创建测试配置
```python
# tests/conftest.py 内容：
import pytest
from fastapi.testclient import TestClient
from proxy import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_chat_request():
    return {
        "model": "gemini-local",
        "messages": [{"role": "user", "content": "Hello"}]
    }
```

### 步骤3：添加路由测试
```python
# tests/test_health.py
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ts" in data

# tests/test_models.py  
def test_models_endpoint(client):
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert "data" in data
```

### 步骤4：添加服务层测试
```python
# tests/test_gemini_service.py
import pytest
from unittest.mock import patch, AsyncMock
from services.gemini_service import run_gemini_cli

@pytest.mark.asyncio
async def test_run_gemini_cli_success():
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"Test output", b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc
        
        result = await run_gemini_cli("test prompt")
        assert result == "Test output"
```

### 步骤5：添加错误处理测试
```python
# tests/test_error_handling.py
def test_invalid_json_request(client):
    response = client.post("/v1/chat/completions", data="invalid json")
    assert response.status_code == 400

def test_missing_required_fields(client):
    response = client.post("/v1/chat/completions", json={})
    assert response.status_code == 400
```

## 🎯 测试质量指标

### 代码覆盖率目标
```bash
# 整体覆盖率目标
- 语句覆盖率: > 85%
- 分支覆盖率: > 80%
- 函数覆盖率: > 90%

# 关键模块覆盖率
- 路由层: > 95%
- 核心业务逻辑: > 90%
- 错误处理: > 85%
```

### 测试执行指标
- 测试执行时间: < 30秒
- 测试稳定性: 100% 通过率
- 测试可维护性: 清晰的测试结构

## 🔍 测试验证方法

### 1. 本地测试执行
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试模块
python -m pytest tests/test_health.py -v

# 生成覆盖率报告
python -m pytest tests/ --cov=proxy --cov-report=html
```

### 2. 持续集成测试
```yaml
# GitHub Actions 测试配置
- name: Run tests
  run: |
    python -m pytest tests/ -v
    python -m pytest tests/ --cov=proxy --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### 3. 测试质量检查
```bash
# 测试代码质量
python -m pylint tests/

# 测试导入检查
python -m mypy tests/

# 测试格式检查
python -m black --check tests/
```

## ⚠️ 测试风险控制

### 风险1：测试环境依赖
**控制措施**：
- 使用mock对象隔离外部依赖
- 配置测试专用环境变量
- 提供测试数据生成工具

### 风险2：测试维护成本
**控制措施**：
- 清晰的测试组织结构
- 可重用的测试工具函数
- 详细的测试文档

### 风险3：测试执行稳定性
**控制措施**：
- 避免测试间的依赖
- 使用独立的测试数据库
- 合理的测试超时设置

## 📝 测试改进检查清单

### 完成标准
- [ ] 所有现有测试通过
- [ ] 新增单元测试覆盖核心功能
- [ ] 集成测试验证端到端流程
- [ ] 错误场景测试完整
- [ ] 测试覆盖率达标
- [ ] 测试执行稳定

### 质量指标
- 测试通过率: 100%
- 代码覆盖率: > 85%
- 测试执行时间: < 30秒
- 测试维护性: 良好

## 🔄 持续测试改进

### 测试监控
- 定期检查测试覆盖率
- 监控测试执行时间
- 跟踪测试失败率

### 测试优化
- 定期重构测试代码
- 优化测试执行性能
- 更新测试最佳实践

---

*本测试策略将指导测试修复和改进工作，确保项目具有高质量的测试覆盖和可靠的测试执行。*