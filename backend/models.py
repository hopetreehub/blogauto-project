from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, DECIMAL, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects import sqlite
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

class PromptType(enum.Enum):
    KEYWORD_ANALYSIS = "keyword_analysis"
    TITLE_GENERATION = "title_generation"
    BLOG_WRITING = "blog_writing"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    keywords = relationship("Keyword", back_populates="creator")
    titles = relationship("GeneratedTitle", back_populates="creator")
    content = relationship("GeneratedContent", back_populates="creator")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    api_keys = relationship("APIKey", back_populates="user")

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(2), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    keywords = relationship("Keyword", back_populates="country")

class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    keyword = Column(String(500), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"))
    search_volume = Column(Integer, default=0)
    competition = Column(String(20))
    cpc = Column(DECIMAL(10, 2), default=0.00)
    opportunity_score = Column(Integer)
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    country = relationship("Country", back_populates="keywords")
    creator = relationship("User", back_populates="keywords")
    titles = relationship("GeneratedTitle", back_populates="keyword")

class GeneratedTitle(Base):
    __tablename__ = "generated_titles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    keyword_id = Column(String(36), ForeignKey("keywords.id"))
    title = Column(Text, nullable=False)
    length_option = Column(String(20))
    language = Column(String(5), default="ko")
    tone = Column(String(20))
    duplicate_rate = Column(DECIMAL(5, 2), default=0.00)
    ai_model = Column(String(50))
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    keyword = relationship("Keyword", back_populates="titles")
    creator = relationship("User", back_populates="titles")
    content = relationship("GeneratedContent", back_populates="title")

class GeneratedContent(Base):
    __tablename__ = "generated_content"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title_id = Column(String(36), ForeignKey("generated_titles.id"))
    content = Column(Text, nullable=False)
    keywords = Column(Text)  # Store as JSON string or comma-separated
    seo_score = Column(Integer)
    geo_score = Column(Integer)
    copyscape_result = Column(String(20), default="Pending")
    ai_model = Column(String(50))
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    title = relationship("GeneratedTitle", back_populates="content")
    creator = relationship("User", back_populates="content")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    default_language = Column(String(5), default="ko")
    default_tone = Column(String(20), default="professional")
    keywords_per_search = Column(Integer, default=10)
    titles_per_generation = Column(Integer, default=5)
    auto_save = Column(Boolean, default=True)
    project_folder = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="settings")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    service_name = Column(String(50), nullable=False)
    api_key_encrypted = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class SystemPrompt(Base):
    __tablename__ = "system_prompts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_type = Column(Enum(PromptType), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    prompt_content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    version = Column(String(20), default="1.0")
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_name = Column(String(100), nullable=False)
    template_type = Column(Enum(PromptType), nullable=False)
    template_content = Column(Text, nullable=False)
    variables = Column(Text)  # JSON string for template variables
    usage_count = Column(Integer, default=0)
    is_system_template = Column(Boolean, default=False)
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

class Site(Base):
    __tablename__ = "sites"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    
    # WordPress 연동 정보
    wordpress_url = Column(String(500))
    wordpress_username = Column(String(100))
    wordpress_password_encrypted = Column(Text)  # 암호화된 비밀번호
    
    # 지침 설정
    keyword_guideline_id = Column(String(36), ForeignKey("system_prompts.id"))
    title_guideline_id = Column(String(36), ForeignKey("system_prompts.id"))
    blog_guideline_id = Column(String(36), ForeignKey("system_prompts.id"))
    
    # 사이트 설정
    is_active = Column(Boolean, default=True)
    auto_posting_enabled = Column(Boolean, default=False)
    posting_interval_hours = Column(Integer, default=24)
    
    # 사용자 및 통계
    created_by = Column(String(36), ForeignKey("users.id"))
    total_keywords_generated = Column(Integer, default=0)
    total_titles_generated = Column(Integer, default=0)
    total_posts_generated = Column(Integer, default=0)
    total_posts_published = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    keyword_guideline = relationship("SystemPrompt", foreign_keys=[keyword_guideline_id])
    title_guideline = relationship("SystemPrompt", foreign_keys=[title_guideline_id])
    blog_guideline = relationship("SystemPrompt", foreign_keys=[blog_guideline_id])
    automation_sessions = relationship("AutomationSession", back_populates="site")

