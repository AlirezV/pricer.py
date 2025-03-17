import argparse
import re
import psycopg2
from setting import valied_names

def connect():
    conn = psycopg2.connect( user="postgres", password="1234", database="postgres")
    return conn

def add_item(items, date, name, price):
    items[date] = (name, price)
    return items

def save(items, conn):
    if items[date][0] not in valied_names:
        print("Name is not correct!")        
    else:
        try:
            cursor = conn.cursor() 
            for date, (name, price) in items.items():
                cursor.execute("insert into %s values ('%s', '%s', %s );" %(name, date, name, price ))
            conn.commit() 
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print("database error: %s" % e)
    
def load(table_name, conn):
    items = {}
    if table_name not in valied_names:
        print("Table name is not correct!")        
    try:
        cursor = conn.cursor()
        cursor.execute("select * from %s;" % table_name)
        item = cursor.fetchall()
        for row in item:
            date, name, price = row
            items[date] = (name , price)
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print("database error: %s" % e)
    return items

def display_items(items):
    for date, (name, price) in items.items():
        print(f"{date} - {name}: {price}")

def filter_item(items, name):
    found = False
    for date, (item_name, price) in items.items():
        if item_name == name:
            print(f"{date} - {name}: {price}")
            found = True
    if not found:
        print(f"'{name}' was not found.")

def sort_items(items, reverse=False):
    sorted_items = dict(sorted(items.items(), key=lambda item: item[1], reverse=reverse))
    display_items(sorted_items)

def report(items):
    if items:
        max_price_item = max(items.items(), key=lambda x: x[1][1])
        min_price_item = min(items.items(), key=lambda x: x[1][1])
        print(f"Highest price: {max_price_item[1][0]} at the price {max_price_item[1][1]} (Date: {max_price_item[0]})")
        print(f"Lowest price: {min_price_item[1][0]} at the price {min_price_item[1][1]} (Date: {min_price_item[0]})")
    else:
        print("There are no items.")

def price_item(items, date, name):
        
        if date in items:
            print(name, " in ", date, ": ", items[date][1])
        else:
            print("%s on %s not found." %(name,date))
         
def main():
    parser = argparse.ArgumentParser(description="pricing plan")
    parser.add_argument("action", choices=["add", "list", "filter", "sort", "report", "price"], help="The opeartion you want to performe")
    parser.add_argument("--date", type=str, help="item date")
    parser.add_argument("--name", type=str, help="item name")
    parser.add_argument("--price", type=float, help="item price")
    parser.add_argument("--reverse", action="store_true", help="sort in descending order")

    args = parser.parse_args()
    conn = connect()
    items = load(args.name, conn) if args.name else {}

    if args.action == "add":
        if args.date and args.name and args.price is not None:
            items = add_item(items, args.date, args.name, args.price)
            save(items, conn)
            print(f"item: '{args.name}' at the price {args.price} on date of {args.date} added.")
        else:
            print("please insert name, price and date of currency.")
    elif args.action == "list":
        display_items(items)
    elif args.action == "filter":
        if args.name:
            filter_item(items, args.name)
        else:
            print("please insert name of item.")
    elif args.action == "sort":
        sort_items(items, args.reverse)
    elif args.action == "report":
        report(items)
    elif args.action == "price":
        if args.name and args.date:
            price_item(items, args.date, args.name)
        else:
            print("please provide both --name and --date!")
    

if __name__ == "__main__":
    main()
