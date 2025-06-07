from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FolderCreate(BaseModel):
    """創建資料夾請求模型"""
    name: str
    description: Optional[str] = None

class FolderResponse(BaseModel):
    """資料夾響應模型"""
    name: str
    path: str
    video_count: int
    total_size: int
    created_time: float
    description: Optional[str] = None

class FileUploadResponse(BaseModel):
    """文件上傳響應模型"""
    filename: str
    original_name: str
    size: int
    path: str

class FolderFileInfo(BaseModel):
    """資料夾文件信息模型"""
    filename: str
    size: int
    path: str
    created_time: float 