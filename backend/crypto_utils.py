#!/usr/bin/env python3
"""
API 키 암호화 및 보안 관리 시스템
Step 6: API 키 암호화 시스템 구현
"""

import os
import base64
import hashlib
import secrets
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
import json

class CryptoManager:
    """
    API 키 암호화 및 보안 관리 클래스
    - AES-256 암호화 사용
    - PBKDF2 키 유도 함수
    - 안전한 키 저장 및 관리
    """
    
    def __init__(self, master_password: Optional[str] = None):
        self.master_password = master_password or os.environ.get('MASTER_PASSWORD', 'default_dev_password')
        self.salt_file = '/tmp/crypto_salt.key'
        self.encrypted_data_file = '/tmp/encrypted_api_keys.json'
        
        # 솔트 생성 또는 로드
        self.salt = self._get_or_create_salt()
        
        # 암호화 키 생성
        self.cipher_suite = self._create_cipher_suite()
    
    def _get_or_create_salt(self) -> bytes:
        """솔트 생성 또는 기존 솔트 로드"""
        try:
            if os.path.exists(self.salt_file):
                with open(self.salt_file, 'rb') as f:
                    return f.read()
            else:
                # 새 솔트 생성
                salt = os.urandom(16)
                with open(self.salt_file, 'wb') as f:
                    f.write(salt)
                os.chmod(self.salt_file, 0o600)  # 소유자만 읽기/쓰기
                return salt
        except Exception as e:
            print(f"솔트 처리 중 오류: {e}")
            # 메모리에서만 사용할 임시 솔트
            return os.urandom(16)
    
    def _create_cipher_suite(self) -> Fernet:
        """PBKDF2를 사용한 암호화 키 생성"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,  # 강력한 보안을 위한 반복 횟수
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        return Fernet(key)
    
    def encrypt_api_key(self, api_key: str, service_name: str) -> str:
        """API 키 암호화"""
        try:
            encrypted_key = self.cipher_suite.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted_key).decode()
        except Exception as e:
            raise ValueError(f"API 키 암호화 실패: {e}")
    
    def decrypt_api_key(self, encrypted_key: str, service_name: str) -> str:
        """API 키 복호화"""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted_key = self.cipher_suite.decrypt(encrypted_data)
            return decrypted_key.decode()
        except Exception as e:
            raise ValueError(f"API 키 복호화 실패: {e}")
    
    def store_api_key(self, service_name: str, api_key: str, metadata: Dict[str, Any] = None) -> bool:
        """API 키를 안전하게 저장"""
        try:
            # 기존 데이터 로드
            stored_data = self._load_encrypted_data()
            
            # 새 키 암호화
            encrypted_key = self.encrypt_api_key(api_key, service_name)
            
            # 메타데이터 추가
            key_data = {
                'encrypted_key': encrypted_key,
                'created_at': datetime.now().isoformat(),
                'last_used': None,
                'usage_count': 0,
                'metadata': metadata or {}
            }
            
            stored_data[service_name] = key_data
            
            # 저장
            return self._save_encrypted_data(stored_data)
            
        except Exception as e:
            print(f"API 키 저장 실패: {e}")
            return False
    
    def retrieve_api_key(self, service_name: str) -> Optional[str]:
        """저장된 API 키 조회"""
        try:
            stored_data = self._load_encrypted_data()
            
            if service_name not in stored_data:
                return None
            
            key_data = stored_data[service_name]
            
            # 사용 통계 업데이트
            key_data['last_used'] = datetime.now().isoformat()
            key_data['usage_count'] = key_data.get('usage_count', 0) + 1
            
            # 업데이트된 데이터 저장
            self._save_encrypted_data(stored_data)
            
            # 키 복호화 후 반환
            return self.decrypt_api_key(key_data['encrypted_key'], service_name)
            
        except Exception as e:
            print(f"API 키 조회 실패: {e}")
            return None
    
    def delete_api_key(self, service_name: str) -> bool:
        """API 키 삭제"""
        try:
            stored_data = self._load_encrypted_data()
            
            if service_name in stored_data:
                del stored_data[service_name]
                return self._save_encrypted_data(stored_data)
            
            return True
            
        except Exception as e:
            print(f"API 키 삭제 실패: {e}")
            return False
    
    def list_stored_keys(self) -> Dict[str, Dict[str, Any]]:
        """저장된 키 목록 조회 (메타데이터만)"""
        try:
            stored_data = self._load_encrypted_data()
            
            # 민감한 정보 제외하고 메타데이터만 반환
            result = {}
            for service_name, key_data in stored_data.items():
                result[service_name] = {
                    'created_at': key_data.get('created_at'),
                    'last_used': key_data.get('last_used'),
                    'usage_count': key_data.get('usage_count', 0),
                    'metadata': key_data.get('metadata', {}),
                    'has_key': True
                }
            
            return result
            
        except Exception as e:
            print(f"키 목록 조회 실패: {e}")
            return {}
    
    def _load_encrypted_data(self) -> Dict[str, Any]:
        """암호화된 데이터 파일 로드"""
        try:
            if os.path.exists(self.encrypted_data_file):
                with open(self.encrypted_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            return {}
    
    def _save_encrypted_data(self, data: Dict[str, Any]) -> bool:
        """암호화된 데이터 파일 저장"""
        try:
            with open(self.encrypted_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.chmod(self.encrypted_data_file, 0o600)  # 소유자만 읽기/쓰기
            return True
        except Exception as e:
            print(f"데이터 저장 실패: {e}")
            return False
    
    def rotate_encryption_key(self, new_master_password: str) -> bool:
        """마스터 패스워드 변경 및 키 재암호화"""
        try:
            # 기존 데이터 모두 복호화
            old_data = {}
            stored_data = self._load_encrypted_data()
            
            for service_name, key_data in stored_data.items():
                try:
                    decrypted_key = self.decrypt_api_key(key_data['encrypted_key'], service_name)
                    old_data[service_name] = {
                        'api_key': decrypted_key,
                        'metadata': key_data.get('metadata', {}),
                        'created_at': key_data.get('created_at'),
                        'usage_count': key_data.get('usage_count', 0)
                    }
                except Exception as e:
                    print(f"키 복호화 실패 ({service_name}): {e}")
                    continue
            
            # 새 마스터 패스워드로 암호화 매니저 재생성
            self.master_password = new_master_password
            self.cipher_suite = self._create_cipher_suite()
            
            # 모든 키를 새 암호화로 재저장
            new_stored_data = {}
            for service_name, data in old_data.items():
                try:
                    encrypted_key = self.encrypt_api_key(data['api_key'], service_name)
                    new_stored_data[service_name] = {
                        'encrypted_key': encrypted_key,
                        'created_at': data['created_at'],
                        'last_used': datetime.now().isoformat(),
                        'usage_count': data['usage_count'],
                        'metadata': data['metadata']
                    }
                except Exception as e:
                    print(f"키 재암호화 실패 ({service_name}): {e}")
                    continue
            
            # 새 데이터 저장
            return self._save_encrypted_data(new_stored_data)
            
        except Exception as e:
            print(f"키 로테이션 실패: {e}")
            return False
    
    def validate_api_key_format(self, api_key: str, service_name: str) -> bool:
        """API 키 형식 검증"""
        validations = {
            'openai': {
                'prefix': 'sk-',
                'min_length': 40,
                'max_length': 60
            },
            'google': {
                'min_length': 30,
                'max_length': 50
            },
            'anthropic': {
                'prefix': 'sk-ant-',
                'min_length': 40,
                'max_length': 100
            }
        }
        
        if service_name.lower() not in validations:
            # 알려지지 않은 서비스는 기본 검증만
            return len(api_key) >= 20 and len(api_key) <= 200
        
        rules = validations[service_name.lower()]
        
        # 길이 검증
        if len(api_key) < rules.get('min_length', 20):
            return False
        if len(api_key) > rules.get('max_length', 200):
            return False
        
        # 접두사 검증
        if 'prefix' in rules and not api_key.startswith(rules['prefix']):
            return False
        
        return True
    
    def get_key_hash(self, api_key: str) -> str:
        """API 키의 안전한 해시 생성 (로깅/추적용)"""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]

# 전역 암호화 매니저 인스턴스
crypto_manager = CryptoManager()

class SecureAPIKeyManager:
    """
    FastAPI와 통합된 보안 API 키 관리자
    """
    
    def __init__(self):
        self.crypto = crypto_manager
        self.memory_cache = {}  # 임시 메모리 캐시
        self.cache_ttl = 300  # 5분 TTL
    
    def store_key_from_header(self, service_name: str, api_key: str, user_id: str = None) -> bool:
        """헤더에서 받은 API 키를 안전하게 저장"""
        if not self.crypto.validate_api_key_format(api_key, service_name):
            return False
        
        metadata = {
            'user_id': user_id,
            'key_hash': self.crypto.get_key_hash(api_key),
            'source': 'header'
        }
        
        return self.crypto.store_api_key(service_name, api_key, metadata)
    
    def get_key_for_request(self, service_name: str, user_id: str = None) -> Optional[str]:
        """요청을 위한 API 키 조회 (캐시 활용)"""
        cache_key = f"{service_name}:{user_id or 'anonymous'}"
        
        # 캐시 확인
        if cache_key in self.memory_cache:
            cached_data = self.memory_cache[cache_key]
            if datetime.now() < cached_data['expires']:
                return cached_data['api_key']
            else:
                del self.memory_cache[cache_key]
        
        # 저장소에서 조회
        api_key = self.crypto.retrieve_api_key(service_name)
        
        if api_key:
            # 캐시에 저장
            self.memory_cache[cache_key] = {
                'api_key': api_key,
                'expires': datetime.now() + timedelta(seconds=self.cache_ttl)
            }
        
        return api_key
    
    def clear_cache(self, service_name: str = None):
        """캐시 클리어"""
        if service_name:
            keys_to_remove = [key for key in self.memory_cache.keys() if key.startswith(f"{service_name}:")]
            for key in keys_to_remove:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()

# 전역 보안 API 키 매니저 인스턴스
secure_api_manager = SecureAPIKeyManager()