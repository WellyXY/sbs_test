"""
文件處理工具
提供文件和文件夾操作的輔助函數
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import mimetypes

# 支持的視頻格式
SUPPORTED_VIDEO_FORMATS = {
    '.mp4', '.mov', '.avi', '.mkv', '.webm', 
    '.flv', '.wmv', '.m4v', '.3gp', '.ts'
}

def validate_folder_path(folder_path: str) -> bool:
    """
    驗證文件夾路徑是否有效
    
    Args:
        folder_path: 文件夾路徑
        
    Returns:
        是否有效
    """
    if not folder_path:
        return False
    
    try:
        path = Path(folder_path)
        return path.exists() and path.is_dir()
    except Exception:
        return False


def get_folder_info(folder_path: str) -> Dict:
    """
    獲取文件夾信息
    
    Args:
        folder_path: 文件夾路徑
        
    Returns:
        文件夾信息字典
    """
    if not validate_folder_path(folder_path):
        return {
            'exists': False,
            'path': folder_path,
            'name': '',
            'size': 0,
            'file_count': 0,
            'video_count': 0
        }
    
    path = Path(folder_path)
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.ts'}
    
    total_size = 0
    file_count = 0
    video_count = 0
    
    try:
        for item in path.rglob('*'):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
                
                if item.suffix.lower() in video_extensions:
                    video_count += 1
    except Exception as e:
        print(f"獲取文件夾信息失敗: {str(e)}")
    
    return {
        'exists': True,
        'path': str(path.absolute()),
        'name': path.name,
        'size': total_size,
        'file_count': file_count,
        'video_count': video_count
    }


def scan_video_files(folder_path: str) -> List[str]:
    """
    掃描文件夾中的視頻文件
    
    Args:
        folder_path: 文件夾路徑
        
    Returns:
        視頻文件路徑列表
    """
    video_files = []
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.ts'}
    
    if not validate_folder_path(folder_path):
        return video_files
    
    try:
        path = Path(folder_path)
        for item in path.rglob('*'):
            if item.is_file() and item.suffix.lower() in video_extensions:
                video_files.append(str(item.absolute()))
        
        # 按文件名排序
        video_files.sort(key=lambda x: Path(x).name.lower())
        
    except Exception as e:
        print(f"掃描視頻文件失敗: {str(e)}")
    
    return video_files


def validate_video_file(file_path: str) -> bool:
    """驗證文件是否為支持的視頻格式"""
    if not os.path.exists(file_path):
        return False
    
    # 檢查文件擴展名
    file_extension = Path(file_path).suffix.lower()
    if file_extension not in SUPPORTED_VIDEO_FORMATS:
        return False
    
    # 檢查MIME類型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and not mime_type.startswith('video/'):
        return False
    
    # 檢查文件大小（避免空文件）
    if os.path.getsize(file_path) == 0:
        return False
    
    return True


def get_file_info(file_path: str) -> dict:
    """獲取文件基本信息"""
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    return {
        "size": stat.st_size,
        "created_time": stat.st_ctime,
        "modified_time": stat.st_mtime,
        "extension": Path(file_path).suffix.lower()
    }


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字節）
        
    Returns:
        格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def create_safe_filename(filename: str) -> str:
    """
    創建安全的文件名（移除特殊字符）
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    import re
    
    # 移除或替換不安全的字符
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_filename = re.sub(r'\s+', '_', safe_filename)  # 替換空格
    safe_filename = safe_filename.strip('._')  # 移除開頭和結尾的點和下劃線
    
    return safe_filename


def ensure_directory(directory_path: str) -> bool:
    """
    確保目錄存在，如果不存在則創建
    
    Args:
        directory_path: 目錄路徑
        
    Returns:
        是否成功
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"創建目錄失敗 {directory_path}: {str(e)}")
        return False


def copy_file(source_path: str, destination_path: str) -> bool:
    """
    複製文件
    
    Args:
        source_path: 源文件路徑
        destination_path: 目標文件路徑
        
    Returns:
        是否成功
    """
    try:
        # 確保目標目錄存在
        destination_dir = os.path.dirname(destination_path)
        ensure_directory(destination_dir)
        
        shutil.copy2(source_path, destination_path)
        return True
    except Exception as e:
        print(f"複製文件失敗 {source_path} -> {destination_path}: {str(e)}")
        return False


def is_video_file(file_path: str) -> bool:
    """
    檢查文件是否為視頻文件
    
    Args:
        file_path: 文件路徑
        
    Returns:
        是否為視頻文件
    """
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.ts'}
    
    try:
        extension = Path(file_path).suffix.lower()
        return extension in video_extensions
    except Exception:
        return False


def get_relative_path(file_path: str, base_path: str) -> str:
    """
    獲取相對於基礎路徑的相對路徑
    
    Args:
        file_path: 文件路徑
        base_path: 基礎路徑
        
    Returns:
        相對路徑
    """
    try:
        return os.path.relpath(file_path, base_path)
    except Exception:
        return file_path 