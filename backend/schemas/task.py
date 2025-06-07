from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """任務狀態枚舉"""
    CREATED = "created"        # 已創建
    IN_PROGRESS = "in_progress"  # 進行中
    COMPLETED = "completed"    # 已完成
    PAUSED = "paused"         # 已暫停

class TaskCreate(BaseModel):
    """創建任務請求模型"""
    name: str
    description: Optional[str] = None
    folder_a: str  # A組資料夾名稱
    folder_b: str  # B組資料夾名稱
    is_blind: bool = True  # 是否為盲測

class VideoPairResponse(BaseModel):
    """視頻對響應模型"""
    id: str
    task_id: str
    video_a_path: str
    video_a_name: str
    video_b_path: str
    video_b_name: str
    is_evaluated: bool = False

class TaskBasicResponse(BaseModel):
    """任務基本響應模型（用於列表）"""
    id: str
    name: str
    description: Optional[str] = None
    folder_a: str
    folder_b: str
    is_blind: bool
    status: TaskStatus
    video_pairs_count: int
    completed_pairs: int
    created_time: float
    updated_time: float

class TaskResponse(BaseModel):
    """任務完整響應模型（用於詳情）"""
    id: str
    name: str
    description: Optional[str] = None
    folder_a: str
    folder_b: str
    is_blind: bool
    status: TaskStatus
    video_pairs_count: int
    completed_pairs: int
    created_time: float
    updated_time: float
    video_pairs: Optional[List[VideoPairResponse]] = []

class TaskListResponse(BaseModel):
    """任務列表響應模型"""
    tasks: List[TaskBasicResponse]
    total: int 