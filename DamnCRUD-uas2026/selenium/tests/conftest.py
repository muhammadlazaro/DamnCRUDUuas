import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


def create_driver():
    """Create and configure Chrome WebDriver for Selenium tests"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--start-maximized")
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        # Fallback jika Chrome tidak ditemukan
        driver = webdriver.Chrome(options=options)
    
    return driver


@pytest.fixture(scope="function")
def driver():
    """
    Fixture untuk WebDriver
    Scope: function - setiap test case mendapat driver baru
    """
    driver_instance = create_driver()
    yield driver_instance
    driver_instance.quit()


@pytest.fixture(scope="session")
def base_url():
    """Base URL untuk aplikasi"""
    return "http://localhost:8080"


@pytest.fixture(autouse=True)
def add_markers(request):
    """
    Automatically add markers untuk test cases
    """
    test_name = request.node.name
    if "FT_006" in test_name:
        request.node.add_marker(pytest.mark.ft006)
    elif "FT_008" in test_name:
        request.node.add_marker(pytest.mark.ft008)
    elif "FT_009" in test_name:
        request.node.add_marker(pytest.mark.ft009)
    elif "FT_016" in test_name:
        request.node.add_marker(pytest.mark.ft016)
    elif "FT_019" in test_name:
        request.node.add_marker(pytest.mark.ft019)


def pytest_configure(config):
    """
    Configure pytest dengan marker definitions
    """
    config.addinivalue_line(
        "markers", "ft006: mark test sebagai FT_006 - Add Contact Valid"
    )
    config.addinivalue_line(
        "markers", "ft008: mark test sebagai FT_008 - Edit Contact"
    )
    config.addinivalue_line(
        "markers", "ft009: mark test sebagai FT_009 - Delete Contact"
    )
    config.addinivalue_line(
        "markers", "ft016: mark test sebagai FT_016 - Search Not Found"
    )
    config.addinivalue_line(
        "markers", "ft019: mark test sebagai FT_019 - Upload Invalid Photo"
    )
