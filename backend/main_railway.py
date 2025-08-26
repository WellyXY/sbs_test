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
    """获取单个任务详情"""
    try:
        task = next((t for t in tasks_storage if t["id"] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "success": True,
            "data": task
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取任务错误: {e}")
        return {"success": False, "error": f"获取任务失败: {str(e)}"}

# 其他API端點（评估等）可以在这里添加...

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "未找到請求的資源", "status_code": 404}
    )

if __name__ == "__main__":
    print(f"🚀 启动Railway应用程序，端口: {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)