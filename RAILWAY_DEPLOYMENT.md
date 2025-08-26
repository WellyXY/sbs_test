# 🚀 Railway 持久化存储部署指南

这个指南将帮助你在Railway上部署应用程序，并确保文件不会在每次更新代码时丢失。

## 🎯 问题解决

**问题**: Railway等云平台每次重新部署时会重建容器，导致本地文件系统的文件丢失。

**解决方案**: 使用Railway Volume功能实现持久化存储。

## 📋 部署步骤

### 1. 准备项目

确保你的项目包含以下文件：
- `railway.toml` - Railway配置文件 ✅
- `backend/main_railway.py` - 支持Volume的应用程序版本 ✅
- `Procfile` - 启动配置 ✅

### 2. 在Railway上部署

1. **连接GitHub仓库**
   - 登录 [railway.app](https://railway.app)
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择你的项目仓库

2. **设置环境变量**
   
   在Railway项目的Variables面板中添加：
   
   ```bash
   # 基础配置
   PORT=8000
   
   # 持久化存储路径（使用Volume挂载点）
   DATA_DIR=/app/data
   UPLOAD_PATH=/app/data/uploads
   EXPORT_PATH=/app/data/exports
   
   # 可选：数据库URL（如果使用SQLite）
   DATABASE_URL=/app/data/side_by_side.db
   ```

3. **配置Volume**
   
   在Railway项目面板中：
   - 点击 "Variables" 标签页
   - 滚动到底部找到 "Volumes" 部分
   - 点击 "New Volume"
   - 设置：
     - **Volume Name**: `app-data`
     - **Mount Path**: `/app/data`
   - 点击 "Create"

### 3. 验证部署

部署完成后，访问以下端点验证：

```bash
# 健康检查（确认Volume配置正确）
GET https://your-app.railway.app/api/health

# 预期响应
{
  "status": "healthy",
  "data_dir": "/app/data",
  "upload_dir": "/app/data/uploads",
  "export_dir": "/app/data/exports",
  "directories_exist": {
    "data": true,
    "uploads": true,
    "exports": true
  }
}
```

## 📁 存储目录结构

使用Volume后，你的持久化数据将存储在：

```
/app/data/                    # Volume挂载点
├── uploads/                  # 用户上传的文件
│   ├── folder1/
│   ├── folder2/
│   └── ...
├── exports/                  # 导出的文件
├── folders.json             # 文件夹数据
├── tasks.json               # 任务数据
├── evaluations.json         # 评估数据
└── side_by_side.db          # SQLite数据库（如果使用）
```

## 🔧 本地开发配置

为了在本地开发时也能测试Volume配置，可以设置环境变量：

```bash
# 创建 .env 文件
echo "DATA_DIR=./local_data" > backend/.env
echo "UPLOAD_PATH=./local_data/uploads" >> backend/.env
echo "EXPORT_PATH=./local_data/exports" >> backend/.env

# 运行应用
cd backend
python main_railway.py
```

## 🔍 故障排除

### 问题1: Volume没有正确挂载

**症状**: `/api/health` 端点显示 `directories_exist` 为 `false`

**解决方案**:
1. 检查Railway项目中Volume配置是否正确
2. 确认Mount Path为 `/app/data`
3. 重新部署项目

### 问题2: 文件仍然丢失

**可能原因**:
- Volume配置时间晚于应用启动
- 多个实例写入同一Volume

**解决方案**:
1. 删除并重新创建Volume
2. 确保只有一个应用实例
3. 检查应用日志

### 问题3: 权限问题

**症状**: 无法创建文件或目录

**解决方案**:
1. 检查Volume挂载权限
2. 确认应用程序有写入权限

## 💡 最佳实践

1. **定期备份**: 即使使用Volume，也建议定期备份重要数据
2. **监控存储使用**: Railway Volume有存储限制，注意监控使用量
3. **数据迁移**: 如需迁移到其他平台，可以通过API导出所有数据

## 📊 替代方案

如果Railway Volume不能满足需求，可以考虑：

### 方案A: 云存储服务

```python
# 示例：使用AWS S3
import boto3

s3_client = boto3.client('s3')

def upload_to_s3(file_path, bucket, key):
    s3_client.upload_file(file_path, bucket, key)
```

### 方案B: 数据库存储

```python
# 示例：将小文件存储为Base64
import base64

def store_file_in_db(file_content):
    encoded = base64.b64encode(file_content).decode('utf-8')
    # 保存到数据库
```

## 🎉 完成！

按照以上步骤，你的Railway应用程序现在应该能够：
- ✅ 持久化保存上传的文件
- ✅ 在代码更新时保留数据
- ✅ 正确处理文件存储和访问

如有问题，请检查Railway项目日志或参考故障排除部分。