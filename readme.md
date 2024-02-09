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
3. Configure the system (see [Configuration](#configuration) section)
4. Start the system: `pip .\Load_Shaving_Controller.py`

## Usage

Once the system is up and running, it will continuously monitor the solar energy production. Based on the available solar energy, the system will automatically turn off load shaving to reduce the reliance on the grid and save money.

## Configuration

The Solar Load Shaving On/Off system can be configured using the following parameters:

- `power_vaule`: The minimum solar energy level required load shaving to be turned on. Default: 200 W



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
