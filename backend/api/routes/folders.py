"""
文件夾管理 API 路由
處理文件夾掃描和視頻匹配操作
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from api.schemas import (
    FolderScanRequest, FolderScanApiResponse, FolderScanResponse,
    VideoMatchRequest, VideoMatchApiResponse, VideoMatchResponse,
    VideoMatchPair
)
from utils.video_matcher import VideoMatcher
from utils.file_utils import validate_folder_path, get_folder_info, scan_video_files

router = APIRouter()


@router.post("/scan", response_model=FolderScanApiResponse, summary="掃描文件夾")
async def scan_folder(request: FolderScanRequest):
    """
    掃描指定文件夾中的視頻文件
    
    - **path**: 文件夾路徑
    """
    try:
        folder_path = request.path
        
        # 驗證文件夾路徑
        if not validate_folder_path(folder_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件夾路徑無效或不存在: {folder_path}"
            )
        
        # 獲取文件夾信息
        folder_info = get_folder_info(folder_path)
        
        # 掃描視頻文件
        video_files = scan_video_files(folder_path)
        
        # 提取文件名（相對路徑）
        video_file_names = []
        for video_file in video_files:
            try:
                # 獲取相對於掃描文件夾的相對路徑
                import os
                rel_path = os.path.relpath(video_file, folder_path)
                video_file_names.append(rel_path)
            except Exception:
                video_file_names.append(os.path.basename(video_file))
        
        response_data = FolderScanResponse(
            path=folder_info['path'],
            name=folder_info['name'],
            video_count=len(video_files),
            video_files=video_file_names
        )
        
        return FolderScanApiResponse(
            success=True,
            data=response_data,
            message=f"成功掃描文件夾，找到 {len(video_files)} 個視頻文件"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"掃描文件夾失敗: {str(e)}"
        )


@router.post("/match", response_model=VideoMatchApiResponse, summary="匹配視頻文件")
async def match_videos(request: VideoMatchRequest):
    """
    匹配兩個文件夾中的視頻文件
    
    - **folder_a_path**: 文件夾A路徑（基線版本）
    - **folder_b_path**: 文件夾B路徑（對比版本）
    """
    try:
        folder_a_path = request.folder_a_path
        folder_b_path = request.folder_b_path
        
        # 驗證文件夾路徑
        if not validate_folder_path(folder_a_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件夾A路徑無效: {folder_a_path}"
            )
        
        if not validate_folder_path(folder_b_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件夾B路徑無效: {folder_b_path}"
            )
        
        # 執行視頻匹配
        matcher = VideoMatcher()
        matched_pairs = matcher.match_videos(folder_a_path, folder_b_path)
        
        # 獲取完整匹配結果
        match_results = matcher.get_match_results()
        
        # 轉換為響應格式
        response_pairs = []
        for pair in matched_pairs:
            response_pairs.append(VideoMatchPair(
                video_a=pair['video_a'],
                video_b=pair['video_b'],
                name=pair['name']
            ))
        
        response_data = VideoMatchResponse(
            matched_pairs=response_pairs,
            unmatched_a=match_results['unmatched_a'],
            unmatched_b=match_results['unmatched_b']
        )
        
        # 獲取匹配質量報告
        quality_report = matcher.validate_match_quality()
        
        message = f"匹配完成: {len(matched_pairs)} 個視頻對"
        if not quality_report['is_good_match']:
            message += f" (匹配率: {quality_report['overall_match_rate']:.1%})"
        
        return VideoMatchApiResponse(
            success=True,
            data=response_data,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"匹配視頻文件失敗: {str(e)}"
        ) 