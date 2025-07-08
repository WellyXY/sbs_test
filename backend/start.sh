#!/bin/bash

# 創建必要的目錄
mkdir -p static uploads exports

# 設置權限
chmod 755 static uploads exports

# 顯示目錄結構
echo "📁 目錄結構："
ls -la

# 啟動應用
echo "�� 啟動 FastAPI 應用..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --log-level debug 