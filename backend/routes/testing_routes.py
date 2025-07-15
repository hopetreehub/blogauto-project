from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import statistics
import math

router = APIRouter(prefix="/api/testing", tags=["testing"])

# A/B 테스트 데이터 저장소 (실제로는 데이터베이스 사용)
ab_tests = {}
test_results = {}

class TestVariant(BaseModel):
    id: str
    name: str
    content: str
    metrics: Dict[str, float] = {
        "views": 0,
        "clicks": 0,
        "conversions": 0,
        "bounceRate": 0.0,
        "avgTimeOnPage": 0.0
    }
    isWinner: Optional[bool] = False

class ABTest(BaseModel):
    id: Optional[str] = None
    name: str
    status: str = "draft"  # draft, running, paused, completed
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    variants: List[TestVariant]
    targetMetric: str = "clicks"
    confidenceLevel: float = 95.0
    sampleSize: int = 1000
    currentSampleSize: int = 0
    category: Optional[str] = None
    tags: Optional[List[str]] = []

class TestResult(BaseModel):
    testId: str
    variantId: str
    userId: str
    action: str  # view, click, conversion
    timestamp: datetime
    sessionDuration: Optional[float] = None

@router.post("/create")
async def create_ab_test(test: ABTest):
    """새 A/B 테스트 생성"""
    test_id = f"test_{len(ab_tests) + 1}_{datetime.now().timestamp()}"
    test.id = test_id
    test.status = "draft"
    
    ab_tests[test_id] = test
    test_results[test_id] = []
    
    return {
        "success": True,
        "test_id": test_id,
        "message": "A/B 테스트가 생성되었습니다"
    }

@router.get("/list")
async def get_ab_tests(status: Optional[str] = None):
    """A/B 테스트 목록 조회"""
    tests = list(ab_tests.values())
    
    if status:
        tests = [t for t in tests if t.status == status]
    
    # 각 테스트의 현재 성과 계산
    for test in tests:
        if test.id in test_results:
            update_test_metrics(test)
    
    return {
        "success": True,
        "tests": tests,
        "total": len(tests)
    }

@router.get("/{test_id}")
async def get_ab_test(test_id: str):
    """특정 A/B 테스트 상세 조회"""
    if test_id not in ab_tests:
        raise HTTPException(status_code=404, detail="테스트를 찾을 수 없습니다")
    
    test = ab_tests[test_id]
    update_test_metrics(test)
    
    # 통계적 분석 추가
    analysis = perform_statistical_analysis(test)
    
    return {
        "success": True,
        "test": test,
        "analysis": analysis
    }

@router.put("/{test_id}/status")
async def update_test_status(test_id: str, status: str):
    """테스트 상태 업데이트"""
    if test_id not in ab_tests:
        raise HTTPException(status_code=404, detail="테스트를 찾을 수 없습니다")
    
    test = ab_tests[test_id]
    old_status = test.status
    test.status = status
    
    # 상태 변경에 따른 날짜 업데이트
    if status == "running" and old_status == "draft":
        test.startDate = datetime.now().isoformat()
    elif status == "completed":
        test.endDate = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": f"테스트 상태가 {status}로 변경되었습니다"
    }

@router.post("/{test_id}/track")
async def track_test_event(test_id: str, result: TestResult):
    """테스트 이벤트 추적"""
    if test_id not in ab_tests:
        raise HTTPException(status_code=404, detail="테스트를 찾을 수 없습니다")
    
    if test_id not in test_results:
        test_results[test_id] = []
    
    test_results[test_id].append(result)
    
    # 실시간 메트릭 업데이트
    test = ab_tests[test_id]
    update_test_metrics(test)
    
    return {
        "success": True,
        "message": "이벤트가 기록되었습니다"
    }

