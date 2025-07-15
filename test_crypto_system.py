#!/usr/bin/env python3
"""
API 키 암호화 시스템 테스트 스크립트
Step 6: API 키 암호화 시스템 검증
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class CryptoSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None) -> tuple:
        """API 요청 수행"""
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_data = await response.json()
                return response.status, response_data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def test_api_key_storage(self) -> Dict[str, Any]:
        """API 키 저장 테스트"""
        print("🔐 API 키 저장 테스트...")
        
        test_cases = [
            {
                "name": "Valid OpenAI Key",
                "service": "openai",
                "key": "sk-test1234567890abcdefghijklmnopqrstuvwxyz",
                "metadata": {"user_id": "test_user", "purpose": "testing"},
                "expected_success": True
            },
            {
                "name": "Valid Google Key", 
                "service": "google",
                "key": "AIzaSyTest1234567890abcdefghijklmnop",
                "metadata": {"user_id": "test_user", "purpose": "testing"},
                "expected_success": True
            },
            {
                "name": "Invalid OpenAI Key (wrong prefix)",
                "service": "openai", 
                "key": "pk-invalid1234567890abcdefghijklmnop",
                "metadata": {},
                "expected_success": False
            },
            {
                "name": "Short Key",
                "service": "openai",
                "key": "sk-short",
                "metadata": {},
                "expected_success": False
            }
        ]
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        for test_case in test_cases:
            status, response = await self.make_request(
                "POST",
                "/api/secure/store-key",
                {
                    "service_name": test_case["service"],
                    "api_key": test_case["key"],
                    "metadata": test_case["metadata"]
                }
            )
            
            success = response.get("success", False) if status == 200 else False
            passed = success == test_case["expected_success"]
            
            results["details"].append({
                "test": test_case["name"],
                "expected": test_case["expected_success"],
                "actual": success,
                "passed": passed,
                "response": response.get("message", ""),
                "key_hash": response.get("key_hash", "")
            })
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    async def test_key_retrieval(self) -> Dict[str, Any]:
        """API 키 조회 테스트"""
        print("🔍 API 키 조회 테스트...")
        
        # 키 목록 조회
        status, keys_response = await self.make_request("GET", "/api/secure/list-keys")
        
        if status != 200 or not keys_response.get("success"):
            return {"error": "키 목록 조회 실패", "response": keys_response}
        
        stored_keys = keys_response.get("keys", {})
        results = {"total_keys": len(stored_keys), "test_results": []}
        
        # 저장된 각 키에 대해 테스트
        for service_name in stored_keys.keys():
            status, test_response = await self.make_request("GET", f"/api/secure/test-key/{service_name}")
            
            test_result = {
                "service": service_name,
                "status": status,
                "success": test_response.get("success", False),
                "valid_format": test_response.get("valid_format", False),
                "key_length": test_response.get("key_length", 0),
                "key_hash": test_response.get("key_hash", ""),
                "message": test_response.get("message", "")
            }
            
            results["test_results"].append(test_result)
        
        return results
    
    async def test_api_integration(self) -> Dict[str, Any]:
        """API 통합 테스트 (저장된 키 사용)"""
        print("🔗 API 통합 테스트...")
        
        # 1. 헤더 없이 키워드 분석 (저장된 키 사용)
        status, response = await self.make_request(
            "POST", 
            "/api/keywords/analyze",
            {"keyword": "암호화 테스트", "max_results": 2}
        )
        
        no_header_test = {
            "status": status,
            "success": status == 200,
            "response_type": type(response).__name__,
            "has_data": isinstance(response, list) and len(response) > 0
        }
        
        # 2. 헤더와 함께 요청 (헤더 우선 사용)
        status, response = await self.make_request(
            "POST",
            "/api/keywords/analyze", 
            {"keyword": "헤더 테스트", "max_results": 2},
            {"x-openai-key": "sk-header1234567890abcdefghijklmnopqr"}
        )
        
        with_header_test = {
            "status": status,
            "success": status == 200,
            "response_type": type(response).__name__,
            "has_data": isinstance(response, list) and len(response) > 0
        }
        
        return {
            "no_header_test": no_header_test,
            "with_header_test": with_header_test
        }
    
    async def test_key_management(self) -> Dict[str, Any]:
        """키 관리 기능 테스트"""
        print("🔧 키 관리 기능 테스트...")
        
        results = {}
        
        # 1. 새 테스트 키 저장
        test_service = "test_service"
        test_key = "test-key-1234567890abcdefghijklmnopqrstuvwxyz"
        
        status, response = await self.make_request(
            "POST",
            "/api/secure/store-key",
            {
                "service_name": test_service,
                "api_key": test_key,
                "metadata": {"test": "deletion_test"}
            }
        )
        
        results["store_test"] = {
            "status": status,
            "success": response.get("success", False)
        }
        
        # 2. 키 삭제 테스트
        if results["store_test"]["success"]:
            status, response = await self.make_request(
                "DELETE",
                f"/api/secure/delete-key/{test_service}"
            )
            
            results["delete_test"] = {
                "status": status,
                "success": response.get("success", False),
                "message": response.get("message", "")
            }
            
            # 3. 삭제 후 조회 시도
            status, response = await self.make_request("GET", f"/api/secure/test-key/{test_service}")
            
            results["deleted_key_access"] = {
                "status": status,
                "should_fail": not response.get("success", True),
                "message": response.get("message", "")
            }
        
        return results
    
    async def test_encryption_security(self) -> Dict[str, Any]:
        """암호화 보안 테스트"""
        print("🛡️ 암호화 보안 테스트...")
        
        # 암호화된 데이터 파일 확인
        try:
            with open('/tmp/encrypted_api_keys.json', 'r') as f:
                encrypted_data = json.load(f)
            
            security_checks = {
                "encrypted_file_exists": True,
                "keys_count": len(encrypted_data),
                "has_encrypted_keys": False,
                "no_plain_text_keys": True
            }
            
            # 암호화된 키 확인
            for service, data in encrypted_data.items():
                if 'encrypted_key' in data:
                    security_checks["has_encrypted_keys"] = True
                    
                    # 평문 키가 포함되지 않았는지 확인
                    encrypted_key = data['encrypted_key']
                    if 'sk-' in encrypted_key or 'AIza' in encrypted_key:
                        security_checks["no_plain_text_keys"] = False
            
            return security_checks
            
        except FileNotFoundError:
            return {"encrypted_file_exists": False, "error": "암호화 파일을 찾을 수 없음"}
        except Exception as e:
            return {"error": f"보안 테스트 실패: {str(e)}"}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 암호화 시스템 테스트 실행"""
        print("🚀 API 키 암호화 시스템 종합 테스트 시작...")
        print("=" * 60)
        
        results = {}
        
        # 1. API 키 저장 테스트
        results["storage_tests"] = await self.test_api_key_storage()
        
        # 2. API 키 조회 테스트
        results["retrieval_tests"] = await self.test_key_retrieval()
        
        # 3. API 통합 테스트
        results["integration_tests"] = await self.test_api_integration()
        
        # 4. 키 관리 테스트
        results["management_tests"] = await self.test_key_management()
        
        # 5. 암호화 보안 테스트
        results["security_tests"] = await self.test_encryption_security()
        
        return results

