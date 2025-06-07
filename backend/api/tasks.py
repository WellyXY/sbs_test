from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import os
import uuid
import time
from pathlib import Path

from schemas.task import TaskCreate, TaskResponse, TaskBasicResponse, TaskStatus, TaskListResponse, VideoPairResponse
from utils.file_utils import validate_video_file
from utils.video_matcher import match_videos

router = APIRouter()

# 基礎目錄
UPLOAD_BASE_DIR = "uploads"
TASKS_DATA_FILE = "tasks_data.json"

# 模擬數據庫（實際項目中應使用真實數據庫）
tasks_db = {}

def load_tasks():
    """載入任務數據"""
    import json
    try:
        if os.path.exists(TASKS_DATA_FILE):
            with open(TASKS_DATA_FILE, 'r', encoding='utf-8') as f:
                global tasks_db
                tasks_db = json.load(f)
    except Exception as e:
        print(f"載入任務數據失敗: {e}")

def save_tasks():
    """保存任務數據"""
    import json
    try:
        with open(TASKS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存任務數據失敗: {e}")

def get_folder_videos(folder_name: str) -> List[str]:
    """獲取資料夾中的視頻文件"""
    folder_path = os.path.join(UPLOAD_BASE_DIR, folder_name)
    if not os.path.exists(folder_path):
        return []
    
    videos = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and validate_video_file(file_path):
            videos.append(filename)
    
    return sorted(videos)

@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """獲取任務列表"""
    try:
        load_tasks()
        all_tasks = []
        
        for task_id, task_data in tasks_db.items():
            # 只返回基本任務信息，不包含video_pairs
            task_basic = TaskBasicResponse(
                id=task_data["id"],
                name=task_data["name"],
                description=task_data.get("description", ""),
                folder_a=task_data["folder_a"],
                folder_b=task_data["folder_b"],
                is_blind=task_data["is_blind"],
                status=task_data["status"],
                video_pairs_count=task_data["video_pairs_count"],
                completed_pairs=task_data["completed_pairs"],
                created_time=task_data["created_time"],
                updated_time=task_data["updated_time"]
            )
            all_tasks.append(task_basic)
        
        # 分頁
        start = (page - 1) * limit
        end = start + limit
        paginated_tasks = all_tasks[start:end]
        
        return TaskListResponse(
            tasks=paginated_tasks,
            total=len(all_tasks)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取任務列表失敗: {str(e)}")

@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    """創建新任務"""
    try:
        # 驗證資料夾是否存在
        folder_a_path = os.path.join(UPLOAD_BASE_DIR, task_data.folder_a)
        folder_b_path = os.path.join(UPLOAD_BASE_DIR, task_data.folder_b)
        
        if not os.path.exists(folder_a_path):
            raise HTTPException(status_code=404, detail=f"資料夾 {task_data.folder_a} 不存在")
        
        if not os.path.exists(folder_b_path):
            raise HTTPException(status_code=404, detail=f"資料夾 {task_data.folder_b} 不存在")
        
        # 獲取兩個資料夾的視頻文件
        videos_a = get_folder_videos(task_data.folder_a)
        videos_b = get_folder_videos(task_data.folder_b)
        
        if not videos_a:
            raise HTTPException(status_code=400, detail=f"資料夾 {task_data.folder_a} 中沒有視頻文件")
        
        if not videos_b:
            raise HTTPException(status_code=400, detail=f"資料夾 {task_data.folder_b} 中沒有視頻文件")
        
        # 匹配視頻對
        matched_pairs = match_videos(videos_a, videos_b)
        
        if not matched_pairs:
            raise HTTPException(status_code=400, detail="無法匹配到任何視頻對，請檢查文件名稱")
        
        # 創建任務
        task_id = str(uuid.uuid4())
        current_time = time.time()
        
        task = TaskResponse(
            id=task_id,
            name=task_data.name,
            description=task_data.description,
            folder_a=task_data.folder_a,
            folder_b=task_data.folder_b,
            is_blind=task_data.is_blind,
            status=TaskStatus.CREATED,
            video_pairs_count=len(matched_pairs),
            completed_pairs=0,
            created_time=current_time,
            updated_time=current_time
        )
        
        # 保存任務數據
        load_tasks()
        tasks_db[task_id] = task.dict()
        
        # 保存視頻對數據
        tasks_db[task_id]['video_pairs'] = matched_pairs
        
        save_tasks()
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"創建任務失敗: {str(e)}")

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """獲取任務詳情"""
    try:
        load_tasks()
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="任務不存在")
        
        task_data = tasks_db[task_id].copy()
        
        # 包含視頻對信息
        video_pairs = task_data.get('video_pairs', [])
        video_pairs_response = []
        for i, pair in enumerate(video_pairs):
            video_pairs_response.append({
                "id": f"{task_id}_{i}",
                "task_id": task_id,
                "video_a_path": f"uploads/{task_data['folder_a']}/{pair['video_a']}",
                "video_a_name": pair['video_a'],
                "video_b_path": f"uploads/{task_data['folder_b']}/{pair['video_b']}",
                "video_b_name": pair['video_b'],
                "is_evaluated": pair.get('completed', False)
            })
        
        task_data['video_pairs'] = video_pairs_response
        
        return TaskResponse(**task_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取任務失敗: {str(e)}")

@router.get("/{task_id}/video-pairs", response_model=List[VideoPairResponse])
async def get_task_video_pairs(task_id: str):
    """獲取任務的視頻對列表"""
    try:
        load_tasks()
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="任務不存在")
        
        task_data = tasks_db[task_id]
        video_pairs = task_data.get('video_pairs', [])
        
        # 轉換為響應格式
        pairs_response = []
        for pair in video_pairs:
            pairs_response.append(VideoPairResponse(
                id=f"{task_id}_{len(pairs_response)}",
                video_a_path=f"/uploads/{task_data['folder_a']}/{pair['video_a']}",
                video_a_name=pair['video_a'],
                video_b_path=f"/uploads/{task_data['folder_b']}/{pair['video_b']}",
                video_b_name=pair['video_b'],
                is_completed=pair.get('completed', False)
            ))
        
        return pairs_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取視頻對失敗: {str(e)}")

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """刪除任務"""
    try:
        load_tasks()
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="任務不存在")
        
        del tasks_db[task_id]
        save_tasks()
        
        return {"message": f"任務 {task_id} 已成功刪除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除任務失敗: {str(e)}")

# 初始化時載入任務數據
load_tasks() 