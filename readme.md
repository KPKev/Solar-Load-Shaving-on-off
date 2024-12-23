# Solar Load Shaving & AC Support Mode On/Off

# Schneider Electric
## (Device): SW 4024 3.4 kW Solar Hybrid Inverter 120/240 Vac / 24 Vdc
This repository houses **KPKev's** evolving solution for **automating** and **controlling** solar inverter settings—namely **Load Shaving** and **AC Support** modes—through a **headless** Selenium web interface.

---

# KPKev's Solar Controller (Version 2.4)

**KPKev's Solar Controller** is a Python-based script that automates interactions with a solar inverter web interface. It can:
- Check battery voltage and solar power levels.
- Automatically **Enable** or **Disable** Load Shaving and AC Support modes based on custom thresholds.
- Maintain a "forced disable" state (to protect the battery) until your battery voltage recovers.
- Prompt for user-configurable settings (IP/port, thresholds, cycle interval).
- Provide an ASCII-art banner and a summary after each cycle.

---

## Features

1. **Voltage Safeguard**  
   - If your battery dips below a certain voltage (e.g., 25.1 V), the script forces both Load Shaving and AC Support **off** to protect the battery.

2. **Re-Enable Logic**  
   - Once the voltage rises above your specified threshold (e.g., 26.5 V), the script resumes normal logic.

3. **User-Friendly Prompts**  
   - You can set the IP, port, solar threshold, battery threshold, **re-enable** voltage, and the script's **countdown interval** (in minutes).

4. **Headless Selenium**  
   - The script runs in **headless mode** via ChromeDriver/Selenium, so no browser window is displayed.

5. **ASCII Art Banner**  
   - Displays a cool ASCII-art intro at the start.

6. **Cycle Summaries**  
   - Each cycle ends with a summary of the battery voltage, current solar power, Load Shaving state, AC Support state, and whether you’re in “Charge mode” or “Support mode.”

---

## Requirements

1. **Python 3.7+** (recommended)  
2. **Selenium** library for Python  
3. **ChromeDriver** (must match your installed Chrome version)  
4. **Google Chrome** (or Chromium) installed  
5. A stable network connection to your solar inverter’s IP
Example install:
pip install selenium


---

## Ensure your ChromeDriver binary is in your system PATH or in the same directory as the script.
### Script Overview
solar_controller_2.4.py
Imports & Globals

1. **Manages forced-disable state and the default re-enable threshold.**  
   

2. **ASCII Art Display**  
   - Displays the “KPKev presents: The Solar Controller” banner.

Asks for IP, port, thresholds, cycle interval, reset flag.
Core Logic


## Runtime Prompts

1. Login to the inverter webpage (headless Selenium).
2. Extract battery voltage and solar power.
3. If battery < threshold => forcibly disable modes.
4. If forced_disable is active, do not re-enable until battery ≥ re-enable threshold.
5. Otherwise, toggle modes based on the solar watt threshold.
6. Print a cycle summary (battery voltage, final states, etc.).
7. **Countdown**
   - Wait for the user-defined number of minutes, then start the next cycle.

