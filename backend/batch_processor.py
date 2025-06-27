import asyncio
from typing import List, Dict, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
from models import User, Keyword, GeneratedTitle, GeneratedContent
from logger import app_logger
import json

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    KEYWORD_ANALYSIS = "keyword_analysis"
    TITLE_GENERATION = "title_generation"
    CONTENT_GENERATION = "content_generation"
    BATCH_WORKFLOW = "batch_workflow"

@dataclass
class BatchTask:
    id: str
    task_type: TaskType
    user_id: str
    parameters: Dict
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict] = None
    progress: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class BatchProcessor:
    """배치 처리 시스템"""
    
    def __init__(self):
        self.tasks: Dict[str, BatchTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.max_concurrent_tasks = 3
        
    async def submit_task(self, task: BatchTask) -> str:
        """배치 작업 제출"""
        self.tasks[task.id] = task
        
        app_logger.info(
            f"Batch task submitted",
            task_id=task.id,
            task_type=task.task_type.value,
            user_id=task.user_id
        )
        
        # 동시 실행 작업 수 체크
        if len(self.running_tasks) < self.max_concurrent_tasks:
            await self._start_task(task.id)
        
        return task.id
    
    async def _start_task(self, task_id: str):
        """작업 실행 시작"""
        if task_id not in self.tasks:
            return
            
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        app_logger.info(
            f"Starting batch task",
            task_id=task_id,
            task_type=task.task_type.value
        )
        
        # 비동기 작업 생성
        async_task = asyncio.create_task(self._execute_task(task))
        self.running_tasks[task_id] = async_task
        
        # 작업 완료 콜백 설정
        async_task.add_done_callback(
            lambda t: asyncio.create_task(self._task_completed(task_id))
        )
    
    async def _execute_task(self, task: BatchTask):
        """작업 실행"""
        try:
            if task.task_type == TaskType.KEYWORD_ANALYSIS:
                result = await self._execute_keyword_analysis(task)
            elif task.task_type == TaskType.TITLE_GENERATION:
                result = await self._execute_title_generation(task)
            elif task.task_type == TaskType.CONTENT_GENERATION:
                result = await self._execute_content_generation(task)
            elif task.task_type == TaskType.BATCH_WORKFLOW:
                result = await self._execute_batch_workflow(task)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            app_logger.error(
                f"Batch task failed",
                error=e,
                task_id=task.id,
                task_type=task.task_type.value
            )
        finally:
            task.completed_at = datetime.now()
    
    async def _execute_keyword_analysis(self, task: BatchTask) -> Dict:
        """키워드 분석 배치 작업"""
        keywords = task.parameters.get("keywords", [])
        country = task.parameters.get("country", "KR")
        
        results = []
        total_keywords = len(keywords)
        
        for i, keyword in enumerate(keywords):
            # 진행률 업데이트
            task.progress = int((i / total_keywords) * 100)
            
            # 실제 키워드 분석 실행 (여기서는 모의 데이터)
            result = {
                "keyword": keyword,
                "search_volume": 1000 + i * 100,
                "competition": "Medium",
                "cpc": 1.5,
                "opportunity_score": 80 + i
            }
            results.append(result)
            
            # 작업 간 지연 (API 레이트 리미팅)
            await asyncio.sleep(0.5)
        
        return {
            "type": "keyword_analysis",
            "total_keywords": total_keywords,
            "results": results
        }
    
    async def _execute_title_generation(self, task: BatchTask) -> Dict:
        """제목 생성 배치 작업"""
        keywords = task.parameters.get("keywords", [])
        count_per_keyword = task.parameters.get("count_per_keyword", 3)
        
        results = {}
        total_operations = len(keywords)
        
        for i, keyword in enumerate(keywords):
            task.progress = int((i / total_operations) * 100)
            
            # 실제 제목 생성 (여기서는 모의 데이터)
            titles = []
            for j in range(count_per_keyword):
                titles.append({
                    "title": f"{keyword}의 완벽한 가이드 {j+1}",
                    "duplicate_rate": 5.0 + j
                })
            
            results[keyword] = titles
            await asyncio.sleep(1.0)  # AI API 호출 간격
        
        return {
            "type": "title_generation",
            "total_keywords": len(keywords),
            "titles_per_keyword": count_per_keyword,
            "results": results
        }
    
    async def _execute_content_generation(self, task: BatchTask) -> Dict:
        """콘텐츠 생성 배치 작업"""
        titles = task.parameters.get("titles", [])
        
        results = []
        total_titles = len(titles)
        
        for i, title in enumerate(titles):
            task.progress = int((i / total_titles) * 100)
            
            # 실제 콘텐츠 생성 (여기서는 모의 데이터)
            content = {
                "title": title,
                "content": f"# {title}\n\n이것은 자동 생성된 콘텐츠입니다...",
                "seo_score": 85,
                "geo_score": 78,
                "word_count": 1500
            }
            results.append(content)
            
            await asyncio.sleep(2.0)  # AI API 호출 간격 (콘텐츠 생성은 더 오래 걸림)
        
        return {
            "type": "content_generation",
            "total_titles": len(titles),
            "results": results
        }
    
    async def _execute_batch_workflow(self, task: BatchTask) -> Dict:
        """전체 워크플로우 배치 작업 (키워드 -> 제목 -> 콘텐츠)"""
        keywords = task.parameters.get("keywords", [])
        titles_per_keyword = task.parameters.get("titles_per_keyword", 3)
        content_per_keyword = task.parameters.get("content_per_keyword", 1)
        
        total_steps = len(keywords) * (1 + titles_per_keyword + content_per_keyword)
        current_step = 0
        
        workflow_results = {
            "keywords": {},
            "titles": {},
            "content": {}
        }
        
        for keyword in keywords:
            # 1. 키워드 분석
            keyword_result = {
                "search_volume": 1000,
                "competition": "Medium",
                "opportunity_score": 85
            }
            workflow_results["keywords"][keyword] = keyword_result
            current_step += 1
            task.progress = int((current_step / total_steps) * 100)
            await asyncio.sleep(0.5)
            
            # 2. 제목 생성
            titles = []
            for i in range(titles_per_keyword):
                title = f"{keyword}의 실전 가이드 {i+1}"
                titles.append({
                    "title": title,
                    "duplicate_rate": 5.0 + i
                })
                current_step += 1
                task.progress = int((current_step / total_steps) * 100)
                await asyncio.sleep(1.0)
            
            workflow_results["titles"][keyword] = titles
            
            # 3. 콘텐츠 생성
            for i in range(content_per_keyword):
                title = titles[i]["title"]
                content = {
                    "title": title,
                    "content": f"# {title}\n\n자동 생성된 고품질 콘텐츠...",
                    "seo_score": 85,
                    "word_count": 1500
                }
                
                if keyword not in workflow_results["content"]:
                    workflow_results["content"][keyword] = []
                workflow_results["content"][keyword].append(content)
                
                current_step += 1
                task.progress = int((current_step / total_steps) * 100)
                await asyncio.sleep(2.0)
        
        return {
            "type": "batch_workflow",
            "total_keywords": len(keywords),
            "total_steps": total_steps,
            "results": workflow_results
        }
    
    async def _task_completed(self, task_id: str):
        """작업 완료 처리"""
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]
        
        task = self.tasks.get(task_id)
        if task:
            app_logger.info(
                f"Batch task completed",
                task_id=task_id,
                status=task.status.value,
                duration_seconds=(task.completed_at - task.started_at).total_seconds() if task.completed_at and task.started_at else 0
            )
        
        # 대기 중인 작업이 있으면 시작
        await self._start_next_pending_task()
    
    async def _start_next_pending_task(self):
        """대기 중인 다음 작업 시작"""
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            return
        
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                await self._start_task(task_id)
                break
    
    def get_task_status(self, task_id: str) -> Optional[BatchTask]:
        """작업 상태 조회"""
        return self.tasks.get(task_id)
    
    def get_user_tasks(self, user_id: str) -> List[BatchTask]:
        """사용자별 작업 목록"""
        return [
            task for task in self.tasks.values()
            if task.user_id == user_id
        ]
    
    async def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.RUNNING:
            # 실행 중인 작업 취소
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                del self.running_tasks[task_id]
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        
        app_logger.info(f"Batch task cancelled", task_id=task_id)
        return True

# 글로벌 배치 프로세서 인스턴스
batch_processor = BatchProcessor()