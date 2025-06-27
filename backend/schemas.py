from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Keyword schemas
class KeywordBase(BaseModel):
    keyword: str
    country_id: Optional[int] = None

class KeywordCreate(KeywordBase):
    pass

class KeywordResponse(KeywordBase):
    id: UUID
    search_volume: int
    competition: Optional[str]
    cpc: float
    opportunity_score: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# API request/response schemas
class KeywordAnalysisRequest(BaseModel):
    keyword: str
    country: str = "KR"
    max_results: int = 10

class KeywordAnalysisResponse(BaseModel):
    keyword: str
    search_volume: int
    competition: str
    cpc: float
    opportunity_score: int

class TitleGenerationRequest(BaseModel):
    keyword: str
    length: str = "medium"
    language: str = "ko"
    tone: str = "professional"
    count: int = 5

class TitleGenerationResponse(BaseModel):
    title: str
    duplicate_rate: float

class ContentGenerationRequest(BaseModel):
    title: str
    keywords: Optional[str] = None
    length: str = "medium"

class ContentGenerationResponse(BaseModel):
    content: str
    seo_score: int
    geo_score: int
    copyscape_result: str

# User settings schemas
class UserSettingsBase(BaseModel):
    default_language: str = "ko"
    default_tone: str = "professional"
    keywords_per_search: int = 10
    titles_per_generation: int = 5
    auto_save: bool = True
    project_folder: Optional[str] = None

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(UserSettingsBase):
    pass

class UserSettingsResponse(UserSettingsBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# API Key schemas
class APIKeyBase(BaseModel):
    service_name: str
    api_key: str

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyResponse(BaseModel):
    id: UUID
    service_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard stats
class DashboardStats(BaseModel):
    keywords_analyzed: int
    titles_generated: int
    content_generated: int
    posts_published: int