# Solar Load Shaving & AC Support Mode On/Off

## Schneider Electric - Solar Hybrid Inverter
### (Device): SW 4024 3.4 kW Solar Hybrid Inverter 120/240 Vac / 24 Vdc
This repository houses **KPKev's** evolving solution for **automating** and **controlling** solar inverter settings—namely **Load Shaving** and **AC Support** modes—through a **headless** Selenium web interface.

---

# 🌞 Solar Load Shaving Controller 🚀

### By **KPKev**  
**Efficiently manage your solar inverter’s Load Shaving and AC Support Modes. Protect your battery and optimize energy usage.**

---

## 🌟 Features

### 🔧 **Core Functionality**
- Dynamically enables/disables **Load Shaving** and **AC Support Mode** based on:
  - **Battery Voltage Thresholds**
  - **Solar Input Power**

### 🛡️ **Battery Protection**
- **Force Disable Mode**  
  When battery voltage drops **below** your threshold, both Load Shaving and AC Support are automatically disabled.
  
- **Re-Enable Logic**  
  Normal operation resumes only when the battery voltage rises to a user-configured **Re-enable Voltage Threshold**.  

### 🔄 **Enhanced Voltage Reading**
- **3 Retries** to obtain a valid (>0 V) battery voltage reading.  
- If after 3 attempts the voltage is still **invalid (empty or 0 V)**, the script automatically **disables** both modes to protect the battery, then aborts the cycle.

### ⏱️ **Custom Cycle Timing**
- User-adjustable **countdown interval** between cycles (default: **15 minutes**).

### 🖥️ **Headless Mode**
- Operates without displaying a browser window, saving system resources.

### 📊 **Detailed Cycle Summaries**
- Logs the final status of **Load Shaving** and **AC Support**, along with battery voltage and solar power values, after each cycle.

---

## 📝 What’s New in Version 2.4?

1. **3-Retry Mechanism for Battery Voltage**  
   - Ensures a valid (>0 V) reading is obtained or forces modes **off** if not.  

2. **Editable Settings**  
   - IP/Port, solar threshold, battery thresholds, **re-enable voltage**, and **cycle interval** can all be **set at startup** via prompts.

3. **Force Disable Reset**  
   - Optionally reset the “forced_disable” flag at script launch (default: no).

4. **Cycle Summaries**  
   - Each cycle ends with a summary of battery voltage, solar power, Load Shaving state, AC Support state, and mode (Charge/Support).

---

## 🛠️ Requirements

- **Python 3.8+**
- **Selenium** for Python
- **ChromeDriver** (matching your local Chrome/Chromium version)
- An accessible **solar inverter** on your local network
- (Optional) `pytz` library to handle time zones

**Install dependences**

pip install selenium pytz


# 🚀 Quick Start
**Clone this repo:**


git clone https://github.com/KPKev/Solar-Load-Shaving-on-off.git
cd Solar-Load-Shaving-on-off

**Run the app:**
python solar_controller.py

**Answer the startup prompts:** 
- IP & port of the inverter 
- Solar threshold (watts) 
- Battery thresholds (volts) 
- Re-enable threshold (volts) 
- Cycle interval (minutes, default 15) 
- Whether to reset forced_disable (yes/no) 
- Observe the ASCII-art banner and real-time logs. 

# 🔄 Workflow Overview

**Network Check**
Verifies that the IP/port are reachable.

**Login & Extraction**
Logs into the inverter’s web interface, handles popups, retrieves battery voltage & solar power.

**Voltage Retries**
Tries up to 3 times to obtain a valid (>0 V) battery voltage.
If unsuccessful, Load Shaving and AC Support get disabled for safety, and the cycle aborts.

**Forced Disable**
If battery voltage < threshold, automatically turn both modes off and mark forced_disable = True.

***Re-Enable Logic**
If forced_disable is True but battery voltage ≥ re-enable threshold, reset forced_disable to False and proceed with normal logic.

**Adjust Settings**
Depending on solar power, either enable or disable Load Shaving & AC Support.

**Cycle Summary**
Logs final battery voltage, solar power, mode states, etc.

**Countdown**
Waits user-specified minutes, then repeats.


# 🖼️ Example Output

## 🌞 Solar Load Shaving Controller 🚀

**- [INFO] Current cycle: Support mode**  
- **[INFO] Extracted voltage: 26.2 V**  
- **[INFO] Power Value (W): 300**  
- **[INFO] Adjusting Load Shaving...**  
- **[INFO] (Load Shaving) Verified successfully: 'Enable'**  
- **[INFO] Adjusting AC Support Mode...**  
- **[INFO] (AC Support Mode) Verified successfully: 'Enable'**  
- **[INFO] All changes applied based on current power and voltage thresholds.**  
- **[INFO] Final Status => Power: 300W, Voltage: 26.2V**  

**- [INFO] === Cycle Summary ===**  
  - **Mode: Support mode**  
  - **forced_disable: False**  
  - **Battery Voltage: 26.20 V**  
  - **Solar Power: 300 W**  
  - **Load Shaving: Enable**  
  - **AC Support: Enable**  

**- [INFO] =====================**  

**[INFO] Cycle completed. Starting countdown for the next cycle (15 minutes).**


# 🚧 Troubleshooting

**Selenium/Timeout Errors**
Confirm your inverter’s IP/port are correct and reachable.
Ensure ChromeDriver matches your installed Chrome version.

**No Voltage Reading**
The script will retry 3 times. If still invalid, it forcibly disables modes and exits.

**Permission/Path Issues**
Make sure ChromeDriver is executable and on your system’s PATH, or place it alongside solar_controller.py.

# 🙌 Contributing
Feel free to open issues or pull requests to discuss enhancements or bug fixes. PRs that improve reliability or add new features are welcome.

#📜 License
**Licensed under the MIT License.
MIT License
Copyright (c) 2024 KPKev
Permission is hereby granted, free of charge, to any person obtaining...**

