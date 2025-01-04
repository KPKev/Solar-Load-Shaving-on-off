import os
import sys
import time
import json
import ctypes
import threading
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
import platform
import subprocess
import pytz
import socket

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

# pystray for tray icon
import pystray
from PIL import Image, ImageDraw

# ====================================================
# 1) GLOBALS / CONFIG
# ====================================================

stop_event = threading.Event()  # signals the main loop to stop
forced_disable = False          # same logic as your original script
re_enable_threshold = 26.9      # updated from config
current_config = {}             # will hold config in-memory

CONFIG_FILE = "solar_app_config.json"

def load_config():
    """Load config from JSON if available."""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_config(cfg):
    """Save config to JSON."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

# ====================================================
# 2) LOGGING (Daily rotation in logs/ folder)
#    File naming: solar_controller.log.MM-DD-YYYY
# ====================================================

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("SolarController")
logger.setLevel(logging.DEBUG)

# Console => Info+
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

log_file_path = os.path.join(LOG_DIR, "solar_controller.log")
fh = TimedRotatingFileHandler(
    log_file_path,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
fh.suffix = "%m-%d-%Y"
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

def log_and_print(level, message):
    level = level.lower()
    if level == 'debug':
        logger.debug(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    else:
        logger.info(message)

# ====================================================
# 3) CONSOLE HIDE/UNHIDE (Windows only)
# ====================================================

def get_console_window():
    """Returns console window handle if any (Windows)."""
    return ctypes.windll.kernel32.GetConsoleWindow()

def show_console():
    """Show console window (Windows only)."""
    hWnd = get_console_window()
    if hWnd != 0:
        # 1 => SW_SHOWNORMAL
        ctypes.windll.user32.ShowWindow(hWnd, 1)

def hide_console():
    """Hide console window (Windows only)."""
    hWnd = get_console_window()
    if hWnd != 0:
        # 0 => SW_HIDE
        ctypes.windll.user32.ShowWindow(hWnd, 0)

# ====================================================
# 4) ORIGINAL SOLAR LOGIC (Robust, forced_disable, etc.)
# ====================================================
def print_current_time_ct():
    central_tz = pytz.timezone('America/Chicago')
    now_central = datetime.now(central_tz)
    log_and_print('info', f"Current Time (CT): {now_central.strftime('%Y-%m-%d %I:%M:%S %p')}")

def is_reachable(ip, port=80):
    log_and_print('info', f"Checking connectivity to {ip}:{port}...")
    try:
        with socket.create_connection((ip, port), timeout=5):
            log_and_print('info', f"{ip}:{port} is reachable.")
            return True
    except OSError:
        log_and_print('error', f"{ip}:{port} is not reachable.")
        return False

def robust_wait_and_click(driver, by, locator, action_desc="Click element", max_attempts=3, base_wait=5):
    for attempt in range(1, max_attempts+1):
        log_and_print('debug', f"{action_desc}, attempt {attempt}/{max_attempts}, wait={base_wait*attempt}s")
        try:
            elem = WebDriverWait(driver, base_wait*attempt).until(
                EC.element_to_be_clickable((by, locator))
            )
            elem.click()
            log_and_print('info', f"SUCCESS: {action_desc} on attempt {attempt}")
            return True
        except TimeoutException:
            log_and_print('warning', f"Timeout: {action_desc} attempt {attempt}")
        except Exception as ex:
            log_and_print('warning', f"Error: {action_desc} attempt {attempt} => {ex}")
    log_and_print('error', f"All {max_attempts} attempts failed: {action_desc}")
    return False

def robust_wait_and_send_keys(driver, by, locator, keys, action_desc="Send keys", max_attempts=3, base_wait=5):
    for attempt in range(1, max_attempts+1):
        log_and_print('debug', f"{action_desc}, attempt {attempt}/{max_attempts}, wait={base_wait*attempt}s")
        try:
            elem = WebDriverWait(driver, base_wait*attempt).until(
                EC.element_to_be_clickable((by, locator))
            )
            elem.clear()
            elem.send_keys(keys)
            log_and_print('info', f"SUCCESS: {action_desc} on attempt {attempt}")
            return True
        except TimeoutException:
            log_and_print('warning', f"Timeout: {action_desc} attempt {attempt}")
        except Exception as ex:
            log_and_print('warning', f"Error: {action_desc} attempt {attempt} => {ex}")
    log_and_print('error', f"All {max_attempts} attempts failed: {action_desc}")
    return False

def set_and_verify_dropdown(driver, dropdown_xpath, write_button_xpath, desired_state, label, max_retries=3):
    log_and_print('info', f"---- set_and_verify_dropdown: {label} ----")
    for attempt in range(1, max_retries+1):
        try:
            dd_elem = WebDriverWait(driver, 10*attempt).until(
                EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
            )
            select_obj = Select(dd_elem)
            current_state = select_obj.first_selected_option.text.strip()
            log_and_print('info', f"{label} => Current: '{current_state}', Desired: '{desired_state}'")

            if current_state == desired_state:
                log_and_print('info', f"{label} is already '{desired_state}'.")
                return True

            select_obj.select_by_visible_text(desired_state)
            success = robust_wait_and_click(driver, By.XPATH, write_button_xpath, f"Save {label}")
            if not success:
                log_and_print('error', f"Failed Save for {label}, attempt {attempt}")
                continue

            # wait 12s
            log_and_print('debug', f"Waiting 12s for {label} to persist.")
            time.sleep(12)

            # verify
            dd_elem = WebDriverWait(driver, 10*attempt).until(
                EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
            )
            select_obj = Select(dd_elem)
            new_state = select_obj.first_selected_option.text.strip()
            if new_state == desired_state:
                log_and_print('info', f"{label} verified => {new_state}")
                return True
            else:
                log_and_print('error', f"{label} => '{new_state}' != '{desired_state}'")
        except TimeoutException:
            log_and_print('error', f"Timeout setting {label}, attempt {attempt}")
        except NoSuchElementException:
            log_and_print('error', f"Option '{desired_state}' not found for {label}")
            return False
        except Exception as e:
            log_and_print('error', f"Unexpected error in {label}: {e}")
    return False

def forcibly_disable_both_modes(driver, reason="Unknown"):
    log_and_print('info', f"Forcibly disabling both modes (Reason={reason})")

    robust_wait_and_click(driver, By.LINK_TEXT, "System Devices", "Click 'System Devices'")
    robust_wait_and_click(driver, By.CSS_SELECTOR, "span[data-xbdevice-tag='CSW_1394882_0']", "Click 'CSW (0)' device")
    robust_wait_and_click(driver, By.LINK_TEXT, "Settings", "Click 'Settings'")
    robust_wait_and_click(driver, By.LINK_TEXT, "AC Support", "Click 'AC Support'")

    log_and_print('info', "Waiting 2s before forcibly disabling.")
    time.sleep(2)

    load_shaving_dd = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                       "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[2]/div[1]/select")
    load_shaving_btn = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                        "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[3]/div/button[2]")
    ac_support_dd = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                     "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[2]/div[1]/select")
    ac_support_btn = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                      "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[3]/div/button[2]")

    set_and_verify_dropdown(driver, load_shaving_dd, load_shaving_btn, "Disable", "Load Shaving (Forced)")
    set_and_verify_dropdown(driver, ac_support_dd, ac_support_btn, "Disable", "AC Support Mode (Forced)")

def report_cycle_summary(driver, forced_disable, mode_label, voltage_value, power_value):
    load_shaving_dd = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                       "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[2]/div[1]/select")
    ac_support_dd = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                     "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[2]/div[1]/select")

    try:
        ls_elem = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, load_shaving_dd))
        )
        ls_state = Select(ls_elem).first_selected_option.text.strip()
    except:
        ls_state = "Unknown"
    try:
        ac_elem = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, ac_support_dd))
        )
        ac_state = Select(ac_elem).first_selected_option.text.strip()
    except:
        ac_state = "Unknown"

    log_and_print('info', "---- Cycle Summary ----")
    log_and_print('info', f"  Mode: {mode_label}")
    log_and_print('info', f"  forced_disable: {forced_disable}")
    log_and_print('info', f"  Battery Voltage: {voltage_value:.2f} V")
    log_and_print('info', f"  Solar Power: {power_value} W")
    log_and_print('info', f"  Load Shaving: {ls_state}")
    log_and_print('info', f"  AC Support: {ac_state}")
    log_and_print('info', "-----------------------")

def login_and_extract(ip, port, solar_threshold, battery_threshold, reenable_voltage):
    global forced_disable
    global re_enable_threshold
    re_enable_threshold = reenable_voltage

    if not is_reachable(ip, port):
        log_and_print('error', "Device unreachable => forcibly disable & abort cycle.")
        try:
            chrome_opts = Options()
            chrome_opts.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_opts)
            forcibly_disable_both_modes(driver, reason="unreachable")
            driver.quit()
        except Exception as e:
            log_and_print('error', f"Disable attempt error => {e}")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)

    print_current_time_ct()
    log_and_print('info', "WebDriver launched in headless mode.")

    try:
        mode_label = "Charge mode" if forced_disable else "Support mode"
        log_and_print('info', f"Entering cycle => {mode_label}")

        login_url = f"http://{ip}/login.html"
        log_and_print('info', f"Open page => {login_url}")
        driver.get(login_url)

        robust_wait_and_send_keys(driver, By.NAME, "login_username", "admin", "Enter username")
        robust_wait_and_send_keys(driver, By.NAME, "login_password", "December1", "Enter password")
        robust_wait_and_click(driver, By.ID, "inpLoginBtn", "Click 'Login'")

        robust_wait_and_click(driver, By.ID, "btnOk", "Accept & Agree popup", max_attempts=1, base_wait=3)

        log_and_print('info', "Waiting 15s after login for main page to load.")
        time.sleep(15)

        data_xpath = "/html/body/div[52]"
        power_value = 0
        try:
            data_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, data_xpath))
            )
            data_text = data_elem.text.strip()
            log_and_print('info', f"Extracted power text => '{data_text}'")
            power_value = int(data_text.split()[0])
            log_and_print('info', f"Power Value => {power_value} W")
        except Exception as e:
            log_and_print('error', f"Failed to get power => {e}, forcibly disable.")
            forcibly_disable_both_modes(driver, reason="data parse or lag")
            driver.quit()
            return

        # voltage
        voltage_value = None
        voltage_xpath = (
            "/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/"
            "div[1]/div[5]/div/div[2]/table/tbody/tr/td[1]/table/tbody/"
            "tr[1]/td/span"
        )
        for attempt in range(1, 4):
            log_and_print('debug', f"Voltage read attempt {attempt}/3")
            try:
                v_elem = WebDriverWait(driver, 10*attempt).until(
                    EC.presence_of_element_located((By.XPATH, voltage_xpath))
                )
                v_text = v_elem.text.strip()
                if not v_text:
                    log_and_print('warning', f"Voltage text empty => wait 5s & retry")
                    time.sleep(5)
                    continue
                extracted = float(v_text.split()[0])
                if extracted == 0.0:
                    log_and_print('warning', f"Voltage 0.0 => wait 5s & retry")
                    time.sleep(5)
                    continue
                voltage_value = extracted
                log_and_print('info', f"Battery voltage => {voltage_value} V (attempt {attempt})")
                break
            except Exception as e2:
                log_and_print('warning', f"Could not parse voltage => {e2}, retry after 5s")
                time.sleep(5)

        if voltage_value is None:
            log_and_print('error', "No valid voltage => forcibly disable.")
            forcibly_disable_both_modes(driver, reason="invalid voltage read")
            driver.quit()
            return

        # forced_disable logic
        if forced_disable:
            log_and_print('info', f"forced_disable=True => check if voltage >= {re_enable_threshold}")
            if voltage_value >= re_enable_threshold:
                log_and_print('info', f"Voltage {voltage_value} >= {re_enable_threshold}, re-enable normal logic.")
                forced_disable = False
            else:
                log_and_print('info', f"Voltage still below {re_enable_threshold}, remain forced disable.")
                forcibly_disable_both_modes(driver, reason="low voltage")
                report_cycle_summary(driver, forced_disable, "Charge mode", voltage_value, power_value)
                driver.quit()
                return

        if not forced_disable:
            log_and_print('info', f"Not forced_disable => check battery threshold {current_config['battery_threshold']}")
            if voltage_value < current_config["battery_threshold"]:
                log_and_print('warning', f"Voltage {voltage_value} < {current_config['battery_threshold']} => forcing disable.")
                forced_disable = True
                forcibly_disable_both_modes(driver, reason="low voltage")
                report_cycle_summary(driver, forced_disable, "Charge mode", voltage_value, power_value)
                driver.quit()
                return
            else:
                log_and_print('info', f"Voltage {voltage_value} >= {current_config['battery_threshold']}, normal logic proceed.")

        # normal => navigate & set states
        if not robust_wait_and_click(driver, By.LINK_TEXT, "System Devices", "Navigate => System Devices"):
            forcibly_disable_both_modes(driver, reason="lag/unreachable")
            driver.quit()
            return
        if not robust_wait_and_click(driver, By.CSS_SELECTOR, "span[data-xbdevice-tag='CSW_1394882_0']", "Click 'CSW (0)'"):
            forcibly_disable_both_modes(driver, reason="lag/unreachable")
            driver.quit()
            return
        if not robust_wait_and_click(driver, By.LINK_TEXT, "Settings", "Navigate => Settings"):
            forcibly_disable_both_modes(driver, reason="lag/unreachable")
            driver.quit()
            return
        if not robust_wait_and_click(driver, By.LINK_TEXT, "AC Support", "Navigate => AC Support"):
            forcibly_disable_both_modes(driver, reason="lag/unreachable")
            driver.quit()
            return

        log_and_print('info', "Wait 2s before setting load shaving/AC support.")
        time.sleep(2)

        desired_ls = "Enable" if power_value >= solar_threshold else "Disable"
        desired_ac = "Enable" if power_value >= solar_threshold else "Disable"

        ls_dd = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                 "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[2]/div[1]/select")
        ls_btn = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                  "div/div[6]/div[2]/div/form/table/tbody/tr[4]/td[3]/div/button[2]")
        ls_ok = set_and_verify_dropdown(driver, ls_dd, ls_btn, desired_ls, "Load Shaving")
        if not ls_ok:
            forcibly_disable_both_modes(driver, reason="dropdown error")
            report_cycle_summary(driver, forced_disable, "Support mode", voltage_value, power_value)
            driver.quit()
            return

        ac_dd = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                 "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[2]/div[1]/select")
        ac_btn = ("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/div/div/div[2]/div/"
                  "div/div[6]/div[2]/div/form/table/tbody/tr[2]/td[3]/div/button[2]")
        ac_ok = set_and_verify_dropdown(driver, ac_dd, ac_btn, desired_ac, "AC Support Mode")
        if not ac_ok:
            forcibly_disable_both_modes(driver, reason="dropdown error")
            report_cycle_summary(driver, forced_disable, "Support mode", voltage_value, power_value)
            driver.quit()
            return

        log_and_print('info', f"Success => Power: {power_value}W, Voltage: {voltage_value}V")
        report_cycle_summary(driver, forced_disable, mode_label, voltage_value, power_value)

    except Exception as e:
        log_and_print('error', f"Unexpected error => {e}, forcibly disable.")
        forcibly_disable_both_modes(driver, reason="critical error")
    finally:
        driver.quit()
        log_and_print('info', "WebDriver closed.")

# ====================================================
# 5) MAIN SOLAR LOOP
# ====================================================
def main_solar_loop():
    """Runs in a background thread, calling login_and_extract() repeatedly."""
    global current_config
    global forced_disable

    while not stop_event.is_set():
        ip = current_config["ip"]
        port = current_config["port"]
        solar_threshold = current_config["solar_threshold"]
        battery_threshold = current_config["battery_threshold"]
        re_enable_voltage = current_config["re_enable_voltage"]
        cycle_interval = current_config["cycle_interval"]

        # perform one cycle
        login_and_extract(ip, port, solar_threshold, battery_threshold, re_enable_voltage)
        if stop_event.is_set():
            break

        # Wait for next cycle
        log_and_print('info', f"Cycle done. Waiting {cycle_interval} minutes for next cycle.")
        end_time = datetime.now() + timedelta(minutes=cycle_interval)
        while datetime.now() < end_time:
            if stop_event.is_set():
                break
            time.sleep(1)

    log_and_print('info', "main_solar_loop => Exiting gracefully.")

# ====================================================
# 6) CONSOLE SETTINGS PROMPT
# ====================================================
def console_settings_prompt():
    """
    Show console prompts for IP, port, thresholds, etc., then save to config.
    """
    global current_config
    global forced_disable

    print("\n=== Enter Settings (Press Enter to keep existing) ===\n")

    ip_old = current_config["ip"]
    ip_new = input(f"IP (default={ip_old}): ").strip()
    if ip_new:
        current_config["ip"] = ip_new

    port_old = current_config["port"]
    port_new = input(f"Port (default={port_old}): ").strip()
    if port_new:
        try:
            current_config["port"] = int(port_new)
        except:
            print("Invalid port. Keeping old.")

    sol_old = current_config["solar_threshold"]
    sol_new = input(f"Solar threshold (W) (default={sol_old}): ").strip()
    if sol_new:
        try:
            current_config["solar_threshold"] = int(sol_new)
        except:
            print("Invalid solar threshold. Keeping old.")

    bat_old = current_config["battery_threshold"]
    bat_new = input(f"Battery threshold (V) (default={bat_old}): ").strip()
    if bat_new:
        try:
            current_config["battery_threshold"] = float(bat_new)
        except:
            print("Invalid battery threshold. Keeping old.")

    re_old = current_config["re_enable_voltage"]
    re_new = input(f"Re-enable voltage (V) (default={re_old}): ").strip()
    if re_new:
        try:
            current_config["re_enable_voltage"] = float(re_new)
        except:
            print("Invalid re-enable voltage. Keeping old.")

    cyc_old = current_config["cycle_interval"]
    cyc_new = input(f"Cycle interval (minutes) (default={cyc_old}): ").strip()
    if cyc_new:
        try:
            current_config["cycle_interval"] = float(cyc_new)
        except:
            print("Invalid cycle interval. Keeping old.")

    # forced_disable reset prompt
    reset_fd_in = input("Reset forced_disable? (Yes/No) [Default: No]: ").strip().lower()
    if reset_fd_in in ("yes", "y"):
        forced_disable = False
        print("[INFO] forced_disable has been reset to False.")
    else:
        print(f"[INFO] forced_disable remains => {forced_disable}")

    save_config(current_config)
    print("[INFO] Settings saved.\n")

# ====================================================
# 7) TRAY ICON & MENU
# ====================================================
def open_logs_folder():
    if platform.system() == 'Windows':
        os.startfile(LOG_DIR)
    elif platform.system() == 'Darwin':
        subprocess.call(["open", LOG_DIR])
    else:
        subprocess.call(["xdg-open", LOG_DIR])

def on_logs_clicked(icon, item):
    log_and_print('info', "User requested 'View Logs'.")
    open_logs_folder()

def on_settings_clicked(icon, item):
    """
    Show the console, run settings prompt, hide console again.
    """
    log_and_print('info', "User clicked 'Settings' in tray menu.")
    show_console()  # re-show console so user can see
    console_settings_prompt()
    # user is done => hide console again
    hide_console()

def on_quit_clicked(icon, item):
    log_and_print('info', "User clicked Quit in tray menu.")
    stop_event.set()
    icon.stop()

def create_sun_icon_transparent():
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((6,6,26,26), fill=(255, 200, 0, 255))  # yellow sun
    return img

def tray_app_run():
    worker = threading.Thread(target=main_solar_loop, daemon=True)
    worker.start()

    tray_icon = pystray.Icon(
        "SolarController",
        create_sun_icon_transparent(),
        "Solar Controller"
    )
    tray_icon.menu = pystray.Menu(
        pystray.MenuItem("Settings", on_settings_clicked),
        pystray.MenuItem("View Logs", on_logs_clicked),
        pystray.MenuItem("Quit", on_quit_clicked)
    )
    tray_icon.run()

    # once user quits
    worker.join()
    log_and_print('info', "Tray app fully exited.")

# ====================================================
# 8) MAIN
# ====================================================
def main():
    global current_config

    # We do want a console, so do NOT compile with --windowed
    # We'll show the console prompts initially, then hide the console.

    # Hard-coded brand-new defaults
    defaults = {
        "ip": "192.168.7.10",
        "port": 80,
        "solar_threshold": 100,
        "battery_threshold": 25.0,
        "re_enable_voltage": 26.9,
        "cycle_interval": 10
    }

    cfg = load_config()
    if not cfg:
        cfg = defaults
        save_config(cfg)
    else:
        # fill missing keys
        for k, v in defaults.items():
            if k not in cfg:
                cfg[k] = v
        save_config(cfg)

    current_config = cfg

    # 1) Show console prompts once at startup
    print("\n=== Welcome to Solar Controller ===")
    print("Press Enter to keep existing defaults.\n")
    console_settings_prompt()

    # 2) After user is done => hide the console
    hide_console()

    # 3) Start tray mode
    tray_app_run()


if __name__ == "__main__":
    main()
