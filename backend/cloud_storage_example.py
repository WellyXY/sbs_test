"""
云存储备选方案示例
如果Railway Volume不能满足需求，可以使用云存储服务
"""

import os
import asyncio
from typing import Optional
import aiohttp
import base64
import json

# ============ AWS S3 解决方案 ============

try:
    import boto3
    from botocore.exceptions import ClientError
    
    class S3Storage:
        def __init__(self):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.environ.get('S3_BUCKET_NAME')
        
        async def upload_file(self, file_content: bytes, key: str) -> str:
            """上传文件到S3"""
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file_content
                )
                return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            except ClientError as e:
                raise Exception(f"S3上传失败: {e}")
        
        async def download_file(self, key: str) -> bytes:
            """从S3下载文件"""
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
                return response['Body'].read()
            except ClientError as e:
                raise Exception(f"S3下载失败: {e}")
        
        async def delete_file(self, key: str) -> bool:
            """从S3删除文件"""
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
                return True
            except ClientError as e:
                print(f"S3删除失败: {e}")
                return False

except ImportError:
    print("boto3未安装，S3存储不可用")
    S3Storage = None

# ============ Google Cloud Storage 解决方案 ============

try:
    from google.cloud import storage
    
    class GCSStorage:
        def __init__(self):
            # 使用环境变量GOOGLE_APPLICATION_CREDENTIALS指向服务账号密钥文件
            self.client = storage.Client()
            self.bucket_name = os.environ.get('GCS_BUCKET_NAME')
            self.bucket = self.client.bucket(self.bucket_name)
        
        async def upload_file(self, file_content: bytes, key: str) -> str:
            """上传文件到GCS"""
            try:
                blob = self.bucket.blob(key)
                blob.upload_from_string(file_content)
                return f"https://storage.googleapis.com/{self.bucket_name}/{key}"
            except Exception as e:
                raise Exception(f"GCS上传失败: {e}")
        
        async def download_file(self, key: str) -> bytes:
            """从GCS下载文件"""
            try:
                blob = self.bucket.blob(key)
                return blob.download_as_bytes()
            except Exception as e:
                raise Exception(f"GCS下载失败: {e}")

except ImportError:
    print("google-cloud-storage未安装，GCS存储不可用")
    GCSStorage = None

# ============ Cloudflare R2 解决方案 ============

class R2Storage:
    def __init__(self):
        self.account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        self.access_key = os.environ.get('CLOUDFLARE_R2_ACCESS_KEY')
        self.secret_key = os.environ.get('CLOUDFLARE_R2_SECRET_KEY')
        self.bucket_name = os.environ.get('CLOUDFLARE_R2_BUCKET')
        
        # R2 兼容 S3 API
        if S3Storage:
            import boto3
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='auto'
            )
    
    async def upload_file(self, file_content: bytes, key: str) -> str:
        """上传文件到Cloudflare R2"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content
            )
            return f"https://{self.bucket_name}.{self.account_id}.r2.cloudflarestorage.com/{key}"
        except Exception as e:
            raise Exception(f"R2上传失败: {e}")

# ============ 数据库存储解决方案 ============

class DatabaseStorage:
    """
    将文件以Base64编码存储在数据库中
    适合小文件，不推荐用于大型视频文件
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def upload_file(self, file_content: bytes, filename: str, folder: str) -> str:
        """将文件编码后存储在数据库"""
        try:
            # 编码文件
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # 存储到数据库（示例，需要根据实际数据库调整）
            query = """
            INSERT INTO files (filename, folder, content, size, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            """
            
            await self.db.execute(query, (
                filename, 
                folder, 
                encoded_content, 
                len(file_content)
            ))
            
            return f"/api/files/{folder}/{filename}"
        except Exception as e:
            raise Exception(f"数据库存储失败: {e}")
    
    async def download_file(self, filename: str, folder: str) -> bytes:
        """从数据库下载文件"""
        try:
            query = "SELECT content FROM files WHERE filename = ? AND folder = ?"
            result = await self.db.fetch_one(query, (filename, folder))
            
            if not result:
                raise Exception("文件不存在")
            
            # 解码文件
            return base64.b64decode(result['content'])
        except Exception as e:
            raise Exception(f"数据库下载失败: {e}")

# ============ 存储工厂类 ============

class StorageFactory:
    """存储方案工厂类"""
    
    @staticmethod
    def create_storage(storage_type: str = None):
        """
        根据环境变量或参数创建存储实例
        
        优先级:
        1. 参数指定的storage_type
        2. 环境变量STORAGE_TYPE
        3. 默认使用本地存储
        """
        
        storage_type = storage_type or os.environ.get('STORAGE_TYPE', 'local')
        
        if storage_type == 's3' and S3Storage:
            return S3Storage()
        elif storage_type == 'gcs' and GCSStorage:
            return GCSStorage()
        elif storage_type == 'r2':
            return R2Storage()
        elif storage_type == 'database':
            # 需要传入数据库连接
            return DatabaseStorage(None)  # 实际使用时需要传入db连接
        else:
            # 默认本地存储（适用于有Volume的情况）
            return LocalStorage()

class LocalStorage:
    """本地存储（适用于Railway Volume）"""
    
    def __init__(self):
        self.upload_dir = os.environ.get('UPLOAD_PATH', './uploads')
        self.export_dir = os.environ.get('EXPORT_PATH', './exports')
    
    async def upload_file(self, file_content: bytes, key: str) -> str:
        """保存文件到本地"""
        file_path = os.path.join(self.upload_dir, key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return f"/uploads/{key}"
    
    async def download_file(self, key: str) -> bytes:
        """从本地读取文件"""
        file_path = os.path.join(self.upload_dir, key)
        with open(file_path, 'rb') as f:
            return f.read()

# ============ 使用示例 ============

async def example_usage():
    """使用示例"""
    
    # 创建存储实例
    storage = StorageFactory.create_storage()
    
    # 上传文件
    with open('example.mp4', 'rb') as f:
        file_content = f.read()
    
    url = await storage.upload_file(file_content, 'videos/example.mp4')
    print(f"文件上传成功: {url}")
    
    # 下载文件
    downloaded_content = await storage.download_file('videos/example.mp4')
    print(f"下载文件大小: {len(downloaded_content)} bytes")

# ============ 环境变量配置示例 ============

"""
在Railway中设置以下环境变量：

# 存储类型选择
STORAGE_TYPE=s3  # 可选: s3, gcs, r2, database, local

# AWS S3 配置
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Google Cloud Storage 配置
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCS_BUCKET_NAME=your-bucket-name

# Cloudflare R2 配置
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY=your_access_key
CLOUDFLARE_R2_SECRET_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET=your-bucket-name
"""

if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_usage())