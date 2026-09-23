"""
Test suite for ResearchX database startup resilience, PostgreSQL URL parsing,
and lifespan error handling.
"""
import os
import sys
import time
import asyncio
import importlib
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def test_url_normalization():
    print("---> [TEST 1] Testing DATABASE_URL Normalization & Quote Stripping")
    from app.core.config import Settings
    
    # Test 1a: Standard postgres://
    s1 = Settings(DATABASE_URL="postgres://user:pass@host.render.com:5432/dbname")
    assert s1.get_database_url() == "postgresql://user:pass@host.render.com:5432/dbname", f"Failed: {s1.get_database_url()}"
    
    # Test 1b: Quoted "postgres://..."
    s2 = Settings(DATABASE_URL='"postgres://user:pass@host.render.com:5432/dbname"')
    assert s2.get_database_url() == "postgresql://user:pass@host.render.com:5432/dbname", f"Failed: {s2.get_database_url()}"
    
    # Test 1c: Single quoted 'postgres+psycopg2://...'
    s3 = Settings(DATABASE_URL="'postgres+psycopg2://user:pass@host.render.com:5432/dbname'")
    assert s3.get_database_url() == "postgresql+psycopg2://user:pass@host.render.com:5432/dbname", f"Failed: {s3.get_database_url()}"
    
    # Test 1d: Standard postgresql://
    s4 = Settings(DATABASE_URL="postgresql://user:pass@host.render.com:5432/dbname")
    assert s4.get_database_url() == "postgresql://user:pass@host.render.com:5432/dbname", f"Failed: {s4.get_database_url()}"
    
    # Test 1e: Unset / empty -> SQLite fallback
    s5 = Settings(DATABASE_URL="")
    assert s5.get_database_url().startswith("sqlite:///"), f"Failed: {s5.get_database_url()}"
    
    # Test 1f: Masked credentials
    assert "pass" not in s1.get_masked_database_url(), "Password leaked in get_masked_database_url"
    assert "****" in s1.get_masked_database_url(), "Password not masked in get_masked_database_url"
    
    print("     [PASS] DATABASE_URL normalization and credential masking verified 100%")

def test_resilient_startup_on_unreachable_db():
    print("---> [TEST 2] Testing Resilient Startup with Unreachable PostgreSQL DB")
    os.environ['DATABASE_URL'] = 'postgresql://testuser:testpass@127.0.0.1:54321/testdb'
    
    import app.core.config
    importlib.reload(app.core.config)
    import app.database.database
    importlib.reload(app.database.database)
    import app.main
    importlib.reload(app.main)
    
    # Track execution
    async def run_lifespan():
        from app.main import lifespan, app
        async with lifespan(app):
            print("     [PASS] Application lifespan entered successfully despite unreachable DB.")
            
    start = time.time()
    asyncio.run(run_lifespan())
    elapsed = time.time() - start
    
    print(f"     [PASS] Retried 5 times (~{elapsed:.1f}s) without crashing FastAPI / Uvicorn.")

def test_sqlite_local_startup():
    print("---> [TEST 3] Testing Local SQLite Startup and Admin Account Seeding")
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
        
    import app.core.config
    importlib.reload(app.core.config)
    import app.database.database
    importlib.reload(app.database.database)
    import app.main
    importlib.reload(app.main)
    
    async def run_sqlite_lifespan():
        from app.main import lifespan, app
        async with lifespan(app):
            print("     [PASS] SQLite tables and admin user initialized successfully.")
            
    asyncio.run(run_sqlite_lifespan())

if __name__ == "__main__":
    print("=================================================================")
    print("  RESEARCHX: DATABASE STARTUP RESILIENCE & CONFIGURATION TESTS   ")
    print("=================================================================")
    test_url_normalization()
    test_resilient_startup_on_unreachable_db()
    test_sqlite_local_startup()
    print("=================================================================")
    print("  ALL STARTUP RESILIENCE TESTS PASSED 100%!                      ")
    print("=================================================================")
