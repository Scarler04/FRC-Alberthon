import requests
import json

"""
ERATUM : This code is made to scrape de data of the soliguide api :)
"""

url = 'https://api.soliguide.fr/new-search/fr'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://soliguide.fr',
    'Referer': 'https://soliguide.fr/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'X-Ph-User-Distinct-Id': '0196e94e-194a-7074-a23b-02b40c1144cd',
    'X-Ph-User-Session-Id': '0196e94e-196a-71e5-badd-ccc805b5c9a1',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

data = {
    "category": "accomodation_and_housing",
    "label": "Hébergement et logement",
    "word": None,
    "location": {
        "label": "Paris",
        "coordinates": [2.362203, 48.846223],
        "name": "Paris",
        "geoType": "departement",
        "geoValue": "departement-paris",
        "department": "Paris",
        "departmentCode": "75",
        "country": "fr",
        "region": "Île-de-France",
        "regionCode": "11",
        "timeZone": "Europe/Paris",
        "slugs": {
            "departement": "paris",
            "pays": "fr",
            "department": "paris",
            "country": "fr",
            "region": "ile-de-france"
        },
        "areas": {
            "departement": "Paris",
            "departementCode": "75",
            "pays": "fr",
            "country": "fr"
        },
        "distance": 5000
    },
    "country": "fr",
    "publics": {},
    "modalities": {},
    "languages": None,
    "placeType": "LIEU",
    "close": None,
    "options": {
        "limit": 1000,
        "page": 1
    }
}

response = requests.post(url, headers=headers, json=data)

doc = response.json()

with open('soliguide_response.json', 'w') as f:
    json.dump(doc, f)