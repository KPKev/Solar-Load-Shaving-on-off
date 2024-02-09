# Solar Load Shaving On/Off 


This project aims to implement a solar load shaving system that automatically manages the power consumption of a home based on the available solar energy. The system will turn off load shaving when solar energy is insufficient and turn it back on when sufficient solar energy is available again.


Default: power_value > 200 W  #enables load shaving
power_value < 199 W  #disables load shaving
Checks ewvery 15 minutes/900 seconds


## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Solar Load Shaving On/Off system is designed to optimize the use of solar energy in a building. By intelligently managing the power consumption, the system aims to reduce reliance on the grid and maximize the utilization of solar energy.

## Installation

To install and run the Solar Load Shaving On/Off system, follow these steps:

1. Clone the repository: `https://github.com/KPKev/Solar-Load-Shaving-on-off`
2. Install the required dependencies: `npm install`
3. `pip install selenium`
This command ensures that the selenium package is installed in the user's Python environment, allowing them to use webdriver, By, WebDriverWait, expected_conditions, Select, Options, TimeoutException, NoSuchElementException, Keys, and ActionChains in their scripts.

`from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains`
For this Python project that uses Selenium and the components listed, all the dependencies related to Selenium can be installed with a single pip command because they are all part of the Selenium package. There's no need to install separate packages for each import statement you've provided, as they all come with the Selenium package once it's installed.
4. `import time` do not forget to import this at the begining of the script or anything based off of time will not work and/or the app wont start.

Note on WebDrivers
Remember, while the Selenium package provides the API for interacting with web browsers, it does not include the WebDrivers (like ChromeDriver for Google Chrome or GeckoDriver for Mozilla Firefox) needed to interface with the actual browser. You will need to download and set up the appropriate WebDriver separately.

### Setting up WebDrivers

To run Selenium scripts, you must download and set up the appropriate WebDriver for the browser you intend to automate:

- **Chrome**: Download [ChromeDriver](https://sites.google.com/chromium.org/driver/) and ensure it's in your PATH or specified in your script.
- **Firefox**: Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases) and ensure it's in your PATH or specified in your script.

For other browsers, please refer to the Selenium documentation for the respective WebDriver download instructions
5. Configure the system (see [Configuration](#configuration) section)
6. Start the system: `pip .\Load_Shaving_Controller.py`

## Usage

Once the system is up and running, it will continuously monitor the solar energy production. Based on the available solar energy, the system will automatically turn on/off load shaving to save money.

## Configuration

The Solar Load Shaving On/Off system can be configured using the following parameters:

- `power_vaule`: The minimum solar energy level required load shaving to be turned on. Default: 200 W
-`time.sleep(900)`  # 15 minutes app refreshes


To configure the system, modify the `Load_Shaving_Controller.py` file located in the root directory of the project.

## Contributing

Contributions to the Solar Load Shaving On/Off system are welcome. To contribute, follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit them: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).