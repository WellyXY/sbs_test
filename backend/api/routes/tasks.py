"""
任務管理 API 路由
處理任務的創建、查詢、更新和刪除操作
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from database.database import get_db
from api.models import Task, VideoPair
from api.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, 
    TaskDetailResponse, BaseResponse
)
from utils.video_matcher import VideoMatcher
from utils.file_utils import validate_folder_path

router = APIRouter()


@router.get("/", response_model=TaskListResponse, summary="獲取任務列表")
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    獲取任務列表
    
    - **skip**: 跳過的記錄數 (分頁用)
    - **limit**: 返回的記錄數限制
    """
    try:
        tasks = db.query(Task).offset(skip).limit(limit).all()
        return TaskListResponse(
            success=True,
            data=[TaskResponse.from_orm(task) for task in tasks],
            message=f"成功獲取 {len(tasks)} 個任務"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取任務列表失敗: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskDetailResponse, summary="獲取任務詳情")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    獲取指定任務的詳細信息
    
    - **task_id**: 任務ID
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任務不存在"
            )
        
        return TaskDetailResponse(
            success=True,
            data=TaskResponse.from_orm(task),
            message="成功獲取任務詳情"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取任務詳情失敗: {str(e)}"
        )


@router.post("/", response_model=TaskDetailResponse, summary="創建新任務")
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """
    創建新的視頻盲測任務
    
    - **name**: 任務名稱
    - **folder_a_path**: 文件夾A的路徑 (基線版本)
    - **folder_b_path**: 文件夾B的路徑 (對比版本)
    """
    try:
        # 驗證文件夾路徑
        if not validate_folder_path(task_data.folder_a_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件夾A路徑無效: {task_data.folder_a_path}"
            )
        
        if not validate_folder_path(task_data.folder_b_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件夾B路徑無效: {task_data.folder_b_path}"
            )
        
        # 創建任務
        db_task = Task(
            name=task_data.name,
            folder_a_path=task_data.folder_a_path,
            folder_b_path=task_data.folder_b_path,
            status="pending"
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # 匹配視頻文件
        matcher = VideoMatcher()
        matched_pairs = matcher.match_videos(
            task_data.folder_a_path,
            task_data.folder_b_path
        )
        
        # 創建視頻對
        video_pairs = []
        for pair in matched_pairs:
            video_pair = VideoPair(
                task_id=db_task.id,
                video_a_path=pair['video_a'],
                video_b_path=pair['video_b'],
                video_a_name=os.path.basename(pair['video_a']),
                video_b_name=os.path.basename(pair['video_b'])
            )
            video_pairs.append(video_pair)
        
        db.add_all(video_pairs)
        
        # 更新任務統計
        db_task.total_pairs = len(video_pairs)
        db_task.status = "in_progress" if video_pairs else "completed"
        
        db.commit()
        db.refresh(db_task)
        
        return TaskDetailResponse(
            success=True,
            data=TaskResponse.from_orm(db_task),
            message=f"成功創建任務，匹配到 {len(video_pairs)} 個視頻對"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建任務失敗: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskDetailResponse, summary="更新任務")
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    更新指定任務的信息
    
    - **task_id**: 任務ID
    - **task_update**: 更新的任務數據
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任務不存在"
            )
        
        # 更新字段
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        
        return TaskDetailResponse(
            success=True,
            data=TaskResponse.from_orm(task),
            message="任務更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新任務失敗: {str(e)}"
        )


@router.delete("/{task_id}", response_model=BaseResponse, summary="刪除任務")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    刪除指定的任務及其相關數據
    
    - **task_id**: 任務ID
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任務不存在"
            )
        
        db.delete(task)
        db.commit()
        
        return BaseResponse(
            success=True,
            message="任務刪除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除任務失敗: {str(e)}"
        )


@router.get("/{task_id}/video-pairs", summary="獲取任務的視頻對")
async def get_task_video_pairs(task_id: str, db: Session = Depends(get_db)):
    """
    獲取指定任務的所有視頻對
    
    - **task_id**: 任務ID
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任務不存在"
            )
        
        video_pairs = db.query(VideoPair).filter(VideoPair.task_id == task_id).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": pair.id,
                    "video_a_path": pair.video_a_path,
                    "video_b_path": pair.video_b_path,
                    "video_a_name": pair.video_a_name,
                    "video_b_name": pair.video_b_name,
                    "is_evaluated": pair.is_evaluated,
                    "created_at": pair.created_at
                }
                for pair in video_pairs
            ],
            "message": f"成功獲取 {len(video_pairs)} 個視頻對"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取視頻對失敗: {str(e)}"
        ) 