import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ======================================================
# Helper: Login Function
# ======================================================

def login(driver, base_url):
    """
    Melakukan login ke aplikasi.
    Raises TimeoutException jika gagal menemukan elemen atau redirect tidak terjadi.
    """
    driver.get(f"{base_url}/login.php")

    try:
        # Tunggu field username muncul (maks 30 detik)
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )

        # Input username
        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        username_field.send_keys("admin")

        # Input password (pastikan sesuai dengan data di DB + salt)
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys("nimda666!")

        # Klik tombol login
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Tunggu redirect ke index.php
        WebDriverWait(driver, 20).until(
            EC.url_contains("index.php")
        )

    except TimeoutException as e:
        print("LOGIN GAGAL - TimeoutException terjadi!")
        print("Current URL:", driver.current_url)
        print("Page source (potongan awal):")
        print(driver.page_source[:1500])
        driver.save_screenshot("login_error.png")
        raise
    except Exception as e:
        print("LOGIN GAGAL - Error lain:")
        print(str(e))
        driver.save_screenshot("login_unexpected_error.png")
        raise


# ======================================================
# FT_006 - Add Contact Valid
# ======================================================

@pytest.mark.ft006
def test_FT_006_add_contact_valid(driver, base_url):
    login(driver, base_url)

    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Add New Contact"))
    ).click()

    WebDriverWait(driver, 15).until(
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

    assert "Selenium Tester" in driver.page_source, "Nama kontak baru tidak muncul di halaman"


# ======================================================
# FT_008 - Edit Contact
# ======================================================

@pytest.mark.ft008
def test_FT_008_edit_contact(driver, base_url):
    login(driver, base_url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn-success"))
    )

    edit_buttons = driver.find_elements(By.CSS_SELECTOR, "a.btn-success")
    assert len(edit_buttons) > 0, "Tidak ada tombol edit yang ditemukan (data kosong?)"

    edit_buttons[0].click()

    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.NAME, "name"))
    )

    title_field = driver.find_element(By.NAME, "title")
    title_field.clear()
    title_field.send_keys("Updated Title")

    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(driver, 15).until(
        EC.url_contains("index.php")
    )

    assert "Updated Title" in driver.page_source, "Perubahan title tidak muncul"


# ======================================================
# FT_009 - Delete Contact Confirm
# ======================================================

@pytest.mark.ft009
def test_FT_009_delete_contact_confirm(driver, base_url):
    login(driver, base_url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#employee tbody tr"))
    )

    first_row = driver.find_element(By.CSS_SELECTOR, "#employee tbody tr")
    first_name = first_row.find_elements(By.TAG_NAME, "td")[1].text

    delete_button = first_row.find_element(By.CSS_SELECTOR, "a.btn-danger")
    delete_button.click()

    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

    WebDriverWait(driver, 20).until_not(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#employee tbody"),
            first_name
        )
    )

    assert first_name not in driver.page_source, "Kontak yang dihapus masih muncul"


# ======================================================
# FT_016 - Search Not Found
# ======================================================

@pytest.mark.ft016
def test_FT_016_search_not_found(driver, base_url):
    login(driver, base_url)

    search_box = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.dataTables_filter input")
        )
    )

    search_box.clear()
    search_box.send_keys("zzzzzzzznotfound")

    WebDriverWait(driver, 15).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#employee tbody"),
            "No matching records found"
        )
    )

    assert "No matching records found" in driver.page_source


# ======================================================
# FT_019 - Upload Invalid Photo
# ======================================================

@pytest.mark.ft019
def test_FT_019_upload_invalid_photo(driver, base_url):
    login(driver, base_url)

    driver.get(f"{base_url}/profil.php")

    upload_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )

    # Pastikan folder test_files ada dan file test.pdf ada
    file_path = os.path.abspath("test_files/test.pdf")
    assert os.path.exists(file_path), f"File tidak ditemukan: {file_path}"

    upload_input.send_keys(file_path)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 15).until(
        lambda d: "Ekstensi tidak diijinkan" in d.page_source
    )

    assert "Ekstensi tidak diijinkan" in driver.page_source