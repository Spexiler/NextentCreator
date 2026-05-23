# NextentCreator API 配置指南

本文档详细说明如何配置 NextentCreator 的各种 API。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [大模型 API 配置](#大模型-api-配置)
3. [服务配置](#服务配置)
4. [配置验证](#配置验证)
5. [常见问题](#常见问题)

---

## 🚀 快速开始

### 第一步：复制配置模板

```bash
cd NextentCreator/config
cp .env.example .env
```

### 第二步：编辑 `.env` 文件

打开 `.env` 文件，填入你的 API 密钥：

```env
# 选择 LLM 提供商
LLM_PROVIDER=openai

# 填入你的 API Key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 第三步：安装依赖并启动

```bash
cd backend/agents
pip install -r requirements.txt
python main.py
```

---

## 🤖 大模型 API 配置

NextentCreator 支持以下大模型 API：

### 1. OpenAI (推荐)

**获取 API Key**: https://platform.openai.com/api-keys

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

**可选模型**:
| 模型 | 说明 | 价格 |
|------|------|------|
| `gpt-4o-mini` | 快速、经济（推荐） | $0.15/1M tokens |
| `gpt-4o` | 最新旗舰模型 | $5/1M tokens |
| `gpt-4-turbo` | 高性能模型 | $10/1M tokens |
| `gpt-3.5-turbo` | 经济实惠 | $0.5/1M tokens |

---

### 2. Claude (Anthropic)

**获取 API Key**: https://console.anthropic.com/

```env
LLM_PROVIDER=claude
CLAUDE_API_KEY=your-api-key-here
CLAUDE_BASE_URL=https://api.anthropic.com/v1
CLAUDE_MODEL=claude-3-haiku-20240307
```

**可选模型**:
| 模型 | 说明 | 价格 |
|------|------|------|
| `claude-3-haiku-20240307` | 快速、经济（推荐） | $0.25/1M tokens |
| `claude-3-sonnet-20240229` | 平衡性能 | $3/1M tokens |
| `claude-3-opus-20240229` | 最强性能 | $15/1M tokens |

---

### 3. 文心一言 (百度)

**获取 API Key**: https://console.bce.baidu.com/qianfan/

```env
LLM_PROVIDER=wenxin
WENXIN_API_KEY=your-api-key-here
WENXIN_SECRET_KEY=your-secret-key-here
WENXIN_MODEL=ERNIE-Bot-4
```

**可选模型**:
- `ERNIE-Bot-4` - 最新版本
- `ERNIE-Bot` - 标准版本
- `ERNIE-Bot-turbo` - 快速版本

---

### 4. 通义千问 (阿里云)

**获取 API Key**: https://dashscope.console.aliyun.com/

```env
LLM_PROVIDER=qwen
QWEN_API_KEY=your-api-key-here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1
QWEN_MODEL=qwen-turbo
```

**可选模型**:
- `qwen-turbo` - 快速版本（推荐）
- `qwen-plus` - 增强版本
- `qwen-max` - 最强版本

---

### 5. DeepSeek

**获取 API Key**: https://platform.deepseek.com/

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

**特点**: 兼容 OpenAI API 格式，价格实惠

---

## ⚙️ 服务配置

### Python Agent 服务

```env
# 服务监听地址
AGENT_HOST=0.0.0.0

# 服务端口
AGENT_PORT=8000
```

启动服务：
```bash
cd backend/agents
python main.py
```

服务地址：`http://localhost:8000`

### PHP API 网关

编辑 `backend/api/index.php`：

```php
$config = [
    'python_api_url' => 'http://localhost:8000',  // Python 服务地址
    'version' => '1.0.0',
    'name' => 'NextentCreator API'
];
```

---

## ✅ 配置验证

### 方法一：启动服务检查

```bash
cd backend/agents
python main.py
```

如果看到：
```
🚀 启动 NextentCreator Agent API...
📡 服务地址: http://localhost:8000
🤖 Agent数量: 6
```

说明配置成功！

### 方法二：API 测试

```bash
# 测试 Agent 服务
curl http://localhost:8000/

# 测试内容创作
curl -X POST http://localhost:8000/create \
  -H "Content-Type: application/json" \
  -d '{"type": "article", "topic": "Python编程"}'
```

---

## ❓ 常见问题

### Q1: 提示 "LLM 客户端未正确配置"

**原因**: 缺少依赖或配置文件

**解决方案**:
```bash
# 安装依赖
pip install python-dotenv pyyaml httpx

# 检查配置文件
ls config/.env
```

### Q2: API 调用失败

**可能原因**:
1. API Key 错误或过期
2. 网络连接问题
3. API 余额不足

**解决方案**:
1. 检查 API Key 是否正确
2. 检查网络连接
3. 登录对应平台查看余额

### Q3: 如何切换不同的 LLM？

只需修改 `.env` 文件中的 `LLM_PROVIDER`：

```env
# 切换到 Claude
LLM_PROVIDER=claude

# 切换到文心一言
LLM_PROVIDER=wenxin
```

重启服务即可生效。

### Q4: 如何使用代理？

对于 OpenAI 等需要代理的服务：

```env
OPENAI_BASE_URL=https://your-proxy.com/v1
```

或设置系统代理：
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

### Q5: Python 3.13 安装 pydantic 失败怎么办？

**原因**: pydantic 2.5.0 没有 Python 3.13 的预编译 wheel，源码编译需要 Rust 工具链。

**解决方案**: 已更新 requirements.txt 中的 pydantic 版本约束为 `pydantic>=2.10.0,<3`，该版本自带 Python 3.13 的预编译 wheel，无需 Rust 编译：

```bash
pip install -r backend/agents/requirements.txt
```

如果仍遇到问题，建议使用 Python 3.11 或 3.12 运行本项目。

---

## 四、MiMo 配置使用说明

### 1. 配置环境变量

编辑 `.env` 文件（位于 `config/.env`），添加以下配置：

```bash
LLM_PROVIDER=mimo
MIMO_API_KEY=你的API密钥
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2-flash
```

### 2. 获取 API Key

1. 访问 [Xiaomi MiMo 开放平台](https://100t.xiaomimimo.com)
2. 使用小米账号登录
3. 创建 API Key 并复制

### 3. 模型选择

| 模型名称 | 定位 | 适用场景 |
|---------|------|---------|
| `mimo-v2-flash` | 轻量快速版 | 日常对话、内容创作（推荐） |
| `mimo-v2-pro` | 旗舰级 | 高强度推理、复杂任务 |

### 4. 认证方式

MiMo API 使用 `api-key` 请求头（非 `Authorization: Bearer`）：

```bash
# 正确认证方式
curl -X POST https://api.xiaomimimo.com/v1/chat/completions \
  -H "api-key: 你的API密钥" \
  -H "Content-Type: application/json" \
  -d '{"model": "mimo-v2-flash", "messages": [{"role": "user", "content": "你好"}]}'
```

### 5. 验证连接

```bash
cd backend/agents
python -c "
from llm_client import LLMClient
import asyncio
client = LLMClient()
print(f'MiMo 配置检查: provider={client.provider}, model={client.model}, base_url={client.base_url}')
"
```

如果 API Key 有效，启动 Python Agent 服务后，Agent 将使用 MiMo 模型进行真实内容生成。

---

## 📁 配置文件说明

| 文件 | 说明 |
|------|------|
| `config/.env.example` | 配置模板（提交到 Git） |
| `config/.env` | 实际配置（不提交，包含密钥） |
| `config/api_config.yaml` | YAML 格式配置（可选） |

**重要**: `.env` 文件包含敏感信息，已添加到 `.gitignore`，不会被提交到 Git。

---

## 🔒 安全建议

1. **不要将 API Key 提交到 Git**
2. **定期更换 API Key**
3. **设置 API 使用限额**
4. **使用环境变量而非硬编码**

---

## 📞 获取帮助

如有问题，请：
1. 查看本文档的常见问题部分
2. 检查 GitHub Issues: https://github.com/Spexiler/NextentCreator/issues
3. 提交新的 Issue 描述你的问题
