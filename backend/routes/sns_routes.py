from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import asyncio
import httpx
# from ..utils.crypto_utils import encrypt_data, decrypt_data

router = APIRouter(prefix="/api/sns", tags=["sns"])

# SNS 플랫폼 설정
SNS_PLATFORMS = {
    "twitter": {
        "name": "Twitter/X",
        "api_endpoint": "https://api.twitter.com/2/tweets",
        "char_limit": 280,
        "media_support": True
    },
    "facebook": {
        "name": "Facebook",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "char_limit": 63206,
        "media_support": True
    },
    "instagram": {
        "name": "Instagram",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "char_limit": 2200,
        "media_support": True,
        "requires_media": True
    },
    "linkedin": {
        "name": "LinkedIn",
        "api_endpoint": "https://api.linkedin.com/v2",
        "char_limit": 3000,
        "media_support": True
    },
    "youtube": {
        "name": "YouTube",
        "api_endpoint": "https://www.googleapis.com/youtube/v3",
        "char_limit": 5000,
        "media_support": True,
        "video_only": True
    },
    "threads": {
        "name": "Threads",
        "api_endpoint": "https://graph.threads.net/v1.0",
        "char_limit": 500,
        "media_support": True,
        "oauth_required": True,
        "two_step_posting": True
    }
}

# 임시 저장소 (실제로는 데이터베이스 사용)
connected_accounts = {}
scheduled_posts = []

class SNSAccount(BaseModel):
    platform: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    account_info: Optional[Dict] = None

class SNSPost(BaseModel):
    content: str
    platforms: List[str]
    scheduled_time: Optional[datetime] = None
    hashtags: Optional[List[str]] = []
    media_urls: Optional[List[str]] = []
    location: Optional[str] = None

class PostResponse(BaseModel):
    post_id: str
    platform: str
    status: str
    url: Optional[str] = None
    error: Optional[str] = None

@router.post("/connect")
async def connect_sns_account(account: SNSAccount):
    """SNS 계정 연결"""
    try:
        # 토큰 암호화 (임시로 평문 저장)
        encrypted_token = account.access_token  # encrypt_data(account.access_token)
        
        # 계정 정보 저장
        connected_accounts[account.platform] = {
            "access_token": encrypted_token,
            "refresh_token": account.refresh_token,
            "expires_at": account.expires_at,
            "account_info": account.account_info,
            "connected_at": datetime.utcnow()
        }
        
        return {
            "status": "success",
            "platform": account.platform,
            "message": f"{SNS_PLATFORMS[account.platform]['name']} 계정이 연결되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts")
async def get_connected_accounts():
    """연결된 SNS 계정 목록 조회"""
    accounts = []
    for platform, account_data in connected_accounts.items():
        accounts.append({
            "platform": platform,
            "name": SNS_PLATFORMS[platform]["name"],
            "connected": True,
            "connected_at": account_data["connected_at"],
            "account_info": account_data.get("account_info", {})
        })
    
    # 연결되지 않은 플랫폼도 포함
    for platform, platform_info in SNS_PLATFORMS.items():
        if platform not in connected_accounts:
            accounts.append({
                "platform": platform,
                "name": platform_info["name"],
                "connected": False
            })
    
    return accounts

@router.post("/post")
async def create_sns_post(post: SNSPost):
    """SNS 포스트 생성 및 게시"""
    results = []
    
    for platform in post.platforms:
        if platform not in connected_accounts:
            results.append(PostResponse(
                post_id="",
                platform=platform,
                status="error",
                error=f"{platform} 계정이 연결되지 않았습니다."
            ))
            continue
        
        try:
            # 플랫폼별 포스트 처리
            result = await post_to_platform(platform, post)
            results.append(result)
        except Exception as e:
            results.append(PostResponse(
                post_id="",
                platform=platform,
                status="error",
                error=str(e)
            ))
    
    return results

@router.post("/schedule")
async def schedule_sns_post(post: SNSPost):
    """SNS 포스트 예약"""
    if not post.scheduled_time:
        raise HTTPException(status_code=400, detail="예약 시간이 필요합니다.")
    
    post_data = {
        "id": len(scheduled_posts) + 1,
        "content": post.content,
        "platforms": post.platforms,
        "scheduled_time": post.scheduled_time,
        "hashtags": post.hashtags,
        "media_urls": post.media_urls,
        "status": "scheduled",
        "created_at": datetime.utcnow()
    }
    
    scheduled_posts.append(post_data)
    
    return {
        "status": "success",
        "post_id": post_data["id"],
        "scheduled_time": post.scheduled_time,
        "platforms": post.platforms
    }

