import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os

# ChromeDriver path
chrome_driver_path = "./chromedriver-win64/chromedriver.exe"

# Your Shopee credentials
username = "vtm6rc1d0q"
password = "Hphuonglinh"


def save_cookies(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def load_cookies(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)


def login_shopee(username, password):
    driver.get("https://shopee.vn/buyer/login")
    print("Navigated to login page")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "loginKey"))
    )
    print("Username input located")

    # Enter username
    username_input = driver.find_element(By.NAME, "loginKey")
    username_input.send_keys(username)
    print("Username entered")

    # Enter password
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)
    print("Password entered")

    # Click login button
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='vvOL40 iesrPs AsFRg8 qCI4rz ZKayWA AnY7KS']"))
    )
    print("Login button located")
    login_button.click()
    print("Login button clicked")

    # Pause to allow manual verification
    print("Please complete the CAPTCHA and any additional verification manually...")
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='navbar__username']"))
    )
    print("Login successful")
    save_cookies(driver, "shopee_cookies.pkl")
    print("Session cookies saved")


def scrape_shopee_reviews(url):
    driver.get(url)
    time.sleep(2)  # Wait for the page to load

    # Scroll down to load more reviews
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for the reviews to load

    reviews = []
    review_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='shopee-product-rating__main']")

    for review_element in review_elements:
        try:
            username = review_element.find_element(By.CSS_SELECTOR,
                                                   "div[class*='shopee-product-rating__author-name']").text
            rating = \
            review_element.find_element(By.CSS_SELECTOR, "div[class*='shopee-product-rating__rating']").get_attribute(
                'class').split()[-1]
            comment = review_element.find_element(By.CSS_SELECTOR, "div[class*='shopee-product-rating__content']").text

            reviews.append({
                "username": username,
                "rating": rating,
                "comment": comment
            })
        except Exception as e:
            print(f"Error extracting review: {e}")

    return reviews


# Initialize undetected ChromeDriver
driver = uc.Chrome()

# Check if session cookies exist
if os.path.exists("shopee_cookies.pkl"):
    driver.get("https://shopee.vn")
    load_cookies(driver, "shopee_cookies.pkl")
    driver.refresh()
    print("Session cookies loaded, no need to log in again")
    time.sleep(5)  # Wait for the cookies to take effect
else:
    # Login to Shopee
    try:
        login_shopee(username, password)
    except Exception as e:
        print(f"Login failed: {e}")
        driver.quit()
        exit(1)

# URL of the Shopee product
product_url = "https://shopee.vn/Remote-%C4%90i%E1%BB%81u-khi%E1%BB%83n-FPT-tv-4K-FX6-truy%E1%BB%81n-h%C3%ACnh-h%C3%A0ng-lo%E1%BA%A1i-t%E1%BB%91t-b%E1%BA%A3o-h%C3%A0nh-2-th%C3%A1ng-i.618602080.21477604558?sp_atk=1e8baed7-335a-45a8-8e3e-2151eb58f7be&xptdk=1e8baed7-335a-45a8-8e3e-2151eb58f7be"
reviews = scrape_shopee_reviews(product_url)

# Close the driver
driver.quit()

# Print the reviews
for review in reviews:
    print(review)
