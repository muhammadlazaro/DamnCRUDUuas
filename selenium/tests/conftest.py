import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


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
    driver_instance = create_driver()
    yield driver_instance
    try:
        driver_instance.quit()
    except:
        pass


@pytest.fixture(scope="session")
def base_url():
    """Base URL untuk aplikasi"""
    return "http://localhost:8080"
