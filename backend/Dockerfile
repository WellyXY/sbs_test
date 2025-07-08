# syntax=docker/dockerfile:1

# --- Stage 1: Builder ---
# 這個階段專門用來安裝依賴，以便最大限度地利用緩存
FROM python:3.9-slim as builder

WORKDIR /install

# 僅複製依賴文件
COPY backend/requirements.txt .

# 安裝依賴到一個獨立的目錄
RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt


# --- Stage 2: Runner ---
# 這個階段用來構建最終的運行環境，體積更小，更安全
FROM python:3.9-slim

# 創建一個非 root 用戶來運行應用
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# 從 builder 階段複製已安裝的依賴
COPY --from=builder /install /usr/local

# 複製後端應用代碼
COPY backend/ .

# 創建應用需要的目錄，並設置正確的權限
RUN mkdir -p uploads exports static data && chown -R appuser:appuser .

# 切換到非 root 用戶
USER appuser

# 開放端口
EXPOSE 8000

# 直接在 Dockerfile 中定義健康檢查
# Railway 會自動使用這個指令來檢查服務是否就緒
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1

# 最終的啟動命令
# 使用完整的 main.py，因為之前的測試文件已被移除
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 