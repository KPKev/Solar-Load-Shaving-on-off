import time
from datetime import timedelta, datetime
import pytz
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---------------------------------------------------
# Global / module-level state
# ---------------------------------------------------
forced_disable = False  # Tracks whether we've forcibly disabled both modes
re_enable_threshold = 26.5  # Default re-enable voltage

# Example ASCII art (you can replace this text with any style you like)
ascii_art = r"""
            ▄ •▄  ▄▄▄·▄ •▄ ▄▄▄ . ▌ ▐·     ▄▄▄·▄▄▄  ▄▄▄ ..▄▄ · ▄▄▄ . ▐ ▄ ▄▄▄▄▄.▄▄ ·                     
            █▌▄▌▪▐█ ▄██▌▄▌▪▀▄.▀·▪█·█▌    ▐█ ▄█▀▄ █·▀▄.▀·▐█ ▀. ▀▄.▀·•█▌▐█•██  ▐█ ▀.                     
            ▐▀▀▄· ██▀·▐▀▀▄·▐▀▀▪▄▐█▐█•     ██▀·▐▀▀▄ ▐▀▀▪▄▄▀▀▀█▄▐▀▀▪▄▐█▐▐▌ ▐█.▪▄▀▀▀█▄                    
            ▐█.█▌▐█▪·•▐█.█▌▐█▄▄▌ ███     ▐█▪·•▐█•█▌▐█▄▄▌▐█▄▪▐█▐█▄▄▌██▐█▌ ▐█▌·▐█▄▪▐█                    
            ·▀  ▀.▀   ·▀  ▀ ▀▀▀ . ▀      .▀   .▀  ▀ ▀▀▀  ▀▀▀▀  ▀▀▀ ▀▀ █▪ ▀▀▀  ▀▀▀▀                     
▄▄▄▄▄ ▄ .▄▄▄▄ .    .▄▄ ·       ▄▄▌   ▄▄▄· ▄▄▄       ▄▄·        ▐ ▄ ▄▄▄▄▄▄▄▄        ▄▄▌  ▄▄▌  ▄▄▄ .▄▄▄  
•██  ██▪▐█▀▄.▀·    ▐█ ▀. ▪     ██•  ▐█ ▀█ ▀▄ █·    ▐█ ▌▪▪     •█▌▐█•██  ▀▄ █·▪     ██•  ██•  ▀▄.▀·▀▄ █·
 ▐█.▪██▀▐█▐▀▀▪▄    ▄▀▀▀█▄ ▄█▀▄ ██▪  ▄█▀▀█ ▐▀▀▄     ██ ▄▄ ▄█▀▄ ▐█▐▐▌ ▐█.▪▐▀▀▄  ▄█▀▄ ██▪  ██▪  ▐▀▀▪▄▐▀▀▄ 
 ▐█▌·██▌▐▀▐█▄▄▌    ▐█▄▪▐█▐█▌.▐▌▐█▌▐▌▐█ ▪▐▌▐█•█▌    ▐███▌▐█▌.▐▌██▐█▌ ▐█▌·▐█•█▌▐█▌.▐▌▐█▌▐▌▐█▌▐▌▐█▄▄▌▐█•█▌
 ▀▀▀ ▀▀▀ · ▀▀▀      ▀▀▀▀  ▀█▄▀▪.▀▀▀  ▀  ▀ .▀  ▀    ·▀▀▀  ▀█▄▀▪▀▀ █▪ ▀▀▀ .▀  ▀ ▀█▄▀▪.▀▀▀ .▀▀▀  ▀▀▀ .▀  ▀

                                    K P K e v  p r e s e n t s
                            T h e   S o l a r   C o n t r o l l e r 
"""

print(ascii_art)
time.sleep(1)  # Just a small delay so the title is clearly visible


def print_current_time_ct():
    """
    Prints the current date and time in Central Time (CT) in 12-hour format.
    """
    central_tz = pytz.timezone('America/Chicago')
    now_central = datetime.now(central_tz)
    print(f"[INFO] Current Time (CT): {now_central.strftime('%Y-%m-%d %I:%M:%S %p')}")

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
    print("")  # Move to a new line after countdown completes.

def is_reachable(ip, port=80):
    """
    Checks if the IP address is reachable.
    """
    print(f"[INFO] Checking connectivity to {ip}:{port}...")
    try:
        with socket.create_connection((ip, port), timeout=5):
            print(f"[INFO] {ip}:{port} is reachable.")
            return True
    except OSError:
        print(f"[ERROR] {ip}:{port} is not reachable.")
        return False

