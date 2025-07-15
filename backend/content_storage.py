"""
생성된 콘텐츠 저장 및 관리 시스템
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid

class ContentStorage:
    def __init__(self):
        self.storage_dir = Path("/mnt/e/project/test-blogauto-project/backend/saved_content")
        self.storage_dir.mkdir(exist_ok=True)
        self.content_file = self.storage_dir / "content_history.json"
        self.init_storage()
    
    def init_storage(self):
        """저장소 초기화"""
        if not self.content_file.exists():
            self.save_content_list([])
    
    def load_content_list(self) -> List[Dict[str, Any]]:
        """저장된 콘텐츠 목록 로드"""
        try:
            with open(self.content_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_content_list(self, content_list: List[Dict[str, Any]]):
        """콘텐츠 목록 저장"""
        with open(self.content_file, 'w', encoding='utf-8') as f:
            json.dump(content_list, f, ensure_ascii=False, indent=2)
    
    def save_content(self, content_data: Dict[str, Any]) -> str:
        """새로운 콘텐츠 저장"""
        content_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 콘텐츠 메타데이터 생성
        content_meta = {
            "id": content_id,
            "title": content_data.get("title", "제목 없음"),
            "keyword": content_data.get("keyword", ""),
            "content_type": content_data.get("content_type", "content"),
            "created_at": timestamp,
            "updated_at": timestamp,
            "word_count": len(content_data.get("content", "")),
            "seo_score": content_data.get("seo_score", 0),
            "status": "draft"  # draft, published, archived
        }
        
        # 개별 콘텐츠 파일 저장
        content_file = self.storage_dir / f"{content_id}.json"
        full_content = {
            **content_meta,
            "content": content_data.get("content", ""),
            "keywords_used": content_data.get("keywords_used", []),
            "images": content_data.get("images", []),
            "metadata": content_data.get("metadata", {})
        }
        
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(full_content, f, ensure_ascii=False, indent=2)
        
        # 콘텐츠 목록 업데이트
        content_list = self.load_content_list()
        content_list.insert(0, content_meta)  # 최신 순으로 정렬
        
        # 최대 1000개까지만 유지
        if len(content_list) > 1000:
            # 오래된 콘텐츠 파일 삭제
            old_content = content_list[1000:]
            for old_item in old_content:
                old_file = self.storage_dir / f"{old_item['id']}.json"
                if old_file.exists():
                    old_file.unlink()
            content_list = content_list[:1000]
        
        self.save_content_list(content_list)
        return content_id
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """특정 콘텐츠 조회"""
        content_file = self.storage_dir / f"{content_id}.json"
        if not content_file.exists():
            return None
        
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def update_content(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """콘텐츠 업데이트"""
        content = self.get_content(content_id)
        if not content:
            return False
        
        # 업데이트 적용
        content.update(updates)
        content["updated_at"] = datetime.now().isoformat()
        
        # 파일 저장
        content_file = self.storage_dir / f"{content_id}.json"
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        # 목록에서도 메타데이터 업데이트
        content_list = self.load_content_list()
        for i, item in enumerate(content_list):
            if item["id"] == content_id:
                content_list[i].update({
                    "title": content.get("title"),
                    "updated_at": content["updated_at"],
                    "word_count": len(content.get("content", "")),
                    "seo_score": content.get("seo_score", 0),
                    "status": content.get("status", "draft")
                })
                break
        
        self.save_content_list(content_list)
        return True
    
    def delete_content(self, content_id: str) -> bool:
        """콘텐츠 삭제"""
        content_file = self.storage_dir / f"{content_id}.json"
        if content_file.exists():
            content_file.unlink()
        
        # 목록에서 제거
        content_list = self.load_content_list()
        content_list = [item for item in content_list if item["id"] != content_id]
        self.save_content_list(content_list)
        return True
    
    def search_content(self, query: str = "", status: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """콘텐츠 검색"""
        content_list = self.load_content_list()
        
        # 필터링
        if status:
            content_list = [item for item in content_list if item.get("status") == status]
        
        if query:
            query = query.lower()
            content_list = [
                item for item in content_list 
                if query in item.get("title", "").lower() or 
                   query in item.get("keyword", "").lower()
            ]
        
        return content_list[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """저장 통계"""
        content_list = self.load_content_list()
        
        total_content = len(content_list)
        total_words = sum(item.get("word_count", 0) for item in content_list)
        avg_seo_score = sum(item.get("seo_score", 0) for item in content_list) / max(total_content, 1)
        
        status_counts = {}
        for item in content_list:
            status = item.get("status", "draft")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_content": total_content,
            "total_words": total_words,
            "avg_seo_score": round(avg_seo_score, 1),
            "status_counts": status_counts,
            "storage_size_mb": self._get_storage_size()
        }
    
    def _get_storage_size(self) -> float:
        """저장소 크기 계산 (MB)"""
        total_size = 0
        for file_path in self.storage_dir.glob("*.json"):
            total_size += file_path.stat().st_size
        return round(total_size / (1024 * 1024), 2)

# 전역 저장소 인스턴스
content_storage = ContentStorage()