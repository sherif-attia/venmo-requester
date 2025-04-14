<div align="center">

# venmo-auto-requester <br> 🤖🗓️💰

> Auto-request money from friends based on a Google Sheet.

[![ci](https://github.com/sherifattia/venmo-auto-requester/actions/workflows/ci.yml/badge.svg)](https://github.com/sherifattia/venmo-auto-requester/actions/workflows/ci.yml)
![version](https://img.shields.io/badge/continuous_delivery-v0.1.0-blue)
[![coverage](https://codecov.io/gh/sherifattia/venmo-auto-requester/graph/badge.svg?token=4G33EVU2LH)](https://codecov.io/gh/sherifattia/venmo-auto-requester)
![python](https://img.shields.io/badge/python-3.13-blue?logo=python&logoColor=ffdd54)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)


</div>

## 📊 Google Sheet Format

| Username            | Note                   | Amount | Frequency | Payment Date |
|---------------------|------------------------|--------|-----------|---------------|
| george-bush-2       | 🏠 Rent                | $3,000 | Monthly   | 1             |
| george-bush-2       | 🔌 Utilities           | $500   | Monthly   | 5             |
| donald-trump-$$$    | 📺 YouTube Premium     | $125   | Monthly   | 10            |
| barack-obama        | 💳 Costco Membership   | $100   | Yearly    | 04-20         |
| bill-clinton-69     | 🍿 Netflix Family Plan | $75    | Yearly    | 09-12         |


## ⏰ Schedule

- Runs daily at **10 AM**
- Sends Venmo requests for rows matching today's date
