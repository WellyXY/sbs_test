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
    
    # 創建上傳目錄
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    print("✅ 文件目錄初始化完成")
    
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
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# app.mount("/exports", StaticFiles(directory="exports"), name="exports")

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

# 簡單的內存存儲（生產環境應該使用數據庫）
folders_storage = []
tasks_storage = []

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
    
    # 創建資料夾對象並保存到內存
    new_folder = {
        "name": folder_name,
        "path": f"/uploads/{folder_name}",
        "video_count": 0,
        "total_size": 0,
        "created_time": int(time.time()) if 'time' in globals() else 1686123456
    }
    folders_storage.append(new_folder)
    
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
        
        # 模擬返回空文件列表（實際應該掃描文件系統）
        mock_files = [
            {
                "filename": f"video_{i}.mp4",
                "size": 10000000 + i * 1000000,
                "path": f"/uploads/{folder_name}/video_{i}.mp4",
                "created_time": int(time.time()) - i * 3600
            }
            for i in range(folder.get("video_count", 0))
        ]
        
        return {
            "success": True, 
            "data": mock_files, 
            "message": f"資料夾 '{folder_name}' 的文件列表 ({len(mock_files)} 個文件)"
        }
    except Exception as e:
        print(f"❌ DEBUG: 獲取文件列表錯誤: {e}")
        return {"success": False, "error": f"獲取文件列表失敗: {str(e)}"}

@app.post("/api/folders/{folder_name}/upload")
async def upload_files(folder_name: str, files: list = File(...)):
    # 檢查資料夾是否存在
    folder = next((f for f in folders_storage if f["name"] == folder_name), None)
    if not folder:
        raise HTTPException(status_code=404, detail="資料夾不存在")
    
    try:
        # 模擬文件上傳成功（實際應該保存文件）
        uploaded_count = len(files)
        total_size = 0
        
        # 計算總大小
        for file in files:
            if hasattr(file, 'size') and file.size:
                total_size += file.size
        
        # 更新資料夾統計
        folder["video_count"] += uploaded_count
        folder["total_size"] += total_size
        
        return {
            "success": True, 
            "data": {
                "uploaded_files": uploaded_count,
                "folder_name": folder_name,
                "total_size": total_size
            },
            "message": f"成功上傳 {uploaded_count} 個文件到資料夾 '{folder_name}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")

@app.delete("/api/folders/{folder_name}")
async def delete_folder(folder_name: str):
    # 檢查資料夾是否存在
    global folders_storage
    folder = next((f for f in folders_storage if f["name"] == folder_name), None)
    if not folder:
        return {"success": False, "error": "資料夾不存在"}
    
    # 從存儲中移除
    folders_storage = [f for f in folders_storage if f["name"] != folder_name]
    
    return {
        "success": True,
        "message": f"資料夾 '{folder_name}' 已刪除"
    }

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

# Tasks API端點
@app.get("/api/tasks/")
async def get_tasks():
    return {"success": True, "data": tasks_storage, "message": "任務列表"}

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
    
    return {
        "success": True,
        "data": new_task,
        "message": f"任務 '{task_name}' 創建成功"
    }

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