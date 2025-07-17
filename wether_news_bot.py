import os

import requests
import telebot
from dotenv import load_dotenv
from datetime import datetime
import locale

# Загрузка токена из файла .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EVENTS_API_KEY=os.getenv("EVENTS_API_KEY")

bot = telebot.TeleBot(TOKEN)


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    return response.json()


def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    return response.json().get('articles', [])

def get_events(city=None):
    url = "https://api.timepad.ru/v1/events/"
    headers = {
        "Authorization": f"Bearer {EVENTS_API_KEY}"
    }
    params = {
        "sort": "date",  # сортировка по дате
        "limit": 5,  # сколько событий возвращать
        "fields": "name,starts_at,description,url,location",  # необходимые поля
        "is_deleted": False,
        "is_confirmed": True
    }
    if city:
        params["cities"] = city

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('values', [])
    else:
        print(f"TimePad API error: {response.status_code} {response.text}")
        return []

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    pass

def format_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%d %B %Y, %H:%M')
    except Exception:
        return dt_str


# /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id,
                     "Привет! Я твой информационный помощник. \n\n"
                     "Набери /help, чтобы узнать, что я умею.")


# /help
@bot.message_handler(commands=["help"])
def help_handler(message):
    bot.send_message(message.chat.id,
                     "Доступные команды:\n"
                     "/start - запустить бота\n"
                     "/help - показать это меню\n"
                     "/weather - узнать погоду (в разработке)\n"
                     "/news - свежие новости (в разработке)\n"
                     "/events - события рядом (в разработке)")


# /weather
@bot.message_handler(commands=["weather"])
def weather_handler(message):
    try:
        # Получить название города после команды
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите город. Пример: /weather Москва")
            return

        city = parts[1]
        data = get_weather(city)
        if data.get('cod') != 200:
            bot.send_message(message.chat.id, f"Город '{city}' не найден. Попробуйте еще раз.")
            return

        temp = round(data['main']['temp'])  # Проверить, как отображаются отрицательные температуры
        descr = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind = round(data['wind']['speed'])
        msg = (f"Погода в городе {city}:\n"
               f"{descr.capitalize()}\n"
               f"Температура: {temp}°C\n"
               f"Влажность: {humidity}%\n"
               f"Ветер: {wind} м/с")
        bot.send_message(message.chat.id, msg)
    except Exception as e:
        print(f'Ошибка: {e}')
        bot.send_message(message.chat.id, "Произошла ошибка при получении погоды.")


# /news
@bot.message_handler(commands=["news"])
def news_handler(message):
    articles = get_news()
    if not articles:
        bot.send_message(message.chat.id, "Не удалось получить новости. Попробуйте позже.")
        return

    # Отправим 5 свежих новостей без кнопки
    news_messages = []
    for article in articles[:5]:
        title = article.get('title', 'Без заголовка')
        url = article.get('url', '')
        news_messages.append(f"{title}\n{url}")

    bot.send_message(message.chat.id, "\n\n".join(news_messages))

    # # Отправим 5 свежих новостей, к каждой — кнопку "Подробнее"
    # for article in articles[:5]:
    #     title = article.get('title', 'Без заголовка')
    #     url = article.get('url', '')
    #
    #     markup = types.InlineKeyboardMarkup()
    #     if url:
    #         markup.add(types.InlineKeyboardButton("Подробнее", url=url))
    #
    #     bot.send_message(message.chat.id, title, reply_markup=markup)


# /events
@bot.message_handler(commands=["events"])
def events_handler(message):
    try:
        parts = message.text.split(maxsplit=1)
        city = parts[1] if len(parts) > 1 else None

        events = get_events(city)
        if not events:
            bot.send_message(message.chat.id, "Не удалось найти события. Попробуйте позже или укажите другой город.")
            return

        event_messages = []
        for ev in events:
            name = ev.get('name', 'Без названия')
            starts_at = ev.get('starts_at', 'Дата неизвестна')
            readable_date = format_datetime(starts_at) if starts_at != 'Дата неизвестна' else starts_at
            url = ev.get('url', '')
            loc = ev.get('location', {})
            location_str = ""
            if isinstance(loc, dict):
                city_name = loc.get('city', '')
                address = loc.get('address', '')
                location_str = f" ({city_name}, {address})" if city_name or address else ""
            event_messages.append(f"{name}{location_str}\nДата: {readable_date}\n{url}")

        bot.send_message(message.chat.id, "\n\n".join(event_messages))

    except Exception as e:
        print(f'Ошибка: {e}')
        bot.send_message(message.chat.id, "Произошла ошибка при получении событий.")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен!")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка при запуске бота {e}")
