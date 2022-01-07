from sqlite3 import connect
import requests

PATH = "https://recruitment.developers.emako.pl/products/example?id="

sql = connect(database="database.sqlite")
cursor = sql.cursor()

def fetch_api(index):
    endpoint = PATH + index
    return requests.get(endpoint).json()

def type_check(data):
    if data['type'] == 'product':
        insert_product(data)
    elif data['type'] == 'bundle':
        insert_bundle(data)

def insert_product(product):
    for item in product["details"]["supply"]:
        for stock in item["stock_data"]:
            cursor.execute(
                "INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES ('%s','%s','%s','%s','%s')"
                %
                (product['created_at'], product['id'], item["variant_id"], stock['stock_id'], stock['quantity']))
    sql.commit()

def insert_bundle(bundle):
    for index in range(len(bundle['bundle_items'])):
        product = fetch_api(str(bundle['bundle_items'][index]['id']))
        for _ in range(bundle['bundle_items'][index]['quantity']):
            insert_product(product)

def main():
    index = input('Wpisz id produktu: ')
    response_api = fetch_api(str(index))
    type_check(response_api)
    
main()

sql.close()