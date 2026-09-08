# Automated Damper Demand Index (IKP) with Telegram Bot

## Overview
This project automates the extraction of non-linear drift data from ETABS to evaluate structural eccentricity and calculate the Damper Demand Index (IKP) for Nitinol SMA damper placement.

## Key Features
- Parse `.csv` / matrix output directly from ETABS.
- Calculate spatial IKP based on structural drift and eccentricity.
- Automated real-time notifications via Telegram API.

## Tech Stack
- Python (Pandas, NumPy)
- ETABS API / CSV Parser
- Telegram Bot API
