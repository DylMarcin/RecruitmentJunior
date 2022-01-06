from sqlite3 import connect
import requests
import base64
import json

DOMAIN = "https://recruitment.developers.emako.pl"
HTTP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

sql = connect(database="database.sqlite")

# Insert your code here
def load_from_file(file):
    with open(file) as json_file:
        data = json.load(json_file)
    return f"{data['username']}:{data['password']}"

def str_to_base64(data):
    urlSafeEncodedBytes = base64.urlsafe_b64encode(data.encode("utf-8"))
    return str(urlSafeEncodedBytes, "utf-8")

def get_access_token(credentials):
    token = requests.post('https://recruitment.developers.emako.pl/login/aws?grant_type=bearer', headers = {'Authorization':f'Basic {credentials}'})
    return token.json()['access_token']

def fetch_api(token):
    endpoint = DOMAIN + '/products'
    response_API = requests.get(endpoint, data = '{}', headers = {'Authorization':f'Bearer {token}'})
    return response_API.json()['result']

def slice_json(json):
    data = []
    for product in json:
        for i in range(len(product['details']['supply'])):
            if 'variants' in product and len(product['details']['supply'][i]['stock_data'])>0:
                cache = {
                    'variant_id':product['variants'][i],
                    'stock':product['details']['supply'][i]['stock_data'],
                }
                data.append(cache)
    return [{'variant_id': entry['variant_id'], 'stock_id': stock['stock_id'], 'quantity': stock['quantity']} for entry in data for stock in entry['stock']]

def update_database(data):
    cursor = sql.cursor()

    for element in data:
        cursor.execute("UPDATE product_stocks SET supply = '%s' WHERE variant_id = '%s' AND stock_id = '%s'" % (element['quantity'], element['variant_id'], element['stock_id']))
    
    sql.commit()


def main():
    credentials = load_from_file('credentials.json') # Wczytanie z pliku .json danych logowania
    base64str = str_to_base64(credentials) # Konwersja stringa danych logowania na format Base64
    access_token = get_access_token(base64str) # Wysłanie requesta do API w celu otrzymania tokenu dostępu
    data = fetch_api(access_token) # Pobranie danych z API
    sliced_json = slice_json(data) # Wyciągnięcie tylko potrzebnych elementów z jsona
    update_database(sliced_json) # Zaktualizowanie bazy danych na dysku do aktualnych stanów API

main()

sql.close()