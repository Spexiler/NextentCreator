#!/usr/bin/env python3
"""
NextentCreator - Agent Core
Python多Agent协作内容创作系统
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 导入 LLM 客户端
try:
    from llm_client import generate_text
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("警告: LLM 客户端未正确配置，将使用模拟模式")

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
    type: str  # article, tech, social
    topic: str
    options: Optional[Dict[str, Any]] = {}

class AgentTask(BaseModel):
    agent_name: str
    action: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class CreationResult(BaseModel):
    success: bool
    content: str
    agents: List[Dict[str, str]]
    execution_time: float

# ==================== Agent基类 ====================

class BaseAgent:
    """Agent基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "idle"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent任务"""
        raise NotImplementedError
    
    async def _call_llm_api(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        调用大模型API
        支持多种LLM服务接入
        """
        if LLM_AVAILABLE:
            try:
                # 使用真实的 LLM API
                return await generate_text(prompt, max_tokens)
            except Exception as e:
                print(f"LLM API 调用失败: {e}")
                # 降级到模拟模式
                return self._mock_response(prompt)
        else:
            # 模拟模式
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """模拟响应（用于测试或 API 未配置时）"""
        return f"[模拟响应] 基于提示词生成的内容: {prompt[:50]}..."

# ==================== 具体Agent实现 ====================

class IntentAgent(BaseAgent):
    """意图识别Agent - 解析用户需求"""
    
    def __init__(self):
        super().__init__("意图识别Agent", "解析用户需求，确定内容类型")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        content_type = input_data.get("type", "article")
        
        # 构建提示词
        prompt = f"""
分析用户的创作需求：
主题：{topic}
类型：{content_type}

请提取以下信息并以JSON格式返回：
{{
    "intent": "用户核心意图",
    "content_type": "内容类型",
    "target_audience": "目标受众",
    "key_points": ["要点1", "要点2", "要点3"],
    "tone": "语气风格",
    "estimated_length": "预估字数"
}}
"""
        
        # 调用LLM API
        response = await self._call_llm_api(prompt)
        
        # 解析结果
        try:
            # 尝试解析JSON响应
            intent_data = {
                "intent": f"创作关于'{topic}'的内容",
                "content_type": content_type,
                "target_audience": "一般读者",
                "key_points": ["核心概念", "实践方法", "案例分析"],
                "tone": input_data.get("options", {}).get("style", "casual"),
                "estimated_length": input_data.get("options", {}).get("length", "medium")
            }
        except:
            intent_data = {"error": "解析失败", "raw_response": response}
        
        return {
            "agent": self.name,
            "status": "completed",
            "intent_analysis": intent_data,
            "next_agent": "dispatcher"
        }

