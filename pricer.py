import argparse
import re
import psycopg2

def add_item(items, date, name, price):
    items[date] = (name, price)
    return items

def save_to_psql(items):
    
    valied_names = ["bitcoin", "dogecoin", "dollar_toman", "ethereum", "seke_toman"]
    if items[date][0] not in valied_names:
        print("Name is not correct!")        
    else:
        try:
            conn = psycopg2.connect( user="postgres", password="1234", database="postgres")
            cursor = conn.cursor()
            for date, (name, price) in items.items():
                cursor.execute("insert into %s values ('%s', '%s', %s );" %(name, date, name, price ))
            conn.commit()
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print("database error: %s" % e)
    
def load_from_psql(table_name):
    items = {}
    valied_tables = ["bitcoin", "dogecoin", "dollar_toman", "ethereum", "seke_toman"]
    if table_name not in valied_tables:
        print("Table name is not correct!")        
    try:
        conn = psycopg2.connect( user="postgres", password="1234", database="postgres")
        cursor = conn.cursor()
        cursor.execute("select * from %s;" % table_name)
        iitems = cursor.fetchall()
        for row in iitems:
            time, name, price = row
            date = re.sub(r'(.*)-(.*)-(.*)',r'\1/\2/\3',time)
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
    items = load_from_psql(args.name) if args.name else {}

    if args.action == "price":
        if args.name and args.date:
            price_item(items, args.date, args.name)
        else:
            print("please provide both --name and --date!")
    
    if args.action == "add":
        if args.date and args.name and args.price is not None:
            items = add_item(items, args.date, args.name, args.price)
            save_to_psql(items)
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

if __name__ == "__main__":
    main()






#def save_to_csv(items, filename="prices.csv"):
#    with open(filename, mode="w", newline='') as file:
 #       writer = csv.writer(file)
  #      writer.writerow(["Name", "Price"])
   #     for name, price in items.items():
    #        writer.writerow([name, price])


#def load_from_csv(filename="items.csv"):
 #   items = {}
  #  try:
   #     with open(filename, mode="r") as file:
    #        reader = csv.reader(file)
     #       next(reader)  
      #      for row in reader:
       #         name, price = row
        #        items[name] = float(price)
#    except FileNotFoundError:
 #       pass
  #  return items
