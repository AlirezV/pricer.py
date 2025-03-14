import csv
import re
import psycopg2

def read(file):    
    items = {}
    with open(file, mode="r") as fil:
        reader = fil.read()
        pattern = r'"(\d{4}\/\d{2}\/\d{2})":.*?"azadi",\s"sell":\s(\d{7}),'
        price_list = re.findall(pattern, reader)
        for item in price_list:
            time, price = item
            items[time] = price
        conn = psycopg2.connect(
            user="postgres", password="1234", database="postgres"
            )
        cursor = conn.cursor()
        for time, price in items.items():
            cursor.execute(
                "insert into seke_toman values('%s', '%s' ,%s );" %(time, 'seke_toman', price)
                )
        conn.commit()
        cursor.close()
        conn.close()

def read_csv(file):    
    items = {}
    with open(file, mode="r") as fil:
        reader = csv.reader(fil)
        #pattern = r'"(\d{4}\/\d{2}\/\d{2})":.*?"azadi",\s"sell":\s(\d{7}),'
        next(reader)
        for row in reader:
            
            pattern = r'(\d*)\/(\d*)\/(\d{4})'
            repl = r'\3/\1/\2'
            time = re.sub(pattern, repl, row[1])
            pattern2 = r'[",]'
            repl2 = ''
            price = re.sub(pattern2, repl2, row[3])
            #price = round(float(row[3]), 4)
            items[time] = price
        conn = psycopg2.connect(
            user="postgres", password="1234", database="postgres"
            )
        cursor = conn.cursor()
        for time, price in items.items():
            #print(time,'bitcoin_dollar', price)
            cursor.execute(
                "insert into dollar_toman values('%s', '%s' ,%s );" %(time, 'dollar_toman', price)
                )
        conn.commit()
        cursor.close()
        conn.close()

files = ["usd.csv"]
#files = ["2020.txt", "2021.txt", "2022.txt", "2023.txt", "2024.txt"]
for file in files:
    #read(file)
    read_csv(file)
        
                
        