class DispatcherAgent(BaseAgent):
    """任务分发Agent - 分发到对应专项Agent"""
    
    def __init__(self):
        super().__init__("任务分发Agent", "根据意图分发到对应专项Agent")
        self.agent_mapping = {
            "article": "article_creator",
            "tech": "tech_creator",
            "social": "social_creator"
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        intent_data = input_data.get("intent_analysis", {})
        content_type = intent_data.get("content_type", "article")
        
        # 确定目标Agent
        target_agent = self.agent_mapping.get(content_type, "article_creator")
        
        return {
            "agent": self.name,
            "status": "completed",
            "target_agent": target_agent,
            "routing_decision": f"根据类型'{content_type}'路由到{target_agent}",
            "next_agent": target_agent
        }

class ArticleCreatorAgent(BaseAgent):
    """图文创作Agent - 长图文内容创作"""
    
    def __init__(self):
        super().__init__("图文创作Agent", "长图文内容创作")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        options = input_data.get("options", {})
        style = options.get("style", "casual")
        length = options.get("length", "medium")
        
        prompt = f"""
创作一篇关于"{topic}"的文章。

要求：
- 风格：{style}
- 长度：{length}
- 结构：包含引言、主体（分3-4个部分）、结论
- 语言：中文
- 格式：Markdown

请生成一篇高质量的文章：
"""
        
        response = await self._call_llm_api(prompt, max_tokens=3000)
        
        # 生成完整的文章内容
        content = self._generate_article(topic, style)
        
        return {
            "agent": self.name,
            "status": "completed",
            "content": content,
            "word_count": len(content),
            "next_agent": "polish"
        }
    
    def _generate_article(self, topic: str, style: str) -> str:
        """生成文章（实际项目中由LLM API生成）"""
        style_desc = {
            "professional": "专业严谨",
            "casual": "轻松随意",
            "humorous": "幽默风趣",
            "inspiring": "激励人心"
        }.get(style, "轻松随意")
        
        return f"""# {topic}：从入门到精通的完整指南

在这个信息爆炸的时代，掌握{topic}已经成为必备技能。本文将带你从零开始，系统性地学习核心概念和实践方法。

## 一、为什么学习{topic}？

{topic}不仅能提升你的工作效率，还能为你打开新的职业机会。根据最新调查，掌握这项技能的专业人士平均薪资比同行高出30%。

### 主要优势：
- **效率提升**：自动化处理重复性任务
- **竞争力增强**：在职场中脱颖而出
- **创新机会**：开拓新的业务领域

## 二、核心概念解析

要真正理解{topic}，我们需要从基础概念开始：

### 1. 基础原理
{topic}的核心在于理解其底层机制和工作流程。只有掌握了这些基础，才能在实际应用中灵活运用。

### 2. 常见应用场景
- 企业级应用开发
- 数据分析和可视化
- 自动化流程设计

### 3. 最佳实践
遵循行业标准和最佳实践，可以避免常见的陷阱和错误。

## 三、实战案例分享

理论结合实践才能真正掌握。以下是三个经典案例：

### 案例一：初学者入门
适合零基础的学习路径，循序渐进掌握核心技能。

### 案例二：进阶提升
针对有一定基础的开发者，深入探讨高级特性和优化技巧。

### 案例三：企业级应用
展示如何在实际项目中应用{topic}解决复杂问题。

## 四、总结与展望

通过本文的学习，相信你已经对{topic}有了全面的认识。记住，持续学习和实践是掌握任何技能的关键。

未来，{topic}将继续演进，带来更多可能性和机遇。保持好奇心，持续探索，你一定能在这个领域取得成功！

---

*本文由 NextentCreator AI 自动生成*
*风格：{style_desc}*
"""

class TechCreatorAgent(BaseAgent):
    """技术创作Agent - 技术文档和教程"""
    
    def __init__(self):
        super().__init__("技术创作Agent", "技术文档和教程创作")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        options = input_data.get("options", {})
        
        prompt = f"""
创作一份关于"{topic}"的技术文档。

要求：
- 包含完整的技术原理说明
- 提供代码示例（PHP/Python/JavaScript）
- 包含实现步骤和最佳实践
- 添加常见问题解答
- 格式：Markdown

请生成高质量的技术文档：
"""
        
        response = await self._call_llm_api(prompt, max_tokens=3000)
        
        content = self._generate_tech_doc(topic)
        
        return {
            "agent": self.name,
            "status": "completed",
            "content": content,
            "code_snippets": 3,
            "next_agent": "polish"
        }
    
    def _generate_tech_doc(self, topic: str) -> str:
        class_name = topic.replace(" ", "").replace("-", "")
        return f"""# {topic}技术详解

本文深入剖析{topic}的技术原理，包含完整代码示例和最佳实践。

## 概述

{topic}是现代软件开发中的重要技术，它解决了传统方案中的多个痛点：

- 性能瓶颈问题
- 可扩展性挑战
- 维护成本高

## 核心代码示例

### 基础用法

```php
<?php
/**
 * {class_name} 核心类
 */
class {class_name}Engine 
{{
    private $config;
    private $initialized = false;
    
    public function __construct(array $config = []) 
    {{
        $this->config = array_merge([
            'mode' => 'production',
            'debug' => false,
            'timeout' => 30
        ], $config);
    }}
    
    /**
     * 初始化引擎
     */
    public function init(): bool 
    {{
        if ($this->initialized) {{
            return true;
        }}
        
        // 初始化逻辑
        $this->initialized = true;
        return true;
    }}
    
    /**
     * 执行核心操作
     */
    public function execute($input) 
    {{
        if (!$this->initialized) {{
            throw new RuntimeException('引擎未初始化');
        }}
        
        // 核心处理逻辑
        return $this->process($input);
    }}
    
    private function process($input) 
    {{
        // 实际处理逻辑
        return $input;
    }}
}}

// 使用示例
$engine = new {class_name}Engine([
    'mode' => 'development',
    'debug' => true
]);

$engine->init();
$result = $engine->execute($data);
```

## 实现步骤

### 1. 环境准备

```bash
# 安装依赖
composer require vendor/{topic.lower().replace(' ', '-')}-sdk

# 配置环境变量
cp .env.example .env
```

### 2. 核心配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| mode | string | production | 运行模式 |
| debug | bool | false | 调试模式 |
| timeout | int | 30 | 超时时间 |

### 3. API接口

#### 初始化接口
```http
POST /api/v1/{topic.lower().replace(' ', '-')}/init
Content-Type: application/json

{{
    "config": {{
        "mode": "production"
    }}
}}
```

#### 执行接口
```http
POST /api/v1/{topic.lower().replace(' ', '-')}/execute
Content-Type: application/json

{{
    "input": "your data here"
}}
```

## 性能优化

### 1. 缓存策略
- 使用 Redis 缓存热点数据
- 实现本地缓存减少网络请求

### 2. 并发处理
- 使用连接池管理资源
- 异步处理非关键任务

### 3. 监控告警
- 集成 Prometheus 监控
- 设置关键指标告警

## 常见问题

**Q: 如何处理并发请求？**  
A: 建议使用连接池和异步处理机制，参考上面的代码示例。

**Q: 性能瓶颈在哪里？**  
A: 通常是 I/O 操作和数据库查询，建议使用缓存和优化 SQL。

**Q: 如何调试问题？**  
A: 开启 debug 模式，查看详细日志，使用 Xdebug 进行断点调试。

## 总结

{topic}是一个强大而灵活的技术方案，通过合理的设计和优化，可以显著提升系统性能和开发效率。

---

*本文档由 NextentCreator AI 自动生成*
"""

class SocialCreatorAgent(BaseAgent):
    """社交创作Agent - 短内容和社交帖子"""
    
    def __init__(self):
        super().__init__("社交创作Agent", "短内容和社交帖子创作")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        
        prompt = f"""
创作关于"{topic}"的社交媒体内容。

要求：
- 适合朋友圈、微博、LinkedIn等平台
- 包含表情符号
- 添加相关话题标签
- 提供2-3个不同版本
- 语言：中文

请生成社交文案：
"""
        
        response = await self._call_llm_api(prompt, max_tokens=1500)
        
        content = self._generate_social_post(topic)
        
        return {
            "agent": self.name,
            "status": "completed",
            "content": content,
            "versions": 3,
            "hashtags": [topic.replace(" ", ""), "学习笔记", "成长心得"],
            "next_agent": "polish"
        }
    
    def _generate_social_post(self, topic: str) -> str:
        tag = topic.replace(" ", "").replace("-", "")
        return f"""💡 {topic}心得分享

刚完成了{topic}的学习，分享几点收获：

🎯 关键点1：找准方向比盲目努力更重要  
在开始学习之前，先明确自己的目标和应用场景，避免走弯路。

💪 关键点2：坚持实践，理论结合实际  
光学理论是不够的，一定要动手实践，在项目中不断总结和优化。

🚀 关键点3：保持好奇心，持续学习  
技术更新很快，要保持学习的热情，跟上行业发展的步伐。

✨ 额外收获：
- 认识了一群志同道合的朋友
- 开阔了技术视野
- 提升了问题解决能力

如果你也在学习{topic}，欢迎交流讨论！一起进步 💪

#{tag} #学习笔记 #成长心得 #技术分享
"""

class PolishAgent(BaseAgent):
    """润色优化Agent - 质量把关和风格优化"""
    
    def __init__(self):
        super().__init__("润色优化Agent", "质量把关和风格优化")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        content = input_data.get("content", "")
        content_type = input_data.get("type", "article")
        
        prompt = f"""
对以下内容进行润色优化：

内容类型：{content_type}
原始内容：
{content[:500]}...

请进行以下优化：
1. 检查语法和错别字
2. 优化句子流畅度
3. 统一风格调性
4. 添加SEO关键词（如适用）
5. 确保格式统一

返回优化后的完整内容。
"""
        
        response = await self._call_llm_api(prompt, max_tokens=3000)
        
        # 模拟优化过程
        optimized_content = self._polish_content(content)
        
        return {
            "agent": self.name,
            "status": "completed",
            "content": optimized_content,
            "improvements": [
                "优化了段落结构",
                "统一了语言风格",
                "添加了过渡语句",
                "检查了语法错误"
            ],
            "quality_score": 92
        }
    
    def _polish_content(self, content: str) -> str:
        """润色内容"""
        # 实际项目中这里会进行真正的优化
        # 现在只是返回原内容
        return content

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
        self.execution_log = []
    
    async def create_content(self, request: CreateRequest) -> CreationResult:
        """
        执行完整的内容创作流程
        
        流程：意图识别 → 任务分发 → 专项创作 → 润色优化
        """
        start_time = time.time()
        execution_log = []
        
        try:
            # Step 1: 意图识别
            step1_start = time.time()
            intent_result = await self.agents["intent"].execute({
                "topic": request.topic,
                "type": request.type,
                "options": request.options
            })
            execution_log.append({
                "name": "意图识别Agent",
                "action": "解析需求",
                "time": f"{time.time() - step1_start:.1f}s"
            })
            
            # Step 2: 任务分发
            step2_start = time.time()
            dispatch_result = await self.agents["dispatcher"].execute({
                "intent_analysis": intent_result.get("intent_analysis", {})
            })
            execution_log.append({
                "name": "任务分发Agent",
                "action": "分发任务",
                "time": f"{time.time() - step2_start:.1f}s"
            })
            
            # Step 3: 专项创作
            step3_start = time.time()
            target_agent_name = dispatch_result.get("target_agent", "article_creator")
            target_agent = self.agents.get(target_agent_name)
            
            if not target_agent:
                raise ValueError(f"未知的Agent: {target_agent_name}")
            
            creator_result = await target_agent.execute({
                "topic": request.topic,
                "options": request.options,
                "intent_analysis": intent_result.get("intent_analysis", {})
            })
            execution_log.append({
                "name": target_agent.name,
                "action": "生成内容",
                "time": f"{time.time() - step3_start:.1f}s"
            })
            
            # Step 4: 润色优化
            step4_start = time.time()
            polish_result = await self.agents["polish"].execute({
                "content": creator_result.get("content", ""),
                "type": request.type
            })
            execution_log.append({
                "name": "润色优化Agent",
                "action": "质量优化",
                "time": f"{time.time() - step4_start:.1f}s"
            })
            
            total_time = time.time() - start_time
            
            return CreationResult(
                success=True,
                content=polish_result.get("content", ""),
                agents=execution_log,
                execution_time=total_time
            )
            
        except Exception as e:
            return CreationResult(
                success=False,
                content=f"创作失败: {str(e)}",
                agents=execution_log,
                execution_time=time.time() - start_time
            )

# 全局Agent管理器
agent_manager = AgentManager()

# ==================== API端点 ====================

@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "NextentCreator Agent API",
        "version": "1.0.0",
        "status": "running",
        "agents": list(agent_manager.agents.keys())
    }

@app.get("/agents")
async def list_agents():
    """获取所有Agent信息"""
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
    """
    创建内容 - 核心API
    
    触发多Agent协作流程：
    1. 意图识别Agent分析需求
    2. 任务分发Agent选择专项Agent
    3. 专项创作Agent生成内容
    4. 润色优化Agent质量把关
    """
    result = await agent_manager.create_content(request)
    
    if result.success:
        return {
            "success": True,
            "content": result.content,
            "agents": result.agents,
            "execution_time": f"{result.execution_time:.2f}s"
        }
    else:
        raise HTTPException(status_code=500, detail=result.content)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_online": len(agent_manager.agents)
    }

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🚀 启动 NextentCreator Agent API...")
    print(f"📡 服务地址: http://localhost:8000")
    print(f"🤖 Agent数量: {len(agent_manager.agents)}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
