# This app goes to my solar web interface of the inverter, logs in, extracts power_value data in watts, 
# and adjusts the Load Shave setting based on how many watts the solar panales are outputing, the app cycles every 15 minutes. .
import time
from datetime import timedelta, datetime
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def print_current_time_ct():
    """
    Prints the current date and time in Central Time (CT) in 12-hour format.
    """
    central_tz = pytz.timezone('America/Chicago')
    now_central = datetime.now(central_tz)
    

def countdown(t):
    """
    Displays a real-time countdown for t minutes.
    """
    end_time = datetime.now() + timedelta(minutes=t)
    while True:
        remaining_time = end_time - datetime.now()
        if remaining_time.total_seconds() <= 0:
            print("\r00:00:00 Time's up!", end="")
            break
        # Update the countdown every second
        print(f"\r{str(remaining_time)[:-7]}", end="")
        time.sleep(1)

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
    print_current_time_ct()
    print("WebDriver initialized.")

    try:
        driver.get("http://192.168.7.3/login.html")
        print("")
        print("")
        print("Navigated to login page.")
        print("")
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.NAME, "login_username"))).send_keys("admin")
        print("")
        print("Username entered.")
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.NAME, "login_password"))).send_keys("December1")
        print("")
        print("Password entered.")
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "inpLoginBtn"))).click()
        print("")
        print("Login button clicked.")
        print("")

        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "btnOk"))).click()
            print("")
            print("Accept and Agree button clicked.")
            print("")
        except TimeoutException:
            print("")
            print("Accept and Agree button not found or not clickable.")
            print("")
            time.sleep(2)
        print("Waiting for page to load... just one moment")
        print("")
        time.sleep(8)  # Adjusted comment to match the actual wait time

        # Simplified the data extraction logic
        try:
            data_xpath = '/html/body/div[52]'  # Assuming this is correct
            data_element = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, data_xpath)))
            data_text = data_element.text
            print("")
            print(f"Extracted data: {data_text}")
        except NoSuchElementException:
            print("The specified element was not found using the provided XPath.")
        print("")
        # Navigation and interaction logic
        print("Navigating to 'System Devices'...")
        time.sleep(2)
        print("")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "System Devices"))).click()
        print("")
        print("Navigated to 'System Devices' successfully.")
        time.sleep(4)
        print("")
        print("Clicking on 'CSW (0)'...")
        print("")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-xbdevice-tag='CSW_1394882_0']"))).click()
        print("")
        print("Clicked on 'CSW (0)' successfully.")
        print("")
        time.sleep(2)
        print("")

        print("Navigating to 'Settings' within 'CSW (0)'...")
        print("")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Settings"))).click()
        print("")
        print("Navigated to 'Settings' within 'CSW (0)' successfully.")
        print("")
        time.sleep(2)
        print("")
        print("Navigating to AC Support'")
        print("")
        #<a class="accordion-toggle" data-toggle="collapse" data-parent="#settingsAccordion" href="#asid_3e8ae9d7"><div><table class="accordianHeaderTable"><tbody><tr><td><div class="sprmgr_ac_25x25_skyblue"></div></td><td class="leftCell"><span>AC Support</span></td></tr></tbody></table></div></a>
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "AC Support"))).click()
        print("")
        print("Navigated to 'AC Support' successfully.")
        print("")
        time.sleep(1)
        print("Adjusting 'Load Shave' setting...")
        print("")

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

        if power_value >= 100:
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
        print("")
        print("Changes saved successfully.")
        print("")
        time.sleep(2)
        print("")
        print("Preparing for cycle")
        print("")
        time.sleep(2)
        print("")
        print(".")
        print("")
        time.sleep(1)
        print("")
        print("..")
        print("")
        time.sleep(2)
        print("")
        print("...")
        print("")
        time.sleep(3)
        print ("Initiating Operation Deep Freeze")
        print("")
        time.sleep(4)
        print("Waiting 15 minutes before the next cycle...")
        print("")
        time.sleep(2)
        print(f"Load Shaving has been adjusted based on the total power value: {power_value}")
        print("100 W's or more will enable load shaving, otherwise it will be disabled.")
        print("")
        time.sleep(2)
        print(f"The solar panels are currently producing a total of : {data_text}'s")
        print("")
        
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
        
        
        print("WebDriver closed.")
        
        
        
        
    finally:
        driver.quit()
        

while True:
    login_and_extract()
    print("")
    
    print("TIME LEFT")
    # Instead of a static wait, use the countdown function for a dynamic 15-minute countdown
    countdown(15)

