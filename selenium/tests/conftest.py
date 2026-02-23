import pytest
import os
import subprocess
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


def get_chromedriver_path():
    """Get chromedriver path from system or use default"""
    try:
        result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    possible_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        'chromedriver',
        None
    ]
    
    for path in possible_paths:
        if path is None:
            return None
        try:
            subprocess.run([path, '--version'], capture_output=True, check=True)
            return path
        except:
            continue
    
    return None


def check_app_availability(url, max_retries=30, timeout=1):
    """Check if application is available with retry logic"""
    print(f"\n[HEALTH CHECK] Checking app availability at {url}")
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{url}/login.php", timeout=timeout)
            if response.status_code == 200:
                print(f"[HEALTH CHECK] App is available! ✓")
                return True
        except requests.exceptions.ConnectionError:
            print(f"[HEALTH CHECK] Attempt {attempt + 1}/{max_retries} - Connection refused, retrying...")
        except requests.exceptions.Timeout:
            print(f"[HEALTH CHECK] Attempt {attempt + 1}/{max_retries} - Timeout, retrying...")
        except Exception as e:
            print(f"[HEALTH CHECK] Attempt {attempt + 1}/{max_retries} - Error: {e}")
        
        time.sleep(2)
    
    print(f"[HEALTH CHECK] App is NOT available after {max_retries} attempts ✗")
    return False


def create_driver():
    """Create and configure Chrome WebDriver for Selenium tests"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--start-maximized")
    
    chromedriver_path = get_chromedriver_path()
    
    if chromedriver_path:
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    return driver


@pytest.fixture(scope="session", autouse=True)
def check_app_ready():
    """Session-level fixture to check if app is available before running tests"""
    app_url = "http://web"
    if not check_app_availability(app_url):
        pytest.skip(f"Application not available at {app_url}")


@pytest.fixture(scope="function")
def driver():
    """
    Fixture untuk WebDriver
    Scope: function - setiap test case mendapat driver baru
    """
    print("\n[FIXTURE] Creating Chrome WebDriver...")
    driver_instance = create_driver()
    print("[FIXTURE] WebDriver created successfully")
    driver_instance.maximize_window()
    yield driver_instance
    print("[FIXTURE] Closing WebDriver...")
    try:
        driver_instance.quit()
    except Exception as e:
        print(f"[FIXTURE] Error closing driver: {e}")


@pytest.fixture(scope="session")
def base_url():
    """Base URL untuk aplikasi"""
    return "http://web"
