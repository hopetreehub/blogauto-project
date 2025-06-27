"""
시스템 지침 관리 서비스
키워드 분석, 제목 생성, 블로그 글쓰기 지침을 통합 관리
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import SystemPrompt, PromptTemplate, PromptType, User
from datetime import datetime

class PromptManager:
    def __init__(self, db: Session):
        self.db = db
        self._initialize_default_prompts()

    def _initialize_default_prompts(self):
        """기본 지침들을 데이터베이스에 초기화"""
        
        # 키워드 분석 기본 지침
        keyword_prompt = """당신은 최고의 SEO 전문가이자 실시간 키워드 분석 시스템 설계자입니다. 이 시스템은 사용자가 입력한 "아이템 이름"과 "카테고리"를 바탕으로, 최신 트렌드와 계절성, 검색량, 경쟁도, 클릭률 등의 데이터를 자동 분석하여, 지금 이 시점에서 블로그 글 작성에 최적화된 키워드 10개를 도출해야 합니다.

[분석 기준]
1. 검색 의도 분석: 정보형, 거래형, 탐색형 키워드 균형
2. 롱테일 키워드 우선순위: 경쟁도 낮고 전환율 높은 키워드
3. 계절성 반영: 현재 시기에 맞는 키워드 가중치 적용
4. 지역성 고려: 한국 사용자 검색 패턴 반영
5. 트렌드 분석: 최근 1-3개월 급상승 키워드 포함

[출력 형식]
각 키워드마다 다음 정보 제공:
- 키워드명
- 예상 월간 검색량
- 경쟁도 (낮음/보통/높음)
- SEO 난이도 점수 (1-100)
- 추천 이유
- 관련 LSI 키워드 3개"""

        # 제목 생성 기본 지침
        title_prompt = """당신은 시의성과 검색 전략에 능통한 블로그 제목 생성 전문가입니다. 사용자가 단 하나의 "키워드"를 입력하면, 현재 시기·상황에 최적화되어 있고 독자 입장에서 꼭 클릭하고 싶어지는 블로그 제목을 생성하는 것이 당신의 임무입니다.

[제목 생성 원칙]
1. SEO 최적화: 키워드 자연스러운 포함, 35자 이내 권장
2. 클릭 유도: 호기심, 긴급성, 혜택을 강조하는 표현
3. 감정 자극: 공감, 놀라움, 성취감 등 감정적 연결
4. 시의성 반영: 2025년 트렌드, 계절감, 최신성 강조
5. 검증된 패턴: 질문형, 리스트형, How-to형, 비교형 활용

[제목 타입별 템플릿]
- 질문형: "왜 모든 사람이 {키워드}에 열광할까?"
- 리스트형: "{키워드} 핵심 포인트 5가지"
- How-to형: "{키워드} 완벽 마스터하는 법"
- 비교형: "{키워드} vs 대안, 어떤 게 좋을까?"
- 트렌드형: "2025년 {키워드} 트렌드 전망"

[출력 요구사항]
5개의 제목 후보와 각각의 SEO 점수, 클릭 유도 점수, 바이럴 잠재력 점수를 제공하세요."""

        # 블로그 글쓰기 기본 지침
        blog_prompt = """당신은 AI 세대를 선도하는 블로그 글쓰기 마스터입니다. SEO(검색엔진 최적화)뿐 아니라 최신 AI 검색 환경을 위한 GEO(Generative Engine Optimization, 생성형 엔진 최적화)까지 완전히 이해하고 있으며, AI 챗봇이 자연스럽게 인용할 수 있는 콘텐츠 구조와 문장 구성 방식을 알고 있습니다.

[당신의 임무]
사용자가 입력하는 단 하나의 "키워드"를 바탕으로, SEO와 GEO 전략을 모두 반영한 최고의 블로그 글을 자동으로 생성하세요.

[세부 조건]
1. 당신은 SEO 전문가, GEO 전략가, 스토리텔러, 브랜드 콘텐츠 심리 분석가로서 활동합니다.
2. GEO 최적화를 위해 AI 챗봇이 잘 인용하는 구조(명확한 헤딩, 인용하기 좋은 문장, 출처 암시 문장 등)를 포함시킵니다.
3. 글은 반드시 감성적이며, AI가 아닌 인간이 쓴 것처럼 매끄럽고 설득력 있게 작성되어야 합니다.
4. 문장 중간에 자연스럽게 "최근 연구에 따르면", "한 보고서에 따르면", "통계적으로 밝혀진 바에 의하면" 등의 인용 친화적 표현을 포함해야 합니다.
5. LSI 키워드(의미 연관 키워드)와 트렌디한 관련어를 자동으로 탐색하여 본문에 녹여야 합니다.

