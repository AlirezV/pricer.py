import requests
import json
import time
from datetime import datetime
from pricer import connect, disconnect
import psycopg2

conn = connect()

def list_ids():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",        
        "order": "market_cap_desc",   
        "per_page": 100,              
        "page": 1,                    
        "sparkline": "false"          
    }
    response = requests.get(url, params=params)
    coin_ids = []
    if response.status_code == 200:
        data = response.json()
        for coin in data:
            coin_ids.append(coin["id"])
        print("List of ids added")
    else:
        print("Error in receive data: ", response.status_code)
        print(response.text)
        exit(1)
    time.sleep(10)
    return coin_ids

def request_coins(coins_id):
    params_coin = {
        "vs_currency": "usd",
        "days": "365"  
    }
    url_coin = f"https://api.coingecko.com/api/v3/coins/{coins_id}/market_chart"
    while True:
        response_coin = requests.get(url_coin, params=params_coin)
        if response_coin.status_code == 200:
            data_coin = response_coin.json()
            prices = data_coin.get("prices", [])
            days_price = {}
            for entry in prices:
                timestamp_ms, price = entry
                dt = datetime.fromtimestamp(timestamp_ms/1000)
                day = dt.strftime("20%y/%m/%d")
                days_price[day] = price   
            print(json.dumps(days_price, indent=4))
            break
        elif response_coin.status_code == 429:
            print("Error 429, we should wait for 60s then\
                will request from api again")
            time.sleep(61)
        else:
            print("We couldnt receive data cause: ",response_coin.status_code ,
                    response_coin.text)
            exit(1)
    time.sleep(10)
    return days_price

def create_table(coins_id):
    cursor = conn.cursor()
    try:
        for coin_id in coins_id:
            cursor.execute(f"create table \"{coin_id}\"(date varchar(50), \
                    name varchar(50), price float);")
        conn.commit()
        print("Tables successfully created!")
    except psycopg2.Error as e:
            print(f"Creating tables had a error:{e}")
            pass

def save_to_db(coins_id):
    cursor = conn.cursor()
    try:
        for coin in coins_id:
            days_price = request_coins(coin)
            for date, price in days_price.items():
                cursor.execute(
                    f"insert into \"{coin}\" values('{date}','{coin}',{price});"
                    )
            print(f"{coin} added to database.")
        conn.commit()
        print("Data successfully saved to database... .")
    except psycopg2.Error as e:
        print(f"Sending data to database had problem cause: {e}")
        exit(1)

def main():
    coins_id = list_ids()
    create_table(coins_id)
    save_to_db(coins_id)
    disconnect() #from psql database
    
if __name__ == "__main__":
    main()
    