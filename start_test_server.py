#!/usr/bin/env python3
"""
테스트용 서버 시작 스크립트 (포트 5001)
"""
import subprocess
import sys
import os
import time

def start_backend():
    """백엔드 서버 시작"""
    print("🚀 백엔드 서버 시작 중 (포트 5001)...")
    
    # 환경 설정
    env = os.environ.copy()
    env['PORT'] = '5001'
    
    # real_api_simple.py 실행
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    cmd = [sys.executable, 'real_api_simple.py']
    
    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 서버 시작 대기
    time.sleep(3)
    
    if process.poll() is None:
        print("✅ 백엔드 서버가 성공적으로 시작되었습니다.")
        print(f"   PID: {process.pid}")
        print("   URL: http://localhost:5001")
        return process
    else:
        stdout, stderr = process.communicate()
        print("❌ 백엔드 서버 시작 실패:")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        return None

if __name__ == "__main__":
    process = start_backend()
    if process:
        try:
            print("\n서버가 실행 중입니다. Ctrl+C로 종료하세요.")
            process.wait()
        except KeyboardInterrupt:
            print("\n\n종료 중...")
            process.terminate()
            process.wait()
            print("✅ 서버가 종료되었습니다.")