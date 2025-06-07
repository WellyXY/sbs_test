# 🚀 部署指南

## 方案一：GitHub + 免費雲服務 (推薦新手)

### 1. 發佈到 GitHub

```bash
# 初始化 Git 倉庫
git init
git add .
git commit -m "Initial commit: Side-by-Side 視頻盲測服務"

# 在 GitHub 創建新倉庫後
git branch -M main
git remote add origin https://github.com/你的用戶名/side-by-side.git
git push -u origin main
```

### 2. 前端部署 (Vercel)

1. 前往 [vercel.com](https://vercel.com)
2. 用 GitHub 帳號登錄
3. 點擊 "New Project" 並選擇你的倉庫
4. 設置構建配置：
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. 設置環境變數：
   - `REACT_APP_API_URL`: 你的後端 API 地址

### 3. 後端部署 (Railway)

1. 前往 [railway.app](https://railway.app)
2. 用 GitHub 帳號登錄
3. 點擊 "New Project" > "Deploy from GitHub repo"
4. 選擇你的倉庫並設置：
   - Root Directory: `backend`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. 添加環境變數：
   - `DATABASE_URL`: 使用 Railway 的 PostgreSQL 插件

## 方案二：Docker 容器化部署 (推薦正式環境)

### 1. 本地測試

```bash
# 構建並啟動所有服務
docker-compose up --build

# 在瀏覽器訪問 http://localhost:80
```

### 2. 生產環境部署

#### A. 使用 DigitalOcean Droplet

```bash
# 1. 創建 Droplet (Ubuntu 22.04)
# 2. 安裝 Docker 和 Docker Compose
sudo apt update
sudo apt install docker.io docker-compose

# 3. 克隆代碼
git clone https://github.com/你的用戶名/side-by-side.git
cd side-by-side

# 4. 設置環境變數
cp .env.example .env
# 編輯 .env 文件設置生產環境配置

# 5. 啟動服務
docker-compose -f docker-compose.prod.yml up -d
```

#### B. 使用 AWS EC2

1. 創建 EC2 實例 (t3.medium 或以上)
2. 配置安全組開放 80, 443 端口
3. 安裝 Docker 和設置 SSL 證書
4. 部署應用

### 3. 生產環境配置

創建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - REACT_APP_API_URL=https://你的域名/api

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/side_by_side
    volumes:
      - uploads:/app/uploads
      - exports:/app/exports

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=side_by_side
      - POSTGRES_USER=your_user
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  uploads:
  exports:
```

## 方案三：雲平台部署

### 1. Heroku (簡單但有限制)

```bash
# 安裝 Heroku CLI
# 前端部署
cd frontend
heroku create your-app-frontend
git subtree push --prefix frontend heroku main

# 後端部署
cd ../backend
heroku create your-app-backend
heroku addons:create heroku-postgresql:mini
git subtree push --prefix backend heroku main
```

### 2. Google Cloud Platform

1. 使用 Cloud Run 部署容器化應用
2. 使用 Cloud SQL 作為資料庫
3. 使用 Cloud Storage 存儲視頻文件

### 3. AWS

1. 使用 ECS 或 EKS 部署容器
2. 使用 RDS 作為資料庫
3. 使用 S3 存儲視頻文件

## 🔧 環境變數配置

### 前端 (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_UPLOAD_LIMIT=100MB
```

### 後端 (.env)
```
DATABASE_URL=sqlite:///./side_by_side.db
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
UPLOAD_PATH=./uploads
EXPORT_PATH=./exports
```

## 📊 監控與維護

### 1. 日誌監控
- 使用 ELK Stack 或 Grafana + Loki
- 設置錯誤報警

### 2. 性能監控
- 使用 Prometheus + Grafana
- 監控 CPU、記憶體、存儲使用情況

### 3. 備份策略
- 定期備份資料庫
- 備份上傳的視頻文件
- 設置災難恢復計劃

## 🔒 安全考慮

1. **HTTPS**: 使用 Let's Encrypt 免費 SSL 證書
2. **環境變數**: 敏感信息不要提交到 Git
3. **CORS**: 正確配置跨域訪問
4. **文件上傳**: 限制文件類型和大小
5. **認證**: 添加用戶認證系統（如果需要）

## 💡 最佳實踐

1. **CI/CD**: 設置自動化部署流水線
2. **藍綠部署**: 零停機時間部署
3. **負載均衡**: 使用多個實例處理高併發
4. **CDN**: 使用 CloudFlare 或 AWS CloudFront 加速
5. **資料庫優化**: 定期清理和索引優化 