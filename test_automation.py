import unittest
import time
import warnings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class WebAppTest(unittest.TestCase):

    def setUp(self):
        # --- ROBUST LINUX / EC2 / JENKINS SETUP ---
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox")   
        chrome_options.add_argument("--disable-dev-shm-usage") 
        chrome_options.add_argument("--disable-gpu")  
        chrome_options.add_argument("--window-size=1920,1080") 
        chrome_options.add_argument("--remote-debugging-port=9222") 
        
        warnings.simplefilter("ignore", ResourceWarning)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.base_url = "https://www.saucedemo.com/"
        self.driver.implicitly_wait(5) 

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    # --- TEST CASE 1: Valid Login ---
    def test_01_valid_login(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, "user-name").send_keys("standard_user")
        self.driver.find_element(By.ID, "password").send_keys("secret_sauce")
        self.driver.find_element(By.ID, "login-button").click()
        self.assertIn("inventory.html", self.driver.current_url)

    # --- TEST CASE 2: Invalid Login ---
    def test_02_invalid_login(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, "user-name").send_keys("wrong_user")
        self.driver.find_element(By.ID, "password").send_keys("wrong_pass")
        self.driver.find_element(By.ID, "login-button").click()
        error_msg = self.driver.find_element(By.CSS_SELECTOR, "h3[data-test='error']").text
        self.assertIn("Username and password do not match", error_msg)

    # --- TEST CASE 3: Add Item to Cart ---
    def test_03_add_to_cart(self):
        self._login()
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        cart_badge = self.driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
        self.assertEqual(cart_badge, "1")

    # --- TEST CASE 4: Remove Item from Cart ---
    def test_04_remove_from_cart(self):
        self._login()
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        self.driver.find_element(By.ID, "remove-sauce-labs-backpack").click()
        badges = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        self.assertEqual(len(badges), 0)

    # --- TEST CASE 5: Verify Inventory Item Details ---
    def test_05_verify_item_details(self):
        self._login()
        item_name = self.driver.find_element(By.CLASS_NAME, "inventory_item_name").text
        self.assertEqual(item_name, "Sauce Labs Backpack")

    # --- TEST CASE 6: Proceed to Checkout ---
    def test_06_proceed_checkout(self):
        self._login()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.driver.find_element(By.ID, "checkout").click()
        self.assertIn("checkout-step-one.html", self.driver.current_url)

    # --- TEST CASE 7: Checkout Missing Information Error ---
    def test_07_checkout_error_validation(self):
        self._login()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "continue").click()
        error = self.driver.find_element(By.CSS_SELECTOR, "h3[data-test='error']").text
        self.assertIn("First Name is required", error)

    # --- TEST CASE 8: Complete Checkout Flow (FIXED) ---
    def test_08_complete_checkout(self):
        self._login()
        self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.driver.find_element(By.ID, "checkout").click()
        
        self.driver.find_element(By.ID, "first-name").send_keys("Test")
        self.driver.find_element(By.ID, "last-name").send_keys("User")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        
        # --- MAJOR FIX: Use JavaScript to Force Click 'Continue' ---
        # This solves the issue where the button is not clicked in headless mode
        continue_btn = self.driver.find_element(By.ID, "continue")
        self.driver.execute_script("arguments[0].click();", continue_btn)
        
        # Now wait for the 'Finish' button on the next page
        wait = WebDriverWait(self.driver, 10)
        finish_btn = wait.until(EC.element_to_be_clickable((By.ID, "finish")))
        finish_btn.click()
        
        success_msg = self.driver.find_element(By.CLASS_NAME, "complete-header").text
        self.assertIn("Thank you for your order", success_msg)

    # --- TEST CASE 9: Verify Sorting ---
    def test_09_sort_products(self):
        self._login()
        self.driver.find_element(By.CLASS_NAME, "product_sort_container").click()
        self.driver.find_element(By.CSS_SELECTOR, "option[value='lohi']").click()
        prices = self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        first_price = float(prices[0].text.replace("$", ""))
        last_price = float(prices[-1].text.replace("$", ""))
        self.assertTrue(first_price <= last_price)

    # --- TEST CASE 10: Logout ---
    def test_10_logout(self):
        self._login()
        self.driver.find_element(By.ID, "react-burger-menu-btn").click()
        
        wait = WebDriverWait(self.driver, 10)
        logout_link = wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        logout_link.click()
        
        self.assertTrue(self.driver.find_element(By.ID, "login-button").is_displayed())

    # --- HELPER METHOD ---
    def _login(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, "user-name").send_keys("standard_user")
        self.driver.find_element(By.ID, "password").send_keys("secret_sauce")
        self.driver.find_element(By.ID, "login-button").click()

if __name__ == "__main__":
    unittest.main()
