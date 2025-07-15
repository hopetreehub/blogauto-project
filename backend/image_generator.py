"""
독립적인 이미지 생성 모듈
기존 콘텐츠 생성 시스템과 완전 분리
"""
import openai
import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
import base64
from pathlib import Path

class ImageGenerator:
    def __init__(self):
        self.api_key = None
        self.images_dir = Path("/mnt/e/project/test-blogauto-project/backend/generated_images")
        self.images_dir.mkdir(exist_ok=True)
        
    def set_api_key(self, api_key: str):
        """API 키 설정"""
        self.api_key = api_key
        openai.api_key = api_key
        
    def generate_image_prompt(self, title: str, keyword: str, style: str = "professional") -> str:
        """제목과 키워드를 기반으로 이미지 프롬프트 생성"""
        style_templates = {
            "professional": "Professional, clean, modern style with good lighting and high quality",
            "creative": "Creative, artistic, vibrant colors with unique perspective",
            "minimalist": "Minimalist, simple, clean design with focus on essential elements",
            "infographic": "Infographic style, data visualization, charts and diagrams",
            "illustration": "Digital illustration, vector style, colorful and engaging"
        }
        
        base_prompt = f"Create a high-quality image related to '{title}' and '{keyword}'"
        style_prompt = style_templates.get(style, style_templates["professional"])
        
        full_prompt = f"{base_prompt}. {style_prompt}. No text or watermarks in the image."
        
        return full_prompt
    
    async def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> Dict[str, Any]:
        """DALL-E 3를 사용한 이미지 생성"""
        if not self.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다")
            
        try:
            # DALL-E 3 API 호출
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt
            
            # 이미지 다운로드 및 저장
            image_filename = await self._download_and_save_image(image_url)
            
            return {
                "success": True,
                "image_url": image_url,
                "local_path": str(image_filename),
                "revised_prompt": revised_prompt,
                "original_prompt": prompt,
                "size": size,
                "quality": quality,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    
    async def _download_and_save_image(self, image_url: str) -> Path:
        """이미지 다운로드 및 로컬 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.images_dir / f"generated_image_{timestamp}.png"
        
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        return filename
    
    def generate_content_images(self, title: str, keyword: str, num_images: int = 2) -> Dict[str, Any]:
        """콘텐츠용 다중 이미지 생성"""
        images = []
        
        # 다양한 스타일로 이미지 생성
        styles = ["professional", "infographic"][:num_images]
        
        for i, style in enumerate(styles):
            prompt = self.generate_image_prompt(title, keyword, style)
            
            # 각 이미지마다 약간 다른 프롬프트 생성
            if i == 0:
                prompt += " Main featured image, hero style"
            else:
                prompt += f" Supporting image {i+1}, complementary style"
                
            # 동기 함수로 수정 필요
            # result = self.generate_image(prompt)
            # images.append(result)
            # TODO: 이 메서드는 async로 변경하거나 별도 구현 필요
            pass
        
        return {
            "title": title,
            "keyword": keyword,
            "images": images,
            "total_generated": len(images)
        }

# 이미지 생성 인스턴스
image_generator = ImageGenerator()