def set_and_verify_dropdown(
    driver,
    dropdown_xpath: str, 
    write_button_xpath: str, 
    desired_state: str, 
    label: str, 
    max_retries: int = 3
) -> bool:
    """
    Sets the dropdown to 'Enable' or 'Disable' (only if it's not already that),
    waits 12 seconds, and verifies the result up to max_retries times.
    """
    try:
        dropdown_elem = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
        )
    except TimeoutException:
        print(f"[ERROR] Could not locate {label} dropdown. Check XPath.")
        return False

    select_obj = Select(dropdown_elem)
    current_state = select_obj.first_selected_option.text.strip()

    print(f"[INFO] ({label}) Current state: '{current_state}'. Desired state: '{desired_state}'.")

    # If the current state is already what we want, skip
    if current_state == desired_state:
        print(f"[INFO] ({label}) Already set to '{desired_state}'. No change needed.")
        return True

    # Otherwise, proceed
    for attempt in range(1, max_retries + 1):
        print(f"[INFO] ({label}) Attempt {attempt} of {max_retries}: Setting to '{desired_state}'...")

        # Re-locate the dropdown
        try:
            dropdown_elem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
            )
        except TimeoutException:
            print(f"[ERROR] Could not locate {label} dropdown on attempt #{attempt}.")
            return False
        
        select_obj = Select(dropdown_elem)

        # Select the desired state
        try:
            select_obj.select_by_visible_text(desired_state)
            print(f"[INFO] ({label}) State selected: {desired_state}")
        except NoSuchElementException:
            print(f"[ERROR] ({label}) The option '{desired_state}' not found in dropdown.")
            return False

        # Click "Save"
        try:
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, write_button_xpath))
            )
            save_button.click()
            print(f"[INFO] ({label}) Save button clicked.")
        except TimeoutException:
            print(f"[ERROR] Could not click Save for {label}. Check button XPath.")
            return False

        # Wait 12 seconds
        print(f"[INFO] Waiting 12 seconds to allow {label} to persist...")
        time.sleep(12)

        # Verify
        try:
            dropdown_elem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
            )
            select_obj = Select(dropdown_elem)
            new_state = select_obj.first_selected_option.text.strip()

            if new_state == desired_state:
                print(f"[INFO] ({label}) Verified successfully: '{new_state}'")
                return True
            else:
                print(f"[ERROR] ({label}) is '{new_state}' but expected '{desired_state}'.")
                if attempt < max_retries:
                    print(f"[INFO] Retrying {label} selection...")
                else:
                    print(f"[ERROR] All {max_retries} retries exhausted for {label}.")
        except Exception as e:
            print(f"[ERROR] Could not verify {label} state on attempt #{attempt}: {e}")
            if attempt < max_retries:
                print(f"[INFO] Retrying {label} selection...")
            else:
                print(f"[ERROR] All {max_retries} retries exhausted for {label}.")

    return False  # If we get here, we never achieved the desired state

def forcibly_disable_both_modes(driver):
    """
    Navigate to AC Support page and forcibly disable
    both 'Load Shaving' and 'AC Support Mode' if not already.
    """
    print("[INFO] Forcibly disabling Load Shaving and AC Support...")

    print("[INFO] Navigating to 'System Devices'...")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "System Devices"))
    ).click()

    print("[INFO] Clicking on 'CSW (0)'...")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-xbdevice-tag='CSW_1394882_0']"))
    ).click()

    print("[INFO] Navigating to 'Settings'...")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Settings"))
    ).click()

    print("[INFO] Navigating to 'AC Support'...")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "AC Support"))
    ).click()

    # 2-second wait before forcibly setting
    print("[INFO] Waiting 2 seconds before forcibly disabling settings...")
    time.sleep(2)

    load_shaving_dropdown_xpath = (
        "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
        "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[2]/div[1]/select"
    )
    load_shaving_write_button_xpath = (
        "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
        "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[3]/div/button[2]"
    )

    ac_support_dropdown_xpath = (
        "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
        "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[2]/div[1]/select"
    )
    ac_support_write_button_xpath = (
        "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
        "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[3]/div/button[2]"
    )

    # Force each to 'Disable'
    set_and_verify_dropdown(
        driver=driver,
        dropdown_xpath=load_shaving_dropdown_xpath,
        write_button_xpath=load_shaving_write_button_xpath,
        desired_state="Disable",
        label="Load Shaving (Forced)"
    )

    set_and_verify_dropdown(
        driver=driver,
        dropdown_xpath=ac_support_dropdown_xpath,
        write_button_xpath=ac_support_write_button_xpath,
        desired_state="Disable",
        label="AC Support Mode (Forced)"
    )

