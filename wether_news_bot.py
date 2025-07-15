import telebot
import requests
from telebot import types
from config import API_TOKEN, WEATHER_API_KEY, NEWS_API_KEY
import os
from dotenv import load_dotenv

# Загрузка токена из файла .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    return response.json()

def get_news():
   url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
   response = requests.get(url)
   return response.json().get('articles', [])


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

        temp = round(data['main']['temp']) # Проверить, как отображаются отрицательные температуры
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
    bot.send_message(message.chat.id,
                     "События скоро будут доступны! Событие дня: вы молодец!")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен!")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка при запуске бота {e}")