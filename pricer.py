import argparse
import psycopg2
from setting import valied_names, user, password, database

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
    parser.add_argument("action", choices=["add", "list", "filter", "sort",
            "report", "price"], help="The opeartion you want to performe")
    parser.add_argument("--date", type=str, help="item date")
    parser.add_argument("--name", type=str, help="item name")
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
    elif args.action == "list":
        if args.name is not None:
            display_items(items)
        else:
            print("please insert name of currency with --name")    
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