@router.post("/{test_id}/simulate")
async def simulate_test_data(test_id: str, days: int = 7):
    """테스트 데이터 시뮬레이션 (개발/테스트용)"""
    if test_id not in ab_tests:
        raise HTTPException(status_code=404, detail="테스트를 찾을 수 없습니다")
    
    test = ab_tests[test_id]
    
    # 각 변형에 대해 시뮬레이션 데이터 생성
    for day in range(days):
        for variant in test.variants:
            # 일일 방문자 수 (변형별로 약간의 차이)
            daily_visitors = random.randint(50, 150)
            
            # 변형별 성과 차이 시뮬레이션
            if variant.id == 'b':  # B 변형이 약간 더 좋은 성과
                click_rate = random.uniform(0.15, 0.25)
                conversion_rate = random.uniform(0.08, 0.12)
            else:
                click_rate = random.uniform(0.10, 0.20)
                conversion_rate = random.uniform(0.05, 0.10)
            
            for _ in range(daily_visitors):
                user_id = f"user_{random.randint(1000, 9999)}"
                timestamp = datetime.now() - timedelta(days=days-day, hours=random.randint(0, 23))
                
                # 조회 이벤트
                view_result = TestResult(
                    testId=test_id,
                    variantId=variant.id,
                    userId=user_id,
                    action="view",
                    timestamp=timestamp
                )
                test_results[test_id].append(view_result)
                
                # 클릭 이벤트
                if random.random() < click_rate:
                    click_result = TestResult(
                        testId=test_id,
                        variantId=variant.id,
                        userId=user_id,
                        action="click",
                        timestamp=timestamp + timedelta(seconds=random.randint(5, 30)),
                        sessionDuration=random.uniform(30, 300)
                    )
                    test_results[test_id].append(click_result)
                    
                    # 전환 이벤트
                    if random.random() < conversion_rate:
                        conversion_result = TestResult(
                            testId=test_id,
                            variantId=variant.id,
                            userId=user_id,
                            action="conversion",
                            timestamp=timestamp + timedelta(seconds=random.randint(60, 600))
                        )
                        test_results[test_id].append(conversion_result)
    
    # 메트릭 업데이트
    update_test_metrics(test)
    
    return {
        "success": True,
        "message": f"{days}일간의 시뮬레이션 데이터가 생성되었습니다",
        "total_events": len(test_results[test_id])
    }

@router.get("/{test_id}/report")
async def get_test_report(test_id: str):
    """테스트 결과 리포트 생성"""
    if test_id not in ab_tests:
        raise HTTPException(status_code=404, detail="테스트를 찾을 수 없습니다")
    
    test = ab_tests[test_id]
    update_test_metrics(test)
    
    # 상세 분석
    analysis = perform_statistical_analysis(test)
    
    # 리포트 생성
    report = {
        "test_info": {
            "id": test.id,
            "name": test.name,
            "status": test.status,
            "duration": calculate_test_duration(test),
            "total_participants": test.currentSampleSize
        },
        "results": [],
        "winner": None,
        "confidence_level": 0,
        "recommendations": []
    }
    
    # 각 변형의 결과
    for variant in test.variants:
        variant_results = {
            "variant_id": variant.id,
            "variant_name": variant.name,
            "metrics": variant.metrics,
            "conversion_rate": calculate_conversion_rate(variant),
            "relative_improvement": 0
        }
        report["results"].append(variant_results)
    
    # 승자 결정 및 개선율 계산
    if len(test.variants) >= 2 and analysis["significant"]:
        control = report["results"][0]
        variant = report["results"][1]
        
        if variant["conversion_rate"] > control["conversion_rate"]:
            report["winner"] = variant["variant_id"]
            improvement = ((variant["conversion_rate"] - control["conversion_rate"]) / control["conversion_rate"]) * 100
            variant["relative_improvement"] = improvement
        else:
            report["winner"] = control["variant_id"]
            improvement = ((control["conversion_rate"] - variant["conversion_rate"]) / variant["conversion_rate"]) * 100
            control["relative_improvement"] = improvement
    
    report["confidence_level"] = analysis["confidence_level"]
    
    # 권장사항 생성
    report["recommendations"] = generate_recommendations(test, analysis)
    
    return {
        "success": True,
        "report": report
    }