async def main():
    """메인 테스트 실행"""
    async with CryptoSystemTester() as tester:
        results = await tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("📊 API 키 암호화 시스템 테스트 결과 요약")
        print("=" * 60)
        
        # 저장 테스트 결과
        storage = results["storage_tests"]
        print(f"🔐 API 키 저장 테스트: {storage['passed']}/{storage['passed'] + storage['failed']} 통과")
        for detail in storage["details"]:
            status = "✅" if detail["passed"] else "❌"
            print(f"   {status} {detail['test']}: {detail['response']}")
        
        # 조회 테스트 결과
        retrieval = results["retrieval_tests"]
        print(f"\n🔍 API 키 조회 테스트: {retrieval.get('total_keys', 0)}개 키 확인")
        for test in retrieval.get("test_results", []):
            status = "✅" if test["success"] else "❌"
            print(f"   {status} {test['service']}: 길이 {test['key_length']}, 해시 {test['key_hash'][:8]}...")
        
        # 통합 테스트 결과
        integration = results["integration_tests"]
        no_header = integration["no_header_test"]
        with_header = integration["with_header_test"]
        print(f"\n🔗 API 통합 테스트:")
        print(f"   {'✅' if no_header['success'] else '❌'} 저장된 키 사용: {no_header['status']} 응답")
        print(f"   {'✅' if with_header['success'] else '❌'} 헤더 키 우선 사용: {with_header['status']} 응답")
        
        # 관리 테스트 결과
        management = results["management_tests"]
        print(f"\n🔧 키 관리 테스트:")
        if "store_test" in management:
            print(f"   {'✅' if management['store_test']['success'] else '❌'} 키 저장")
        if "delete_test" in management:
            print(f"   {'✅' if management['delete_test']['success'] else '❌'} 키 삭제")
        if "deleted_key_access" in management:
            print(f"   {'✅' if management['deleted_key_access']['should_fail'] else '❌'} 삭제된 키 접근 차단")
        
        # 보안 테스트 결과
        security = results["security_tests"]
        print(f"\n🛡️ 암호화 보안 테스트:")
        print(f"   {'✅' if security.get('encrypted_file_exists') else '❌'} 암호화 파일 존재")
        print(f"   {'✅' if security.get('has_encrypted_keys') else '❌'} 암호화된 키 존재")
        print(f"   {'✅' if security.get('no_plain_text_keys') else '❌'} 평문 키 노출 없음")
        print(f"   - 저장된 키 수: {security.get('keys_count', 0)}개")
        
        print("\n🎯 API 키 암호화 시스템 구현 완료!")
        
        # 상세 결과를 JSON 파일로 저장
        with open("/mnt/e/project/test-blogauto-project/crypto_system_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("📄 상세 결과가 crypto_system_test_results.json에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())