class AutomationSession(Base):
    __tablename__ = "automation_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String(36), ForeignKey("sites.id"), nullable=False)
    category = Column(String(100), nullable=False)
    
    # 진행 단계 상태
    step_status = Column(String(50), default="started")  # started, keywords_generated, titles_generated, content_generated, published, completed
    
    # 생성된 데이터 (JSON 형태로 저장)
    generated_keywords = Column(Text)  # JSON: [{keyword, score, trend_data}, ...]
    generated_titles = Column(Text)    # JSON: [{title, viral_score, seo_score, click_potential}, ...]
    generated_contents = Column(Text)  # JSON: [{title, content, seo_score, geo_score, word_count}, ...]
    
    # 선택된 항목들
    selected_keywords = Column(Text)   # JSON: [keyword1, keyword2, ...]
    selected_titles = Column(Text)     # JSON: [title1, title2, ...]
    
    # 포스팅 결과
    posted_contents = Column(Text)     # JSON: [{title, wordpress_post_id, post_url, status}, ...]
    
    # 세션 통계
    keywords_count = Column(Integer, default=0)
    titles_count = Column(Integer, default=0)
    contents_count = Column(Integer, default=0)
    published_count = Column(Integer, default=0)
    
    # 세션 설정
    auto_posting_enabled = Column(Boolean, default=False)
    posting_schedule = Column(Text)    # JSON: 포스팅 스케줄 설정
    
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="automation_sessions")
    creator = relationship("User", foreign_keys=[created_by])
    keyword_batches = relationship("GeneratedKeywordBatch", back_populates="session")
    title_batches = relationship("GeneratedTitleBatch", back_populates="session")
    posting_results = relationship("PostingResult", back_populates="session")

class GeneratedKeywordBatch(Base):
    __tablename__ = "generated_keyword_batches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("automation_sessions.id"), nullable=False)
    category = Column(String(100), nullable=False)
    
    # 키워드 데이터 (JSON)
    keywords_data = Column(Text, nullable=False)  # JSON: [{keyword, search_volume, competition, trend_score, seo_score, seasonal, reason}, ...]
    
    # 배치 통계
    total_count = Column(Integer, default=0)
    average_seo_score = Column(DECIMAL(5, 2), default=0.00)
    average_trend_score = Column(DECIMAL(5, 2), default=0.00)
    
    # 생성 설정
    generation_params = Column(Text)  # JSON: 생성 시 사용된 파라미터
    guideline_used = Column(String(36), ForeignKey("system_prompts.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("AutomationSession", back_populates="keyword_batches")
    guideline = relationship("SystemPrompt", foreign_keys=[guideline_used])

class GeneratedTitleBatch(Base):
    __tablename__ = "generated_title_batches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("automation_sessions.id"), nullable=False)
    keyword = Column(String(500), nullable=False)
    
    # 제목 데이터 (JSON)
    titles_data = Column(Text, nullable=False)  # JSON: [{title, seo_score, viral_score, click_potential, length, format_type}, ...]
    
    # 배치 통계
    total_count = Column(Integer, default=0)
    average_viral_score = Column(DECIMAL(5, 2), default=0.00)
    average_seo_score = Column(DECIMAL(5, 2), default=0.00)
    average_click_potential = Column(DECIMAL(5, 2), default=0.00)
    
    # 생성 설정
    generation_params = Column(Text)  # JSON: 생성 시 사용된 파라미터
    guideline_used = Column(String(36), ForeignKey("system_prompts.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("AutomationSession", back_populates="title_batches")
    guideline = relationship("SystemPrompt", foreign_keys=[guideline_used])

class PostingResult(Base):
    __tablename__ = "posting_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("automation_sessions.id"), nullable=False)
    site_id = Column(String(36), ForeignKey("sites.id"), nullable=False)
    
    # 포스팅 내용
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    
    # WordPress 포스팅 정보
    wordpress_post_id = Column(String(50))
    post_url = Column(String(1000))
    post_status = Column(String(50), default="draft")  # draft, published, scheduled, failed
    
    # 스케줄링 정보
    scheduled_time = Column(DateTime(timezone=True))
    posted_time = Column(DateTime(timezone=True))
    
    # 에러 및 상태 정보
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # 포스팅 설정
    posting_params = Column(Text)  # JSON: 포스팅 시 사용된 설정
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("AutomationSession", back_populates="posting_results")
    site = relationship("Site", foreign_keys=[site_id])