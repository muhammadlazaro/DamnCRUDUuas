import pytest
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:8080"


# ======================================================
# Health Check (FAIL if app not ready — DO NOT SKIP)
# ======================================================

def wait_for_app(url, max_retries=30):
    print(f"\n[HEALTH CHECK] Waiting for app at {url}")
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{url}/login.php", timeout=2)
            if r.status_code == 200:
                print("[HEALTH CHECK] App is ready ✓")
                return
        except Exception:
            pass

        print(f"[HEALTH CHECK] Attempt {attempt+1}/{max_retries}...")
        time.sleep(2)

    raise RuntimeError(f"Application not reachable at {url}")


@pytest.fixture(scope="session", autouse=True)
def check_app_ready():
    wait_for_app(BASE_URL)


# ======================================================
# WebDriver Fixture (parallel-safe + Selenium Manager)
# ======================================================

@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # ❗ TIDAK pakai Service()
    # ❗ TIDAK pakai manual chromedriver path
    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)

    yield driver

    driver.quit()


# ======================================================
# Base URL Fixture
# ======================================================

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL