import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import datetime
from io import StringIO 


def date_code(ticker):

    url = f'https://ca.finance.yahoo.com/quote/{ticker}/options/'

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

def options(ticker, date):
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

    result = result[['Contract Name', 'Ticker', 'Date', 'Type', 'Strike', 'Bid', 'Ask', '% Change','Volume', 'Open Interest', 'Implied Volatility']]

    return result

def database(ticker):
    dates = date_code(ticker=ticker)

    df = pd.DataFrame()
    for date in dates:
        data = options(ticker=ticker, date=date)
        df = pd.concat([df, data], ignore_index=True)
        print(f'Date Completed: {date}', end='\r')

    return df




##------------------------------------------EXAMPLES------------------------------------------##

#print(date_code('AAPL')) ## Pulls Date Codes For All Available Options Chains Given A Ticker
#print(options('AAPL', '1737072000')) ## Pulls Option Chain For Specific Date and Ticker
#print(database('AAPL')) ## Outputs The Complete Options Chain For All Expiries
