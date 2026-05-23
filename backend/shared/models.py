from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ContentRequest(BaseModel):
    type: str
    topic: str
    options: Optional[Dict[str, Any]] = {}


class AgentStep(BaseModel):
    name: str
    action: str
    time: str


class ContentResult(BaseModel):
    success: bool
    content: str
    agents: List[AgentStep]
    execution_time: float


class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    status: str = "idle"


class AgentFlow(BaseModel):
    flow: List[AgentInfo]
    current_step: int = 0
    selected_type: Optional[str] = None


class TaskStatus(BaseModel):
    task_id: str
    status: str
    created_at: str
    updated_at: Optional[str] = None