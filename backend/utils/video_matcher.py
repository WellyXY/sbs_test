"""
視頻文件匹配工具
根據文件名自動匹配兩個文件夾中的視頻對
"""

import os
import re
from typing import List, Dict, Tuple
from pathlib import Path


class VideoMatcher:
    """視頻文件匹配器"""
    
    # 支持的視頻格式
    SUPPORTED_FORMATS = {
        '.mp4', '.mov', '.avi', '.mkv', '.webm',
        '.flv', '.wmv', '.m4v', '.3gp', '.ts'
    }
    
    def __init__(self):
        self.matched_pairs = []
        self.unmatched_a = []
        self.unmatched_b = []
    
    def scan_video_files(self, folder_path: str) -> List[str]:
        """
        掃描文件夾中的視頻文件
        
        Args:
            folder_path: 文件夾路徑
            
        Returns:
            視頻文件路徑列表
        """
        video_files = []
        
        if not os.path.exists(folder_path):
            return video_files
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file).suffix.lower()
                    
                    if file_ext in self.SUPPORTED_FORMATS:
                        video_files.append(file_path)
            
            # 按文件名排序
            video_files.sort(key=lambda x: os.path.basename(x).lower())
            
        except Exception as e:
            print(f"掃描文件夾失敗 {folder_path}: {str(e)}")
        
        return video_files
    
    def extract_base_name(self, file_path: str) -> str:
        """
        提取文件的基礎名稱（去除擴展名和可能的後綴）
        
        Args:
            file_path: 文件路徑
            
        Returns:
            基礎文件名
        """
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        
        # 移除常見的後綴模式
        patterns_to_remove = [
            r'_compressed$',
            r'_enhanced$',
            r'_baseline$',
            r'_original$',
            r'_v\d+$',
            r'_\d+$',
            r'_final$',
            r'_output$'
        ]
        
        for pattern in patterns_to_remove:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        return base_name.lower().strip()
    
    def match_videos(self, folder_a_path: str, folder_b_path: str) -> List[Dict[str, str]]:
        """
        匹配兩個文件夾中的視頻文件
        
        Args:
            folder_a_path: 文件夾A路徑
            folder_b_path: 文件夾B路徑
            
        Returns:
            匹配的視頻對列表
        """
        # 重置結果
        self.matched_pairs = []
        self.unmatched_a = []
        self.unmatched_b = []
        
        # 掃描兩個文件夾
        videos_a = self.scan_video_files(folder_a_path)
        videos_b = self.scan_video_files(folder_b_path)
        
        print(f"文件夾A找到 {len(videos_a)} 個視頻文件")
        print(f"文件夾B找到 {len(videos_b)} 個視頻文件")
        
        # 創建基礎名稱到文件路徑的映射
        mapping_a = {}
        mapping_b = {}
        
        for video in videos_a:
            base_name = self.extract_base_name(video)
            if base_name not in mapping_a:
                mapping_a[base_name] = []
            mapping_a[base_name].append(video)
        
        for video in videos_b:
            base_name = self.extract_base_name(video)
            if base_name not in mapping_b:
                mapping_b[base_name] = []
            mapping_b[base_name].append(video)
        
        # 匹配文件
        matched_base_names = set()
        
        for base_name in mapping_a:
            if base_name in mapping_b:
                # 找到匹配，取第一個文件（如果有多個同名文件）
                video_a = mapping_a[base_name][0]
                video_b = mapping_b[base_name][0]
                
                self.matched_pairs.append({
                    'video_a': video_a,
                    'video_b': video_b,
                    'name': base_name
                })
                
                matched_base_names.add(base_name)
        
        # 記錄未匹配的文件
        for base_name, videos in mapping_a.items():
            if base_name not in matched_base_names:
                self.unmatched_a.extend(videos)
        
        for base_name, videos in mapping_b.items():
            if base_name not in matched_base_names:
                self.unmatched_b.extend(videos)
        
        print(f"成功匹配 {len(self.matched_pairs)} 個視頻對")
        print(f"文件夾A未匹配: {len(self.unmatched_a)} 個文件")
        print(f"文件夾B未匹配: {len(self.unmatched_b)} 個文件")
        
        return self.matched_pairs
    
    def get_match_results(self) -> Dict:
        """
        獲取完整的匹配結果
        
        Returns:
            包含匹配對和未匹配文件的字典
        """
        return {
            'matched_pairs': self.matched_pairs,
            'unmatched_a': self.unmatched_a,
            'unmatched_b': self.unmatched_b,
            'total_matched': len(self.matched_pairs),
            'total_unmatched_a': len(self.unmatched_a),
            'total_unmatched_b': len(self.unmatched_b)
        }
    
    def validate_match_quality(self) -> Dict:
        """
        驗證匹配質量
        
        Returns:
            匹配質量報告
        """
        total_files_a = len(self.matched_pairs) + len(self.unmatched_a)
        total_files_b = len(self.matched_pairs) + len(self.unmatched_b)
        
        match_rate_a = len(self.matched_pairs) / total_files_a if total_files_a > 0 else 0
        match_rate_b = len(self.matched_pairs) / total_files_b if total_files_b > 0 else 0
        
        return {
            'match_rate_a': match_rate_a,
            'match_rate_b': match_rate_b,
            'overall_match_rate': (match_rate_a + match_rate_b) / 2,
            'is_good_match': match_rate_a > 0.8 and match_rate_b > 0.8,
            'recommendations': self._get_recommendations(match_rate_a, match_rate_b)
        }
    
    def _get_recommendations(self, match_rate_a: float, match_rate_b: float) -> List[str]:
        """
        根據匹配率提供建議
        
        Args:
            match_rate_a: 文件夾A的匹配率
            match_rate_b: 文件夾B的匹配率
            
        Returns:
            建議列表
        """
        recommendations = []
        
        if match_rate_a < 0.5 or match_rate_b < 0.5:
            recommendations.append("匹配率較低，請檢查文件命名是否一致")
        
        if len(self.unmatched_a) > 0:
            recommendations.append(f"文件夾A有 {len(self.unmatched_a)} 個文件未匹配")
        
        if len(self.unmatched_b) > 0:
            recommendations.append(f"文件夾B有 {len(self.unmatched_b)} 個文件未匹配")
        
        if not recommendations:
            recommendations.append("匹配質量良好，可以開始盲測")
        
        return recommendations

