# Solar Load Shaving On/Off

This project aims to implement a solar load shaving system that automatically manages the power consumption of a building based on the available solar energy. The system will turn off non-essential loads when solar energy is insufficient and turn them back on when sufficient solar energy is available.

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

1. Clone the repository: `git clone https://github.com/your-username/solar-load-shaving.git`
2. Install the required dependencies: `npm install`
3. Configure the system (see [Configuration](#configuration) section)
4. Start the system: `npm start`

## Usage

Once the system is up and running, it will continuously monitor the solar energy production and the power consumption of the building. Based on the available solar energy, the system will automatically turn off non-essential loads to reduce the reliance on the grid.

## Configuration

The Solar Load Shaving On/Off system can be configured using the following parameters:

- `solar_threshold`: The minimum solar energy level required to keep the non-essential loads turned on. Default: 50%.
- `grid_threshold`: The maximum grid power consumption allowed before turning off non-essential loads. Default: 80%.
- `load_list`: A list of non-essential loads that can be turned off. Default: [load1, load2, load3].

To configure the system, modify the `config.json` file located in the root directory of the project.

## Contributing

Contributions to the Solar Load Shaving On/Off system are welcome. To contribute, follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit them: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).
