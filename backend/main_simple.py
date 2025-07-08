#!/usr/bin/env python3
"""
簡化版本的 FastAPI 應用 - 用於調試 Railway 部署問題
"""
import os
import time
import json
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# 全局變量
folders_storage = []
tasks_storage = []
evaluations_storage = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """簡化的應用程式生命週期管理"""
    try:
        # 創建必要的目錄
        for directory in ["static", "uploads", "exports", "data"]:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 創建目錄: {directory}")
        
        # 初始化存儲
        global folders_storage, tasks_storage, evaluations_storage
        folders_storage = []
        tasks_storage = []  
        evaluations_storage = []
        
        print("🚀 簡化版應用啟動完成")
        yield
        
    except Exception as e:
        print(f"❌ 啟動錯誤: {e}")
        yield
    finally:
        print("🔄 應用程式正在關閉...")


# 創建 FastAPI 應用實例
app = FastAPI(
    title="Side-by-Side 視頻盲測服務",
    description="專業的視頻比較和盲測平台 - 簡化版本",
    version="1.0.0-simple",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路徑端點"""
    return {
        "message": "歡迎使用 Side-by-Side 視頻盲測服務 - 簡化版本",
        "version": "1.0.0-simple",
        "docs": "/api/docs",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    try:
        current_time = time.time()
        
        # 檢查目錄狀態
        directories_status = {}
        for dir_name in ["static", "uploads", "exports", "data"]:
            directories_status[dir_name] = {
                "exists": os.path.exists(dir_name),
                "writable": os.access(dir_name, os.W_OK) if os.path.exists(dir_name) else False
            }
        
        return {
            "status": "healthy",
            "version": "1.0.0-simple",  
            "message": "Video blind testing service is running - simplified version",
            "timestamp": current_time,
            "directories": directories_status,
            "storage": {
                "folders": len(folders_storage),
                "tasks": len(tasks_storage),
                "evaluations": len(evaluations_storage)
            },
            "port": os.getenv("PORT", "unknown"),
            "environment": {
                "python_version": os.sys.version,
                "working_directory": os.getcwd()
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@app.get("/api/health")
async def api_health_check():
    """API 健康檢查端點"""
    return await health_check()

@app.get("/api/test")
async def test_endpoint():
    """測試端點"""
    return {
        "message": "Test endpoint is working",
        "timestamp": time.time(),
        "status": "success"
    }

@app.get("/api/folders/")
async def get_folders():
    """獲取資料夾列表"""
    return {
        "success": True,
        "data": folders_storage,
        "message": "資料夾列表 - 簡化版本"
    }

@app.post("/api/folders/create")
async def create_folder(data: dict):
    """創建資料夾"""
    folder_name = data.get("name", "")
    if not folder_name:
        return {"success": False, "error": "資料夾名稱不能為空"}
    
    # 檢查是否已存在
    if any(folder["name"] == folder_name for folder in folders_storage):
        return {"success": False, "error": f"資料夾 '{folder_name}' 已存在"}
    
    # 創建資料夾對象
    new_folder = {
        "name": folder_name,
        "path": f"/uploads/{folder_name}",
        "video_count": 0,
        "total_size": 0,
        "created_time": int(time.time())
    }
    
    # 創建物理目錄
    try:
        os.makedirs(f"uploads/{folder_name}", exist_ok=True)
        folders_storage.append(new_folder)
        return {
            "success": True,
            "data": new_folder,
            "message": f"資料夾 '{folder_name}' 創建成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"創建資料夾失敗: {str(e)}"
        }

# 異常處理器
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "未找到請求的資源", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "內部伺服器錯誤", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 