[작성 단계]
1. 사용자가 제공한 키워드 하나로 SEO 검색 의도 + GEO 인용 가능성 기반 서브주제 3개 추출
2. SEO + GEO를 모두 만족하는 클릭 유도형 블로그 제목 3개 생성
3. 가장 임팩트 있는 제목 선택 후 서론-본론-결론 구성의 블로그 글 전체 작성 (800~1200자)
4. 본문에는 LSI 키워드와 AI 인용 유도형 문장 포함
5. Call-to-Action(CTA) 문구도 자연스럽게 포함

[출력 형식]
- 블로그 제목 제안 3개
- 선택된 제목 기반 블로그 본문 전체 (SEO + GEO 완전 최적화, 800~1200자)

[주의사항]
- 사용자의 입력은 단 하나의 키워드
- AI 냄새 없이 100% 사람처럼 써야 하며, 추가 질문 없이 자동으로 완성"""

        # 기본 지침들 생성
        default_prompts = [
            {
                "prompt_type": PromptType.KEYWORD_ANALYSIS,
                "name": "기본 키워드 분석 지침",
                "description": "SEO 전문가 기반 키워드 분석 시스템",
                "prompt_content": keyword_prompt,
                "is_default": True
            },
            {
                "prompt_type": PromptType.TITLE_GENERATION,
                "name": "기본 제목 생성 지침",
                "description": "시의성과 SEO를 고려한 제목 생성 시스템",
                "prompt_content": title_prompt,
                "is_default": True
            },
            {
                "prompt_type": PromptType.BLOG_WRITING,
                "name": "기본 블로그 글쓰기 지침",
                "description": "SEO + GEO 최적화된 블로그 글쓰기 시스템",
                "prompt_content": blog_prompt,
                "is_default": True
            }
        ]

        # 기본 지침이 없는 경우에만 생성
        for prompt_data in default_prompts:
            existing = self.db.query(SystemPrompt).filter(
                SystemPrompt.prompt_type == prompt_data["prompt_type"],
                SystemPrompt.is_default == True
            ).first()
            
            if not existing:
                new_prompt = SystemPrompt(
                    prompt_type=prompt_data["prompt_type"],
                    name=prompt_data["name"],
                    description=prompt_data["description"],
                    prompt_content=prompt_data["prompt_content"],
                    is_default=prompt_data["is_default"],
                    is_active=True,
                    version="1.0"
                )
                self.db.add(new_prompt)
        
        self.db.commit()

    def get_prompts_by_type(self, prompt_type: PromptType) -> List[Dict[str, Any]]:
        """타입별 지침 목록 조회"""
        prompts = self.db.query(SystemPrompt).filter(
            SystemPrompt.prompt_type == prompt_type,
            SystemPrompt.is_active == True
        ).order_by(SystemPrompt.is_default.desc(), SystemPrompt.created_at.desc()).all()
        
        return [
            {
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "prompt_content": prompt.prompt_content,
                "is_default": prompt.is_default,
                "version": prompt.version,
                "created_at": prompt.created_at,
                "updated_at": prompt.updated_at
            }
            for prompt in prompts
        ]

    def get_active_prompt(self, prompt_type: PromptType) -> Optional[Dict[str, Any]]:
        """활성화된 기본 지침 조회"""
        prompt = self.db.query(SystemPrompt).filter(
            SystemPrompt.prompt_type == prompt_type,
            SystemPrompt.is_default == True,
            SystemPrompt.is_active == True
        ).first()
        
        if prompt:
            return {
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "prompt_content": prompt.prompt_content,
                "version": prompt.version
            }
        return None

    def create_prompt(self, prompt_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """새 지침 생성"""
        # 기본 지침으로 설정하는 경우 기존 기본 지침 해제
        if prompt_data.get("is_default"):
            self.db.query(SystemPrompt).filter(
                SystemPrompt.prompt_type == prompt_data["prompt_type"],
                SystemPrompt.is_default == True
            ).update({"is_default": False})

        new_prompt = SystemPrompt(
            prompt_type=PromptType(prompt_data["prompt_type"]),
            name=prompt_data["name"],
            description=prompt_data.get("description", ""),
            prompt_content=prompt_data["prompt_content"],
            is_default=prompt_data.get("is_default", False),
            is_active=True,
            version=prompt_data.get("version", "1.0"),
            created_by=created_by
        )
        
        self.db.add(new_prompt)
        self.db.commit()
        self.db.refresh(new_prompt)
        
        return {
            "id": new_prompt.id,
            "name": new_prompt.name,
            "description": new_prompt.description,
            "prompt_type": new_prompt.prompt_type.value,
            "is_default": new_prompt.is_default,
            "version": new_prompt.version
        }

    def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        """지침 업데이트"""
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            return False

        # 기본 지침으로 설정하는 경우 기존 기본 지침 해제
        if prompt_data.get("is_default") and not prompt.is_default:
            self.db.query(SystemPrompt).filter(
                SystemPrompt.prompt_type == prompt.prompt_type,
                SystemPrompt.is_default == True,
                SystemPrompt.id != prompt_id
            ).update({"is_default": False})

        # 업데이트 가능한 필드들
        if "name" in prompt_data:
            prompt.name = prompt_data["name"]
        if "description" in prompt_data:
            prompt.description = prompt_data["description"]
        if "prompt_content" in prompt_data:
            prompt.prompt_content = prompt_data["prompt_content"]
        if "is_default" in prompt_data:
            prompt.is_default = prompt_data["is_default"]
        if "is_active" in prompt_data:
            prompt.is_active = prompt_data["is_active"]
        if "version" in prompt_data:
            prompt.version = prompt_data["version"]
        
        prompt.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def delete_prompt(self, prompt_id: str) -> bool:
        """지침 삭제 (소프트 삭제)"""
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            return False

        prompt.is_active = False
        prompt.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_all_prompts_summary(self) -> Dict[str, Any]:
        """모든 지침 요약 정보"""
        summary = {}
        
        for prompt_type in PromptType:
            prompts = self.get_prompts_by_type(prompt_type)
            active_count = len([p for p in prompts if p.get("is_active", True)])
            default_prompt = next((p for p in prompts if p["is_default"]), None)
            
            summary[prompt_type.value] = {
                "total_count": len(prompts),
                "active_count": active_count,
                "default_prompt": {
                    "id": default_prompt["id"] if default_prompt else None,
                    "name": default_prompt["name"] if default_prompt else "없음",
                    "version": default_prompt["version"] if default_prompt else "N/A"
                }
            }
        
        return summary

    def export_prompts(self, prompt_type: Optional[PromptType] = None) -> Dict[str, Any]:
        """지침 내보내기 (JSON 형태)"""
        if prompt_type:
            prompts = self.get_prompts_by_type(prompt_type)
            return {
                "prompt_type": prompt_type.value,
                "prompts": prompts,
                "exported_at": datetime.utcnow().isoformat()
            }
        else:
            all_prompts = {}
            for ptype in PromptType:
                all_prompts[ptype.value] = self.get_prompts_by_type(ptype)
            
            return {
                "all_prompts": all_prompts,
                "exported_at": datetime.utcnow().isoformat()
            }

    def import_prompts(self, import_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """지침 가져오기"""
        imported_count = 0
        errors = []
        
        try:
            if "all_prompts" in import_data:
                # 전체 가져오기
                for prompt_type_str, prompts in import_data["all_prompts"].items():
                    for prompt_data in prompts:
                        try:
                            prompt_data["prompt_type"] = prompt_type_str
                            prompt_data["is_default"] = False  # 가져온 지침은 기본값 아님
                            self.create_prompt(prompt_data, created_by)
                            imported_count += 1
                        except Exception as e:
                            errors.append(f"Error importing {prompt_data.get('name', 'Unknown')}: {str(e)}")
            
            elif "prompts" in import_data:
                # 특정 타입 가져오기
                for prompt_data in import_data["prompts"]:
                    try:
                        prompt_data["prompt_type"] = import_data["prompt_type"]
                        prompt_data["is_default"] = False
                        self.create_prompt(prompt_data, created_by)
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Error importing {prompt_data.get('name', 'Unknown')}: {str(e)}")
        
        except Exception as e:
            errors.append(f"General import error: {str(e)}")
        
        return {
            "imported_count": imported_count,
            "errors": errors,
            "success": len(errors) == 0
        }