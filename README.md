# Side-by-Side 視頻盲測服務

## 項目概述

本服務提供一個高效、易用的 Side-by-Side 視頻盲測平台，幫助用戶快速比較兩組視頻輸出效果，特別適用於視頻編解碼優化、AI視頻生成、視頻增強算法等場景。

## 功能特色

- 🎯 **智能匹配**: 自動根據文件名匹配對應視頻
- 🎬 **同步播放**: Side-by-Side 視頻同步播放控制
- 🕶️ **盲測模式**: 隨機左右排序，避免主觀偏見
- 📊 **數據統計**: 完整的評分統計和數據導出
- 🔄 **任務管理**: 靈活的任務創建和管理功能

## 技術架構

### 前端
- **框架**: React 18 + TypeScript
- **樣式**: TailwindCSS
- **視頻播放器**: React Player
- **狀態管理**: Zustand
- **路由**: React Router

### 後端
- **框架**: FastAPI (Python)
- **資料庫**: SQLite (開發) / PostgreSQL (生產)
- **文件處理**: 本地存儲 + 雲端支持
- **API文檔**: 自動生成 Swagger 文檔

## 快速開始

### 環境要求
- Node.js 18+
- Python 3.9+
- Docker (可選)

### 安裝步驟

1. **克隆項目**
```bash
git clone <repository-url>
cd side_by_side
```

2. **前端設置**
```bash
cd frontend
npm install
npm run dev
```

3. **後端設置**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

4. **Docker 部署**
```bash
docker-compose up -d
```

## 使用流程

1. **創建任務**: 選擇兩個包含視頻文件的資料夾
2. **自動匹配**: 系統根據文件名自動匹配視頻對
3. **盲測評估**: 在 Side-by-Side 界面進行視頻比較
4. **評分記錄**: 提交評分和評語
5. **結果匯總**: 查看統計數據並導出結果

## 支持的視頻格式

- MP4
- MOV
- AVI
- MKV
- WebM

## 項目結構

```
side_by_side/
├── frontend/          # React 前端應用
├── backend/           # FastAPI 後端服務
├── database/          # 資料庫遷移和種子文件
├── docker/            # Docker 配置文件
├── docs/              # 項目文檔
└── tests/             # 測試文件
```

## 貢獻指南

歡迎提交 Issue 和 Pull Request 來改進這個項目。

## 許可證

MIT License # 觸發重新部署
