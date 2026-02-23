from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options
    )

    driver.implicitly_wait(10)
    return driver