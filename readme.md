# Solar Load Shaving & AC Support Mode On/Off

This repository houses **KPKev's** evolving solution for **automating** and **controlling** solar inverter settings—namely **Load Shaving** and **AC Support** modes—through a **headless** Selenium web interface.

---

## Key Features

1. **Battery Voltage Safeguard**  
   - If the battery drops below a specified threshold, the script **forces both Load Shaving and AC Support to “Disable.”**

2. **Re-Enable Logic**  
   - The script won’t re-enable these modes until battery voltage reaches a higher “re-enable” threshold, preventing premature load usage that could damage the battery.

3. **User-Friendly Runtime Prompts**  
   - Configure IP/Port, solar watt threshold, battery thresholds, re-enable voltage, and the countdown interval directly from the terminal when you run the script.

4. **Headless Automation**  
   - Uses **Selenium** in **headless** mode, so it runs quietly in the background without popping up a Chrome window.

5. **Cycle Summaries**  
   - Every “cycle” (interval of time you set), it logs final states, including battery voltage, solar power, Load Shaving setting, AC Support setting, and whether we’re in **“Charge mode”** (forced disabled) or **“Support mode”** (normal logic).

---

## Version 2.4

**v2.4** is the latest major iteration of this script. Key changes include:

- **Editable Countdown** between cycles (default 15 minutes).  
- All existing logic from prior versions:
  - Forced disable below `battery_voltage_threshold`.
  - Normal logic only resumes above `re_enable_threshold`.
  - Option to **reset** the “forced_disable” flag at script start.  
  - Full **ASCII art** banner and **detailed logging**.

If you’d like to reference older versions (e.g., v2.0, v2.1, etc.), check out the repository’s commit history or branches.

---

## Requirements

- **Python 3.7+** (recommended)  
- **Selenium** library  
- **ChromeDriver** installed (matching your Chrome/Chromium version)  
- **Google Chrome** (or Chromium) installed  
- Reliable network connection to the solar inverter

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