# Global variables to track forced-disable state & threshold
forced_disable = False
re_enable_threshold = 26.5

def report_cycle_summary(
    driver,
    forced_disable: bool,
    mode_label: str,
    voltage_value: float,
    power_value: float
):
    """
    Print a summary of the final states for this cycle:
      - Battery voltage & solar power
      - forced_disable & mode_label
      - The final states of Load Shaving and AC Support
    """

    # Attempt to re-locate the final dropdown states
    load_shaving_dropdown_xpath = (
        "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
        "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[2]/div[1]/select"
    )
    ac_support_dropdown_xpath = (
        "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
        "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[2]/div[1]/select"
    )

    try:
        # Load Shaving
        ls_elem = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, load_shaving_dropdown_xpath))
        )
        ls_select = Select(ls_elem)
        ls_state = ls_select.first_selected_option.text.strip()
    except:
        ls_state = "Unknown"

    try:
        # AC Support
        ac_elem = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, ac_support_dropdown_xpath))
        )
        ac_select = Select(ac_elem)
        ac_state = ac_select.first_selected_option.text.strip()
    except:
        ac_state = "Unknown"

    print("\n[INFO] === Cycle Summary ===")
    print(f"       Mode: {mode_label}")
    print(f"       forced_disable: {forced_disable}")
    print(f"       Battery Voltage: {voltage_value:.2f} V")
    print(f"       Solar Power: {power_value} W")
    print(f"       Load Shaving: {ls_state}")
    print(f"       AC Support: {ac_state}")
    print("[INFO] =====================\n")

