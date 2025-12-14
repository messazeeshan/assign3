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
        # --- ROBUST LINUX / DOCKER SETUP ---
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
        self.driver.implicitly_wait(10) 

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    # --- HELPER: FORCE CLICK ---
    def force_click(self, by, value):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.presence_of_element_located((by, value)))
        self.driver.execute_script("arguments[0].click();", element)

    # --- TEST CASES (10 Total) ---

    def test_01_valid_login(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, "user-name").send_keys("standard_user")
        self.driver.find_element(By.ID, "password").send_keys("secret_sauce")
        self.force_click(By.ID, "login-button")
        self.assertIn("inventory.html", self.driver.current_url)

    def test_02_invalid_login(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, "user-name").send_keys("wrong_user")
        self.driver.find_element(By.ID, "password").send_keys("wrong_pass")
        self.force_click(By.ID, "login-button")
        error_msg = self.driver.find_element(By.CSS_SELECTOR, "h3[data-test='error']").text
        self.assertIn("Username and password do not match", error_msg)

    def test_03_add_to_cart(self):
        self._login()
        self.force_click(By.ID, "add-to-cart-sauce-labs-backpack")
        cart_badge = self.driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
        self.assertEqual(cart_badge, "1")

    def test_04_remove_from_cart(self):
        self._login()
        self.force_click(By.ID, "add-to-cart-sauce-labs-backpack")
        self.force_click(By.ID, "remove-sauce-labs-backpack")
        badges = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        self.assertEqual(len(badges), 0)

    def test_05_verify_item_details(self):
        self._login()
        item_name = self.driver.find_element(By.CLASS_NAME, "inventory_item_name").text
        self.assertEqual(item_name, "Sauce Labs Backpack")

    def test_06_proceed_checkout(self):
        self._login()
        self.force_click(By.CLASS_NAME, "shopping_cart_link")
        self.force_click(By.ID, "checkout")
        self.assertIn("checkout-step-one.html", self.driver.current_url)

    def test_07_checkout_error_validation(self):
        self._login()
        self.force_click(By.CLASS_NAME, "shopping_cart_link")
        self.force_click(By.ID, "checkout")
        self.force_click(By.ID, "continue")
        error = self.driver.find_element(By.CSS_SELECTOR, "h3[data-test='error']").text
        self.assertIn("First Name is required", error)

    # --- REPLACEMENT TEST: Check Footer Links (Simple & Fast) ---
    def test_08_check_footer_links(self):
        self._login()
        # Verify that the Twitter social link exists in the footer
        twitter_link = self.driver.find_element(By.CLASS_NAME, "social_twitter")
        self.assertTrue(twitter_link.is_displayed())

    def test_09_sort_products(self):
        self._login()
        self.force_click(By.CLASS_NAME, "product_sort_container")
        self.driver.find_element(By.CSS_SELECTOR, "option[value='lohi']").click()
        prices = self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        first_price = float(prices[0].text.replace("$", ""))
        last_price = float(prices[-1].text.replace("$", ""))
        self.assertTrue(first_price <= last_price)

    def test_10_logout(self):
        self._login()
        self.force_click(By.ID, "react-burger-menu-btn")
        
        wait = WebDriverWait(self.driver, 10)
        logout_link = wait.until(EC.presence_of_element_located((By.ID, "logout_sidebar_link")))
        self.driver.execute_script("arguments[0].click();", logout_link)
        
        self.assertTrue(self.driver.find_element(By.ID, "login-button").is_displayed())

    # --- HELPER METHOD ---
    def _login(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.ID, "user-name").send_keys("standard_user")
        self.driver.find_element(By.ID, "password").send_keys("secret_sauce")
        self.force_click(By.ID, "login-button")

if __name__ == "__main__":
    unittest.main()
