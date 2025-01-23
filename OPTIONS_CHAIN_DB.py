import pandas as pd
from pandas import Timedelta

from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime, timedelta
from io import StringIO 

import math
from scipy.stats import norm

def delta(S, K, T, r, sigma, type):
    if type == 'C':
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        delta_call = norm.cdf(d1)
        return delta_call
    else:
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        delta_put = norm.cdf(d1) - 1
        return delta_put
    

def spot(ticker):
    url = f'https://ca.finance.yahoo.com/quote/{ticker}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')

    prices = soup.find_all(class_='livePrice yf-1tejb6')
    price_values = [price['data-value'] for price in prices]
    price = price_values[0] if price_values else None

    return float(price) if price else 0.0

def sofr():
    url = 'https://fred.stlouisfed.org/series/SOFR30DAYAVG'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')

    rates = soup.find_all(class_='series-meta-observation-value')

    if rates:
        rate_value = float(rates[0].text.strip()) / 100
        return rate_value
    else:
        return 0.05


def date_code(ticker):

    url = f'https://ca.finance.yahoo.com/quote/{ticker}/options'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')

    listbox = soup.find_all('div', class_='itm yf-1hdw734')
    values = [item['data-value'] for item in listbox if 'data-value' in item.attrs]
    if 'ALL_STRIKE_PRICES' in values: 
        index = values.index('ALL_STRIKE_PRICES') 
        values = values[:index]

    return values

def options(ticker, date, spot, sofr):
    url = f'https://ca.finance.yahoo.com/quote/{ticker}/options/?date={date}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')
    
    tables = soup.find_all('table', class_='yf-wurt5d')
    data = []

    
    for table in tables:
        df = pd.read_html(StringIO(str(table)))[0]
        data.append(df)
    
    result = pd.concat(data, ignore_index=True)
    
    result['Contract Name'] = result['Contract Name'].apply(lambda x: x.strip())
    result['Ticker'] = result['Contract Name'].apply(lambda x: x[:x.find('2')])
    
    date_value = result['Contract Name'].iloc[0][len(result['Contract Name'].iloc[0][:result['Contract Name'].iloc[0].find('2')]):result['Contract Name'].iloc[0].find('C') if 'C' in result['Contract Name'].iloc[0] else result['Contract Name'].iloc[0].find('P')]
    
    result['Date'] = date_value
    result['Type'] = result['Contract Name'].apply(lambda x: 'C' if 'C' in x else 'P')
    result['Date'] = pd.to_datetime(result['Date'], format='%y%m%d')

    result['Strike'] = pd.to_numeric(result['Strike'], errors='coerce')
    result['Bid'] = pd.to_numeric(result['Bid'], errors='coerce')
    result['Ask'] = pd.to_numeric(result['Ask'], errors='coerce')
    result['Volume'] = pd.to_numeric(result['Volume'], errors='coerce').fillna(0)
    result['Open Interest'] = pd.to_numeric(result['Open Interest'], errors='coerce').fillna(0)
    result['Implied Volatility'] = pd.to_numeric(
        result['Implied Volatility'].str.replace('%', '', regex=False), errors='coerce') / 100
    result['Implied Volatility'] = result['Implied Volatility'].clip(lower=0.0000001)

    day = datetime.today()

    result['DTE'] = result['Date'] - day
    result['DTE'] = (result['Date'] - day).dt.days.clip(lower=1e-7)
    result['DTE'] = result['DTE'] / 365

    print(result)

    result['Delta'] = result.apply(lambda row: delta(S=spot, K=row['Strike'], T=row['DTE'], r=sofr, sigma=row['Implied Volatility'], type=row['Type']), axis=1)

    result = result[['Contract Name', 'Ticker', 'Date', 'Type', 'Strike', 'Bid', 'Ask','Volume', 'Open Interest', 'Implied Volatility', 'Delta']]

    return result

def database(ticker):
    spot_price = spot(ticker=ticker)
    dates = date_code(ticker=ticker)
    sofr_rate = sofr()

    df = pd.DataFrame()
    for date in dates:
        data = options(ticker=ticker, date=date, spot=spot_price, sofr=sofr_rate)
        df = pd.concat([df, data], ignore_index=True)
        print(f'Date Completed: {date}', end='\r')

    return df

##------------------------------------------EXAMPLES------------------------------------------##

#print(date_code('AAPL')) ## Pulls Date Codes For All Available Options Chains Given A Ticker
#print(options('AAPL', '1737676800', 200, 0.05)) ## Pulls Option Chain For Specific Date and Ticker
#print(database('AAPL'))
