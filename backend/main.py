"""
Side-by-Side 視頻盲測服務 - 主應用程式
提供視頻對比和盲測功能的 FastAPI 服務
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
from urllib.parse import quote

# 持久化存儲配置
DATA_DIR = "data"
FOLDERS_FILE = os.path.join(DATA_DIR, "folders.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
EVALUATIONS_FILE = os.path.join(DATA_DIR, "evaluations.json")

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
        with open(EVALUATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(evaluations_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存了 {len(evaluations_data)} 個評估")
    except Exception as e:
        print(f"❌ 保存評估數據失敗: {e}")

# 修復導入問題，先註釋掉可能有問題的導入
# from database.database import engine, SessionLocal, Base
# from api import folders
# from api.routes import tasks, evaluations, statistics
# from api.models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時：創建數據庫表（暫時註釋）
    # Base.metadata.create_all(bind=engine)
    print("✅ 應用啟動完成")
    
    # 創建上傳目錄和數據目錄
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    print("✅ 文件目錄初始化完成")
    
    # 啟動時載入持久化數據
    global folders_storage, tasks_storage, evaluations_storage
    folders_storage = load_folders()
    tasks_storage = load_tasks()
    evaluations_storage = load_evaluations()

    print(f"🚀 應用啟動 - 載入了 {len(folders_storage)} 個資料夾，{len(tasks_storage)} 個任務，{len(evaluations_storage)} 個評估")
    
    yield
    
    # 關閉時的清理工作
    print("🔄 應用程式正在關閉...")


# 創建 FastAPI 應用實例
app = FastAPI(
    title="Side-by-Side 視頻盲測服務",
    description="專業的視頻比較和盲測平台，支持智能匹配、同步播放和詳細統計分析",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 暫時允許所有域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態文件服務（暫時註釋避免錯誤）
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

# 註冊路由（暫時註釋）
# from api import tasks
# from api.routes import evaluations, statistics
# app.include_router(folders.router, prefix="/api/folders", tags=["資料夾管理"])
# app.include_router(tasks.router, prefix="/api/tasks", tags=["任務管理"])
# app.include_router(evaluations.router, prefix="/api/evaluations", tags=["評估管理"])
# app.include_router(statistics.router, prefix="/api/statistics", tags=["統計分析"])


@app.get("/", summary="根路徑", description="應用程式根路徑，返回歡迎信息")
async def root():
    """根路徑端點"""
    return {
        "message": "歡迎使用 Side-by-Side 視頻盲測服務",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "healthy"
    }

# 健康檢查端點 - 同時提供兩個路徑
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "message": "Video blind testing service is running"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "version": "1.0.0", "message": "Video blind testing service is running"}

# 持久化存儲會在startup時初始化
folders_storage = []
tasks_storage = []
evaluations_storage = []

# 簡單的folders API端點用於測試
@app.get("/api/folders/")
async def get_folders():
    return {"success": True, "data": folders_storage, "message": "資料夾列表"}

@app.post("/api/folders/create")
async def create_folder(data: dict):
    folder_name = data.get("name", "")
    if not folder_name:
        return {"success": False, "error": "資料夾名稱不能為空"}
    
    # 檢查是否已存在
    if any(folder["name"] == folder_name for folder in folders_storage):
        return {"success": False, "error": f"資料夾 '{folder_name}' 已存在"}
    
    # 創建資料夾對象並保存到文件
    new_folder = {
        "name": folder_name,
        "path": f"/uploads/{folder_name}",
        "video_count": 0,
        "total_size": 0,
        "created_time": int(time.time()) if 'time' in globals() else 1686123456
    }
    folders_storage.append(new_folder)
    save_folders(folders_storage)  # 持久化保存
    
    return {
        "success": True, 
        "data": new_folder,
        "message": f"資料夾 '{folder_name}' 創建成功"
    }

@app.get("/api/folders/{folder_name}/files")
async def get_folder_files(folder_name: str):
    try:
        print(f"🔧 DEBUG: 查找資料夾文件，資料夾名稱: '{folder_name}'")
        print(f"🔧 DEBUG: 當前存儲的資料夾: {[f['name'] for f in folders_storage]}")
        
        # 檢查資料夾是否存在
        folder = next((f for f in folders_storage if f["name"] == folder_name), None)
        if not folder:
            print(f"❌ DEBUG: 找不到資料夾 '{folder_name}'")
            return {"success": False, "error": f"資料夾 '{folder_name}' 不存在"}
        
        print(f"✅ DEBUG: 找到資料夾: {folder}")
        
        # 掃描資料夾中的真實文件
        folder_path = f"uploads/{folder_name}"
        files_list = []
        
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    file_stat = os.stat(file_path)
                    files_list.append({
                        "filename": filename,
                        "size": file_stat.st_size,
                        "path": file_path,
                        "created_time": int(file_stat.st_ctime)
                    })
        
        print(f"✅ DEBUG: 掃描到 {len(files_list)} 個文件")
        
        return {
            "success": True, 
            "data": files_list, 
            "message": f"資料夾 '{folder_name}' 的文件列表 ({len(files_list)} 個文件)"
        }
    except Exception as e:
        print(f"❌ DEBUG: 獲取文件列表錯誤: {e}")
        return {"success": False, "error": f"獲取文件列表失敗: {str(e)}"}

@app.post("/api/folders/{folder_name}/upload")
async def upload_files(folder_name: str, files: list[UploadFile] = File(...)):
    # 檢查資料夾是否存在
    folder = next((f for f in folders_storage if f["name"] == folder_name), None)
    if not folder:
        raise HTTPException(status_code=404, detail="資料夾不存在")
    
    try:
        # 創建資料夾物理目錄
        folder_path = f"uploads/{folder_name}"
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
                    "path": file_path
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
    # 檢查資料夾是否存在
    global folders_storage
    folder = next((f for f in folders_storage if f["name"] == folder_name), None)
    if not folder:
        return {"success": False, "error": "資料夾不存在"}
    
    try:
        # 刪除物理文件夾和文件
        folder_path = f"uploads/{folder_name}"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"✅ 刪除物理資料夾: {folder_path}")
        
        # 從存儲中移除並保存
        folders_storage = [f for f in folders_storage if f["name"] != folder_name]
        save_folders(folders_storage)  # 持久化保存
        
        return {
            "success": True,
            "message": f"資料夾 '{folder_name}' 已刪除"
        }
    except Exception as e:
        print(f"❌ 刪除資料夾錯誤: {e}")
        return {"success": False, "error": f"刪除失敗: {str(e)}"}

@app.get("/api/formats", summary="支持的視頻格式", description="獲取系統支持的視頻文件格式列表")
async def get_supported_formats():
    """獲取支持的視頻格式"""
    return {
        "success": True,
        "data": [
            "mp4", "mov", "avi", "mkv", "webm", 
            "flv", "wmv", "m4v", "3gp", "ts"
        ],
        "message": "支持的視頻格式列表"
    }

# 初始化測試數據端點（臨時解決方案）
@app.post("/api/init-test-data")
async def init_test_data():
    """初始化一些測試數據"""
    global folders_storage, tasks_storage
    
    # 添加你之前的真實資料夾和測試資料夾
    test_folders = [
        {
            "name": "0606dmd",
            "path": "/uploads/0606dmd",
            "video_count": 1,
            "total_size": 1905260,
            "created_time": int(time.time())
        },
        {
            "name": "shanghaidmd",
            "path": "/uploads/shanghaidmd",
            "video_count": 1,
            "total_size": 1863688,
            "created_time": int(time.time())
        },
        {
            "name": "test_folder_a",
            "path": "/uploads/test_folder_a",
            "video_count": 3,
            "total_size": 50000000,
            "created_time": int(time.time())
        },
        {
            "name": "test_folder_b", 
            "path": "/uploads/test_folder_b",
            "video_count": 3,
            "total_size": 48000000,
            "created_time": int(time.time())
        }
    ]
    
    # 添加你之前的真實任務和測試任務
    test_tasks = [
        {
            "id": "task_1",
            "name": "dmd compare",
            "description": "",
            "folder_a": "0606dmd",
            "folder_b": "shanghaidmd",
            "is_blind": True,
            "video_pairs_count": 1,
            "status": "active",
            "created_time": int(time.time()),
            "total_evaluations": 0,
            "completed_evaluations": 0
        },
        {
            "id": "task_test_1",
            "name": "測試對比任務",
            "description": "這是一個測試任務",
            "folder_a": "test_folder_a",
            "folder_b": "test_folder_b",
            "is_blind": True,
            "video_pairs_count": 3,
            "status": "active",
            "created_time": int(time.time()),
            "total_evaluations": 0,
            "completed_evaluations": 0
        },
        {
            "id": "task_demo",
            "name": "演示視頻對比（外部鏈接）",
            "description": "使用外部視頻鏈接進行演示",
            "folder_a": "demo_external",
            "folder_b": "demo_external",
            "is_blind": True,
            "video_pairs_count": 1,
            "status": "active",
            "created_time": int(time.time()),
            "total_evaluations": 0,
            "completed_evaluations": 0,
            "use_external_videos": True
        }
    ]
    
    folders_storage.extend(test_folders)
    tasks_storage.extend(test_tasks)
    
    # 保存到文件（雖然會丟失，但可以測試功能）
    save_folders(folders_storage)
    save_tasks(tasks_storage)
    
    return {
        "success": True,
        "message": f"數據初始化完成：{len(test_folders)}個資料夾（包含你之前的0606dmd、shanghaidmd），{len(test_tasks)}個任務（包含dmd compare）",
        "data": {
            "folders": len(folders_storage),
            "tasks": len(tasks_storage)
        }
    }

# Tasks API端點
@app.get("/api/tasks/")
async def get_tasks():
    return {"success": True, "data": tasks_storage, "message": "任務列表"}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """獲取單個任務詳情"""
    task = next((t for t in tasks_storage if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"任務 '{task_id}' 不存在")
    
    # 特殊處理：外部視頻演示任務
    if task_id == "task_demo":
        video_pairs = [
            {
                "id": "task_demo_pair_1",
                "task_id": "task_demo",
                "video_a_path": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "video_b_path": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "video_a_name": "Big Buck Bunny",
                "video_b_name": "Elephants Dream",
                "is_evaluated": False
            }
        ]
        task_with_pairs = {**task, "video_pairs": video_pairs}
        return {"success": True, "data": task_with_pairs, "message": f"任務 '{task['name']}' 詳情（外部視頻）"}
    
    # 獲取實際的文件列表
    folder_a_path = f"uploads/{task['folder_a']}"
    folder_b_path = f"uploads/{task['folder_b']}"
    
    print(f"🔧 DEBUG: 檢查資料夾路徑:")
    print(f"   資料夾A: {folder_a_path} (存在: {os.path.exists(folder_a_path)})")
    print(f"   資料夾B: {folder_b_path} (存在: {os.path.exists(folder_b_path)})")
    print(f"   當前工作目錄: {os.getcwd()}")
    
    video_pairs = []
    
    try:
        # 讀取資料夾A的文件
        files_a = []
        files_b = []
        
        if os.path.exists(folder_a_path):
            all_files_a = os.listdir(folder_a_path)
            files_a = [f for f in all_files_a if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.ts'))]
            print(f"🔧 DEBUG: 資料夾A所有文件: {all_files_a}")
            print(f"🔧 DEBUG: 資料夾A視頻文件: {files_a}")
        else:
            print(f"❌ DEBUG: 資料夾A不存在: {folder_a_path}")
        
        if os.path.exists(folder_b_path):
            all_files_b = os.listdir(folder_b_path)
            files_b = [f for f in all_files_b if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.ts'))]
            print(f"🔧 DEBUG: 資料夾B所有文件: {all_files_b}")
            print(f"🔧 DEBUG: 資料夾B視頻文件: {files_b}")
        else:
            print(f"❌ DEBUG: 資料夾B不存在: {folder_b_path}")
        
        # 生成視頻對 - 按文件名配對或順序配對
        if files_a and files_b:
            for i, (file_a, file_b) in enumerate(zip(files_a, files_b)):
                # URL編碼文件路徑
                encoded_path_a = f"uploads/{task['folder_a']}/{quote(file_a)}"
                encoded_path_b = f"uploads/{task['folder_b']}/{quote(file_b)}"
                
                video_pairs.append({
                    "id": f"{task_id}_pair_{i+1}",
                    "task_id": task_id,
                    "video_a_path": encoded_path_a,
                    "video_b_path": encoded_path_b,
                    "video_a_name": file_a,
                    "video_b_name": file_b,
                    "is_evaluated": False
                })
            
            print(f"✅ DEBUG: 任務 {task_id} 生成了 {len(video_pairs)} 個視頻對")
            for pair in video_pairs:
                print(f"   對 {pair['id']}: {pair['video_a_name']} vs {pair['video_b_name']}")
        else:
            print(f"❌ DEBUG: 沒有找到視頻文件，使用模擬數據")
            raise Exception("沒有找到視頻文件")
            
    except Exception as e:
        print(f"❌ 讀取視頻文件錯誤: {e}")
        # 如果讀取失敗，仍使用模擬數據
        for i in range(task["video_pairs_count"]):
            video_pairs.append({
                "id": f"{task_id}_pair_{i+1}",
                "task_id": task_id,
                "video_a_path": f"uploads/{task['folder_a']}/video_{i+1}.mp4",
                "video_b_path": f"uploads/{task['folder_b']}/video_{i+1}.mp4", 
                "video_a_name": f"video_{i+1}.mp4",
                "video_b_name": f"video_{i+1}.mp4",
                "is_evaluated": False
            })
    
    # 添加視頻對到任務數據
    task_with_pairs = {**task, "video_pairs": video_pairs}
    
    return {"success": True, "data": task_with_pairs, "message": f"任務 '{task['name']}' 詳情"}

@app.post("/api/tasks/")
async def create_task(data: dict):
    task_name = data.get("name", "")
    folder_a = data.get("folder_a", "")
    folder_b = data.get("folder_b", "")
    is_blind = data.get("is_blind", True)
    description = data.get("description", "")
    
    if not task_name:
        return {"success": False, "error": "任務名稱不能為空"}
    
    if not folder_a or not folder_b:
        return {"success": False, "error": "請選擇兩個資料夾"}
    
    if folder_a == folder_b:
        return {"success": False, "error": "請選擇兩個不同的資料夾"}
    
    # 檢查資料夾是否存在
    folder_a_obj = next((f for f in folders_storage if f["name"] == folder_a), None)
    folder_b_obj = next((f for f in folders_storage if f["name"] == folder_b), None)
    
    if not folder_a_obj:
        return {"success": False, "error": f"資料夾 '{folder_a}' 不存在"}
    
    if not folder_b_obj:
        return {"success": False, "error": f"資料夾 '{folder_b}' 不存在"}
    
    # 計算視頻對數量（模擬）
    video_pairs_count = min(folder_a_obj["video_count"], folder_b_obj["video_count"])
    
    # 創建任務對象
    new_task = {
        "id": f"task_{len(tasks_storage) + 1}",
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
    
    return {
        "success": True,
        "data": new_task,
        "message": f"任務 '{task_name}' 創建成功"
    }

# Evaluations API端點
@app.get("/api/evaluations/")
async def get_evaluations():
    """獲取所有評估"""
    return {"success": True, "data": evaluations_storage, "message": "評估列表"}

@app.post("/api/evaluations/")
async def create_evaluation(data: dict):
    """創建新的評估"""
    video_pair_id = data.get("video_pair_id", "")
    choice = data.get("choice", "")
    is_blind = data.get("is_blind", True)
    
    if not video_pair_id:
        return {"success": False, "error": "視頻對ID不能為空"}
    
    if choice not in ["A", "B", "tie"]:
        return {"success": False, "error": "選擇必須是A、B或tie"}
    
    # 創建評估對象
    new_evaluation = {
        "id": f"eval_{len(evaluations_storage) + 1}",
        "video_pair_id": video_pair_id,
        "choice": choice,
        "is_blind": is_blind,
        "created_time": int(time.time()),
        "user_agent": "web_client"
    }
    
    evaluations_storage.append(new_evaluation)
    save_evaluations(evaluations_storage)  # 持久化保存
    
    print(f"✅ DEBUG: 收到評估 - 視頻對: {video_pair_id}, 選擇: {choice}")
    
    return {
        "success": True,
        "data": new_evaluation,
        "message": f"評估提交成功"
    }

@app.get("/api/evaluations/{video_pair_id}")
async def get_evaluation_by_pair(video_pair_id: str):
    """根據視頻對ID獲取評估"""
    evaluation = next((e for e in evaluations_storage if e["video_pair_id"] == video_pair_id), None)
    if not evaluation:
        raise HTTPException(status_code=404, detail=f"未找到視頻對 '{video_pair_id}' 的評估")
    
    return {"success": True, "data": evaluation, "message": "評估詳情"}

# 錯誤處理器
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404 錯誤處理"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "請求的資源不存在",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500 錯誤處理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False, 
            "error": "服務器內部錯誤",
            "status_code": 500
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"服務器內部錯誤: {str(exc)}"}
    )


if __name__ == "__main__":
    print("🚀 正在啟動 Side-by-Side 視頻盲測服務...")
    
    # 從環境變數獲取端口，預設為8000
    try:
        port = int(os.environ.get("PORT", "8000"))
        print(f"🔧 使用端口: {port}")
        print(f"🔧 PORT環境變數: {os.environ.get('PORT', '未設置')}")
    except (ValueError, TypeError) as e:
        print(f"❌ PORT環境變數錯誤: {e}")
        port = 8000
        print(f"🔧 使用預設端口: {port}")
    
    print(f"📖 API 文檔: http://localhost:{port}/api/docs")
    print("🎯 前端地址: http://localhost:3000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # 生產環境關閉reload
        log_level="info"
    ) 