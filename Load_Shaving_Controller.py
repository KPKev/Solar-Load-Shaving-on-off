# This app goes to my solar web interface of the inverter, logs in, extracts power_value data in watts, 
# and adjusts the Load Shave setting based on how many watts the solar panales are outputing, the app cycles every 15 minutes. .


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.action_chains import ActionChains
def login_and_extract():
    """
    Logs into a web page, extracts data, and performs navigation and interaction actions.

    This function initializes a WebDriver, navigates to a login page, enters the username and password,
    clicks the login button, handles the accept and agree button if present, waits for the page to load,
    extracts data from a specified element, navigates to different pages, adjusts a setting based on the
    extracted data, saves the changes, and finally closes the WebDriver.

    Raises:
        NoSuchElementException: If the specified element is not found using the provided XPath.
        TimeoutException: If the accept and agree button is not found or not clickable.

    """
    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    print("WebDriver initialized.")

    try:
        driver.get("http://192.168.7.2/login.html")
        print("Navigated to login page.")

        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.NAME, "login_username"))).send_keys("admin")
        print("Username entered.")
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.NAME, "login_password"))).send_keys("December1")
        print("Password entered.")
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "inpLoginBtn"))).click()
        print("Login button clicked.")

        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "btnOk"))).click()
            print("Accept and Agree button clicked.")
        except TimeoutException:
            print("Accept and Agree button not found or not clickable.")

        print("Waiting for page to load...")
        time.sleep(8)  # Adjusted comment to match the actual wait time

        # Simplified the data extraction logic
        try:
            data_xpath = '/html/body/div[52]'  # Assuming this is correct
            data_element = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, data_xpath)))
            data_text = data_element.text
            print(f"Extracted data: {data_text}")
        except NoSuchElementException:
            print("The specified element was not found using the provided XPath.")

        # Navigation and interaction logic
        print("Navigating to 'System Devices'...")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "System Devices"))).click()
        print("Navigated to 'System Devices' successfully.")
        time.sleep(1)

        print("Clicking on 'CSW (0)'...")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-xbdevice-tag='CSW_1394882_0']"))).click()
        print("Clicked on 'CSW (0)' successfully.")
        time.sleep(1)

        print("Navigating to 'Settings' within 'CSW (0)'...")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Settings"))).click()
        print("Navigated to 'Settings' within 'CSW (0)' successfully.")
        time.sleep(1)
        print("Navigating to AC Support'")
        #<a class="accordion-toggle" data-toggle="collapse" data-parent="#settingsAccordion" href="#asid_3e8ae9d7"><div><table class="accordianHeaderTable"><tbody><tr><td><div class="sprmgr_ac_25x25_skyblue"></div></td><td class="leftCell"><span>AC Support</span></td></tr></tbody></table></div></a>
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "AC Support"))).click()
        print("Navigated to 'AC Support' successfully.")
        time.sleep(1)
        print("Adjusting 'Load Shave' setting...")

        # Locate the dropdown for "Load Shave" setting
        xpath_to_load_shaving_dropdown = "//select[@id='svrw_9564c870']"
        load_shaving_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_to_load_shaving_dropdown))
        )

        # Click the dropdown to expand it
        load_shaving_dropdown.click()

        # Initialize ActionChains for keyboard interactions
        action = ActionChains(driver)

        # Determine the direction of arrow key based on power value
        
        #data_text = "201 W"  # Placeholder, replace with actual extraction logic################################################################################
        
        power_value = int(data_text.split()[0])

        if power_value >= 200:
        # Press 'DOWN' arrow key to navigate to "Enable"
                action.send_keys(Keys.DOWN).perform()
        else:
    # Press 'UP' arrow key if needed, depending on the dropdown's default state
            action.send_keys(Keys.UP).perform()

        # After highlighting the option, try clicking the dropdown again to select
        load_shaving_dropdown.click()

        # Wait a bit for the dropdown to process the selection
        time.sleep(2)

        # Locate and click the "Write" button to save the changes
        write_button_xpath = "//button[contains(@class, 'svrwbtn_w_9564c870')]"
        write_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, write_button_xpath))
        )
        write_button.click()
        time.sleep(5)
        print("Changes saved successfully.")
        print(f"Load Shave setting changed and saved based on power value: {power_value}")
        print(f"Extracted data: {data_text}")
        
    except Exception as e:
            print(f"An error occurred: {e}")
    finally:
            driver.quit()
            print("WebDriver closed.")

while True:
    login_and_extract()
    print("Waiting 15 minutes before the next check...")
    time.sleep(900)  # 15 minutes

#login_and_configure_load_shave()
