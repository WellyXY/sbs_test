"""
Side-by-Side 視頻盲測服務 - Railway部署版本
使用Volume持久化存储
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager
import time
import json
import shutil
import random
from urllib.parse import quote, unquote
from typing import List
import sys
import traceback
import pandas as pd

# --- Railway Volume配置 ---
# 使用环境变量配置存储路径，默认为本地路径（开发环境）
BASE_DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
UPLOAD_DIR = os.environ.get("UPLOAD_PATH", os.path.join(BASE_DATA_DIR, "uploads"))
EXPORT_DIR = os.environ.get("EXPORT_PATH", os.path.join(BASE_DATA_DIR, "exports"))

# 数据文件路径
FOLDERS_FILE = os.path.join(BASE_DATA_DIR, "folders.json")
TASKS_FILE = os.path.join(BASE_DATA_DIR, "tasks.json")
EVALUATIONS_FILE = os.path.join(BASE_DATA_DIR, "evaluations.json")

# 服务器配置
PORT = int(os.environ.get("PORT", 8000))

print(f"--- [Railway] 数据目录: {BASE_DATA_DIR}")
print(f"--- [Railway] 上传目录: {UPLOAD_DIR}")
print(f"--- [Railway] 导出目录: {EXPORT_DIR}")

# 确保所有目录存在
def ensure_directories():
    """确保所有必要的目录存在"""
    directories = [BASE_DATA_DIR, UPLOAD_DIR, EXPORT_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 确保目录存在: {directory}")

ensure_directories()

SUPPORTED_FORMATS = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

def load_folders():
    """從文件載入資料夾數據"""
    try:
        if os.path.exists(FOLDERS_FILE):
            with open(FOLDERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ 載入了 {len(data)} 個資料夾")
                return data
    except Exception as e:
        print(f"❌ 載入資料夾數據失敗: {e}")
    return []

def save_folders(folders_data):
    """保存資料夾數據到文件"""
    try:
        ensure_directories()  # 确保目录存在
        with open(FOLDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(folders_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存了 {len(folders_data)} 個資料夾")
    except Exception as e:
        print(f"❌ 保存資料夾數據失敗: {e}")

def load_tasks():
    """從文件載入任務數據"""
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ 載入了 {len(data)} 個任務")
                return data
    except Exception as e:
        print(f"❌ 載入任務數據失敗: {e}")
    return []

def save_tasks(tasks_data):
    """保存任務數據到文件"""
    try:
        ensure_directories()  # 确保目录存在
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存了 {len(tasks_data)} 個任務")
    except Exception as e:
        print(f"❌ 保存任務數據失敗: {e}")

def load_evaluations():
    """從文件載入評估數據"""
    try:
        if os.path.exists(EVALUATIONS_FILE):
            with open(EVALUATIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ 載入了 {len(data)} 個評估")
                return data
    except Exception as e:
        print(f"❌ 載入評估數據失敗: {e}")
    return []

def save_evaluations(evaluations_data):
    """保存評估數據到文件"""
    try:
        ensure_directories()  # 确保目录存在
        with open(EVALUATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(evaluations_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存了 {len(evaluations_data)} 個評估")
    except Exception as e:
        print(f"❌ 保存評估數據失敗: {e}")

# 初始化数据存储
folders_storage = load_folders()
tasks_storage = load_tasks()
evaluations_storage = load_evaluations()

print(f"✅ 载入 {len(folders_storage)} 个文件夹")
print(f"✅ 载入 {len(tasks_storage)} 个任务") 
print(f"✅ 载入 {len(evaluations_storage)} 个评估")
print(f"🔍 Volume持久化测试: 重新部署时间 {time.time()}")
print(f"🔍 Volume状态检查:")
print(f"  - DATA_DIR ({BASE_DATA_DIR}) exists: {os.path.exists(BASE_DATA_DIR)}")
if os.path.exists(BASE_DATA_DIR):
    print(f"  - DATA_DIR writable: {os.access(BASE_DATA_DIR, os.W_OK)}")
    try:
        usage = shutil.disk_usage(BASE_DATA_DIR)
        print(f"  - Available space: {usage.free / (1024**3):.2f}GB free of {usage.total / (1024**3):.2f}GB total")
    except Exception as e:
        print(f"  - Space check error: {e}")
else:
    print(f"  - DATA_DIR not found - Volume may not be mounted!")

# 临时方案：如果没有数据，创建示例数据
if len(folders_storage) == 0:
    print("⚠️ 检测到数据丢失，创建示例数据...")
    sample_folders = [
        {
            "name": "示例文件夹A",
            "created_time": time.time(),
            "video_count": 0,
            "total_size": 0
        },
        {
            "name": "示例文件夹B", 
            "created_time": time.time(),
            "video_count": 0,
            "total_size": 0
        }
    ]
    folders_storage.extend(sample_folders)
    save_folders(folders_storage)
    print(f"✅ 创建了 {len(sample_folders)} 个示例文件夹")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    print("🚀 应用程序启动中...")
    ensure_directories()
    
    # 为uploads目录提供静态文件服务
    if os.path.exists(UPLOAD_DIR):
        app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
        print(f"✅ 挂载上传目录: {UPLOAD_DIR}")
    
    yield
    
    print("🔄 应用程序正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title="Side-by-Side Video Testing Service",
    description="視頻對比盲測服務 - Railway版本",
    version="2.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "data_dir": BASE_DATA_DIR,
        "upload_dir": UPLOAD_DIR,
        "export_dir": EXPORT_DIR,
        "directories_exist": {
            "data": os.path.exists(BASE_DATA_DIR),
            "uploads": os.path.exists(UPLOAD_DIR),
            "exports": os.path.exists(EXPORT_DIR)
        }
    }

@app.get("/api/folders")
async def get_folders():
    """獲取所有資料夾"""
    try:
        return {
            "success": True,
            "data": folders_storage,
            "count": len(folders_storage)
        }
    except Exception as e:
        print(f"❌ 獲取資料夾失敗: {e}")
        return {"success": False, "error": f"獲取資料夾失敗: {str(e)}"}

@app.post("/api/folders")
async def create_folder(data: dict):
    """創建新資料夾"""
    try:
        folder_name = data.get("name", "").strip()
        if not folder_name:
            raise HTTPException(status_code=400, detail="資料夾名稱不能為空")
        
        # 檢查是否已存在
        if any(f["name"] == folder_name for f in folders_storage):
            raise HTTPException(status_code=400, detail="資料夾名稱已存在")
        
        # 創建資料夾記錄
        new_folder = {
            "name": folder_name,
            "created_time": time.time(),
            "video_count": 0,
            "total_size": 0
        }
        
        folders_storage.append(new_folder)
        save_folders(folders_storage)
        
        # 創建物理目錄
        folder_path = os.path.join(UPLOAD_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        return {
            "success": True,
            "data": new_folder,
            "message": f"成功創建資料夾 '{folder_name}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 創建資料夾錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"創建資料夾失敗: {str(e)}")

@app.get("/api/folders/{folder_name}/files")
async def get_folder_files(folder_name: str):
    """獲取資料夾內的文件列表"""
    try:
        folder_path = os.path.join(UPLOAD_DIR, folder_name)
        
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="資料夾不存在")
        
        files = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                # 获取文件创建时间
                created_time = os.path.getctime(file_path)
                files.append({
                    "filename": filename,  # 匹配前端接口
                    "size": os.path.getsize(file_path),
                    "path": f"/uploads/{folder_name}/{quote(filename)}",  # 匹配前端接口
                    "created_time": created_time  # 添加创建时间
                })
        
        return {
            "success": True,
            "data": {
                "folder_name": folder_name,
                "files": files,
                "count": len(files)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 獲取文件列表錯誤: {e}")
        print(f"❌ 錯誤詳情: {traceback.format_exc()}")
        return {"success": False, "error": f"獲取文件列表失敗: {str(e)}"}

@app.post("/api/folders/{folder_name}/upload")
async def upload_files(folder_name: str, files: list[UploadFile] = File(...)):
    """上傳文件到指定資料夾"""
    print(f"🔧 DEBUG: Upload request for folder: '{folder_name}'")
    
    # 檢查資料夾是否存在
    folder = next((f for f in folders_storage if f["name"] == folder_name), None)
    if not folder:
        print(f"❌ DEBUG: Folder '{folder_name}' not found in storage")
        raise HTTPException(status_code=404, detail=f"資料夾 '{folder_name}' 不存在")
    
    try:
        # 創建資料夾物理目錄
        folder_path = os.path.join(UPLOAD_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        uploaded_count = 0
        total_size = 0
        uploaded_files = []
        
        # 保存每個文件
        for file in files:
            if file.filename:
                file_path = os.path.join(folder_path, file.filename)
                
                # 讀取文件內容並保存
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
                
                uploaded_count += 1
                file_size = len(contents)
                total_size += file_size
                
                uploaded_files.append({
                    "filename": file.filename,
                    "size": file_size,
                    "url": f"/uploads/{folder_name}/{quote(file.filename)}"
                })
                
                print(f"✅ 上傳文件: {file.filename} ({file_size} bytes)")
        
        # 更新資料夾統計並保存
        folder["video_count"] += uploaded_count
        folder["total_size"] += total_size
        save_folders(folders_storage)  # 持久化保存
        
        return {
            "success": True,
            "data": {
                "uploaded_files": uploaded_count,
                "folder_name": folder_name,
                "total_size": total_size,
                "files": uploaded_files
            },
            "message": f"成功上傳 {uploaded_count} 個文件到資料夾 '{folder_name}'"
        }
    except Exception as e:
        print(f"❌ 上傳錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")

@app.delete("/api/folders/{folder_name}")
async def delete_folder(folder_name: str):
    """刪除資料夾"""
    try:
        # 檢查資料夾是否存在
        folder = next((f for f in folders_storage if f["name"] == folder_name), None)
        if not folder:
            raise HTTPException(status_code=404, detail=f"資料夾 '{folder_name}' 不存在")
        
        # 刪除物理目錄
        folder_path = os.path.join(UPLOAD_DIR, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"✅ 刪除物理目錄: {folder_path}")
        
        # 從存儲中移除資料夾記錄
        folders_storage.remove(folder)
        save_folders(folders_storage)
        
        return {
            "success": True,
            "message": f"成功刪除資料夾 '{folder_name}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 刪除資料夾錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"刪除資料夾失敗: {str(e)}")

# ============ 任务相关API ============

@app.get("/api/tasks")
async def get_tasks():
    """获取所有任务列表"""
    try:
        return {
            "success": True,
            "data": tasks_storage,
            "count": len(tasks_storage)
        }
    except Exception as e:
        print(f"❌ 获取任务列表错误: {e}")
        return {"success": False, "error": f"获取任务列表失败: {str(e)}"}

@app.post("/api/tasks")
async def create_task(data: dict):
    """创建新任务"""
    try:
        task_name = data.get("name", "").strip()
        folder_a = data.get("folder_a", "").strip() 
        folder_b = data.get("folder_b", "").strip()
        is_blind = data.get("is_blind", True)
        description = data.get("description", "").strip()
        
        # 验证输入
        if not task_name:
            return {"success": False, "error": "任務名稱不能為空"}
        
        if not folder_a or not folder_b:
            return {"success": False, "error": "請選擇兩個資料夾"}
        
        if folder_a == folder_b:
            return {"success": False, "error": "請選擇兩個不同的資料夾"}
        
        # 检查文件夹是否存在
        folder_a_obj = next((f for f in folders_storage if f["name"] == folder_a), None)
        folder_b_obj = next((f for f in folders_storage if f["name"] == folder_b), None)
        
        if not folder_a_obj:
            return {"success": False, "error": f"資料夾 '{folder_a}' 不存在"}
        
        if not folder_b_obj:
            return {"success": False, "error": f"資料夾 '{folder_b}' 不存在"}
        
        # 计算视频对数量
        video_pairs_count = min(folder_a_obj["video_count"], folder_b_obj["video_count"])
        
        # 创建任务对象
        new_task = {
            "id": f"task_{len(tasks_storage) + 1}_{int(time.time())}",
            "name": task_name,
            "description": description,
            "folder_a": folder_a,
            "folder_b": folder_b,
            "is_blind": is_blind,
            "video_pairs_count": video_pairs_count,
            "status": "active",
            "created_time": int(time.time()),
            "total_evaluations": 0,
            "completed_evaluations": 0
        }
        
        tasks_storage.append(new_task)
        save_tasks(tasks_storage)  # 持久化保存
        
        print(f"✅ 创建任务: {task_name}")
        
        return {
            "success": True,
            "data": new_task,
            "message": f"任務 '{task_name}' 創建成功"
        }
        
    except Exception as e:
        print(f"❌ 创建任务错误: {e}")
        print(f"❌ 错误详情: {traceback.format_exc()}")
        return {"success": False, "error": f"创建任务失败: {str(e)}"}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """获取单个任务详情，包含动态生成的视频对"""
    try:
        task = next((t for t in tasks_storage if t["id"] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 生成视频对
        video_pairs = generate_video_pairs(task)
        
        # 返回包含视频对的任务数据
        task_with_pairs = task.copy()
        task_with_pairs["video_pairs"] = video_pairs
        
        print(f"✅ 任务 {task_id} 生成了 {len(video_pairs)} 个视频对")
        
        return {
            "success": True,
            "data": task_with_pairs
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取任务错误: {e}")
        print(f"❌ 错误详情: {traceback.format_exc()}")
        return {"success": False, "error": f"获取任务失败: {str(e)}"}

def generate_video_pairs(task):
    """为任务生成视频对"""
    try:
        folder_a_name = task["folder_a"]
        folder_b_name = task["folder_b"]
        
        print(f"🔧 生成视频对: {folder_a_name} vs {folder_b_name}")
        
        # 获取两个文件夹的文件列表
        folder_a_path = os.path.join(UPLOAD_DIR, folder_a_name)
        folder_b_path = os.path.join(UPLOAD_DIR, folder_b_name)
        
        if not os.path.exists(folder_a_path) or not os.path.exists(folder_b_path):
            print(f"❌ 文件夹不存在: {folder_a_path} 或 {folder_b_path}")
            return []
        
        # 获取视频文件
        files_a = [f for f in os.listdir(folder_a_path) 
                  if os.path.isfile(os.path.join(folder_a_path, f)) and 
                  any(f.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm'])]
        
        files_b = [f for f in os.listdir(folder_b_path) 
                  if os.path.isfile(os.path.join(folder_b_path, f)) and 
                  any(f.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm'])]
        
        print(f"🔧 文件夹A有 {len(files_a)} 个视频: {files_a}")
        print(f"🔧 文件夹B有 {len(files_b)} 个视频: {files_b}")
        
        video_pairs = []
        
        # 简单匹配：按索引配对
        max_pairs = min(len(files_a), len(files_b))
        
        for i in range(max_pairs):
            video_a = files_a[i]
            video_b = files_b[i]
            
            pair_id = f"pair_{task['id']}_{i}"
            
            video_pair = {
                "id": pair_id,
                "task_id": task["id"],
                "video_a_path": f"/uploads/{folder_a_name}/{quote(video_a)}",
                "video_b_path": f"/uploads/{folder_b_name}/{quote(video_b)}",
                "video_a_name": video_a,
                "video_b_name": video_b,
                "is_evaluated": False
            }
            
            video_pairs.append(video_pair)
            print(f"✅ 创建视频对 {i+1}: {video_a} vs {video_b}")
        
        print(f"✅ 总共生成了 {len(video_pairs)} 个视频对")
        return video_pairs
        
    except Exception as e:
        print(f"❌ 生成视频对错误: {e}")
        print(f"❌ 错误详情: {traceback.format_exc()}")
        return []

@app.post("/api/evaluations")
async def create_evaluation(data: dict):
    """创建评估结果"""
    try:
        video_pair_id = data.get("video_pair_id", "")
        choice = data.get("choice", "")
        is_blind = data.get("is_blind", True)
        
        print(f"🔧 创建评估: video_pair_id={video_pair_id}, choice={choice}")
        
        if not video_pair_id or not choice:
            return {"success": False, "error": "缺少必要参数"}
        
        # 创建评估对象
        evaluation = {
            "id": f"eval_{len(evaluations_storage) + 1}_{int(time.time())}",
            "video_pair_id": video_pair_id,
            "choice": choice,
            "is_blind": is_blind,
            "created_time": int(time.time())
        }
        
        evaluations_storage.append(evaluation)
        save_evaluations(evaluations_storage)
        
        print(f"✅ 评估已保存: {evaluation['id']}")
        
        return {
            "success": True,
            "data": evaluation,
            "message": "评估提交成功"
        }
        
    except Exception as e:
        print(f"❌ 创建评估错误: {e}")
        print(f"❌ 错误详情: {traceback.format_exc()}")
        return {"success": False, "error": f"创建评估失败: {str(e)}"}

@app.get("/api/evaluations")
async def get_evaluations():
    """获取所有评估结果"""
    try:
        return {
            "success": True,
            "data": evaluations_storage,
            "count": len(evaluations_storage)
        }
    except Exception as e:
        print(f"❌ 获取评估错误: {e}")
        return {"success": False, "error": f"获取评估失败: {str(e)}"}

# 辅助函数：同步获取任务视频对数据
def get_task_video_pairs_sync(task_id: str):
    """同步获取任务的视频对数据，用于统计分析"""
    task = next((t for t in tasks_storage if t["id"] == task_id), None)
    if not task:
        return []
    
    # 如果任务已经有视频对数据，直接返回
    if "video_pairs" in task:
        return task["video_pairs"]
    
    # 否则动态生成（但这种情况下不会有随机化信息）
    try:
        # 暂时返回空列表，让统计功能在没有随机化信息时回退到简单统计
        return []
        
    except Exception as e:
        print(f"❌ 获取任务视频对错误: {e}")
        return []

# Statistics API端点
@app.get("/api/statistics/{task_id}")
async def get_task_statistics(task_id: str):
    """获取任务统计数据"""
    # 检查任务是否存在
    task = next((t for t in tasks_storage if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    
    # 获取该任务的评估数据和视频对映射
    # 修复：video_pair_id格式是 "pair_task_1_1756203256_0"，需要包含task_id
    task_evaluations = [e for e in evaluations_storage if task_id in e["video_pair_id"]]
    
    # 获取任务的视频对数据以了解随机化情况
    task_video_pairs = []
    try:
        task_video_pairs = get_task_video_pairs_sync(task_id)
    except:
        task_video_pairs = []
    
    # 建立视频对ID到随机化信息的映射
    pair_mapping = {}
    has_randomization_info = False
    
    for pair in task_video_pairs:
        if "is_swapped" in pair and "left_folder" in pair:
            has_randomization_info = True
            pair_mapping[pair["id"]] = {
                "is_swapped": pair.get("is_swapped", False),
                "left_folder": pair.get("left_folder", task["folder_a"]),
                "right_folder": pair.get("right_folder", task["folder_b"])
            }
    
    # 计算偏好统计
    total_evaluations = len(task_evaluations)
    preference_folder_a = 0  # 实际偏好文件夹A的数量
    preference_folder_b = 0  # 实际偏好文件夹B的数量
    ties = 0
    
    for evaluation in task_evaluations:
        choice = evaluation["choice"]
        pair_id = evaluation["video_pair_id"]
        
        if choice == "tie":
            ties += 1
        elif choice in ["A", "B"]:
            if has_randomization_info and pair_id in pair_mapping:
                # 使用随机化信息计算真实的文件夹偏好
                pair_info = pair_mapping[pair_id]
                
                # 确定实际选择的文件夹
                if choice == "A":  # 用户选择了左侧视频
                    actual_folder = pair_info["left_folder"]
                else:  # choice == "B", 用户选择了右侧视频
                    actual_folder = pair_info["right_folder"]
                
                # 统计到对应的文件夹
                if actual_folder == task["folder_a"]:
                    preference_folder_a += 1
                elif actual_folder == task["folder_b"]:
                    preference_folder_b += 1
            else:
                # 回退到传统统计（假设A固定在左，B固定在右）
                if choice == "A":
                    preference_folder_a += 1
                elif choice == "B":
                    preference_folder_b += 1
    
    # 计算百分比
    preference_a_percent = (preference_folder_a / total_evaluations * 100) if total_evaluations > 0 else 0
    preference_b_percent = (preference_folder_b / total_evaluations * 100) if total_evaluations > 0 else 0
    ties_percent = (ties / total_evaluations * 100) if total_evaluations > 0 else 0
    
    # 计算完成率（假设每个视频对需要1次评估）
    completion_rate = (total_evaluations / task["video_pairs_count"] * 100) if task["video_pairs_count"] > 0 else 0
    
    statistics = {
        "task_id": task_id,
        "task_name": task["name"],
        "total_evaluations": total_evaluations,
        "video_pairs_count": task["video_pairs_count"],
        "completion_rate": round(completion_rate, 1),
        "preferences": {
            "a_better": preference_folder_a,
            "b_better": preference_folder_b,
            "tie": ties,
            "a_better_percent": round(preference_a_percent, 1),
            "b_better_percent": round(preference_b_percent, 1),
            "tie_percent": round(ties_percent, 1)
        },
        "folder_names": {
            "folder_a": task["folder_a"],
            "folder_b": task["folder_b"]
        }
    }
    
    return {"success": True, "data": statistics, "message": "Task statistics retrieved successfully"}

@app.get("/api/statistics/")
async def get_all_statistics():
    """获取所有任务的统计概览"""
    all_stats = []
    
    for task in tasks_storage:
        # 修复：video_pair_id格式是 "pair_task_1_1756203256_0"，需要包含task_id
        task_evaluations = [e for e in evaluations_storage if task["id"] in e["video_pair_id"]]
        total_evaluations = len(task_evaluations)
        completion_rate = (total_evaluations / task["video_pairs_count"] * 100) if task["video_pairs_count"] > 0 else 0
        
        all_stats.append({
            "task_id": task["id"],
            "task_name": task["name"],
            "total_evaluations": total_evaluations,
            "video_pairs_count": task["video_pairs_count"],
            "completion_rate": round(completion_rate, 1),
            "status": task["status"]
        })
    
    return {"success": True, "data": all_stats, "message": "All task statistics retrieved successfully"}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务及其相关的评估数据"""
    try:
        # 检查任务是否存在
        task_index = None
        for i, task in enumerate(tasks_storage):
            if task["id"] == task_id:
                task_index = i
                break
        
        if task_index is None:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
        
        # 获取任务信息用于日志
        task = tasks_storage[task_index]
        print(f"🔧 删除任务: {task_id} (名称: {task['name']})")
        
        # 删除任务
        deleted_task = tasks_storage.pop(task_index)
        
        # 删除相关的评估数据
        deleted_evaluations = []
        evaluations_to_keep = []
        
        for evaluation in evaluations_storage:
            if task_id in evaluation["video_pair_id"]:
                deleted_evaluations.append(evaluation)
            else:
                evaluations_to_keep.append(evaluation)
        
        # 更新评估存储
        evaluations_storage[:] = evaluations_to_keep
        
        # 保存更新后的数据
        save_tasks(tasks_storage)
        save_evaluations(evaluations_storage)
        
        print(f"✅ 成功删除任务 {task_id}")
        print(f"✅ 删除了 {len(deleted_evaluations)} 个相关评估")
        
        return {
            "success": True, 
            "message": f"Task '{deleted_task['name']}' deleted successfully",
            "deleted_evaluations": len(deleted_evaluations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 删除任务错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")

@app.get("/api/tasks/{task_id}/detailed-results")
async def get_task_detailed_results(task_id: str):
    """获取任务的详细评估结果，用于回顾功能"""
    # 检查任务是否存在
    task = next((t for t in tasks_storage if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    
    try:
        # 直接从任务数据获取视频对信息，避免循环调用
        video_pairs = task.get("video_pairs", [])
        
        # 如果任务中没有video_pairs，尝试动态生成
        if not video_pairs:
            # 获取文件夹中的视频文件
            folder_a_path = os.path.join(UPLOAD_DIR, task['folder_a'])
            folder_b_path = os.path.join(UPLOAD_DIR, task['folder_b'])
            
            if os.path.exists(folder_a_path) and os.path.exists(folder_b_path):
                video_files_a = [f for f in os.listdir(folder_a_path) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'))]
                video_files_b = [f for f in os.listdir(folder_b_path) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'))]
                
                # 简单匹配逻辑
                for i, video_a in enumerate(video_files_a):
                    if i < len(video_files_b):
                        video_b = video_files_b[i]
                        pair = {
                            "id": f"pair_{task_id}_{i}",
                            "video_a_path": f"/uploads/{task['folder_a']}/{video_a}",
                            "video_b_path": f"/uploads/{task['folder_b']}/{video_b}",
                            "video_a_name": video_a,
                            "video_b_name": video_b,
                            "left_folder": task['folder_a'],
                            "right_folder": task['folder_b'],
                            "is_swapped": False
                        }
                        video_pairs.append(pair)
        
        # 获取该任务的所有评估 - 修复过滤逻辑
        task_evaluations = [e for e in evaluations_storage if task_id in e["video_pair_id"]]
        print(f"🔧 DEBUG: 找到 {len(task_evaluations)} 个评估记录")
        
        # 创建视频对ID到评估的映射
        evaluation_map = {e["video_pair_id"]: e for e in task_evaluations}
        print(f"🔧 DEBUG: 评估映射: {list(evaluation_map.keys())}")
        
        # 建立详细结果列表
        detailed_results = []
        
        for i, pair in enumerate(video_pairs):
            pair_id = pair.get("id", f"pair_{task_id}_{i}")
            evaluation = evaluation_map.get(pair_id)
            
            print(f"🔧 DEBUG: 视频对 {i}: pair_id={pair_id}, evaluation={evaluation}")
            
            # 确定实际的文件夹映射
            left_folder = pair.get("left_folder", task["folder_a"])
            right_folder = pair.get("right_folder", task["folder_b"])
            is_swapped = pair.get("is_swapped", False)
            
            # 确定用户的选择对应的实际文件夹
            actual_chosen_folder = None
            if evaluation and evaluation["choice"] in ["A", "B"]:
                if evaluation["choice"] == "A":
                    actual_chosen_folder = left_folder
                else:  # choice == "B"
                    actual_chosen_folder = right_folder
                print(f"🔧 DEBUG: 用户选择={evaluation['choice']}, 实际文件夹={actual_chosen_folder}")
            
            result_item = {
                "pair_index": i + 1,
                "pair_id": pair_id,
                "video_a_path": pair.get("video_a_path", f"/uploads/{task['folder_a']}/{pair.get('video_a_name', '')}"),
                "video_b_path": pair.get("video_b_path", f"/uploads/{task['folder_b']}/{pair.get('video_b_name', '')}"),
                "video_a_name": pair.get("video_a_name", ""),
                "video_b_name": pair.get("video_b_name", ""),
                "left_folder": left_folder,
                "right_folder": right_folder,
                "is_swapped": is_swapped,
                "user_choice": evaluation["choice"] if evaluation else None,
                "actual_chosen_folder": actual_chosen_folder,
                "evaluation_id": evaluation["id"] if evaluation else None,
                "evaluation_timestamp": evaluation.get("created_time") if evaluation else None,
                "is_evaluated": evaluation is not None
            }
            
            detailed_results.append(result_item)
        
        # 计算总体统计
        evaluated_count = len([r for r in detailed_results if r["is_evaluated"]])
        
        response_data = {
            "task_id": task_id,
            "task_name": task["name"],
            "folder_a": task["folder_a"],
            "folder_b": task["folder_b"],
            "total_pairs": len(video_pairs),
            "evaluated_pairs": evaluated_count,
            "completion_rate": round((evaluated_count / len(video_pairs) * 100) if video_pairs else 0, 1),
            "results": detailed_results
        }
        
        return {"success": True, "data": response_data, "message": "Detailed evaluation results retrieved successfully"}
        
    except Exception as e:
        print(f"❌ 获取详细结果错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get detailed results: {str(e)}")

# 其他API端點可以在这里添加...

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "未找到請求的資源", "status_code": 404}
    )

if __name__ == "__main__":
    print(f"🚀 启动Railway应用程序，端口: {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)