# 헬퍼 함수들
def normal_cdf(x):
    """표준정규분포의 누적분포함수 근사"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def update_test_metrics(test: ABTest):
    """테스트 메트릭 업데이트"""
    if test.id not in test_results:
        return
    
    results = test_results[test.id]
    
    for variant in test.variants:
        variant_results = [r for r in results if r.variantId == variant.id]
        
        views = len([r for r in variant_results if r.action == "view"])
        clicks = len([r for r in variant_results if r.action == "click"])
        conversions = len([r for r in variant_results if r.action == "conversion"])
        
        variant.metrics["views"] = views
        variant.metrics["clicks"] = clicks
        variant.metrics["conversions"] = conversions
        
        # 클릭률과 전환율 계산
        if views > 0:
            variant.metrics["clickRate"] = (clicks / views) * 100
            variant.metrics["conversionRate"] = (conversions / views) * 100
        
        # 평균 체류 시간 계산
        session_durations = [r.sessionDuration for r in variant_results if r.sessionDuration]
        if session_durations:
            variant.metrics["avgTimeOnPage"] = statistics.mean(session_durations)
        
        # 이탈률 시뮬레이션 (실제로는 더 복잡한 계산 필요)
        if views > 0:
            variant.metrics["bounceRate"] = random.uniform(25, 45)
    
    # 전체 샘플 크기 업데이트
    test.currentSampleSize = sum(v.metrics["views"] for v in test.variants)

def perform_statistical_analysis(test: ABTest) -> Dict:
    """통계적 유의성 분석"""
    if len(test.variants) < 2:
        return {"significant": False, "confidence_level": 0, "p_value": 1.0}
    
    # 대조군과 실험군
    control = test.variants[0]
    variant = test.variants[1]
    
    # 클릭 수와 조회 수
    control_clicks = control.metrics.get("clicks", 0)
    control_views = control.metrics.get("views", 1)
    variant_clicks = variant.metrics.get("clicks", 0)
    variant_views = variant.metrics.get("views", 1)
    
    # 전환율
    control_rate = control_clicks / control_views if control_views > 0 else 0
    variant_rate = variant_clicks / variant_views if variant_views > 0 else 0
    
    # 최소 샘플 크기 확인
    if control_views < 30 or variant_views < 30:
        return {
            "significant": False,
            "confidence_level": 0,
            "p_value": 1.0,
            "message": "샘플 크기가 너무 작습니다"
        }
    
    # Z-test for proportions (simplified)
    pooled_rate = (control_clicks + variant_clicks) / (control_views + variant_views)
    se = math.sqrt(pooled_rate * (1 - pooled_rate) * (1/control_views + 1/variant_views))
    
    if se == 0:
        return {"significant": False, "confidence_level": 0, "p_value": 1.0}
    
    z_score = (variant_rate - control_rate) / se
    
    # 간단한 정규분포 근사
    p_value = 2 * (1 - normal_cdf(abs(z_score)))
    
    confidence_level = (1 - p_value) * 100
    significant = p_value < 0.05
    
    return {
        "significant": significant,
        "confidence_level": confidence_level,
        "p_value": p_value,
        "z_score": z_score,
        "control_rate": control_rate,
        "variant_rate": variant_rate
    }

def calculate_conversion_rate(variant: TestVariant) -> float:
    """전환율 계산"""
    views = variant.metrics.get("views", 0)
    clicks = variant.metrics.get("clicks", 0)
    
    if views == 0:
        return 0.0
    
    return (clicks / views) * 100

def calculate_test_duration(test: ABTest) -> str:
    """테스트 기간 계산"""
    if not test.startDate:
        return "시작 전"
    
    start = datetime.fromisoformat(test.startDate.replace('Z', '+00:00'))
    
    if test.endDate:
        end = datetime.fromisoformat(test.endDate.replace('Z', '+00:00'))
    else:
        end = datetime.now()
    
    duration = end - start
    
    if duration.days > 0:
        return f"{duration.days}일"
    else:
        return f"{duration.seconds // 3600}시간"

def generate_recommendations(test: ABTest, analysis: Dict) -> List[str]:
    """테스트 결과에 따른 권장사항 생성"""
    recommendations = []
    
    # 통계적 유의성 확인
    if not analysis["significant"]:
        if test.currentSampleSize < test.sampleSize * 0.5:
            recommendations.append("더 많은 데이터가 필요합니다. 목표 샘플 크기의 50% 이상 도달할 때까지 테스트를 계속하세요.")
        else:
            recommendations.append("두 변형 간 유의미한 차이가 없습니다. 다른 변형을 테스트해보세요.")
    else:
        confidence = analysis["confidence_level"]
        if confidence >= 95:
            recommendations.append("통계적으로 유의미한 결과입니다. 승자 변형을 채택할 수 있습니다.")
        elif confidence >= 90:
            recommendations.append("90% 신뢰수준에 도달했습니다. 더 확실한 결과를 위해 조금 더 테스트를 진행하세요.")
    
    # 샘플 크기 확인
    if test.currentSampleSize >= test.sampleSize:
        recommendations.append("목표 샘플 크기에 도달했습니다. 결과를 분석하고 결정을 내릴 시기입니다.")
    
    # 테스트 기간 확인
    if test.startDate:
        start = datetime.fromisoformat(test.startDate.replace('Z', '+00:00'))
        duration = (datetime.now() - start).days
        
        if duration < 7:
            recommendations.append("최소 1주일 이상 테스트를 진행하여 주기적 변동을 고려하세요.")
        elif duration > 30:
            recommendations.append("테스트가 30일 이상 진행되었습니다. 결과를 확정하고 다음 테스트를 계획하세요.")
    
    return recommendations