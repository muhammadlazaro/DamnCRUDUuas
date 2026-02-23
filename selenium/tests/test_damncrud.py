import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver import create_driver

BASE_URL = "http://localhost:8080"


# =========================
# FIXTURE SETUP
# =========================

@pytest.fixture(scope="function")
def driver():
    driver = create_driver()
    driver.maximize_window()
    yield driver
    driver.quit()


def login(driver):
    driver.get(f"{BASE_URL}/login.php")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("nimda666!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("index.php")
    )


# =========================
# FT_006 - Add Contact Valid
# =========================

@pytest.mark.ft006
def test_FT_006_add_contact_valid(driver):
    """Test case untuk menambah kontak dengan data valid"""
    login(driver)

    driver.find_element(By.LINK_TEXT, "Add New Contact").click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "name"))
    )

    driver.find_element(By.NAME, "name").send_keys("Selenium Tester")
    driver.find_element(By.NAME, "email").send_keys("selenium@test.com")
    driver.find_element(By.NAME, "phone").send_keys("081234567890")
    driver.find_element(By.NAME, "title").send_keys("Tester")

    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("index.php")
    )

    assert "Selenium Tester" in driver.page_source


# =========================
# FT_008 - Edit Contact
# =========================

@pytest.mark.ft008
def test_FT_008_edit_contact(driver):
    """Test case untuk mengubah data kontak"""
    login(driver)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn-success"))
    )

    edit_buttons = driver.find_elements(By.CSS_SELECTOR, "a.btn-success")
    assert len(edit_buttons) > 0, "Tidak ada data untuk diedit"

    edit_buttons[0].click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "name"))
    )

    name = driver.find_element(By.NAME, "name")
    email = driver.find_element(By.NAME, "email")
    phone = driver.find_element(By.NAME, "phone")
    title = driver.find_element(By.NAME, "title")

    if name.get_attribute("value") == "":
        name.send_keys("Selenium User")

    if email.get_attribute("value") == "":
        email.send_keys("selenium@email.com")

    if phone.get_attribute("value") == "":
        phone.send_keys("081234567890")

    title.clear()
    title.send_keys("Updated Title")

    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("index.php")
    )

    assert "Updated Title" in driver.page_source


# =========================
# FT_009 - Delete Contact
# =========================

@pytest.mark.ft009
def test_FT_009_delete_contact_confirm(driver):
    """Test case untuk menghapus kontak"""
    login(driver)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#employee tbody tr"))
    )

    first_row = driver.find_element(By.CSS_SELECTOR, "#employee tbody tr")
    first_name = first_row.find_elements(By.TAG_NAME, "td")[1].text

    delete_button = first_row.find_element(By.CSS_SELECTOR, "a.btn-danger")
    delete_button.click()

    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()

    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "#employee tbody tr")
                 .find_elements(By.TAG_NAME, "td")[1].text != first_name
    )

    assert first_name not in driver.page_source


# =========================
# FT_016 - Search Not Found
# =========================

@pytest.mark.ft016
def test_FT_016_search_not_found(driver):
    """Test case untuk mencari kontak yang tidak ada"""
    login(driver)

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.dataTables_filter input")
        )
    )

    search_box = driver.find_element(
        By.CSS_SELECTOR, "div.dataTables_filter input"
    )

    search_box.clear()
    search_box.send_keys("zzzzzzzznotfound")

    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#employee tbody"),
            "No matching records found"
        )
    )

    assert "No matching records found" in driver.page_source


# =========================
# FT_019 - Upload Invalid File
# =========================

@pytest.mark.ft019
def test_FT_019_upload_invalid_photo(driver):
    """Test case untuk upload file yang tidak valid"""
    login(driver)

    driver.get(f"{BASE_URL}/profil.php")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )

    file_path = os.path.abspath("test_files/test.pdf")

    upload = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    upload.send_keys(file_path)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "Ekstensi tidak diijinkan" in driver.page_source