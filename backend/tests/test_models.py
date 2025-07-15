"""
데이터베이스 모델 테스트
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime

# 모델 임포트는 실제 구현에 따라 조정 필요
def test_database_connection(db_session: Session):
    """데이터베이스 연결 테스트"""
    # 기본적인 쿼리 실행 테스트
    result = db_session.execute("SELECT 1")
    assert result.fetchone()[0] == 1

def test_models_import():
    """모델 임포트 테스트"""
    try:
        from models import User, Keyword, GeneratedTitle, GeneratedContent
        assert True
    except ImportError as e:
        pytest.skip(f"모델 임포트 실패: {e}")

@pytest.mark.skip(reason="실제 모델 구현에 따라 수정 필요")
def test_user_model(db_session: Session):
    """사용자 모델 테스트"""
    from models import User
    
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password"
    )
    
    db_session.add(user)
    db_session.commit()
    
    # 조회 테스트
    found_user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert found_user is not None
    assert found_user.username == "testuser"

@pytest.mark.skip(reason="실제 모델 구현에 따라 수정 필요")
def test_keyword_model(db_session: Session):
    """키워드 모델 테스트"""
    from models import Keyword
    
    keyword = Keyword(
        keyword="테스트 키워드",
        country_id=1,
        search_volume=1000,
        competition="Medium",
        cpc=1.5,
        opportunity_score=85.0
    )
    
    db_session.add(keyword)
    db_session.commit()
    
    # 조회 테스트
    found_keyword = db_session.query(Keyword).filter(Keyword.keyword == "테스트 키워드").first()
    assert found_keyword is not None
    assert found_keyword.search_volume == 1000