import os

import requests
import telebot
from dotenv import load_dotenv
from database.config import get_db
from database.crud import get_or_create_user, create_log
from datetime import datetime
import locale
import html

# Загрузка токена из файла .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EVENTS_API_KEY = os.getenv("EVENTS_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")


bot = telebot.TeleBot(TOKEN)


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    print(response.json())
    return response.json()


def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    return response.json().get("articles", [])


def get_events(city=None):
    url = "https://api.timepad.ru/v1/events/"
    headers = {"Authorization": f"Bearer {EVENTS_API_KEY}"}
    params = {
        "sort": "date",  # сортировка по дате
        "limit": 5,  # сколько событий возвращать
        "fields": "name,starts_at,description,url,location",  # необходимые поля
        "is_deleted": False,
        "is_confirmed": True,
    }
    if city:
        params["cities"] = city

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("values", [])
    else:
        print(f"TimePad API error: {response.status_code} {response.text}")
        return []


try:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
except locale.Error:
    pass


def format_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d.%m.%Y, %H:%M")
    except Exception:
        return dt_str


# /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    # Получаем сессию базы данных
    db = next(get_db())
    try:
        # Регистрируем пользователя или получаем существующего
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )

        # Логируем команду
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


# /help
@bot.message_handler(commands=["help"])
def help_handler(message):
    # Получаем сессию базы данных
    db = next(get_db())
    try:
        # Получаем пользователя
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )

        # Логируем команду
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


# /weather
@bot.message_handler(commands=["weather"])
def weather_handler(message):
    # Получаем сессию базы данных
    db = next(get_db())
    # try:
    # Получаем пользователя
    user = get_or_create_user(
        db, message.from_user.id, message.from_user.first_name or "Пользователь"
    )
    print(user)
    # Получить название города после команды
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(
            message.chat.id, "Пожалуйста, укажите город. Пример: /weather Москва"
        )
        # Логируем команду без города
        create_log(db, user.id, "/weather (без города)")
        return

    city = parts[1]
    data = get_weather(city)
    if data.get("cod") != 200:
        bot.send_message(
            message.chat.id, f"Город '{city}' не найден. Попробуйте еще раз."
        )
        # Логируем неудачный запрос
        create_log(db, user.id, f"/weather {city} (город не найден)")
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

    # Логируем успешный запрос
    create_log(db, user.id, f"/weather {city}")

    # except Exception as e:
    #     print(f'Ошибка: {e}')
    #     bot.send_message(message.chat.id, "Произошла ошибка при получении погоды.")
    #     # Логируем ошибку
    #     try:
    #         user = get_or_create_user(db, message.from_user.id, message.from_user.first_name or "Пользователь")
    #         create_log(db, user.id, "/weather (ошибка)")
    #     except:
    #         pass
    # finally:
    db.close()


# /news
@bot.message_handler(commands=["news"])
def news_handler(message):
    # Получаем сессию базы данных
    db = next(get_db())
    try:
        # Получаем пользователя
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )

        articles = get_news()
        if not articles:
            bot.send_message(
                message.chat.id, "Не удалось получить новости. Попробуйте позже."
            )
            # Логируем неудачный запрос
            create_log(db, user.id, "/news (ошибка получения)")
            return

        # Отправим 5 свежих новостей без кнопки
        news_messages = []
        for article in articles[:5]:
            title = article.get("title", "Без заголовка")
            url = article.get("url", "")
            news_messages.append(f"{title}\n{url}")

        bot.send_message(message.chat.id, "\n\n".join(news_messages))

        # Логируем успешный запрос
        create_log(db, user.id, "/news")

    except Exception as e:
        print(f"Ошибка при получении новостей: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при получении новостей.")
        # Логируем ошибку
        try:
            user = get_or_create_user(
                db, message.from_user.id, message.from_user.first_name or "Пользователь"
            )
            create_log(db, user.id, "/news (ошибка)")
        except:
            pass
    finally:
        db.close()

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
    # Получаем сессию базы данных
    db = next(get_db())
    try:
        # Получаем пользователя
        user = get_or_create_user(
            db, message.from_user.id, message.from_user.first_name or "Пользователь"
        )

        # Логируем команду
        create_log(db, user.id, "/events")

        # bot.send_message(message.chat.id,
        #                  "События скоро будут доступны! Событие дня: вы молодец!")
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
            url = ev.get("url", "")
            loc = html.unescape(ev.get("location", {}))
            location_str = ""
            if isinstance(loc, dict):
                city_name = loc.get("city", "")
                address = html.unescape(loc.get("address", ""))
                location_str = (
                    f" ({city_name}, {address})" if city_name or address else ""
                )
            event_messages.append(f"{name}{location_str}\nДата: {readable_date}\n{url}")

        bot.send_message(message.chat.id, "\n\n".join(event_messages))

    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при получении событий.")


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен!")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка при запуске бота {e}")
