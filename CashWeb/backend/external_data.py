import requests

EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
INFLATION_API_URL = "https://api.api-ninjas.com/v1/inflation"
TRENDS_FAKE_SAMPLE = ["cash flow management", "small business finance", "budget planning"]

# Your API key for Inflation API (you can get it free from api-ninjas.com)
NINJAS_API_KEY = "TEvoBMYIg1zg+z2KGp8NpQ==x9e61ksr0QIv1XJM"


def fetch_exchange_rates():
    try:
        response = requests.get(EXCHANGE_API_URL)
        data = response.json()
        return data.get("rates", {})
    except Exception as e:
        print("Error fetching exchange rates:", e)
        return {}


def fetch_inflation_data():
    try:
        headers = {"X-Api-Key": NINJAS_API_KEY}
        response = requests.get(INFLATION_API_URL, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        print("Error fetching inflation data:", e)
        return {}


def fetch_google_trends():
    # For simplicity, return static keywords (later real Google Trends API can be integrated)
    return TRENDS_FAKE_SAMPLE
