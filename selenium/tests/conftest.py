import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def is_app_available(url="http://localhost:8080", timeout=2):
    """Check if application is running"""
    try:
        import urllib.request
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except:
        return False


def create_driver():
    """Create and configure Chrome WebDriver for Selenium tests"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


@pytest.fixture(scope="function")
def driver():
    """
    Fixture untuk WebDriver
    Scope: function - setiap test case mendapat driver baru
    """
    if not is_app_available():
        pytest.skip("Application is not running at localhost:8080")
    
    driver_instance = create_driver()
    yield driver_instance
    driver_instance.quit()


@pytest.fixture(scope="session")
def base_url():
    """Base URL untuk aplikasi"""
    return "http://localhost:8080"
