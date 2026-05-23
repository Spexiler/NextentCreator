# NextentCreator - 多Agent协作AI内容创作引擎

<p align="center">
  <img src="https://img.shields.io/badge/Agent-AI%20Driven-blueviolet" alt="AI Driven">
  <img src="https://img.shields.io/badge/Architecture-Multi--Agent-ff69b4" alt="Multi-Agent">
  <img src="https://img.shields.io/badge/LLM-MiMo%20%7C%20OpenAI%20%7C%20Claude-green" alt="LLM Support">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen" alt="Status">
</p>

> **不是简单的文本生成器，而是一个由6个专业AI Agent组成的协作创作团队。**

## ✨ 核心能力

### 实时Agent协作可视化

创作过程中，你可以**实时观看**每一个Agent的工作状态：

- 意图识别Agent正在分析你的需求...
- 任务分发Agent正在路由到最佳创作Agent...
- 图文/技术/社交创作Agent正在生成内容...
- 润色优化Agent正在进行质量把关...

每个Agent的状态**真实反映后端LLM调用进度**——灰色等待 → 蓝色执行中 → 绿色完成。

### 多LLM支持

- **Xiaomi MiMo**（默认）
- OpenAI GPT-4o
- Claude 3
- 文心一言 / 通义千问 / DeepSeek

### 内容管理

- 一键保存到本地存储
- 历史记录随时回看
- 导出Markdown文件
- 复制到剪贴板

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Frontend (HTML5 + Tailwind)          │
│              ┌─────────────┐    ┌─────────────┐             │
│              │  创作工作台  │    │  实时流程可视化│             │
│              └─────────────┘    └─────────────┘             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ SSE 流式连接
┌─────────────────────────────────────────────────────────────┐
│              Python Agent Core (FastAPI + asyncio)           │
│                                                              │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐ │
│   │ 意图识别  │ → │ 任务分发  │ → │ 专项创作  │ → │ 润色优化 │ │
│   │  Agent   │   │  Agent   │   │  Agent   │   │  Agent  │ │
│   └──────────┘   └──────────┘   └──────────┘   └─────────┘ │
│                                      │                       │
│                         ┌────────────┼────────────┐          │
│                         ▼            ▼            ▼          │
│                    ┌────────┐  ┌────────┐  ┌────────┐       │
│                    │ 图文   │  │ 技术   │  │ 社交   │       │
│                    │ 创作   │  │ 创作   │  │ 创作   │       │
│                    └────────┘  └────────┘  └────────┘       │
│                                                              │
│   每个Agent独立调用LLM，通过SSE实时推送状态到前端           │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 Agent 团队

| Agent | 职责 | 技术特点 |
|-------|------|----------|
| 意图识别Agent | 深度解析用户需求，提取创作要素 | 结构化prompt工程，输出标准化任务描述 |
| 任务分发Agent | 智能路由，选择最优创作Agent | 基于内容类型的策略分发 |
| 图文创作Agent | 长图文内容创作 | Markdown格式，800-1500字结构化文章 |
| 技术创作Agent | 技术文档/教程创作 | 含完整代码示例，1000-2000字 |
| 社交创作Agent | 多平台短内容创作 | 朋友圈/微博/LinkedIn三版本+标签 |
| 润色优化Agent | 质量把关和风格统一 | 语法修正、流畅度优化、风格统一 |

## 🚀 快速开始

### 1. 配置API密钥

```bash
cd NextentCreator/config
# 创建 .env 文件并填入你的 API Key
cat > .env << 'EOF'
LLM_PROVIDER=mimo
MIMO_API_KEY=your_api_key_here
MIMO_MODEL=mimo-v2.5
EOF
```

### 2. 安装依赖并启动

```bash
cd backend/agents
pip install -r requirements.txt
python main.py
```

启动时会自动测试LLM连通性：
```
==================================================
🔍 启动时LLM连通性测试
==================================================
📡 提供商: mimo
🤖 模型: mimo-v2.5
✅ 测试成功！模型响应: 我是MiMo，由小米大模型Core团队开发的智能对话助手...
==================================================
```

### 3. 访问使用

打开浏览器访问 `http://localhost:8000` 或直接打开 `index.html`。

## 📁 项目结构

```
NextentCreator/
├── index.html              # 前端主界面（直接打开即可使用）
├── backend/
│   ├── agents/
│   │   ├── main.py         # FastAPI服务 + Agent管理器
│   │   └── llm_client.py   # 多LLM统一客户端
│   ├── api/
│   │   └── index.php       # PHP API网关（可选）
│   └── shared/             # 共享层
├── config/
│   └── .env                # API密钥配置
├── docs/
│   └── API_CONFIGURATION.md # 详细配置指南
└── README.md
```

## 🎯 使用流程

1. **选择内容类型**：图文文章 / 技术文档 / 社交分享
2. **输入创作主题**：例如"如何学习Python编程"
3. **高级选项**（可选）：调整字数、风格、补充要求
4. **点击"开始创作"**：观看Agent实时协作
5. **获取结果**：保存、导出Markdown、或复制使用

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | HTML5 + Tailwind CSS + Vanilla JS |
| 通信 | SSE (Server-Sent Events) 流式推送 |
| API | Python 3.11 + FastAPI + uvicorn |
| Agent | asyncio + 结构化prompt工程 |
| LLM | httpx异步调用，支持多提供商 |

## 📊 性能表现

- 意图识别：~15-25s
- 任务分发：<1s
- 内容创作：~20-30s
- 润色优化：~15-20s
- **总耗时**：~50-75s（取决于LLM响应速度）

## 📝 更新日志

### v1.0.0 (2026-05-23)
- ✅ 6个Agent完整协作流程
- ✅ SSE实时状态推送
- ✅ 前端实时可视化
- ✅ 本地存储与历史记录
- ✅ Markdown导出
- ✅ MiMo API深度适配
- ✅ 启动时LLM连通性自检

---

<p align="center">
  <b>NextentCreator</b> — 让AI Agent为你工作
</p>
