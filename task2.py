from sqlite3 import connect
import requests

DOMAIN = "https://recruitment.developers.emako.pl/products/example?id="

sql = connect(database="database.sqlite")
cursor = sql.cursor()


def fetch_api(path: str):
    endpoint = DOMAIN + path
    return requests.get(endpoint).json()

def update_database(data):
    if data['type'] == 'product':
        insert_product(data) # Wprowadzenie produktu do bazy
    elif data['type'] == 'bundle':
        unpack_bundle(data) # Rozpakowanie pakietu produktów

def insert_product(product):
    for item in product["details"]["supply"]:
        for stock in item["stock_data"]:
            cursor.execute(
                "INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES ('%s','%s','%s','%s','%s')"
                %
                (product['created_at'], product['id'], item["variant_id"], stock['stock_id'], stock['quantity']))
    sql.commit()

def unpack_bundle(bundle):
    for index in range(len(bundle['bundle_items'])):
        product = fetch_api(str(bundle['bundle_items'][index]['id']))
        for _ in range(bundle['bundle_items'][index]['quantity']):
            insert_product(product)

def main():
    path = input('Wpisz id produktu: ') # Pobranie z klawiatury id produktu
    api_response = fetch_api(path) # Pobranie danych z API
    update_database(api_response)

main()

sql.close()