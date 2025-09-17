"""
Информационный бот: погода, новости, события.
"""

import html
import locale
import os
from datetime import datetime

import requests
import telebot
from dotenv import load_dotenv

from database.config import get_db
from database.crud import get_or_create_user, create_log


# -------------------------------------------------------------------
# Загрузка конфигурации
# -------------------------------------------------------------------
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EVENTS_API_KEY = os.getenv("EVENTS_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")


bot = telebot.TeleBot(TOKEN)


# -------------------------------------------------------------------
# Вспомогательные функции
# -------------------------------------------------------------------
def get_weather(city):
    """Получить погоду по названию города через OpenWeatherMap API."""
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={city}"
        f"&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    )
    response = requests.get(url)
    return response.json()


def get_news():
    """Получить свежие новости через NewsAPI."""
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    return response.json().get("articles", [])


def get_events(city=None):
    """Получить список событий через TimePad API."""
    url = "https://api.timepad.ru/v1/events/"
    headers = {"Authorization": f"Bearer {EVENTS_API_KEY}"}
    params = {
        "sort": "date",            # сортировка по дате
        "limit": 5,                # количество событий
        "fields": "name,starts_at,description,url,location",
        "is_deleted": False,
        "is_confirmed": True,
    }
    if city:
        params["cities"] = city

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("values", [])

    print(f"TimePad API error: {response.status_code} {response.text}")
    return []


def format_datetime(dt_str):
    """Преобразовать ISO-дату в читаемый формат dd.mm.yyyy, HH:MM."""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d.%m.%Y, %H:%M")
    except Exception:
        return dt_str


# -------------------------------------------------------------------
# Настройка локали
# -------------------------------------------------------------------
try:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
except locale.Error:
    pass


# -------------------------------------------------------------------
# Обработчики команд
# -------------------------------------------------------------------
@bot.message_handler(commands=["start"])
def start_handler(message):
    """Команда /start — регистрация пользователя и приветствие."""
    db = next(get_db())
    try:
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )
        create_log(db, user.id, "/start")

        bot.send_message(
            message.chat.id,
            f"Привет, {user.name}! Я твой информационный помощник. \n\n"
            "Набери /help, чтобы узнать, что я умею.",
        )
    except Exception as e:
        print(f"Ошибка при обработке команды /start: {e}")
        bot.send_message(
            message.chat.id,
            "Привет! Я твой информационный помощник. \n\n"
            "Набери /help, чтобы узнать, что я умею.",
        )
    finally:
        db.close()


@bot.message_handler(commands=["help"])
def help_handler(message):
    """Команда /help — список доступных команд."""
    db = next(get_db())
    try:
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )
        create_log(db, user.id, "/help")

        bot.send_message(
            message.chat.id,
            "Доступные команды:\n"
            "/start - запустить бота\n"
            "/help - показать это меню\n"
            "/weather - узнать погоду\n"
            "/news - свежие новости\n"
            "/events - события рядом",
        )
    except Exception as e:
        print(f"Ошибка при обработке команды /help: {e}")
        bot.send_message(
            message.chat.id,
            "Доступные команды:\n"
            "/start - запустить бота\n"
            "/help - показать это меню\n"
            "/weather - узнать погоду\n"
            "/news - свежие новости\n"
            "/events - события рядом",
        )
    finally:
        db.close()


@bot.message_handler(commands=["weather"])
def weather_handler(message):
    """Команда /weather — прогноз погоды для указанного города."""
    db = next(get_db())
    user = get_or_create_user(
        db, message.from_user.id, message.from_user.first_name or "Пользователь"
    )

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(
            message.chat.id, "Пожалуйста, укажите город. Пример: /weather Москва"
        )
        create_log(db, user.id, "/weather (без города)")
        db.close()
        return

    city = parts[1]
    data = get_weather(city)

    if data.get("cod") != 200:
        bot.send_message(
            message.chat.id, f"Город '{city}' не найден. Попробуйте еще раз."
        )
        create_log(db, user.id, f"/weather {city} (город не найден)")
        db.close()
        return

    temp = round(data["main"]["temp"])
    descr = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind = round(data["wind"]["speed"])

    msg = (
        f"Погода в городе {city}:\n"
        f"{descr.capitalize()}\n"
        f"Температура: {temp}°C\n"
        f"Влажность: {humidity}%\n"
        f"Ветер: {wind} м/с"
    )
    bot.send_message(message.chat.id, msg)
    create_log(db, user.id, f"/weather {city}")
    db.close()


@bot.message_handler(commands=["news"])
def news_handler(message):
    """Команда /news — свежие новости."""
    db = next(get_db())
    try:
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )

        articles = get_news()
        if not articles:
            bot.send_message(
                message.chat.id, "Не удалось получить новости. Попробуйте позже."
            )
            create_log(db, user.id, "/news (ошибка получения)")
            return

        news_messages = [
            f"{article.get('title', 'Без заголовка')}\n{article.get('url', '')}"
            for article in articles[:5]
        ]

        bot.send_message(message.chat.id, "\n\n".join(news_messages))
        create_log(db, user.id, "/news")

    except Exception as e:
        print(f"Ошибка при получении новостей: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при получении новостей.")
        try:
            user = get_or_create_user(
                db, message.from_user.id, message.from_user.first_name or "Пользователь"
            )
            create_log(db, user.id, "/news (ошибка)")
        except Exception:
            pass
    finally:
        db.close()


@bot.message_handler(commands=["events"])
def events_handler(message):
    """Команда /events — список событий (по городу, если указан)."""
    db = next(get_db())
    try:
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )
        create_log(db, user.id, "/events")
    except Exception as e:
        print(f"Ошибка при обработке команды /events: {e}")
        bot.send_message(
            message.chat.id, "События скоро будут доступны! Событие дня: вы молодец!"
        )
    finally:
        db.close()

    try:
        parts = message.text.split(maxsplit=1)
        city = parts[1] if len(parts) > 1 else None

        events = get_events(city)
        if not events:
            bot.send_message(
                message.chat.id,
                "Не удалось найти события. Попробуйте позже или укажите другой город.",
            )
            return

        event_messages = []
        for ev in events:
            name = html.unescape(ev.get("name", "Без названия"))
            starts_at = ev.get("starts_at", "Дата неизвестна")
            readable_date = (
                format_datetime(starts_at)
                if starts_at != "Дата неизвестна"
                else starts_at
            )
            loc = ev.get("location", {})
            city_name = loc.get("city", "") if isinstance(loc, dict) else ""
            address = html.unescape(loc.get("address", "")) if isinstance(loc, dict) else ""
            location_str = (
                f" ({city_name}, {address})" if city_name or address else ""
            )
            url = ev.get("url", "")
            event_messages.append(
                f"{name}{location_str}\nДата: {readable_date}\n{url}"
            )

        bot.send_message(message.chat.id, "\n\n".join(event_messages))

    except Exception as e:
        print(f"Ошибка при получении событий: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при получении событий.")


# -------------------------------------------------------------------
# Запуск бота
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("Бот запущен!")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка при запуске бота {e}")
