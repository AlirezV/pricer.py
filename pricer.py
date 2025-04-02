import argparse
import psycopg2
import json
import time
from setting import valied_names, user, password, database

def import_today_price():
    from api_to_db import today_price
    return today_price

def import_list_ids():
    from api_to_db import list_ids
    return list_ids

def connect():
    conn = psycopg2.connect( user=user, password=password,
                            database=database)
    return conn

def disconnect():
    conn = connect()
    cursor = conn.cursor()
    cursor.close()
    conn.close()

def save(date, name, price):
    conn = connect()
    if name not in valied_names:
        print("Name is not correct!")        
    else:
        try:
            cursor = conn.cursor() 
            cursor.execute("insert into %s values ('%s', '%s', %s );"
                           %(name, date, name, price ))
            conn.commit() 
        except psycopg2.Error as e:
            print("database error: %s" % e)
    
def db_select_all(name):
    items = {}
    conn = connect()
    if name not in valied_names:
        print("Table name is not correct!")        
    else:
        try:
            cursor = conn.cursor()
            cursor.execute("select * from %s;" % name)
            item = cursor.fetchall()
            for row in item:
                date, name, price = row
                items[date] = (name , price)
        except psycopg2.Error as e:
            print("database error: %s" % e)
    return items

def db_select_one(name, type, column):
    item = {}
    conn = connect()
    if name not in valied_names:
        print("table_name is not correct!")
    else:
        try:
            cursor = conn.cursor()
            cursor.execute("select * from %s where %s='%s';"
                           %(name, type, column))
            one = cursor.fetchall()
            date, name, price = one
            item[date] = (name, price)
        except psycopg2.Error as e:
            print("database error: %s" % e)
    return item

def list_coins():
    list_ids = import_list_ids()
    coins_ids = list_ids()
    print(json.dumps(coins_ids, indent=4))
    print("Choose from this coins to search in our database")
    
def display_items(items):
    for date, (name, price) in items.items():
        print(f"{date} - {name}: {price}")

def filter_item(items):
        for date, (name, price) in items.items():
            print(f"{date}-{name}: {price}")

def sort_items(items, reverse=False):
    sorted_items = dict(sorted(items.items(), key=lambda item: item[1],
                               reverse=reverse))
    display_items(sorted_items)

def report(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("select max(price) as maxvalue, min(price) as minvalue from %s;" % name)
    max_min = cursor.fetchone()
    max_price, min_price = max_min
    cursor.execute(f"select * from {name} where price='{max_price}';")
    max_rec = cursor.fetchone()
    cursor.execute(f"select * from {name} where price='{min_price}';")
    min_rec = cursor.fetchone()
    date0, name0, price0 = max_rec
    date1, name1, price1 = min_rec
    print(f"highest price: {name0} at the price {price0} (Date: {date0})")
    print(f"lowest price: {name1} at the price {price1} (Date: {date1})")

def profit_price(name, date, price):
    today_price = import_today_price()
    if name not in valied_names:
        print("coin name is not correct")
    else:
        day_price = today_price(name) #a function from api_to_db.py
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"select * from {name} where date='{date}';")
        old_price = cursor.fetchone()[2]
        profit = (price/old_price)*day_price
        benefit = round(profit, 4)
        print(f"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$>>{name}<<$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(f"$ You could have {benefit}$ now, if you were investing in {date}  $")  
        print(f"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$>>{name}<<$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        
def profit_number(date, name, number):
    today_price = import_today_price()
    if name not in valied_names:
        print("coin name is not correct")
    else:
        day_price = today_price(name) #a function from api_to_db.py
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"select * from {name} where date='{date}'")
        old_price = cursor.fetchone()[2]
        profit = (day_price*number)-(old_price*number)
        if profit > 0:
            print(f"if you had bought {number} of {name} in {date}, you whould have made {profit}$ today. $_$")
        elif profit <= 0:
            print(f"if you had bought {number} of {name} in {date}, you would have lost {profit}$ today. ~_~")
            
def price_item(date, name):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"select * from {name} where date='{date}';")
        price = cursor.fetchone()
        date0, name0, price0 = price  
        print(f"{name0} on {date0}: {price0}.") 
        if price is None:
            print(f"{name} on {date} not found!") 
         
def main():
    parser = argparse.ArgumentParser(description="pricing plan")
    parser.add_argument("action", choices=["add", "list", "prices", "filter", "sort",
            "report", "profit", "profit_number", "price"], help="The opeartion you want to performe")
    parser.add_argument("--date", type=str, help="item date")
    parser.add_argument("--name", type=str, help="item name")
    parser.add_argument("--number", type=int, help="item number")
    parser.add_argument("--price", type=float, help="item price")
    parser.add_argument("--reverse", action="store_true",
                        help="sort in descending order")

    args = parser.parse_args()
    items = db_select_all(args.name) if args.name else {}

    if args.action == "add":
        if args.date and args.name and args.price is not None:
            save(args.date, args.name, args.price)
            print(f"item: '{args.name}' at the price {args.price} on date of {args.date} added.")
        else:
            print("please insert name, price and date of currency.")
    elif args.action == "prices":
        print("all prices of this coin that is on our database")
        if args.name is not None:
            display_items(items)
        else:
            print("please insert name of currency with --name")
    elif args.action == "list":
        print("List of our database coins")
        time.sleep(1)
        list_coins()
    elif args.action == "filter":
        if args.name:
            filter_item(items)
        else:
            print("please insert name of item.")
    elif args.action == "sort":
        if args.name and args.reverse is not None:
            sort_items(items, args.reverse)
        else:
            print("please use --name and --reverse")
    elif args.action == "profit":
        if args.date and args.name and args.price is not None:
            profit_price(args.name, args.date, args.price)
        else:
            print("Please insert --name , --date and --price for this request.")
    elif args.action == "profit_number":
        if args.date and args.name and args.number is not None:
            profit_number(args.date, args.name, args.number)
        else:
            print("Please insert --name , --date and --number for this request.")
    elif args.action == "report":
        if args.name is not None:
            report(args.name)
        else:
            print("please insert name of currency with --name")
    elif args.action == "price":
        if args.name and args.date:
            price_item(args.date, args.name)
        else:
            print("please provide both --name and --date!")
            
    disconnect() #from psql database
    
if __name__ == "__main__":
    main()
