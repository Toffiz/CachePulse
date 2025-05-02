import os
import gspread
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from prophet import Prophet
import openai
import telepot
from telepot.loop import MessageLoop
import matplotlib.pyplot as plt

# ==== SETTINGS ====
SHEET_ID = "1XUQSxvToZBj-yBfoutKs1vCcvYjXJEalz-nzUXhr0_k"
WORKSHEET_NAME = "\u041f\u0440\u0438\u043c\u0435\u0440 \u0431\u0438\u0437\u043d\u0435\u0441\u0430: \u041c\u0430\u043b\u044b\u0439 \u0431\u0438\u0437\u043d\u0435\u0441"
CREDENTIALS_FILE = "gay.json"
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"


# ============== AUTH ==============
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

bot = telepot.Bot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY


def get_forecast_df():
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet(WORKSHEET_NAME)
    data = ws.get_all_values()

    # Get dates from row 1, starting column D
    dates = data[0][3:]
    cash_gap_row = data[60][3:]  # Row 61 is index 60

    entries = []
    for i in range(len(dates)):
        try:
            date_str = dates[i].strip()
            val_str = cash_gap_row[i].replace("(", "-").replace(")", "").replace(",", "").strip()
            val = float(val_str) if val_str and val_str != '-' else 0.0

            date_obj = datetime.strptime(date_str, "%d %B")
            if date_obj.year == 1900:
                date_obj = date_obj.replace(year=datetime.now().year)

            entries.append({"ds": date_obj, "y": val})
        except Exception as e:
            print(f"Skip invalid at {i + 3}: {e}")
            continue

    df = pd.DataFrame(entries)
    df = df.dropna()
    return df


def generate_forecast(df):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    return forecast


def handle_predictions(chat_id):
    df = get_forecast_df()
    forecast = generate_forecast(df)
    forecast['balance'] = forecast['yhat']

    upcoming = forecast[
        (forecast['ds'] > datetime.now()) &
        (forecast['ds'] <= datetime.now() + pd.Timedelta(days=14)) &
        (forecast['balance'] < 0)
    ]

    if not upcoming.empty:
        date = upcoming.iloc[0]['ds'].strftime('%d.%m.%Y')
        amount = round(upcoming.iloc[0]['balance'], 2)
        message = f"❗ Ожидается кассовый разрыв {date}, остаток ≈ {amount} ₸"
    else:
        message = "✅ Всё хорошо: кассовых разрывов не ожидается"

    bot.sendMessage(chat_id, message)


def handle_graph(chat_id):
    df = get_forecast_df()
    forecast = generate_forecast(df)

    plt.figure(figsize=(10, 5))
    plt.plot(forecast['ds'], forecast['yhat'], label='Прогноз', color='blue')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], alpha=0.3)
    plt.axhline(0, color='red', linestyle='--')
    plt.title("Прогноз кассового баланса")
    plt.xlabel("Дата")
    plt.ylabel("Остаток (₸)")
    plt.legend()

    path = "forecast_plot.png"
    plt.savefig(path)
    bot.sendPhoto(chat_id, photo=open(path, "rb"))
    os.remove(path)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type != 'text':
        bot.sendMessage(chat_id, "Я понимаю только текст.")
        return

    text = msg['text'].strip().lower()

    if text == "/get_predictions":
        handle_predictions(chat_id)
    elif text == "/get_graph":
        handle_graph(chat_id)
    else:
        bot.sendMessage(chat_id, "Напиши /get_predictions или /get_graph")


# 🟢 Start bot loop
MessageLoop(bot, handle).run_as_thread()
print("🤖 Бот запущен...")

# Prevent exit
import time
while True:
    time.sleep(10)
