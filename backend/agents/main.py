#!/usr/bin/env python3
"""
NextentCreator - Agent Core
Python多Agent协作内容创作系统
"""

import asyncio
import json
import time
import sys
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# 导入 LLM 客户端
try:
    from llm_client import generate_text, LLMClient
    LLM_AVAILABLE = True
except ImportError as e:
    LLM_AVAILABLE = False
    print(f"警告: LLM 客户端未正确配置: {e}")

# FastAPI应用
app = FastAPI(
    title="NextentCreator Agent API",
    description="多Agent协作内容创作系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class CreateRequest(BaseModel):
    type: str
    topic: str
    options: Optional[Dict[str, Any]] = {}


# ==================== Agent基类 ====================

class BaseAgent:
    """Agent基类"""

    def __init__(self, name: str, description: str, agent_id: str):
        self.name = name
        self.description = description
        self.agent_id = agent_id
        self.status = "idle"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    async def _call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        if not LLM_AVAILABLE:
            raise RuntimeError("LLM 客户端未加载")
        try:
            result = await generate_text(prompt, max_tokens)
            if not result or len(result.strip()) < 10:
                raise RuntimeError("LLM 返回空内容")
            return result
        except Exception as e:
            print(f"[{self.name}] LLM 调用失败: {e}")
            raise


# ==================== 各Agent实现 ====================

class IntentAgent(BaseAgent):
    """意图识别Agent"""

    def __init__(self):
        super().__init__("意图识别Agent", "解析用户需求，确定内容类型", "intent")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        content_type = input_data.get("type", "article")
        options = input_data.get("options", {})
        style = options.get("style", "casual")
        length = options.get("length", "medium")

        prompt = f"""你是一位专业的内容策划师。请分析以下创作需求，给出详细的意图分析。

【用户输入】
主题：{topic}
内容类型：{content_type}
风格：{style}
长度：{length}

【分析要求】
1. 用户核心意图：用户想要通过这篇内容达到什么目的？
2. 目标受众：这篇内容适合哪些人阅读？
3. 关键要点：列出3-5个必须覆盖的核心要点
4. 语气风格：具体描述应该采用的写作风格
5. 结构建议：推荐的内容结构

请用中文详细回答，每个部分都要具体展开。"""

        analysis = await self._call_llm(prompt, max_tokens=1500)

        return {
            "agent": self.name,
            "agent_id": self.agent_id,
            "status": "completed",
            "topic": topic,
            "content_type": content_type,
            "style": style,
            "length": length,
            "analysis": analysis,
            "next_agent": "dispatcher"
        }


class DispatcherAgent(BaseAgent):
    """任务分发Agent"""

    def __init__(self):
        super().__init__("任务分发Agent", "分发任务到对应专项Agent", "dispatcher")
        self.agent_mapping = {
            "article": "article_creator",
            "tech": "tech_creator",
            "social": "social_creator"
        }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        content_type = input_data.get("content_type", "article")
        topic = input_data.get("topic", "未知主题")
        style = input_data.get("style", "casual")

        target_agent = self.agent_mapping.get(content_type, "article_creator")
        target_name = {
            "article_creator": "图文创作Agent",
            "tech_creator": "技术创作Agent",
            "social_creator": "社交创作Agent"
        }.get(target_agent, "图文创作Agent")

        return {
            "agent": self.name,
            "agent_id": self.agent_id,
            "status": "completed",
            "target_agent": target_agent,
            "target_name": target_name,
            "routing_decision": f"主题'{topic}'为{content_type}类型，路由到{target_name}",
            "topic": topic,
            "content_type": content_type,
            "style": style,
            "next_agent": target_agent
        }


class ArticleCreatorAgent(BaseAgent):
    """图文创作Agent"""

    def __init__(self):
        super().__init__("图文创作Agent", "长图文内容创作", "article_creator")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        style = input_data.get("style", "casual")
        length = input_data.get("length", "medium")
        analysis = input_data.get("analysis", "")

        prompt = f"""你是一位资深的内容创作者。请创作一篇关于"{topic}"的高质量文章。

【意图分析参考】
{analysis}

【创作要求】
1. 标题吸引人，能激发读者点击欲望
2. 引言用1-2段话引入主题，说明为什么值得阅读
3. 主体分3-4个小节，每个小节有明确小标题
4. 每个小节包含：核心观点 + 具体解释 + 实际案例
5. 结论总结全文要点，给出行动建议
6. 风格：{style}
7. 使用Markdown格式
8. 总字数800-1500字

请直接输出完整文章内容。"""

        content = await self._call_llm(prompt, max_tokens=3000)

        return {
            "agent": self.name,
            "agent_id": self.agent_id,
            "status": "completed",
            "content": content,
            "word_count": len(content),
            "style": style,
            "next_agent": "polish"
        }


class TechCreatorAgent(BaseAgent):
    """技术创作Agent"""

    def __init__(self):
        super().__init__("技术创作Agent", "技术文档和教程创作", "tech_creator")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        style = input_data.get("style", "professional")
        analysis = input_data.get("analysis", "")

        prompt = f"""你是一位技术文档专家。请创作一份关于"{topic}"的技术文档。

【意图分析参考】
{analysis}

【文档结构】
1. 概述：介绍这项技术是什么、解决什么问题
2. 核心概念：解释3-5个关键概念
3. 代码示例：提供2个完整的可运行代码示例
4. 实现步骤：分步骤说明如何使用
5. 最佳实践：3-5条使用建议
6. 常见问题：2-3个常见问题及解答
7. 总结：技术要点和学习路径

【格式要求】
- 使用Markdown格式
- 代码块标注语言类型
- 总字数1000-2000字

请直接输出完整文档内容。"""

        content = await self._call_llm(prompt, max_tokens=3000)

        return {
            "agent": self.name,
            "agent_id": self.agent_id,
            "status": "completed",
            "content": content,
            "code_snippets": 2,
            "style": style,
            "next_agent": "polish"
        }


class SocialCreatorAgent(BaseAgent):
    """社交创作Agent"""

    def __init__(self):
        super().__init__("社交创作Agent", "短内容/社交帖子创作", "social_creator")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        style = input_data.get("style", "casual")
        analysis = input_data.get("analysis", "")

        prompt = f"""你是一位社交媒体内容专家。请创作关于"{topic}"的社交内容。

【意图分析参考】
{analysis}

【创作要求】
提供3个不同版本的文案：
- 版本A：适合朋友圈（亲切、生活化，100-150字）
- 版本B：适合微博（有话题性、易传播，150-200字）
- 版本C：适合LinkedIn（专业、有深度，100-150字）

每个版本都要有吸引力的开头、核心观点、表情符号、3-5个话题标签。
使用Markdown格式，每个版本用##标注。

请直接输出三个版本的文案。"""

        content = await self._call_llm(prompt, max_tokens=2000)

        return {
            "agent": self.name,
            "agent_id": self.agent_id,
            "status": "completed",
            "content": content,
            "versions": 3,
            "style": style,
            "next_agent": "polish"
        }


class PolishAgent(BaseAgent):
    """润色优化Agent"""

    def __init__(self):
        super().__init__("润色优化Agent", "质量把关和风格优化", "polish")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        content = input_data.get("content", "")
        content_type = input_data.get("type", "article")

        if not content or len(content) < 50:
            return {
                "agent": self.name,
                "agent_id": self.agent_id,
                "status": "completed",
                "content": content,
                "detail": "内容过短，跳过润色"
            }

        prompt = f"""你是一位资深编辑。请对以下内容进行专业润色。

【内容类型】{content_type}
【原始内容】
{content[:2500]}

【润色要求】
1. 修正错别字、标点错误、语病
2. 调整句子结构，使阅读更顺畅
3. 统一全文语气、用词风格
4. 添加过渡语句，确保段落衔接自然
5. 删除冗余表述，保留核心信息
6. 优化开头和结尾，增强吸引力

【输出要求】
- 返回完整的优化后内容
- 保持Markdown格式
- 不要添加"优化后的内容："等前缀
- 直接输出文章正文

请直接输出优化后的完整内容。"""

        optimized = await self._call_llm(prompt, max_tokens=3000)

        return {
            "agent": self.name,
            "agent_id": self.agent_id,
            "status": "completed",
            "content": optimized,
            "original_length": len(content),
            "optimized_length": len(optimized),
            "improvements": ["语法检查", "流畅度优化", "风格统一", "逻辑连贯", "表达精炼"],
            "quality_score": 92
        }


# ==================== Agent管理器 ====================

class AgentManager:
    """Agent管理器 - 协调多个Agent工作"""

    def __init__(self):
        self.agents = {
            "intent": IntentAgent(),
            "dispatcher": DispatcherAgent(),
            "article_creator": ArticleCreatorAgent(),
            "tech_creator": TechCreatorAgent(),
            "social_creator": SocialCreatorAgent(),
            "polish": PolishAgent()
        }

    async def create_content_stream(self, request_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        执行完整的内容创作流程，通过SSE流式返回每个Agent的实时状态
        """
        start_time = time.time()
        topic = request_data.get("topic", "")
        content_type = request_data.get("type", "article")
        options = request_data.get("options", {})

        def sse_event(event_type: str, data: Dict[str, Any]) -> str:
            return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

        try:
            # Step 1: 意图识别
            yield sse_event("agent_start", {
                "agent_id": "intent",
                "agent_name": "意图识别Agent",
                "message": f"正在分析主题 '{topic}' 的创作需求..."
            })

            step1_start = time.time()
            intent_result = await self.agents["intent"].execute({
                "topic": topic,
                "type": content_type,
                "options": options
            })
            step1_time = time.time() - step1_start

            yield sse_event("agent_complete", {
                "agent_id": "intent",
                "agent_name": "意图识别Agent",
                "status": "completed",
                "time": f"{step1_time:.1f}s",
                "detail": intent_result.get("analysis", "")[:200] + "..."
            })

            # Step 2: 任务分发
            yield sse_event("agent_start", {
                "agent_id": "dispatcher",
                "agent_name": "任务分发Agent",
                "message": "正在根据意图分析结果分发任务..."
            })

            step2_start = time.time()
            dispatch_result = await self.agents["dispatcher"].execute({
                "topic": intent_result.get("topic", topic),
                "content_type": intent_result.get("content_type", content_type),
                "style": intent_result.get("style", "casual"),
                "analysis": intent_result.get("analysis", "")
            })
            step2_time = time.time() - step2_start

            target_agent_id = dispatch_result.get("target_agent", "article_creator")
            target_name = dispatch_result.get("target_name", "图文创作Agent")

            yield sse_event("agent_complete", {
                "agent_id": "dispatcher",
                "agent_name": "任务分发Agent",
                "status": "completed",
                "time": f"{step2_time:.1f}s",
                "detail": dispatch_result.get("routing_decision", ""),
                "target_agent_id": target_agent_id,
                "target_agent_name": target_name
            })

            # Step 3: 专项创作
            yield sse_event("agent_start", {
                "agent_id": target_agent_id,
                "agent_name": target_name,
                "message": f"正在创作关于 '{topic}' 的内容..."
            })

            step3_start = time.time()
            target_agent = self.agents.get(target_agent_id)
            if not target_agent:
                raise ValueError(f"未知的Agent: {target_agent_id}")

            creator_result = await target_agent.execute({
                "topic": intent_result.get("topic", topic),
                "style": intent_result.get("style", "casual"),
                "length": intent_result.get("length", "medium"),
                "analysis": intent_result.get("analysis", ""),
                "options": options
            })
            step3_time = time.time() - step3_start

            yield sse_event("agent_complete", {
                "agent_id": target_agent_id,
                "agent_name": target_name,
                "status": "completed",
                "time": f"{step3_time:.1f}s",
                "detail": f"生成内容 {creator_result.get('word_count', 0)} 字符",
                "content_preview": creator_result.get("content", "")[:300] + "..."
            })

            # Step 4: 润色优化
            yield sse_event("agent_start", {
                "agent_id": "polish",
                "agent_name": "润色优化Agent",
                "message": "正在对内容进行质量优化..."
            })

            step4_start = time.time()
            polish_result = await self.agents["polish"].execute({
                "content": creator_result.get("content", ""),
                "type": content_type
            })
            step4_time = time.time() - step4_start

            yield sse_event("agent_complete", {
                "agent_id": "polish",
                "agent_name": "润色优化Agent",
                "status": "completed",
                "time": f"{step4_time:.1f}s",
                "detail": f"{polish_result.get('original_length', 0)} → {polish_result.get('optimized_length', 0)} 字符"
            })

            # 最终结果
            total_time = time.time() - start_time
            yield sse_event("complete", {
                "success": True,
                "content": polish_result.get("content", ""),
                "execution_time": f"{total_time:.2f}s",
                "agents": [
                    {"name": "意图识别Agent", "action": "解析需求", "time": f"{step1_time:.1f}s"},
                    {"name": "任务分发Agent", "action": dispatch_result.get("routing_decision", "分发任务"), "time": f"{step2_time:.1f}s"},
                    {"name": target_name, "action": f"生成内容 ({creator_result.get('word_count', 0)}字)", "time": f"{step3_time:.1f}s"},
                    {"name": "润色优化Agent", "action": f"质量优化", "time": f"{step4_time:.1f}s"}
                ]
            })

        except Exception as e:
            yield sse_event("error", {
                "success": False,
                "error": str(e)
            })


# 全局Agent管理器
agent_manager = AgentManager()


# ==================== API端点 ====================

@app.get("/")
async def root():
    return {
        "name": "NextentCreator Agent API",
        "version": "1.0.0",
        "status": "running",
        "agents": list(agent_manager.agents.keys()),
        "llm_available": LLM_AVAILABLE
    }


@app.get("/agents")
async def list_agents():
    agents_info = []
    for agent_id, agent in agent_manager.agents.items():
        agents_info.append({
            "id": agent_id,
            "name": agent.name,
            "description": agent.description,
            "status": agent.status
        })
    return {"agents": agents_info}


@app.post("/create")
async def create(request: CreateRequest):
    """SSE流式接口：实时返回每个Agent的执行状态"""
    request_data = {
        "topic": request.topic,
        "type": request.type,
        "options": request.options
    }

    return StreamingResponse(
        agent_manager.create_content_stream(request_data),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_online": len(agent_manager.agents),
        "llm_available": LLM_AVAILABLE
    }


# ==================== 启动时模型连通性测试 ====================

async def test_llm_connection():
    """启动时测试LLM连通性"""
    print("\n" + "="*50)
    print("🔍 启动时LLM连通性测试")
    print("="*50)

    if not LLM_AVAILABLE:
        print("❌ LLM 客户端未加载，跳过测试")
        print("="*50 + "\n")
        return False

    try:
        client = LLMClient()
        print(f"📡 提供商: {client.provider}")
        print(f"🤖 模型: {client.model}")
        print(f"🔗 Base URL: {client.base_url}")
        print(f"🔑 API Key: {'已配置' if client.api_key else '未配置'}")

        if not client.api_key or client.api_key.startswith("your-"):
            print("⚠️ 警告: API Key 未配置或仍为默认值")
            print("="*50 + "\n")
            return False

        print("\n📤 发送测试请求...")
        test_prompt = "请用一句话介绍你自己。"
        try:
            response = await generate_text(test_prompt, max_tokens=100)
        except Exception as e:
            print(f"❌ LLM API调用异常: {str(e)}")
            print("="*50 + "\n")
            return False

        if response and len(response.strip()) > 0:
            print(f"✅ 测试成功！模型响应:")
            print(f"   {response.strip()[:200]}")
            print("="*50 + "\n")
            return True
        else:
            print("❌ 测试失败: 模型返回空内容")
            print("="*50 + "\n")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        print("="*50 + "\n")
        return False


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🚀 启动 NextentCreator Agent API...")
    print(f"🤖 Agent数量: {len(agent_manager.agents)}")

    # 启动前测试LLM连通性
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    llm_ok = loop.run_until_complete(test_llm_connection())

    if not llm_ok:
        print("⚠️ LLM 未就绪，服务仍可启动但创作功能可能不可用")
        print("   请检查 config/.env 中的 API Key 配置\n")

    print(f"📡 服务地址: http://localhost:8000")
    print("="*50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
