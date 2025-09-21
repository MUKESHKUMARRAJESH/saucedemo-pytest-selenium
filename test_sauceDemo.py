import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

@pytest.fixture
def driver():
    """Sets up a stable browser session for each test."""
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

## ------------------ TEST SUITE ------------------ ##

def test_full_checkout_process(driver):
    """Test Case 1: Verifies the full, successful checkout process."""
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.saucedemo.com/")

    # LOGIN
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    time.sleep(0.5)
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    time.sleep(0.5)
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))
    time.sleep(1)

    # ADD TO CART
    add_to_cart_locator = (By.ID, "add-to-cart-sauced-labs-backpack")
    wait.until(EC.visibility_of_element_located(add_to_cart_locator))
    driver.find_element(*add_to_cart_locator).click()
    wait.until(EC.presence_of_element_located((By.ID, "remove-sauce-labs-backpack")))
    time.sleep(1)

    # GO TO CART AND CHECKOUT
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.visibility_of_element_located((By.ID, "checkout"))).click()
    wait.until(EC.visibility_of_element_located((By.ID, "first-name")))
    time.sleep(1)
    
    # FILL INFO
    driver.find_element(By.ID, "first-name").send_keys("Test")
    time.sleep(0.5)
    driver.find_element(By.ID, "last-name").send_keys("User")
    time.sleep(0.5)
    driver.find_element(By.ID, "postal-code").send_keys("12345")
    time.sleep(0.5)
    driver.find_element(By.ID, "continue").click()

    # FINISH
    wait.until(EC.visibility_of_element_located((By.ID, "finish"))).click()
    completion_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))
    assert completion_header.text == "Thank you for your order!"
    print("\n✅ PASSED: Full checkout process.")
    time.sleep(2)

@pytest.mark.parametrize("username, password, expected_error", [
    ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out."),
    ("incorrect_user", "wrong_password", "Username and password do not match"),
    ("standard_user", "wrong_password", "Username and password do not match")
])
def test_various_invalid_logins(driver, username, password, expected_error):
    """
    Test Case 2 (Upgraded): Verifies error messages for multiple invalid login attempts.
    """
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.saucedemo.com/")
    
    print(f"\nTesting with user: '{username}'...")
    driver.find_element(By.ID, "user-name").send_keys(username)
    time.sleep(0.5)
    driver.find_element(By.ID, "password").send_keys(password)
    time.sleep(0.5)
    driver.find_element(By.ID, "login-button").click()

    error_message_locator = (By.CSS_SELECTOR, "h3[data-test='error']")
    error_message = wait.until(EC.visibility_of_element_located(error_message_locator))
    time.sleep(1)
    
    assert expected_error in error_message.text
    print(f"✅ PASSED: Correct error message shown for '{username}'.")

def test_add_and_remove_item_from_cart_page(driver):
    """Test Case 3: Verifies removing an item from the cart page."""
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.saucedemo.com/")
    
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))

    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    time.sleep(1)
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "cart_item")))
    time.sleep(1)

    driver.find_element(By.ID, "remove-sauce-labs-backpack").click()
    print("\nRemoved item from cart.")
    time.sleep(1)

    item_is_gone = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "cart_item")))
    assert item_is_gone is True
    print("✅ PASSED: Item successfully removed from cart page.")

def test_product_sort_by_price_low_to_high(driver):
    """Test Case 4: Verifies the product sorting feature works correctly."""
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.saucedemo.com/")
    
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))
    
    sorter_dropdown = Select(driver.find_element(By.CLASS_NAME, "product_sort_container"))
    sorter_dropdown.select_by_value("lohi")
    print("\nSorted products by price (low to high).")
    time.sleep(1)

    price_elements = driver.find_elements(By.CLASS_NAME, "inventory_item_price")
    prices = [float(p.text.replace("$", "")) for p in price_elements]
    print(f"Prices found: {prices}")

    assert prices == sorted(prices)
    print("✅ PASSED: Products are correctly sorted by price.")

def test_footer_social_links(driver):
    """Test Case 5: Verifies the Twitter/X social link opens in a new tab."""
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.saucedemo.com/")
    
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))

    original_window = driver.current_window_handle
    print(f"\nOriginal window ID: {original_window}")

    twitter_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "social_twitter")))
    twitter_link.click()
    print("Clicked the X/Twitter link.")
    
    wait.until(EC.number_of_windows_to_be(2))
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break
    
    print(f"Switched to new window: {driver.current_url}")
    time.sleep(2)

    assert "x.com/saucelabs" in driver.current_url
    
    driver.close()
    driver.switch_to.window(original_window)
    print("Closed new tab and switched back to original.")
    time.sleep(1)
    
    assert "inventory.html" in driver.current_url
    print("✅ PASSED: Social media link opened and handled correctly.")