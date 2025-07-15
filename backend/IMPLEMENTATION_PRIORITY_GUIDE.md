# BlogAuto 구현 우선순위 가이드

## 🚨 즉시 수정 필요 (1주 이내)

### 1. 보안 강화
```python
# backend/security_improvements.py
from typing import Optional
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends, Header
from passlib.context import CryptContext

# 1. JWT 인증 시스템
class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.ALGORITHM = "HS256"
    
    def create_access_token(self, data: dict):
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

# 2. API 키 프록시
@app.post("/api/secure/generate-content")
async def secure_generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    # 백엔드에서 API 키 관리
    api_key = await get_user_api_key(current_user["id"])
    # 실제 API 호출
    return await generate_content_internal(request, api_key)
```

### 2. 프론트엔드 보안 개선
```tsx
// nextjs-app/src/utils/secureApi.ts
class SecureAPIClient {
  private token: string | null = null;
  
  async login(email: string, password: string) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.token = data.access_token;
    // 메모리에만 저장, localStorage 사용 금지
    return data;
  }
  
  async secureRequest(endpoint: string, options: RequestInit = {}) {
    if (!this.token) throw new Error('Not authenticated');
    
    return fetch(endpoint, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.token}`
      }
    });
  }
}
```

## 🎨 UX/UI 개선 (2주 이내)

### 1. 디자인 시스템 구축
```tsx
// nextjs-app/src/design-system/tokens.ts
export const colors = {
  primary: {
    50: '#eff6ff',
    500: '#3b82f6',
    900: '#1e3a8a'
  },
  semantic: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444'
  }
};

export const typography = {
  heading: {
    1: 'text-4xl font-bold',
    2: 'text-3xl font-semibold',
    3: 'text-2xl font-medium'
  }
};

// 아이콘 시스템
import { 
  MagnifyingGlassIcon,
  PencilIcon,
  DocumentTextIcon,
  PhotoIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

export const icons = {
  search: MagnifyingGlassIcon,
  edit: PencilIcon,
  document: DocumentTextIcon,
  image: PhotoIcon,
  publish: RocketLaunchIcon
};
```

### 2. 토스트 시스템
```tsx
// nextjs-app/src/components/Toast.tsx
import { createContext, useContext, useState } from 'react';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

const ToastContext = createContext<{
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}>({
  toasts: [],
  addToast: () => {},
  removeToast: () => {}
});

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
};
```

## ⚡ 성능 최적화 (3주 이내)

### 1. 캐싱 시스템 활성화
```python
# backend/caching_config.py
import redis
from functools import wraps
import json
import hashlib

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

def cached(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{hashlib.md5(str(args).encode()).hexdigest()}"
            
            # 캐시 확인
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 실행 및 캐싱
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

# 사용 예시
@cached(expire=3600)
async def get_keywords(keyword: str):
    # API 호출
    return await analyze_keywords(keyword)
```

### 2. 프론트엔드 최적화
```tsx
// nextjs-app/next.config.js
const nextConfig = {
  images: {
    domains: ['oaidalleapiprodscus.blob.core.windows.net'],
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96],
  },
  experimental: {
    optimizeCss: true,
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // 번들 분석
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          vendor: {
            name: 'vendor',
            chunks: 'all',
            test: /node_modules/,
          },
        },
      };
    }
    return config;
  },
};
```

## 🚀 DevOps 구축 (4주 이내)

### 1. GitHub Actions CI/CD
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Frontend tests
      run: |
        cd nextjs-app
        npm ci
        npm test

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t blogauto-backend ./backend
        docker build -t blogauto-frontend ./nextjs-app
    
    - name: Deploy to production
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      run: |
        # 실제 배포 스크립트
        echo "Deploying to production..."
```

### 2. Docker 구성
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/blogauto
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0

  frontend:
    build: ./nextjs-app
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=blogauto
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 💰 비즈니스 모델 구현 (6주 이내)

