import argparse
import csv

def add_item(items, name, price):
    items[name] = price
    return items

def save_to_csv(items, filename="prices.csv"):
    with open(filename, mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Price"])
        for name, price in items.items():
            writer.writerow([name, price])

def load_from_csv(filename="items.csv"):
    items = {}
    try:
        with open(filename, mode="r") as file:
            reader = csv.reader(file)
            next(reader)  
            for row in reader:
                name, price = row
                items[name] = float(price)
    except FileNotFoundError:
        pass
    return items

def display_items(items):
    for name, price in items.items():
        print(f"{name}: {price}")

def filter_item(items, name):
    if name in items:
        print(f"{name}: {items[name]}")
    else:
        print(f"'{name}' was not found.")

def sort_items(items, reverse=False):
    sorted_items = dict(sorted(items.items(), key=lambda item: item[1], reverse=reverse))
    display_items(sorted_items)

def report(items):
    if items:
        max_price_item = max(items, key=items.get)
        min_price_item = min(items, key=items.get)
        print(f"highest price: {max_price_item} at the price {items[max_price_item]}")
        print(f"lowest price: {min_price_item} at the price {items[min_price_item]}")
    else:
        print("there is no item.")

def main():
    parser = argparse.ArgumentParser(description="pricing plan")
    parser.add_argument("action", choices=["add", "list", "filter", "sort", "report"], help="The opeartion you want to performe")
    parser.add_argument("--name", type=str, help="item name")
    parser.add_argument("--price", type=float, help="item price")
    parser.add_argument("--reverse", action="store_true", help="sort in descending order")

    args = parser.parse_args()
    items = load_from_csv()

    if args.action == "add":
        if args.name and args.price:
            items = add_item(items, args.name, args.price)
            save_to_csv(items)
            print(f"item: '{args.name}' at the price {args.price} added.")
        else:
            print("please insert name and price of item.")
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
