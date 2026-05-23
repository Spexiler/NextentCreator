from enum import Enum


class ContentType(str, Enum):
    ARTICLE = "article"
    TECH = "tech"
    SOCIAL = "social"


CONTENT_TYPE_LABELS = {
    ContentType.ARTICLE: "图文文章",
    ContentType.TECH: "技术文档",
    ContentType.SOCIAL: "社交分享",
}

CONTENT_TYPE_ICONS = {
    ContentType.ARTICLE: "📝",
    ContentType.TECH: "💻",
    ContentType.SOCIAL: "📱",
}

content_type_map = {
    "article": "article_creator",
    "tech": "tech_creator",
    "social": "social_creator",
}


class AgentName(str, Enum):
    INTENT = "intent"
    DISPATCHER = "dispatcher"
    ARTICLE_CREATOR = "article_creator"
    TECH_CREATOR = "tech_creator"
    SOCIAL_CREATOR = "social_creator"
    POLISH = "polish"


AGENT_DISPLAY_NAMES = {
    AgentName.INTENT: "意图识别Agent",
    AgentName.DISPATCHER: "任务分发Agent",
    AgentName.ARTICLE_CREATOR: "图文创作Agent",
    AgentName.TECH_CREATOR: "技术创作Agent",
    AgentName.SOCIAL_CREATOR: "社交创作Agent",
    AgentName.POLISH: "润色优化Agent",
}

AGENT_ICONS = {
    AgentName.INTENT: "🎯",
    AgentName.DISPATCHER: "📡",
    AgentName.ARTICLE_CREATOR: "📝",
    AgentName.TECH_CREATOR: "💻",
    AgentName.SOCIAL_CREATOR: "📱",
    AgentName.POLISH: "✨",
}


class AgentRole(str, Enum):
    ANALYZER = "意图识别"
    ROUTER = "任务分发"
    CREATOR = "专项创作"
    POLISHER = "润色优化"


AGENT_ROLE_MAP = {
    AgentName.INTENT: AgentRole.ANALYZER,
    AgentName.DISPATCHER: AgentRole.ROUTER,
    AgentName.ARTICLE_CREATOR: AgentRole.CREATOR,
    AgentName.TECH_CREATOR: AgentRole.CREATOR,
    AgentName.SOCIAL_CREATOR: AgentRole.CREATOR,
    AgentName.POLISH: AgentRole.POLISHER,
}

AGENT_DESCRIPTIONS = {
    AgentName.INTENT: "解析用户需求，确定内容类型",
    AgentName.DISPATCHER: "分发任务到对应专项Agent",
    AgentName.ARTICLE_CREATOR: "长图文内容创作",
    AgentName.TECH_CREATOR: "技术文档/教程创作",
    AgentName.SOCIAL_CREATOR: "短内容/社交帖子创作",
    AgentName.POLISH: "质量把关和风格优化",
}


class ErrorCode(str, Enum):
    UNKNOWN_TYPE = "UNKNOWN_CONTENT_TYPE"
    MISSING_TOPIC = "MISSING_TOPIC"
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    CREATION_FAILED = "CREATION_FAILED"
    LLM_ERROR = "LLM_API_ERROR"