def login_and_extract(ip, port, solar_threshold, battery_voltage_threshold, re_enable_voltage):
    """
    Version 2.4

    1) If "forced_disable" is True, we do NOT re-enable anything unless
       the battery voltage >= re_enable_voltage.
    2) If battery < battery_voltage_threshold, force 'Disable' on
       both modes and set forced_disable = True.
    3) If forced_disable is False, normal logic (enable/disable based on
       solar_threshold).
    4) If forced_disable is True but voltage >= re_enable_voltage, we set
       forced_disable = False and resume normal logic.
    5) We track whether we are in "Charge mode" (forced_disable=True)
       or "Support mode" (forced_disable=False).
    6) After all is done, we call report_cycle_summary(...) to print a
       final summary for this cycle.
    """
    global forced_disable
    global re_enable_threshold

    # Update the global re_enable_threshold from user input
    re_enable_threshold = re_enable_voltage

    # Check if the device is reachable
    if not is_reachable(ip, port):
        print("[ERROR] Device is not reachable. Check network settings.")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    print_current_time_ct()
    print("[INFO] WebDriver initialized in headless mode.")

    try:
        # Mode indicator
        mode_label = "Charge mode" if forced_disable else "Support mode"
        print(f"[INFO] Current cycle: {mode_label}")

        login_url = f"http://{ip}/login.html"
        print(f"[INFO] Navigating to login page: {login_url}")
        driver.get(login_url)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "login_username"))
        ).send_keys("admin")
        print("[INFO] Username entered.")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "login_password"))
        ).send_keys("December1")
        print("[INFO] Password entered.")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "inpLoginBtn"))
        ).click()
        print("[INFO] Login button clicked.")

        # Handle potential "Accept and Agree" popup
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "btnOk"))
            ).click()
            print("[INFO] Accept and Agree button clicked.")
        except TimeoutException:
            print("[INFO] Accept and Agree button not found or not clickable.")

        print("[INFO] Waiting for the page to load fully...")
        time.sleep(15)  # Extended delay to ensure elements load properly

        # -----------------------------
        # Extract current power (watts)
        # -----------------------------
        try:
            data_xpath = '/html/body/div[52]'
            data_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, data_xpath))
            )
            data_text = data_element.text.strip()
            print(f"[INFO] Extracted watts (raw text): {data_text}")
        except TimeoutException:
            print("[ERROR] Failed to extract power value. Check the XPath or page structure.")
            driver.quit()
            return

        # Convert the extracted text to integer
        try:
            power_value = int(data_text.split()[0])
            print(f"[INFO] Power Value (W): {power_value}")
        except (ValueError, IndexError) as e:
            print(f"[ERROR] Could not parse power value from text: '{data_text}'. Error: {e}")
            driver.quit()
            return

        # -----------------------------
        # Extract battery voltage (V)
        # -----------------------------
        try:
            voltage_xpath = (
                '/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/'
                'div[1]/div[5]/div/div[2]/table/tbody/tr/td[1]/table/tbody/'
                'tr[1]/td/span'
            )
            voltage_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, voltage_xpath))
            )
            voltage_text = voltage_element.text.strip()
            voltage_value = float(voltage_text.split()[0])  # Extract numerical value
            print(f"[INFO] Extracted voltage: {voltage_value} V")
        except TimeoutException:
            print("[ERROR] Failed to extract voltage. Check the XPath or page structure.")
            driver.quit()
            return
        except (ValueError, IndexError) as e:
            print(f"[ERROR] Could not parse voltage from text: '{voltage_text}'. Error: {e}")
            driver.quit()
            return

        # ---------------------------------------------------------------
        #   1) If forced_disable is True, check if we can re-enable yet
        # ---------------------------------------------------------------
        if forced_disable:
            print(f"[INFO] 'forced_disable' is currently True.")
            if voltage_value >= re_enable_threshold:
                # We can re-enable the normal logic
                print(f"[INFO] Voltage ({voltage_value}V) >= {re_enable_threshold}V. "
                      "Cancelling forced disable. Normal logic can resume.")
                forced_disable = False
            else:
                # We must keep them disabled; forcibly disable & return
                print(f"[INFO] Battery voltage still below {re_enable_threshold}V. "
                      "Staying in forced_disable mode; disabling both modes.")
                forcibly_disable_both_modes(driver)
                # Summarize final states, then return
                report_cycle_summary(driver, forced_disable, "Charge mode", voltage_value, power_value)
                driver.quit()
                return

        # ------------------------------------------------------
        #   2) If forced_disable is False, check voltage
        # ------------------------------------------------------
        if not forced_disable:
            if voltage_value < battery_voltage_threshold:
                print(f"[WARNING] Voltage ({voltage_value}V) below {battery_voltage_threshold}V => "
                      "Forcing disable of both modes.")
                forced_disable = True
                forcibly_disable_both_modes(driver)
                # Summarize final states, then return
                report_cycle_summary(driver, forced_disable, "Charge mode", voltage_value, power_value)
                driver.quit()
                return
            else:
                # Voltage is above the lower threshold
                print(f"[INFO] Voltage ({voltage_value}V) is above threshold "
                      f"({battery_voltage_threshold}V). Proceeding with normal logic.")

        # ---------------------------------------
        # Proceed with normal logic (enable/disable)
        # ---------------------------------------
        print("[INFO] Navigating to 'System Devices'...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "System Devices"))
        ).click()

        print("[INFO] Clicking on 'CSW (0)'...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-xbdevice-tag='CSW_1394882_0']"))
        ).click()

        print("[INFO] Navigating to 'Settings'...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Settings"))
        ).click()

        print("[INFO] Navigating to 'AC Support'...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "AC Support"))
        ).click()

        # 2-second wait before setting Load Shaving
        print("[INFO] Waiting 2 seconds before setting Load Shaving...")
        time.sleep(2)

        desired_load_shave_state = "Enable" if power_value >= solar_threshold else "Disable"
        desired_ac_support_state = "Enable" if power_value >= solar_threshold else "Disable"

        # ============ 1) Load Shaving ============
        load_shaving_dropdown_xpath = (
            "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
            "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[2]/div[1]/select"
        )
        load_shaving_write_button_xpath = (
            "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
            "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[3]/div/button[2]"
        )
        print("[INFO] Adjusting Load Shaving...")
        ls_result = set_and_verify_dropdown(
            driver=driver,
            dropdown_xpath=load_shaving_dropdown_xpath,
            write_button_xpath=load_shaving_write_button_xpath,
            desired_state=desired_load_shave_state,
            label="Load Shaving"
        )
        if not ls_result:
            print("[ERROR] Load Shaving did NOT persist after all retries. Aborting script.")
            # Summarize final states, then return
            report_cycle_summary(driver, forced_disable, "Support mode", voltage_value, power_value)
            driver.quit()
            return

        # ============ 2) AC Support Mode ============
        ac_support_dropdown_xpath = (
            "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
            "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[2]/div[1]/select"
        )
        ac_support_write_button_xpath = (
            "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
            "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[3]/div/button[2]"
        )
        print("[INFO] Adjusting AC Support Mode...")
        ac_result = set_and_verify_dropdown(
            driver=driver,
            dropdown_xpath=ac_support_dropdown_xpath,
            write_button_xpath=ac_support_write_button_xpath,
            desired_state=desired_ac_support_state,
            label="AC Support Mode"
        )
        if not ac_result:
            print("[ERROR] AC Support Mode did NOT persist after all retries. Aborting script.")
            # Summarize final states, then return
            report_cycle_summary(driver, forced_disable, "Support mode", voltage_value, power_value)
            driver.quit()
            return

        print("[INFO] All changes applied based on current power and voltage thresholds.")
        print(f"[INFO] Final Status => Power: {power_value}W, Voltage: {voltage_value}V")

        # Summarize final states
        report_cycle_summary(driver, forced_disable, mode_label, voltage_value, power_value)

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
    finally:
        driver.quit()
        print("[INFO] WebDriver closed.")


