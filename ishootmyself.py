import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, 
                                      TimeoutException, 
                                      WebDriverException)

class MarketingBot:
    def __init__(self):
        # Configuration
        self.config = {
            "website": {
                "base_url": "http://www.ishotmyself.nl",
                "login_page": "/online-members.php",
                "credentials": {
                    "username": "",  # Add your username
                    "password": "",  # Add your password
                },
                "message": "hallo, als je op zoek bent naar seks, neem dan contact met mij op:to.ly/1tqWI",
            },
            "behavior": {
                "max_users": 50,
                "pages_to_scrape": 2,
                "min_delay": 3,
                "max_delay": 8,
                "page_load_timeout": 30,
            },
            "proxy": {
                "enabled": False,
                "address": "47.74.9.208",
                "port": 3128,
            }
        }
        
        # Initialize browser
        self.browser = self._init_browser()
        self.wait = WebDriverWait(self.browser, 10)
        
    def _init_browser(self):
        """Initialize and configure the browser with optional proxy"""
        options = webdriver.FirefoxOptions()
        
        if self.config["proxy"]["enabled"]:
            profile = webdriver.FirefoxProfile()
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.http', self.config["proxy"]["address"])
            profile.set_preference('network.proxy.http_port', self.config["proxy"]["port"])
            profile.set_preference('network.proxy.ssl', self.config["proxy"]["address"])
            profile.set_preference('network.proxy.ssl_port', self.config["proxy"]["port"])
            browser = webdriver.Firefox(firefox_profile=profile)
        else:
            browser = webdriver.Firefox()
            
        browser.set_page_load_timeout(self.config["behavior"]["page_load_timeout"])
        return browser
    
    def _random_delay(self):
        """Add random delay between actions to appear more human-like"""
        time.sleep(random.uniform(
            self.config["behavior"]["min_delay"],
            self.config["behavior"]["max_delay"]
        ))
    
    def login(self):
        """Handle the login process"""
        try:
            self.browser.get(self.config["website"]["base_url"] + self.config["website"]["login_page"])
            self._random_delay()
            
            # Click login button if present
            try:
                login_btn = self.browser.find_element(By.CSS_SELECTOR, "#lgnbtn")
                login_btn.click()
                self._random_delay()
            except NoSuchElementException:
                pass
            
            # Fill login form
            username_field = self.browser.find_element(By.NAME, "u")
            password_field = self.browser.find_element(By.NAME, "p")
            
            username_field.send_keys(self.config["website"]["credentials"]["username"])
            password_field.send_keys(self.config["website"]["credentials"]["password"])
            
            # Handle remember me checkbox
            try:
                remember_me = self.browser.find_element(By.NAME, "rememberme")
                remember_me.click()
            except NoSuchElementException:
                pass
            
            # Submit login
            submit_btn = self.browser.find_element(By.CSS_SELECTOR, "a.btn:nth-child(3)")
            submit_btn.click()
            
            self._random_delay()
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def scrape_users(self):
        """Scrape user profile URLs from the members page"""
        user_urls = []
        current_page = 1
        
        try:
            while len(user_urls) < self.config["behavior"]["max_users"] and \
                  current_page <= self.config["behavior"]["pages_to_scrape"]:
                
                self.browser.get(f"{self.config['website']['base_url']}/online-members.php")
                self._random_delay()
                
                # Find all user list items
                try:
                    user_elements = self.browser.find_elements(
                        By.XPATH, "/html/body/div[2]/div/div[2]/ul/li"
                    )
                    
                    for user in user_elements:
                        try:
                            user_link = user.find_element(By.TAG_NAME, "a").get_attribute("href")
                            if user_link and user_link not in user_urls:
                                user_urls.append(user_link)
                                if len(user_urls) >= self.config["behavior"]["max_users"]:
                                    break
                        except NoSuchElementException:
                            continue
                            
                except NoSuchElementException:
                    print("Could not find user elements on page")
                    break
                
                # Try to navigate to next page
                try:
                    next_page = self.browser.find_element(
                        By.CSS_SELECTOR, ".pagination>a:nth-child(6)"
                    )
                    next_page.click()
                    current_page += 1
                    self._random_delay()
                except NoSuchElementException:
                    print("No more pages available")
                    break
                    
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
        
        return user_urls
    
    def send_message(self, user_url):
        """Send message to a single user"""
        try:
            self.browser.get(user_url)
            self._random_delay()
            
            # Try to find and click message button
            try:
                message_btn = self.browser.find_element(By.CSS_SELECTOR, ".msg")
                message_btn.click()
                time.sleep(1)
            except NoSuchElementException:
                return False
            
            # Try to send message
            try:
                message_box = self.browser.find_element(By.NAME, "newreply")
                message_box.send_keys(self.config["website"]["message"])
                
                send_btn = self.browser.find_element(
                    By.CSS_SELECTOR, 'a.btn:nth-child(5)'
                )
                send_btn.click()
                
                self._random_delay()
                return True
            except NoSuchElementException:
                return False
                
        except Exception as e:
            print(f"Error messaging user {user_url}: {str(e)}")
            return False
    
    def run(self):
        """Main execution flow"""
        print(f"Starting bot at {datetime.now()}")
        
        if not self.login():
            print("Login failed. Exiting.")
            self.browser.quit()
            return
        
        print("Login successful. Starting user scraping...")
        user_urls = self.scrape_users()
        print(f"Found {len(user_urls)} users to message.")
        
        success_count = 0
        for i, url in enumerate(user_urls, 1):
            print(f"Processing user {i}/{len(user_urls)}")
            if self.send_message(url):
                success_count += 1
                print(f"Message sent ({success_count} total)")
            else:
                print("Failed to send message")
        
        print(f"Completed. Successfully sent {success_count}/{len(user_urls)} messages.")
        print(f"Finished at {datetime.now()}")
        self.browser.quit()

if __name__ == "__main__":
    bot = MarketingBot()
    bot.run()







