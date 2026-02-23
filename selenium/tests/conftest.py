import pytest
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


def get_chromedriver_path():
    """Get chromedriver path from system or use default"""
    try:
        # Try to find chromedriver in PATH
        result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Fallback paths
    possible_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        'chromedriver',
        None  # Let Selenium handle it
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
    
    # Get chromedriver path
    chromedriver_path = get_chromedriver_path()
    
    if chromedriver_path:
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    return driver


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
