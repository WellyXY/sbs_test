from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
import uuid
from pathlib import Path
import mimetypes

from schemas.folder import FolderCreate, FolderResponse, FileUploadResponse
from utils.file_utils import validate_video_file, get_file_info

router = APIRouter()

# 基礎上傳目錄
UPLOAD_BASE_DIR = "uploads"
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)

@router.get("/", response_model=List[FolderResponse])
async def list_folders():
    """獲取所有資料夾列表"""
    try:
        folders = []
        if os.path.exists(UPLOAD_BASE_DIR):
            for folder_name in os.listdir(UPLOAD_BASE_DIR):
                folder_path = os.path.join(UPLOAD_BASE_DIR, folder_name)
                if os.path.isdir(folder_path):
                    # 統計資料夾內的視頻文件數量
                    video_count = 0
                    total_size = 0
                    for file in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, file)
                        if os.path.isfile(file_path) and validate_video_file(file_path):
                            video_count += 1
                            total_size += os.path.getsize(file_path)
                    
                    folders.append(FolderResponse(
                        name=folder_name,
                        path=folder_path,
                        video_count=video_count,
                        total_size=total_size,
                        created_time=os.path.getctime(folder_path)
                    ))
        
        return sorted(folders, key=lambda x: x.created_time, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取資料夾列表失敗: {str(e)}")

@router.post("/create", response_model=FolderResponse)
async def create_folder(folder_data: FolderCreate):
    """創建新資料夾"""
    try:
        # 驗證資料夾名稱
        if not folder_data.name or len(folder_data.name.strip()) == 0:
            raise HTTPException(status_code=400, detail="資料夾名稱不能為空")
        
        folder_name = folder_data.name.strip()
        # 移除不安全字符
        safe_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_', '.')).strip()
        if not safe_name:
            raise HTTPException(status_code=400, detail="資料夾名稱包含無效字符")
        
        folder_path = os.path.join(UPLOAD_BASE_DIR, safe_name)
        
        # 檢查資料夾是否已存在
        if os.path.exists(folder_path):
            raise HTTPException(status_code=400, detail="資料夾已存在")
        
        # 創建資料夾
        os.makedirs(folder_path, exist_ok=True)
        
        return FolderResponse(
            name=safe_name,
            path=folder_path,
            video_count=0,
            total_size=0,
            created_time=os.path.getctime(folder_path)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"創建資料夾失敗: {str(e)}")

@router.post("/{folder_name}/upload", response_model=List[FileUploadResponse])
async def upload_videos(
    folder_name: str,
    files: List[UploadFile] = File(...)
):
    """上傳視頻文件到指定資料夾"""
    try:
        folder_path = os.path.join(UPLOAD_BASE_DIR, folder_name)
        
        # 檢查資料夾是否存在
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="資料夾不存在")
        
        uploaded_files = []
        
        for file in files:
            # 檢查文件類型
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            if not content_type or not content_type.startswith('video/'):
                continue  # 跳過非視頻文件
            
            # 生成安全的文件名
            file_extension = Path(file.filename).suffix
            safe_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
            file_path = os.path.join(folder_path, safe_filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 驗證文件
            if validate_video_file(file_path):
                file_info = get_file_info(file_path)
                uploaded_files.append(FileUploadResponse(
                    filename=safe_filename,
                    original_name=file.filename,
                    size=file_info["size"],
                    path=file_path
                ))
            else:
                # 如果不是有效視頻文件，刪除它
                os.remove(file_path)
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="沒有成功上傳任何視頻文件")
        
        return uploaded_files
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳文件失敗: {str(e)}")

@router.get("/{folder_name}/files")
async def list_folder_files(folder_name: str):
    """獲取資料夾內的文件列表"""
    try:
        folder_path = os.path.join(UPLOAD_BASE_DIR, folder_name)
        
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="資料夾不存在")
        
        files = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and validate_video_file(file_path):
                file_info = get_file_info(file_path)
                files.append({
                    "filename": filename,
                    "size": file_info["size"],
                    "path": file_path,
                    "created_time": os.path.getctime(file_path)
                })
        
        return sorted(files, key=lambda x: x["created_time"], reverse=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取文件列表失敗: {str(e)}")

@router.delete("/{folder_name}")
async def delete_folder(folder_name: str):
    """刪除資料夾及其所有內容"""
    try:
        folder_path = os.path.join(UPLOAD_BASE_DIR, folder_name)
        
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="資料夾不存在")
        
        shutil.rmtree(folder_path)
        return {"message": f"資料夾 {folder_name} 已成功刪除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除資料夾失敗: {str(e)}")

@router.delete("/{folder_name}/files/{filename}")
async def delete_file(folder_name: str, filename: str):
    """刪除指定文件"""
    try:
        file_path = os.path.join(UPLOAD_BASE_DIR, folder_name, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        os.remove(file_path)
        return {"message": f"文件 {filename} 已成功刪除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除文件失敗: {str(e)}") 