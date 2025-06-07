"""
Pydantic 數據模式定義
用於 API 請求和響應的數據驗證
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任務狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class EvaluationChoice(str, Enum):
    """評估選擇枚舉"""
    A = "A"
    B = "B"
    TIE = "tie"
    NULL = None


# 基礎響應模式
class BaseResponse(BaseModel):
    """基礎響應模式"""
    success: bool = True
    message: Optional[str] = None
    error: Optional[str] = None


# 任務相關模式
class TaskCreate(BaseModel):
    """創建任務請求模式"""
    name: str = Field(..., min_length=1, max_length=255, description="任務名稱")
    folder_a_path: str = Field(..., min_length=1, description="文件夾A路徑")
    folder_b_path: str = Field(..., min_length=1, description="文件夾B路徑")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('任務名稱不能為空')
        return v.strip()


class TaskUpdate(BaseModel):
    """更新任務請求模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[TaskStatus] = None
    folder_a_path: Optional[str] = None
    folder_b_path: Optional[str] = None


class VideoPairResponse(BaseModel):
    """視頻對響應模式"""
    id: str
    task_id: str
    video_a_path: str
    video_b_path: str
    video_a_name: str
    video_b_name: str
    is_evaluated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """任務響應模式"""
    id: str
    name: str
    status: TaskStatus
    folder_a_path: str
    folder_b_path: str
    total_pairs: int
    completed_pairs: int
    created_at: datetime
    updated_at: datetime
    video_pairs: Optional[List[VideoPairResponse]] = []

    class Config:
        from_attributes = True


class TaskListResponse(BaseResponse):
    """任務列表響應模式"""
    data: List[TaskResponse]


class TaskDetailResponse(BaseResponse):
    """任務詳情響應模式"""
    data: TaskResponse


# 評估相關模式
class EvaluationCreate(BaseModel):
    """創建評估請求模式"""
    video_pair_id: str = Field(..., description="視頻對ID")
    choice: Optional[EvaluationChoice] = Field(None, description="選擇結果")
    score_a: float = Field(0.0, ge=0.0, le=10.0, description="視頻A評分 (0-10)")
    score_b: float = Field(0.0, ge=0.0, le=10.0, description="視頻B評分 (0-10)")
    comments: Optional[str] = Field(None, max_length=1000, description="評語")
    is_blind: bool = Field(True, description="是否為盲測")
    randomized_order: bool = Field(True, description="是否隨機排序")
    user_id: Optional[str] = Field(None, description="用戶ID")


class EvaluationResponse(BaseModel):
    """評估響應模式"""
    id: str
    task_id: str
    video_pair_id: str
    user_id: Optional[str]
    choice: Optional[str]
    score_a: float
    score_b: float
    comments: Optional[str]
    is_blind: bool
    randomized_order: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationCreateResponse(BaseResponse):
    """創建評估響應模式"""
    data: EvaluationResponse


# 文件夾相關模式
class FolderScanRequest(BaseModel):
    """文件夾掃描請求模式"""
    path: str = Field(..., min_length=1, description="文件夾路徑")


class FolderScanResponse(BaseModel):
    """文件夾掃描響應模式"""
    path: str
    name: str
    video_count: int
    video_files: List[str]


class VideoMatchRequest(BaseModel):
    """視頻匹配請求模式"""
    folder_a_path: str = Field(..., description="文件夾A路徑")
    folder_b_path: str = Field(..., description="文件夾B路徑")


class VideoMatchPair(BaseModel):
    """視頻匹配對模式"""
    video_a: str
    video_b: str
    name: str


class VideoMatchResponse(BaseModel):
    """視頻匹配響應模式"""
    matched_pairs: List[VideoMatchPair]
    unmatched_a: List[str]
    unmatched_b: List[str]


class FolderScanApiResponse(BaseResponse):
    """文件夾掃描API響應模式"""
    data: FolderScanResponse


class VideoMatchApiResponse(BaseResponse):
    """視頻匹配API響應模式"""
    data: VideoMatchResponse


# 統計相關模式
class StatisticsResponse(BaseModel):
    """統計響應模式"""
    total_evaluations: int
    preference_a: int
    preference_b: int
    ties: int
    average_score_a: float
    average_score_b: float
    completion_rate: float


class StatisticsApiResponse(BaseResponse):
    """統計API響應模式"""
    data: StatisticsResponse


# 系統相關模式
class HealthResponse(BaseModel):
    """健康檢查響應模式"""
    status: str
    service: str
    version: str


class SupportedFormatsResponse(BaseModel):
    """支持格式響應模式"""
    formats: List[str]


class HealthApiResponse(BaseResponse):
    """健康檢查API響應模式"""
    data: HealthResponse


class SupportedFormatsApiResponse(BaseResponse):
    """支持格式API響應模式"""
    data: List[str] 