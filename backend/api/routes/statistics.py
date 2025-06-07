"""
統計分析 API 路由
處理視頻評估結果的統計分析
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os
import json

router = APIRouter()

# 數據文件
EVALUATIONS_DATA_FILE = "evaluations_data.json"
TASKS_DATA_FILE = "tasks_data.json"

def load_evaluations():
    """載入評估數據"""
    try:
        if os.path.exists(EVALUATIONS_DATA_FILE):
            with open(EVALUATIONS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"載入評估數據失敗: {e}")
        return {}

def load_tasks():
    """載入任務數據"""
    try:
        if os.path.exists(TASKS_DATA_FILE):
            with open(TASKS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"載入任務數據失敗: {e}")
        return {}

class TaskStatistics(BaseModel):
    """任務統計響應模型"""
    task_id: str
    task_name: str
    folder_a: str
    folder_b: str
    total_pairs: int
    evaluated_pairs: int
    completion_rate: float
    
    # 評估結果統計
    a_wins: int
    b_wins: int
    ties: int
    
    # 百分比
    a_win_percentage: float
    b_win_percentage: float
    tie_percentage: float
    
    # 詳細評估列表
    evaluations: list

@router.get("/{task_id}", response_model=TaskStatistics)
async def get_task_statistics(task_id: str):
    """獲取任務統計信息"""
    try:
        # 載入數據
        tasks_db = load_tasks()
        evaluations_db = load_evaluations()
        
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="任務不存在")
        
        task_data = tasks_db[task_id]
        
        # 獲取該任務的所有評估
        task_evaluations = []
        for eval_id, eval_data in evaluations_db.items():
            if eval_data.get('video_pair_id', '').startswith(task_id):
                task_evaluations.append(eval_data)
        
        # 統計結果
        total_pairs = task_data.get('video_pairs_count', 0)
        evaluated_pairs = len(task_evaluations)
        
        a_wins = sum(1 for e in task_evaluations if e.get('choice') == 'A')
        b_wins = sum(1 for e in task_evaluations if e.get('choice') == 'B')
        ties = sum(1 for e in task_evaluations if e.get('choice') == 'tie')
        
        # 計算百分比
        if evaluated_pairs > 0:
            a_win_percentage = (a_wins / evaluated_pairs) * 100
            b_win_percentage = (b_wins / evaluated_pairs) * 100
            tie_percentage = (ties / evaluated_pairs) * 100
            completion_rate = (evaluated_pairs / total_pairs) * 100
        else:
            a_win_percentage = 0
            b_win_percentage = 0
            tie_percentage = 0
            completion_rate = 0
        
        return TaskStatistics(
            task_id=task_id,
            task_name=task_data.get('name', ''),
            folder_a=task_data.get('folder_a', ''),
            folder_b=task_data.get('folder_b', ''),
            total_pairs=total_pairs,
            evaluated_pairs=evaluated_pairs,
            completion_rate=round(completion_rate, 1),
            a_wins=a_wins,
            b_wins=b_wins,
            ties=ties,
            a_win_percentage=round(a_win_percentage, 1),
            b_win_percentage=round(b_win_percentage, 1),
            tie_percentage=round(tie_percentage, 1),
            evaluations=task_evaluations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取統計信息失敗: {str(e)}")

@router.get("/")
async def get_all_statistics():
    """獲取所有任務的統計概覽"""
    try:
        tasks_db = load_tasks()
        evaluations_db = load_evaluations()
        
        all_stats = []
        for task_id in tasks_db.keys():
            try:
                stats = await get_task_statistics(task_id)
                all_stats.append(stats)
            except:
                continue
        
        return {"statistics": all_stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取統計概覽失敗: {str(e)}") 