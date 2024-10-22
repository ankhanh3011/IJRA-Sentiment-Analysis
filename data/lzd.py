import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import random
import pandas as pd

# Configure ChromeDriver path
chrome_driver_path = "./chromedriver-win64/chromedriver.exe"

# Setup Chrome options for undetected-chromedriver
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
service = Service(executable_path=chrome_driver_path)

# Initialize undetected ChromeDriver
driver = uc.Chrome(service=service, options=options)

# Anti-bot measures
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})

def scroll_and_wait(driver):
    scroll_pause_time = random.uniform(2, 4)  # Random pause time to mimic human behavior
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

def scrape_lazada_reviews(url):
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # Random wait time for the page to load

    reviews = []

    # Scroll and wait to ensure all reviews are loaded
    for _ in range(5):
        scroll_and_wait(driver)

    while True:
        try:
            # Locate the review elements
            review_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.item"))
            )
            print(f"Found {len(review_elements)} review elements")  # Debugging statement

            for review_element in review_elements:
                try:
                    # Find all star images within the rating container
                    star_elements = review_element.find_elements(By.CSS_SELECTOR, "div.container-star.starCtn.left img")
                    rating = sum(1 for star in star_elements if "19" in star.get_attribute("src"))  # Count yellow stars

                    if rating < 5.0:  # Filter for reviews below 5 stars
                        comment = review_element.find_element(By.CSS_SELECTOR, "div.content").text

                        review_data = {
                            "rating": rating,
                            "comment": comment
                        }

                        print(f"Extracted review: {review_data}")  # Debugging statement

                        reviews.append(review_data)
                except Exception as e:
                    print(f"Error extracting review: {e}")

            # Try to find the "Next" button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next"))
                )
                print("Next button found. Clicking to next page.")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(random.uniform(3, 5))  # Random wait time for the next page to load

                # Additional scrolls to ensure reviews are loaded
                for _ in range(5):
                    scroll_and_wait(driver)

            except Exception as e:
                print("Next button not found or no more pages available.")
                break
        except Exception as e:
            print(f"Error locating review elements: {e}")
            break

    return reviews

# URL of the Lazada product
product_url = "https://www.lazada.vn/"
reviews = scrape_lazada_reviews(product_url)

# Close the driver
driver.quit()

# Convert the reviews to a DataFrame
df = pd.DataFrame(reviews)

# Print the DataFrame
print(df.head())

# Save the DataFrame to an Excel file
df.to_excel('lazada_reviews.xlsx', index=False)
