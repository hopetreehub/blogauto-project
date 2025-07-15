#!/usr/bin/env python3
"""
전문가 페르소나 - innerspell.com WordPress 실제 발행
추정 금지 - 모든 것을 직접 연결하고 검증
"""

import requests
import json
import base64
from datetime import datetime
import time
import os

class InnerspellWordPressPublisher:
    def __init__(self):
        self.site_url = "https://innerspell.com"
        self.username = "banana"
        self.password = "Hjhv Pp7n L4RC Op8N fqQg A9SO"
        
        # WordPress REST API 엔드포인트
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        
        # 인증 헤더 생성
        credentials = f"{self.username}:{self.password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'BlogAuto-Publisher/1.0'
        }
        
        print(f"🎯 innerspell.com WordPress 발행 시스템 초기화")
        print(f"📡 API 엔드포인트: {self.api_base}")
        print(f"👤 사용자: {self.username}")
    
    def step1_test_authentication(self):
        """Step 1: WordPress 인증 테스트"""
        print("\\n🔍 Step 1: WordPress 인증 테스트...")
        
        try:
            # 사용자 정보 확인
            response = requests.get(
                f"{self.api_base}/users/me",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ 인증 성공!")
                print(f"   👤 사용자 ID: {user_data.get('id', 'N/A')}")
                print(f"   📝 표시명: {user_data.get('name', 'N/A')}")
                print(f"   ✉️ 이메일: {user_data.get('email', 'N/A')}")
                print(f"   🔑 권한: {', '.join(user_data.get('roles', []))}")
                return user_data
            else:
                print(f"   ❌ 인증 실패: {response.status_code}")
                if response.status_code == 401:
                    print("   💡 사용자명 또는 비밀번호가 잘못되었습니다.")
                elif response.status_code == 403:
                    print("   💡 권한이 부족합니다.")
                else:
                    print(f"   💡 응답: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   💥 연결 오류: {str(e)}")
            return None
    
    def step2_check_site_status(self):
        """Step 2: WordPress 사이트 상태 확인"""
        print("\\n🔍 Step 2: WordPress 사이트 상태 확인...")
        
        try:
            # 사이트 기본 정보 확인
            response = requests.get(
                f"{self.site_url}/wp-json",
                timeout=30
            )
            
            if response.status_code == 200:
                site_data = response.json()
                print(f"   ✅ 사이트 접근 성공!")
                print(f"   🌐 사이트명: {site_data.get('name', 'N/A')}")
                print(f"   📄 설명: {site_data.get('description', 'N/A')}")
                print(f"   🔗 URL: {site_data.get('url', 'N/A')}")
                print(f"   🏠 홈 URL: {site_data.get('home', 'N/A')}")
                
                # 네임스페이스 확인
                namespaces = site_data.get('namespaces', [])
                print(f"   🔧 사용 가능한 API: {', '.join(namespaces)}")
                
                return site_data
            else:
                print(f"   ❌ 사이트 접근 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   💥 사이트 연결 오류: {str(e)}")
            return None
    
    def step3_check_categories_tags(self):
        """Step 3: 카테고리 및 태그 확인"""
        print("\\n🔍 Step 3: 카테고리 및 태그 확인...")
        
        categories_info = {}
        tags_info = {}
        
        # 카테고리 확인
        try:
            response = requests.get(
                f"{self.api_base}/categories",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                categories = response.json()
                print(f"   ✅ 카테고리 조회 성공: {len(categories)}개")
                
                for cat in categories[:5]:  # 상위 5개만 표시
                    print(f"      - {cat.get('name', 'N/A')} (ID: {cat.get('id', 'N/A')})")
                    categories_info[cat.get('name', '').lower()] = cat.get('id')
                    
            else:
                print(f"   ❌ 카테고리 조회 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 카테고리 조회 오류: {str(e)}")
        
        # 태그 확인
        try:
            response = requests.get(
                f"{self.api_base}/tags",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                tags = response.json()
                print(f"   ✅ 태그 조회 성공: {len(tags)}개")
                
                for tag in tags[:5]:  # 상위 5개만 표시
                    print(f"      - {tag.get('name', 'N/A')} (ID: {tag.get('id', 'N/A')})")
                    tags_info[tag.get('name', '').lower()] = tag.get('id')
                    
            else:
                print(f"   ❌ 태그 조회 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 태그 조회 오류: {str(e)}")
        
        return categories_info, tags_info
    
    def step4_create_categories_if_needed(self, categories_info):
        """Step 4: 필요한 카테고리 생성"""
        print("\\n🔍 Step 4: 필요한 카테고리 생성...")
        
        required_categories = ["건강", "웰니스", "라이프스타일"]
        created_categories = {}
        
        for category_name in required_categories:
            category_key = category_name.lower()
            
            if category_key not in categories_info:
                try:
                    # 카테고리 생성
                    category_data = {
                        "name": category_name,
                        "description": f"{category_name} 관련 콘텐츠"
                    }
                    
                    response = requests.post(
                        f"{self.api_base}/categories",
                        headers=self.headers,
                        json=category_data,
                        timeout=30
                    )
                    
                    if response.status_code == 201:
                        new_category = response.json()
                        category_id = new_category.get('id')
                        created_categories[category_key] = category_id
                        print(f"   ✅ 카테고리 '{category_name}' 생성 성공 (ID: {category_id})")
                    else:
                        print(f"   ❌ 카테고리 '{category_name}' 생성 실패: {response.status_code}")
                        
                except Exception as e:
                    print(f"   💥 카테고리 '{category_name}' 생성 오류: {str(e)}")
            else:
                created_categories[category_key] = categories_info[category_key]
                print(f"   ℹ️ 카테고리 '{category_name}' 이미 존재 (ID: {categories_info[category_key]})")
        
        return created_categories
    
    def step5_create_tags_if_needed(self, tags_info):
        """Step 5: 필요한 태그 생성"""
        print("\\n🔍 Step 5: 필요한 태그 생성...")
        
        required_tags = ["면역력", "건강", "가이드", "전문가", "팁"]
        created_tags = {}
        
        for tag_name in required_tags:
            tag_key = tag_name.lower()
            
            if tag_key not in tags_info:
                try:
                    # 태그 생성
                    tag_data = {
                        "name": tag_name,
                        "description": f"{tag_name} 관련 태그"
                    }
                    
                    response = requests.post(
                        f"{self.api_base}/tags",
                        headers=self.headers,
                        json=tag_data,
                        timeout=30
                    )
                    
                    if response.status_code == 201:
                        new_tag = response.json()
                        tag_id = new_tag.get('id')
                        created_tags[tag_key] = tag_id
                        print(f"   ✅ 태그 '{tag_name}' 생성 성공 (ID: {tag_id})")
                    else:
                        print(f"   ❌ 태그 '{tag_name}' 생성 실패: {response.status_code}")
                        
                except Exception as e:
                    print(f"   💥 태그 '{tag_name}' 생성 오류: {str(e)}")
            else:
                created_tags[tag_key] = tags_info[tag_key]
                print(f"   ℹ️ 태그 '{tag_name}' 이미 존재 (ID: {tags_info[tag_key]})")
        
        return created_tags
    
    def step6_publish_health_content(self, categories, tags):
        """Step 6: 건강 콘텐츠 실제 발행"""
        print("\\n🔍 Step 6: 건강 콘텐츠 실제 발행...")
        
        # 생성된 콘텐츠 로드
        try:
            with open('health_content_20250712_024535.json', 'r', encoding='utf-8') as f:
                content_data = json.load(f)
        except Exception as e:
            print(f"   💥 콘텐츠 파일 로드 실패: {str(e)}")
            return None
        
        # WordPress 포스트 데이터 구성
        post_data = {
            "title": content_data.get('title', ''),
            "content": content_data.get('content', ''),
            "status": "publish",  # 즉시 발행
            "excerpt": content_data.get('meta_description', ''),
            "categories": [
                categories.get('건강', 1),
                categories.get('웰니스', 1),
                categories.get('라이프스타일', 1)
            ],
            "tags": [
                tags.get('면역력', 1),
                tags.get('건강', 1),
                tags.get('가이드', 1),
                tags.get('전문가', 1),
                tags.get('팁', 1)
            ],
            "meta": {
                "_yoast_wpseo_metadesc": content_data.get('meta_description', ''),
                "_yoast_wpseo_focuskw": "면역력 높이는 방법"
            }
        }
        
        # 필터링 (None 값 제거)
        post_data["categories"] = [cat_id for cat_id in post_data["categories"] if cat_id]
        post_data["tags"] = [tag_id for tag_id in post_data["tags"] if tag_id]
        
        try:
            print(f"   📤 포스트 발행 요청 중...")
            print(f"   📄 제목: {post_data['title']}")
            print(f"   📝 콘텐츠 길이: {len(post_data['content'])}자")
            print(f"   📂 카테고리 ID: {post_data['categories']}")
            print(f"   🏷️ 태그 ID: {post_data['tags']}")
            
            response = requests.post(
                f"{self.api_base}/posts",
                headers=self.headers,
                json=post_data,
                timeout=60
            )
            
            if response.status_code == 201:
                published_post = response.json()
                post_id = published_post.get('id')
                post_url = published_post.get('link')
                
                print(f"   ✅ 포스트 발행 성공!")
                print(f"   🆔 포스트 ID: {post_id}")
                print(f"   🔗 포스트 URL: {post_url}")
                print(f"   📅 발행 시간: {published_post.get('date', 'N/A')}")
                print(f"   📊 상태: {published_post.get('status', 'N/A')}")
                
                # 발행 결과 저장
                publish_result = {
                    "success": True,
                    "post_id": post_id,
                    "post_url": post_url,
                    "status": published_post.get('status'),
                    "published_at": published_post.get('date'),
                    "title": published_post.get('title', {}).get('rendered', ''),
                    "site": "innerspell.com",
                    "seo_data": content_data.get('seo_data', {}),
                    "categories_used": post_data["categories"],
                    "tags_used": post_data["tags"]
                }
                
                with open('innerspell_publish_result.json', 'w', encoding='utf-8') as f:
                    json.dump(publish_result, f, indent=2, ensure_ascii=False)
                
                return publish_result
                
            else:
                print(f"   ❌ 포스트 발행 실패: {response.status_code}")
                print(f"   📄 응답: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"   💥 포스트 발행 오류: {str(e)}")
            return None
    
    def step7_verify_publication(self, publish_result):
        """Step 7: 발행 결과 검증"""
        print("\\n🔍 Step 7: 발행 결과 검증...")
        
        if not publish_result:
            print("   ❌ 검증할 발행 결과가 없습니다.")
            return False
        
        post_url = publish_result.get('post_url')
        if not post_url:
            print("   ❌ 포스트 URL이 없습니다.")
            return False
        
        try:
            # 실제 웹페이지 접근 테스트
            response = requests.get(post_url, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                title = publish_result.get('title', '')
                
                print(f"   ✅ 웹페이지 접근 성공!")
                print(f"   🔗 URL: {post_url}")
                print(f"   📄 페이지 크기: {len(content)}자")
                print(f"   📝 제목 포함 여부: {'✅' if title in content else '❌'}")
                print(f"   🔍 콘텐츠 확인: {'✅' if '면역력' in content else '❌'}")
                
                # 추가 검증 정보
                verification_info = {
                    "url_accessible": True,
                    "page_size": len(content),
                    "title_found": title in content,
                    "keyword_found": '면역력' in content,
                    "verification_time": datetime.now().isoformat()
                }
                
                return verification_info
                
            else:
                print(f"   ❌ 웹페이지 접근 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   💥 웹페이지 검증 오류: {str(e)}")
            return False

def main():
    print("🎯 전문가 페르소나 - innerspell.com WordPress 실제 발행")
    print("⚠️ 추정 금지 - 모든 연결과 발행을 직접 실행합니다")
    print("=" * 80)
    
    publisher = InnerspellWordPressPublisher()
    
    start_time = time.time()
    
    # Step 1: 인증 테스트
    user_data = publisher.step1_test_authentication()
    if not user_data:
        print("💥 인증 실패로 작업을 중단합니다.")
        return False
    
    # Step 2: 사이트 상태 확인
    site_data = publisher.step2_check_site_status()
    if not site_data:
        print("💥 사이트 접근 실패로 작업을 중단합니다.")
        return False
    
    # Step 3: 카테고리/태그 확인
    categories_info, tags_info = publisher.step3_check_categories_tags()
    
    # Step 4: 카테고리 생성
    categories = publisher.step4_create_categories_if_needed(categories_info)
    
    # Step 5: 태그 생성
    tags = publisher.step5_create_tags_if_needed(tags_info)
    
    # Step 6: 실제 발행
    publish_result = publisher.step6_publish_health_content(categories, tags)
    if not publish_result:
        print("💥 포스트 발행 실패로 작업을 중단합니다.")
        return False
    
    # Step 7: 발행 검증
    verification = publisher.step7_verify_publication(publish_result)
    
    # 최종 결과
    total_time = time.time() - start_time
    
    print("\\n" + "=" * 80)
    print("🎉 innerspell.com WordPress 실제 발행 완료!")
    print("=" * 80)
    print(f"⏱️ 총 소요 시간: {total_time:.2f}초")
    print(f"🌐 사이트: {publish_result.get('site', 'N/A')}")
    print(f"🆔 포스트 ID: {publish_result.get('post_id', 'N/A')}")
    print(f"🔗 포스트 URL: {publish_result.get('post_url', 'N/A')}")
    print(f"📅 발행 시간: {publish_result.get('published_at', 'N/A')}")
    print(f"📊 상태: {publish_result.get('status', 'N/A')}")
    
    if verification:
        print(f"✅ 웹페이지 검증: 성공")
        print(f"📄 페이지 크기: {verification.get('page_size', 'N/A')}자")
        print(f"🔍 제목 확인: {'✅' if verification.get('title_found') else '❌'}")
        print(f"🎯 키워드 확인: {'✅' if verification.get('keyword_found') else '❌'}")
    
    print("\\n💡 실제 WordPress 발행이 성공적으로 완료되었습니다!")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\\n✅ 모든 작업이 성공적으로 완료되었습니다.")
    else:
        print("\\n❌ 작업 중 오류가 발생했습니다.")