@router.get("/scheduled")
async def get_scheduled_posts():
    """예약된 포스트 목록 조회"""
    return scheduled_posts

@router.get("/analytics/{platform}")
async def get_sns_analytics(platform: str):
    """SNS 플랫폼별 분석 데이터 조회"""
    # 실제로는 각 플랫폼 API를 통해 데이터를 가져옴
    # 여기서는 샘플 데이터 반환
    
    analytics_data = {
        "platform": platform,
        "period": "last_7_days",
        "metrics": {
            "impressions": 1234,
            "engagement_rate": 89,
            "clicks": 456,
            "new_followers": 67,
            "posts_published": 12
        },
        "top_posts": [
            {
                "content": "AI 시대의 콘텐츠 마케팅 전략",
                "impressions": 523,
                "engagement": 45,
                "published_at": "2025-07-12T09:00:00"
            },
            {
                "content": "블로그 자동화로 시간 절약하기",
                "impressions": 412,
                "engagement": 38,
                "published_at": "2025-07-11T14:00:00"
            }
        ],
        "audience_insights": {
            "top_countries": ["KR", "US", "JP"],
            "age_range": {"18-24": 15, "25-34": 35, "35-44": 30, "45+": 20},
            "gender": {"male": 45, "female": 55}
        }
    }
    
    return analytics_data

@router.post("/auto-share/{content_id}")
async def auto_share_blog_content(content_id: str):
    """블로그 콘텐츠를 SNS에 자동 공유"""
    # 실제로는 content_id로 블로그 콘텐츠를 조회
    blog_content = {
        "title": "AI 시대의 콘텐츠 마케팅 전략",
        "excerpt": "인공지능이 콘텐츠 마케팅을 어떻게 변화시키고 있는지 알아보세요.",
        "url": f"https://yourblog.com/posts/{content_id}",
        "featured_image": "https://yourblog.com/images/ai-marketing.jpg"
    }
    
    # 각 플랫폼에 맞게 콘텐츠 최적화
    platform_posts = {
        "twitter": f"{blog_content['title']} {blog_content['url']} #AI #마케팅 #블로그",
        "facebook": f"{blog_content['title']}\n\n{blog_content['excerpt']}\n\n자세히 보기: {blog_content['url']}",
        "linkedin": f"새 블로그 포스트를 공유합니다.\n\n{blog_content['title']}\n\n{blog_content['excerpt']}\n\n{blog_content['url']}"
    }
    
    results = []
    for platform, content in platform_posts.items():
        if platform in connected_accounts:
            post = SNSPost(
                content=content,
                platforms=[platform],
                media_urls=[blog_content['featured_image']]
            )
            result = await create_sns_post(post)
            results.extend(result)
    
    return {
        "blog_content_id": content_id,
        "shared_to": [r.platform for r in results if r.status == "success"],
        "results": results
    }

async def post_to_platform(platform: str, post: SNSPost) -> PostResponse:
    """플랫폼별 포스트 처리 (실제 API 호출은 구현 필요)"""
    # 실제로는 각 플랫폼 API를 호출
    # 여기서는 시뮬레이션
    
    # 콘텐츠 길이 확인
    char_limit = SNS_PLATFORMS[platform]["char_limit"]
    if len(post.content) > char_limit:
        raise ValueError(f"콘텐츠가 {platform}의 글자 수 제한({char_limit}자)을 초과했습니다.")
    
    # 플랫폼별 요구사항 확인
    if platform == "instagram" and not post.media_urls:
        raise ValueError("Instagram은 이미지가 필요합니다.")
    
    # 해시태그 추가
    content_with_hashtags = post.content
    if post.hashtags:
        hashtag_string = " ".join([f"#{tag}" for tag in post.hashtags])
        content_with_hashtags = f"{post.content}\n\n{hashtag_string}"
    
    # Threads 특별 처리 (2단계 포스팅)
    if platform == "threads":
        # 실제 구현 시:
        # 1. 미디어 컨테이너 생성
        # 2. threads_publish 엔드포인트로 발행
        post_id = f"threads_{datetime.utcnow().timestamp()}"
        post_url = f"https://www.threads.net/@username/post/{post_id}"
    else:
        # 시뮬레이션된 포스트 ID와 URL
        post_id = f"{platform}_{datetime.utcnow().timestamp()}"
        post_url = f"https://{platform}.com/posts/{post_id}"
    
    return PostResponse(
        post_id=post_id,
        platform=platform,
        status="success",
        url=post_url
    )