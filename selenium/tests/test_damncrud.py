import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ======================================================
# Helper Login Function
# ======================================================

def login(driver, base_url):
    driver.get(f"{base_url}/login.php")

    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys("admin")

    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys("nimda666!")

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 15).until(
        EC.url_contains("index.php")
    )


# ======================================================
# FT_006 - Add Contact Valid
# ======================================================

@pytest.mark.ft006
def test_FT_006_add_contact_valid(driver, base_url):
    login(driver, base_url)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Add New Contact"))
    ).click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "name"))
    )

    driver.find_element(By.NAME, "name").send_keys("Selenium Tester")
    driver.find_element(By.NAME, "email").send_keys("selenium@test.com")
    driver.find_element(By.NAME, "phone").send_keys("081234567890")
    driver.find_element(By.NAME, "title").send_keys("Tester")

    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 15).until(
        EC.url_contains("index.php")
    )

    assert "Selenium Tester" in driver.page_source


# ======================================================
# FT_008 - Edit Contact
# ======================================================

@pytest.mark.ft008
def test_FT_008_edit_contact(driver, base_url):
    login(driver, base_url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn-success"))
    )

    edit_buttons = driver.find_elements(By.CSS_SELECTOR, "a.btn-success")
    assert len(edit_buttons) > 0, "Tidak ada data untuk diedit"

    edit_buttons[0].click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "name"))
    )

    title = driver.find_element(By.NAME, "title")
    title.clear()
    title.send_keys("Updated Title")

    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 15).until(
        EC.url_contains("index.php")
    )

    assert "Updated Title" in driver.page_source


# ======================================================
# FT_009 - Delete Contact
# ======================================================

@pytest.mark.ft009
def test_FT_009_delete_contact_confirm(driver, base_url):
    login(driver, base_url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#employee tbody tr"))
    )

    first_row = driver.find_element(By.CSS_SELECTOR, "#employee tbody tr")
    first_name = first_row.find_elements(By.TAG_NAME, "td")[1].text

    delete_button = first_row.find_element(By.CSS_SELECTOR, "a.btn-danger")
    delete_button.click()

    WebDriverWait(driver, 5).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

    WebDriverWait(driver, 15).until_not(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#employee tbody"),
            first_name
        )
    )

    assert first_name not in driver.page_source


# ======================================================
# FT_016 - Search Not Found
# ======================================================

@pytest.mark.ft016
def test_FT_016_search_not_found(driver, base_url):
    login(driver, base_url)

    search_box = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.dataTables_filter input")
        )
    )

    search_box.clear()
    search_box.send_keys("zzzzzzzznotfound")

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#employee tbody"),
            "No matching records found"
        )
    )

    assert "No matching records found" in driver.page_source


# ======================================================
# FT_019 - Upload Invalid File
# ======================================================

@pytest.mark.ft019
def test_FT_019_upload_invalid_photo(driver, base_url):
    login(driver, base_url)

    driver.get(f"{base_url}/profil.php")

    upload = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )

    file_path = os.path.abspath("test_files/test.pdf")
    upload.send_keys(file_path)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "Ekstensi tidak diijinkan" in driver.page_source