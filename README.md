# Equity Financial Options-Chain Database 
Complete Equity Options Chain For All Available Dates To Expiry.

This Python script scrapes options data from Yahoo Finance for a given ticker symbol using the `requests` library and BeautifulSoup for web scraping, and `pandas` for data manipulation.

## Features
- **Fetch Expiry Dates:** Retrieve all available expiration dates for a given ticker symbol.
- **Scrape Options Data:** Scrape option chain data for a specific expiration date.
- **Complete Options Database:** Build a complete options database for a ticker, combining data across all expiration dates.

## Requirements

Ensure you have Python installed along with the following packages:

```bash
pip install pandas beautifulsoup4 requests
```

## Usage

### Import the script
```python
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import datetime
from io import StringIO
```

### Example Usage

#### Fetch Expiration Dates
```python
from script import date_code

# Fetch available expiration dates for AAPL
dates = date_code('AAPL')
print(dates)
```

#### Fetch Options Data for a Specific Date
```python
from script import options

# Fetch options data for AAPL for a specific expiration date
data = options('AAPL', '1737072000')
print(data)
```

#### Build Complete Options Database
```python
from script import database

# Fetch the entire options database for AAPL
data = database('AAPL')
print(data)
```

## How It Works
### `date_code(ticker)`
- Scrapes available option expiration dates from Yahoo Finance for the given ticker.

### `options(ticker, date)`
- Scrapes the option chain for a given ticker and expiration date.
- Parses the option data and returns a cleaned DataFrame.

### `database(ticker)`
- Iterates through all available expiration dates for a given ticker.
- Combines all the option chains into a single Pandas DataFrame.

## Output
The output DataFrame contains the following columns:
- **Contract Name**
- **Ticker**
- **Date**
- **Type** (Call/Put)
- **Strike**
- **Bid**
- **Ask**
- **% Change**
- **Volume**
- **Open Interest**
- **Implied Volatility**
- **Delta**

## Disclaimer
- This script relies on web scraping and may break if Yahoo Finance changes its website structure.
- Use this script responsibly and comply with Yahoo Finance's terms of service.