### 1. 요금제 시스템
```python
# backend/subscription_model.py
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionPlan:
    PLANS = {
        PlanType.FREE: {
            "name": "무료",
            "price": 0,
            "limits": {
                "contents_per_month": 5,
                "api_calls_per_day": 100,
                "image_generation": False,
                "wordpress_publishing": True,
                "ai_providers": ["gemini"]  # 무료 AI만
            }
        },
        PlanType.PRO: {
            "name": "프로",
            "price": 29000,  # 원화
            "limits": {
                "contents_per_month": 100,
                "api_calls_per_day": 1000,
                "image_generation": True,
                "wordpress_publishing": True,
                "ai_providers": ["openai", "gemini", "claude"]
            }
        },
        PlanType.ENTERPRISE: {
            "name": "엔터프라이즈",
            "price": "custom",
            "limits": {
                "contents_per_month": -1,  # 무제한
                "api_calls_per_day": -1,
                "image_generation": True,
                "wordpress_publishing": True,
                "ai_providers": "all",
                "team_members": -1,
                "priority_support": True
            }
        }
    }

# 사용량 체크 미들웨어
@app.middleware("http")
async def check_usage_limits(request: Request, call_next):
    if request.url.path.startswith("/api/content/generate"):
        user = get_current_user(request)
        if user:
            usage = await get_user_usage(user.id)
            plan_limits = SubscriptionPlan.PLANS[user.plan_type]["limits"]
            
            if usage.contents_this_month >= plan_limits["contents_per_month"]:
                return JSONResponse(
                    status_code=429,
                    content={"error": "월간 콘텐츠 생성 한도 초과"}
                )
    
    response = await call_next(request)
    return response
```

### 2. 분석 대시보드
```tsx
// nextjs-app/src/components/AnalyticsDashboard.tsx
import { useEffect, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';

export function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState({
    contentPerformance: [],
    keywordTrends: [],
    publishingStats: []
  });
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* 콘텐츠 성과 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">콘텐츠 성과</h3>
        <Line 
          data={{
            labels: analytics.contentPerformance.map(d => d.date),
            datasets: [{
              label: '조회수',
              data: analytics.contentPerformance.map(d => d.views),
              borderColor: 'rgb(59, 130, 246)',
              tension: 0.1
            }]
          }}
        />
      </div>
      
      {/* SEO 점수 추이 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">평균 SEO 점수</h3>
        <div className="text-4xl font-bold text-green-600">
          {analytics.avgSeoScore}
        </div>
        <div className="text-sm text-gray-500 mt-2">
          지난 30일 평균
        </div>
      </div>
      
      {/* 키워드 트렌드 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">인기 키워드</h3>
        <Bar 
          data={{
            labels: analytics.keywordTrends.map(k => k.keyword),
            datasets: [{
              label: '사용 횟수',
              data: analytics.keywordTrends.map(k => k.count),
              backgroundColor: 'rgba(59, 130, 246, 0.5)'
            }]
          }}
          options={{
            indexAxis: 'y'
          }}
        />
      </div>
    </div>
  );
}
```

## 📈 성공 지표 모니터링

### 실시간 대시보드 구현
```python
# backend/metrics_dashboard.py
from prometheus_client import Counter, Histogram, Gauge

# 메트릭 정의
api_requests = Counter('blogauto_api_requests_total', 'Total API requests', ['endpoint', 'method'])
api_latency = Histogram('blogauto_api_latency_seconds', 'API latency', ['endpoint'])
active_users = Gauge('blogauto_active_users', 'Current active users')
content_generated = Counter('blogauto_content_generated_total', 'Total content generated', ['type'])

# 커스텀 메트릭 수집
@app.middleware("http")
async def collect_metrics(request: Request, call_next):
    start_time = time.time()
    
    # 요청 카운트
    api_requests.labels(
        endpoint=request.url.path,
        method=request.method
    ).inc()
    
    response = await call_next(request)
    
    # 레이턴시 측정
    api_latency.labels(endpoint=request.url.path).observe(
        time.time() - start_time
    )
    
    return response
```

이 구현 가이드를 따라 단계별로 진행하면 BlogAuto 시스템을 안전하고 확장 가능한 플랫폼으로 발전시킬 수 있습니다.