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
    print("📖 API 文檔: http://localhost:8000/api/docs")
    print("🎯 前端地址: http://localhost:3000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 