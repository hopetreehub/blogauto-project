"""
데이터베이스 최적화
- 인덱스 생성
- 쿼리 최적화
- 연결 풀링
- 배치 처리
"""

import sqlite3
from contextlib import contextmanager
import time
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.optimization_results = []
    
    @contextmanager
    def get_connection(self):
        """최적화된 데이터베이스 연결"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # 성능 최적화 설정
        conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous = NORMAL")  # 더 빠른 쓰기
        conn.execute("PRAGMA cache_size = -64000")  # 64MB 캐시
        conn.execute("PRAGMA temp_store = MEMORY")  # 임시 테이블을 메모리에
        conn.execute("PRAGMA mmap_size = 268435456")  # 256MB 메모리 맵
        
        try:
            yield conn
        finally:
            conn.close()
    
    def create_indexes(self):
        """필요한 인덱스 생성"""
        print("🔧 데이터베이스 인덱스 최적화 시작...")
        
        indexes = [
            # 사용자 관련 인덱스
            ("idx_users_email", "users(email)"),
            ("idx_users_username", "users(username)"),
            
            # 키워드 관련 인덱스
            ("idx_keywords_user_created", "keywords(user_id, created_at DESC)"),
            ("idx_keywords_search_volume", "keywords(search_volume DESC)"),
            
            # 생성된 콘텐츠 인덱스
            ("idx_generated_content_user_created", "generated_content(user_id, created_at DESC)"),
            ("idx_generated_content_site", "generated_content(site_id, created_at DESC)"),
            
            # 생성된 제목 인덱스
            ("idx_generated_titles_user_created", "generated_titles(user_id, created_at DESC)"),
            ("idx_generated_titles_keyword", "generated_titles(keyword_id)"),
            
            # 포스팅 결과 인덱스
            ("idx_posting_results_status", "posting_results(status, created_at DESC)"),
            ("idx_posting_results_site", "posting_results(site_id, created_at DESC)"),
            
            # 자동화 세션 인덱스
            ("idx_automation_sessions_user", "automation_sessions(user_id, created_at DESC)"),
            ("idx_automation_sessions_status", "automation_sessions(status)"),
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for index_name, index_def in indexes:
                try:
                    start_time = time.time()
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
                    elapsed = (time.time() - start_time) * 1000
                    
                    self.optimization_results.append({
                        "type": "index",
                        "name": index_name,
                        "time_ms": round(elapsed, 2),
                        "status": "created"
                    })
                    print(f"  ✅ {index_name} 생성됨 ({elapsed:.2f}ms)")
                except Exception as e:
                    self.optimization_results.append({
                        "type": "index",
                        "name": index_name,
                        "status": "failed",
                        "error": str(e)
                    })
                    print(f"  ❌ {index_name} 실패: {e}")
            
            conn.commit()
    
    def analyze_slow_queries(self):
        """느린 쿼리 분석"""
        print("\n🔍 쿼리 성능 분석...")
        
        test_queries = [
            # 자주 사용되는 쿼리들
            ("사용자별 최근 키워드", """
                SELECT k.*, u.username 
                FROM keywords k 
                JOIN users u ON k.user_id = u.id 
                WHERE k.user_id = '1' 
                ORDER BY k.created_at DESC 
                LIMIT 10
            """),
            
            ("인기 키워드 조회", """
                SELECT keyword, COUNT(*) as usage_count, AVG(search_volume) as avg_volume
                FROM keywords 
                GROUP BY keyword 
                ORDER BY usage_count DESC 
                LIMIT 20
            """),
            
            ("최근 생성된 콘텐츠", """
                SELECT gc.*, gt.title 
                FROM generated_content gc
                LEFT JOIN generated_titles gt ON gc.title_id = gt.id
                ORDER BY gc.created_at DESC
                LIMIT 50
            """),
            
            ("사이트별 포스팅 통계", """
                SELECT site_id, 
                       COUNT(*) as total_posts,
                       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
                FROM posting_results
                GROUP BY site_id
            """)
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for query_name, query in test_queries:
                try:
                    # EXPLAIN QUERY PLAN 실행
                    cursor.execute(f"EXPLAIN QUERY PLAN {query}")
                    plan = cursor.fetchall()
                    
                    # 실제 쿼리 실행 시간 측정
                    start_time = time.time()
                    cursor.execute(query)
                    results = cursor.fetchall()
                    elapsed = (time.time() - start_time) * 1000
                    
                    self.optimization_results.append({
                        "type": "query",
                        "name": query_name,
                        "time_ms": round(elapsed, 2),
                        "rows": len(results),
                        "plan": [dict(row) for row in plan]
                    })
                    
                    print(f"  📊 {query_name}: {elapsed:.2f}ms ({len(results)} rows)")
                    
                except Exception as e:
                    print(f"  ❌ {query_name} 실패: {e}")
    
    def optimize_table_structure(self):
        """테이블 구조 최적화"""
        print("\n🔧 테이블 구조 최적화...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # VACUUM으로 데이터베이스 정리
            start_time = time.time()
            cursor.execute("VACUUM")
            vacuum_time = (time.time() - start_time) * 1000
            print(f"  ✅ VACUUM 완료 ({vacuum_time:.2f}ms)")
            
            # ANALYZE로 쿼리 플래너 최적화
            start_time = time.time()
            cursor.execute("ANALYZE")
            analyze_time = (time.time() - start_time) * 1000
            print(f"  ✅ ANALYZE 완료 ({analyze_time:.2f}ms)")
            
            self.optimization_results.append({
                "type": "maintenance",
                "operations": {
                    "vacuum_ms": round(vacuum_time, 2),
                    "analyze_ms": round(analyze_time, 2)
                }
            })
    
    def create_materialized_views(self):
        """자주 사용되는 집계 데이터를 위한 뷰 생성"""
        print("\n📊 집계 뷰 생성...")
        
        views = [
            ("user_stats", """
                CREATE VIEW IF NOT EXISTS user_stats AS
                SELECT 
                    u.id as user_id,
                    u.username,
                    COUNT(DISTINCT k.id) as total_keywords,
                    COUNT(DISTINCT gc.id) as total_content,
                    COUNT(DISTINCT pr.id) as total_posts
                FROM users u
                LEFT JOIN keywords k ON u.id = k.user_id
                LEFT JOIN generated_content gc ON u.id = gc.user_id
                LEFT JOIN posting_results pr ON gc.id = pr.content_id
                GROUP BY u.id
            """),
            
            ("daily_stats", """
                CREATE VIEW IF NOT EXISTS daily_stats AS
                SELECT 
                    DATE(created_at) as date,
                    COUNT(CASE WHEN type = 'keyword' THEN 1 END) as keywords_created,
                    COUNT(CASE WHEN type = 'content' THEN 1 END) as content_created,
                    COUNT(CASE WHEN type = 'post' THEN 1 END) as posts_published
                FROM (
                    SELECT 'keyword' as type, created_at FROM keywords
                    UNION ALL
                    SELECT 'content' as type, created_at FROM generated_content
                    UNION ALL
                    SELECT 'post' as type, created_at FROM posting_results WHERE status = 'success'
                )
                GROUP BY DATE(created_at)
            """)
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for view_name, view_sql in views:
                try:
                    start_time = time.time()
                    cursor.execute(view_sql)
                    elapsed = (time.time() - start_time) * 1000
                    
                    self.optimization_results.append({
                        "type": "view",
                        "name": view_name,
                        "time_ms": round(elapsed, 2),
                        "status": "created"
                    })
                    print(f"  ✅ {view_name} 뷰 생성됨 ({elapsed:.2f}ms)")
                except Exception as e:
                    print(f"  ❌ {view_name} 실패: {e}")
            
            conn.commit()
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """최적화 결과 보고서"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.optimization_results,
            "summary": {
                "indexes_created": len([r for r in self.optimization_results if r["type"] == "index" and r.get("status") == "created"]),
                "queries_analyzed": len([r for r in self.optimization_results if r["type"] == "query"]),
                "views_created": len([r for r in self.optimization_results if r["type"] == "view" and r.get("status") == "created"]),
            }
        }
        
        # 평균 쿼리 시간
        query_times = [r["time_ms"] for r in self.optimization_results if r["type"] == "query" and "time_ms" in r]
        if query_times:
            report["summary"]["avg_query_time_ms"] = round(sum(query_times) / len(query_times), 2)
        
        return report
    
    def run_all_optimizations(self):
        """모든 최적화 실행"""
        print("🚀 데이터베이스 최적화 시작...")
        print("=" * 60)
        
        # 1. 인덱스 생성
        self.create_indexes()
        
        # 2. 쿼리 성능 분석
        self.analyze_slow_queries()
        
        # 3. 테이블 구조 최적화
        self.optimize_table_structure()
        
        # 4. 집계 뷰 생성
        self.create_materialized_views()
        
        # 5. 보고서 출력
        report = self.get_optimization_report()
        
        print("\n" + "=" * 60)
        print("📊 최적화 결과 요약")
        print("=" * 60)
        print(f"  인덱스 생성: {report['summary']['indexes_created']}개")
        print(f"  쿼리 분석: {report['summary']['queries_analyzed']}개")
        print(f"  뷰 생성: {report['summary']['views_created']}개")
        
        if "avg_query_time_ms" in report["summary"]:
            print(f"  평균 쿼리 시간: {report['summary']['avg_query_time_ms']}ms")
        
        print("=" * 60)
        
        return report


# 배치 처리 유틸리티
class BatchProcessor:
    @staticmethod
    def batch_insert(conn, table: str, columns: List[str], data: List[tuple], batch_size: int = 1000):
        """대량 데이터 삽입 최적화"""
        cursor = conn.cursor()
        placeholders = ",".join(["?" for _ in columns])
        insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(insert_sql, batch)
        
        conn.commit()
    
    @staticmethod
    def batch_update(conn, table: str, updates: List[Dict[str, Any]], batch_size: int = 500):
        """대량 업데이트 최적화"""
        cursor = conn.cursor()
        
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            
            for update in batch:
                set_clause = ", ".join([f"{k} = ?" for k in update["data"].keys()])
                where_clause = " AND ".join([f"{k} = ?" for k in update["where"].keys()])
                
                sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                values = list(update["data"].values()) + list(update["where"].values())
                
                cursor.execute(sql, values)
            
            conn.commit()


if __name__ == "__main__":
    # 데이터베이스 최적화 실행
    db_path = "/mnt/e/project/test-blogauto-project/backend/blogauto_personal.db"
    optimizer = DatabaseOptimizer(db_path)
    optimizer.run_all_optimizations()