def main():
    global forced_disable

    default_ip = "192.168.7.10"
    default_port = 80
    default_solar_threshold = 200
    default_battery_threshold = 25.1
    default_reenable_voltage = 26.5  # user-editable re-enable threshold
    default_cycle_interval = 15      # user-editable countdown in minutes

    print("Please provide the following details (press Enter for defaults):")
    ip_input = input(f"IP address (default: {default_ip}): ").strip()
    ip = ip_input if ip_input else default_ip

    port_input = input(f"Port number (default: {default_port}): ").strip()
    port = int(port_input) if port_input else default_port

    solar_input = input(
        f"Solar input threshold in watts (default: {default_solar_threshold}): "
    ).strip()
    solar_threshold = int(solar_input) if solar_input else default_solar_threshold

    battery_input = input(
        f"Battery voltage threshold in volts (default: {default_battery_threshold}): "
    ).strip()
    battery_voltage_threshold = float(battery_input) if battery_input else default_battery_threshold

    reenable_input = input(
        f"Re-enable voltage in volts (default: {default_reenable_voltage}): "
    ).strip()
    reenable_voltage = float(reenable_input) if reenable_input else default_reenable_voltage

    # Ask user for cycle interval
    cycle_input = input(
        f"Countdown interval in minutes (default: {default_cycle_interval}): "
    ).strip()
    try:
        cycle_interval = float(cycle_input) if cycle_input else default_cycle_interval
    except ValueError:
        print(f"[WARNING] Invalid entry for countdown interval. Using default {default_cycle_interval} min.")
        cycle_interval = default_cycle_interval

    # Prompt to reset forced_disable; default to NO if user just presses Enter
    reset_reenable_input = input(
        "Do you want to reset the re-enable flag (forced_disable)? (Yes/No) [Default: No]: "
    ).strip().lower()

    if not reset_reenable_input:  # If nothing typed
        reset_reenable_input = "no"  # default to "no"

    if reset_reenable_input in ("yes", "y"):
        forced_disable = False
        print("[INFO] forced_disable flag has been reset to False.")
    else:
        print("[INFO] forced_disable flag remains:", forced_disable)

    print(f"[INFO] Starting script (Version 2.4) with:")
    print(f"       - IP Address: {ip}")
    print(f"       - Port: {port}")
    print(f"       - Solar Threshold: {solar_threshold}W")
    print(f"       - Battery Low Threshold: {battery_voltage_threshold}V")
    print(f"       - Re-Enable Threshold: {reenable_voltage}V")
    print(f"       - forced_disable: {forced_disable}")
    print(f"       - Cycle Interval: {cycle_interval} minutes")
    print("-----------------------------------------------------------\n")

    while True:
        login_and_extract(ip, port, solar_threshold, battery_voltage_threshold, reenable_voltage)
        print(f"\n[INFO] Cycle completed. Starting countdown for the next cycle ({cycle_interval} minutes).")
        countdown(cycle_interval)

if __name__ == "__main__":
    main()

