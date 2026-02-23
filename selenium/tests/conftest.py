import pytest
import requests
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:8080"
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "damncrud_user"
DB_PASS = "damncrud_pass"
DB_NAME = "damncrud"


# ======================================================
# Health Check - Database First, then Application
# ======================================================

def check_database_ready(max_retries=90, timeout=3):
    """
    Cek database MySQL/MariaDB sudah ready untuk koneksi.
    Gunakan mysqladmin ping atau connection test.
    """
    print(f"\n[DB CHECK] Waiting for database at {DB_HOST}:{DB_PORT}")
    
    for attempt in range(max_retries):
        try:
            # Try mysqladmin ping (jika tersedia di environment)
            result = subprocess.run(
                ["mysqladmin", "ping", "-h", DB_HOST, "-u", DB_USER, f"-p{DB_PASS}", "-P", str(DB_PORT)],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            if result.returncode == 0:
                print(f"[DB CHECK] ✓ Database is ready! (attempt {attempt+1})")
                return True
        except FileNotFoundError:
            # mysqladmin not available, try via app
            pass
        except Exception:
            pass

        # Fallback: cek via aplikasi - STRICT check
        try:
            r = requests.get(f"{BASE_URL}/login.php", timeout=timeout)
            # MUST have status 200 AND login text AND NO database error
            if (r.status_code == 200 and 
                "Damn, sign in!" in r.text and 
                "Failed to connect to database" not in r.text):
                print(f"[DB CHECK] ✓ Database is ready (via app check)! (attempt {attempt+1})")
                return True
            elif "Failed to connect to database" in r.text:
                print(f"[DB CHECK] Attempt {attempt+1}/{max_retries} - Database still initializing...")
            else:
                print(f"[DB CHECK] Attempt {attempt+1}/{max_retries} - App loading or health check...")
        except Exception as e:
            print(f"[DB CHECK] Attempt {attempt+1}/{max_retries} - Connection failed...")

        time.sleep(2)

    print("[DB CHECK] ✗ Database failed to become ready!")
    return False


def wait_for_app(url, max_retries=30, timeout=3):
    """
    Tunggu aplikasi login page load dengan benar (tanpa database error).
    Database harus sudah ready sebelum ini.
    """
    print(f"\n[APP CHECK] Verifying app at {url}/login.php")
    
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{url}/login.php", timeout=timeout)
            if (r.status_code == 200 and 
                "Damn, sign in!" in r.text and 
                "Failed to connect to database" not in r.text):
                print(f"[APP CHECK] ✓ App login page is correct! (attempt {attempt+1})")
                return True
            else:
                if "Failed to connect to database" in r.text:
                    print(f"[APP CHECK] Attempt {attempt+1} - Database still failing in app...")
                else:
                    print(f"[APP CHECK] Attempt {attempt+1} - App loading...")
        except Exception as e:
            print(f"[APP CHECK] Attempt {attempt+1} - Connection error: {e}")

        time.sleep(1)

    print("[APP CHECK] ✗ App failed to load correctly!")
    return False


@pytest.fixture(scope="session", autouse=True)
def check_app_ready():
    """
    Session fixture: Verify BOTH database AND app ready before any tests run.
    This is mandatory - fail loudly if anything not ready.
    """
    print("\n" + "="*60)
    print("STARTING PRE-TEST HEALTH CHECKS")
    print("="*60)
    
    # Step 1: Wait for database
    if not check_database_ready(max_retries=60):
        raise RuntimeError(
            f"❌ Database not ready at {DB_HOST}:{DB_PORT} after 120 seconds. "
            f"Check: MySQL/MariaDB container running, port forwarded, credentials correct"
        )
    
    # Step 2: Wait for app
    if not wait_for_app(BASE_URL, max_retries=30):
        raise RuntimeError(
            f"❌ Application not ready at {BASE_URL} after 30 seconds. "
            f"Check: Docker container running, database fully initialized"
        )
    
    print("\n" + "="*60)
    print("✓ ALL HEALTH CHECKS PASSED - TESTS CAN RUN")
    print("="*60 + "\n")


# ======================================================
# WebDriver Fixture (parallel-safe + Selenium Manager)
# ======================================================

@pytest.fixture(scope="function")
def driver():
    """
    Create Chrome WebDriver with optimal settings for parallel execution.
    - Uses Selenium Manager (no manual chromedriver management)
    - Function scope: fresh driver per test
    - Headless mode for CI/CD
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    # ❗ Do NOT use Service() - let Selenium Manager handle it
    # ❗ Do NOT set manual chromedriver path - causes parallel execution issues
    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)

    yield driver

    try:
        driver.quit()
    except:
        pass


# ======================================================
# Base URL Fixture
# ======================================================

@pytest.fixture(scope="session")
def base_url():
    """Return base URL for all tests"""
    return BASE_URL