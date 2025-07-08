#!/usr/bin/env python3
"""
超級簡化測試版本 - 排除所有可能的問題源
"""
import os
import sys
import time
from fastapi import FastAPI

# 打印調試信息
print("🔧 DEBUG: 開始導入模塊...")
print(f"🔧 DEBUG: Python 版本: {sys.version}")
print(f"🔧 DEBUG: 工作目錄: {os.getcwd()}")
print(f"🔧 DEBUG: PORT 環境變量: {os.getenv('PORT', 'NOT_SET')}")

# 創建最簡單的 FastAPI 應用
app = FastAPI(title="Railway 測試應用", version="0.0.1")

print("🔧 DEBUG: FastAPI 應用創建完成")

@app.get("/")
def root():
    """最簡單的根路徑"""
    return {"message": "Hello Railway!", "status": "ok"}

@app.get("/health")
def health():
    """最簡單的健康檢查"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/debug")
def debug():
    """調試信息"""
    return {
        "python_version": sys.version,
        "working_dir": os.getcwd(),
        "port": os.getenv("PORT", "NOT_SET"),
        "environment": dict(os.environ),
        "status": "debug_ok"
    }

# 啟動時調試信息
print("🔧 DEBUG: 應用路由註冊完成")
print("🔧 DEBUG: 準備啟動應用...")

if __name__ == "__main__":
    print("🔧 DEBUG: 直接執行模式")
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🔧 DEBUG: 啟動服務器在端口 {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
else:
    print("🔧 DEBUG: 作為模塊導入") 