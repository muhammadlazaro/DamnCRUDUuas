import pytest
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:8080"


# ======================================================
# Health Check (FAIL if app not ready — DO NOT SKIP)
# ======================================================

def wait_for_app(url, max_retries=60, timeout=3):
    """
    Tunggu hingga aplikasi siap dengan database connection.
    Cek: HTTP 200 + login form + TIDAK ada error database
    """
    print(f"\n[HEALTH CHECK] Waiting for app at {url}/login.php (max {max_retries} attempts, 2s interval)")
    
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{url}/login.php", timeout=timeout)
            if r.status_code == 200:
                # Cek bahwa halaman berhasil load DAN database connected
                if "Damn, sign in!" in r.text and "Failed to connect to database" not in r.text:
                    elapsed = (attempt + 1) * 2
                    print(f"[HEALTH CHECK] ✓ App is ready! (attempt {attempt+1}, elapsed {elapsed}s)")
                    return
                else:
                    if "Failed to connect to database" in r.text:
                        print(f"[HEALTH CHECK] Attempt {attempt+1}/{max_retries} - Database not ready yet...")
                    else:
                        print(f"[HEALTH CHECK] Attempt {attempt+1}/{max_retries} - App loading...")
            else:
                print(f"[HEALTH CHECK] Attempt {attempt+1}/{max_retries} - HTTP {r.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"[HEALTH CHECK] Attempt {attempt+1}/{max_retries} - Connection refused")
        except Exception as e:
            print(f"[HEALTH CHECK] Attempt {attempt+1}/{max_retries} - Error: {type(e).__name__}")

        time.sleep(2)

    raise RuntimeError(
        f"Application not ready at {url} after {max_retries} attempts. "
        f"Check: 1) Database initialized, 2) App env vars set, 3) Docker running"
    )


@pytest.fixture(scope="session", autouse=True)
def check_app_ready():
    """Session fixture: check app readiness BEFORE any tests run"""
    wait_for_app(BASE_URL)


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