def normalize_filename(filename: str) -> str:
    """標準化文件名，移除擴展名和常見後綴"""
    # 移除擴展名
    name = Path(filename).stem
    
    # 移除常見的處理後綴
    suffixes_to_remove = [
        '_compressed', '_enhanced', '_processed', '_output',
        '_original', '_source', '_input', '_result',
        '_720p', '_1080p', '_4k', '_hd',
        '_final', '_v1', '_v2', '_v3',
        '(1)', '(2)', '(3)',
        '-1', '-2', '-3',
        '_copy', '_new'
    ]
    
    normalized = name.lower()
    for suffix in suffixes_to_remove:
        normalized = normalized.replace(suffix.lower(), '')
    
    # 移除多餘的空格和下劃線
    normalized = re.sub(r'[_\s]+', '_', normalized)
    normalized = normalized.strip('_')
    
    return normalized

def calculate_similarity(name1: str, name2: str) -> float:
    """計算兩個文件名的相似度"""
    norm1 = normalize_filename(name1)
    norm2 = normalize_filename(name2)
    
    # 完全匹配
    if norm1 == norm2:
        return 1.0
    
    # 使用 Levenshtein 距離計算相似度
    def levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    max_len = max(len(norm1), len(norm2))
    if max_len == 0:
        return 1.0
    
    distance = levenshtein_distance(norm1, norm2)
    similarity = 1.0 - (distance / max_len)
    
    return similarity

def match_videos(videos_a: List[str], videos_b: List[str], threshold: float = 0.6) -> List[Dict]:
    """匹配兩個資料夾中的視頻文件"""
    matched_pairs = []
    used_b_videos = set()
    
    # 為每個A視頻找到最佳匹配的B視頻
    for video_a in videos_a:
        best_match = None
        best_similarity = 0.0
        
        for video_b in videos_b:
            if video_b in used_b_videos:
                continue
                
            similarity = calculate_similarity(video_a, video_b)
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = video_b
        
        if best_match:
            matched_pairs.append({
                'video_a': video_a,
                'video_b': best_match,
                'similarity': best_similarity,
                'completed': False
            })
            used_b_videos.add(best_match)
    
    # 按相似度排序
    matched_pairs.sort(key=lambda x: x['similarity'], reverse=True)
    
    return matched_pairs

def preview_matches(videos_a: List[str], videos_b: List[str]) -> Dict:
    """預覽匹配結果，不實際執行匹配"""
    matches = match_videos(videos_a, videos_b)
    
    return {
        'total_a': len(videos_a),
        'total_b': len(videos_b),
        'matched_pairs': len(matches),
        'unmatched_a': len(videos_a) - len(matches),
        'unmatched_b': len(videos_b) - len([m['video_b'] for m in matches]),
        'preview': matches[:5],  # 只返回前5個匹配作為預覽
        'average_similarity': sum(m['similarity'] for m in matches) / len(matches) if matches else 0
    } 