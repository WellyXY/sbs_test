"""
評估管理 API 路由
處理視頻評估結果的創建和查詢操作
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import json
import uuid
import time

router = APIRouter()

# 評估數據文件
EVALUATIONS_DATA_FILE = "evaluations_data.json"

# 評估請求模型
class EvaluationCreate(BaseModel):
    video_pair_id: str
    choice: Optional[str] = None  # "A", "B", "tie", None
    comments: Optional[str] = None
    is_blind: bool = True

# 評估響應模型
class EvaluationResponse(BaseModel):
    id: str
    video_pair_id: str
    choice: Optional[str]
    comments: Optional[str]
    is_blind: bool
    created_at: float

def load_evaluations():
    """載入評估數據"""
    try:
        if os.path.exists(EVALUATIONS_DATA_FILE):
            with open(EVALUATIONS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"載入評估數據失敗: {e}")
    return {}

def save_evaluations(evaluations_db):
    """保存評估數據"""
    try:
        with open(EVALUATIONS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(evaluations_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存評估數據失敗: {e}")

@router.post("/")
async def create_evaluation(evaluation_data: EvaluationCreate):
    """
    提交視頻對的評估結果
    """
    try:
        # 載入評估數據
        evaluations_db = load_evaluations()
        
        # 創建評估記錄
        evaluation_id = str(uuid.uuid4())
        current_time = time.time()
        
        evaluation = {
            "id": evaluation_id,
            "video_pair_id": evaluation_data.video_pair_id,
            "choice": evaluation_data.choice,
            "comments": evaluation_data.comments,
            "is_blind": evaluation_data.is_blind,
            "created_at": current_time
        }
        
        # 保存評估
        evaluations_db[evaluation_id] = evaluation
        save_evaluations(evaluations_db)
        
        return {
            "success": True,
            "data": evaluation,
            "message": "評估結果已提交"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"提交評估失敗: {str(e)}"
        )

@router.get("/task/{task_id}")
async def get_task_evaluations(task_id: str):
    """
    獲取指定任務的所有評估結果
    """
    try:
        evaluations_db = load_evaluations()
        
        # 獲取該任務的所有評估
        task_evaluations = []
        for evaluation in evaluations_db.values():
            if evaluation.get("video_pair_id", "").startswith(task_id):
                task_evaluations.append(evaluation)
        
        return {
            "success": True,
            "data": task_evaluations,
            "message": f"成功獲取 {len(task_evaluations)} 個評估結果"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取評估結果失敗: {str(e)}"
        )

@router.post("/reset/{task_id}")
async def reset_task_evaluations(task_id: str):
    """
    重置指定任務的所有評估結果
    """
    try:
        evaluations_db = load_evaluations()
        
        # 統計要刪除的評估數量
        deleted_count = 0
        keys_to_delete = []
        
        for eval_id, evaluation in evaluations_db.items():
            if evaluation.get("video_pair_id", "").startswith(task_id):
                keys_to_delete.append(eval_id)
                deleted_count += 1
        
        # 刪除評估記錄
        for eval_id in keys_to_delete:
            del evaluations_db[eval_id]
        
        # 保存更新後的數據
        save_evaluations(evaluations_db)
        
        return {
            "success": True,
            "message": f"成功重置任務 {task_id}，刪除了 {deleted_count} 個評估結果"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重置評估結果失敗: {str(e)}"
        ) 