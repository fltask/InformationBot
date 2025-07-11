import telebot
import os
from dotenv import load_dotenv

# Загрузка токена из файла .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

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
    bot.send_message(message.chat.id,
                     "Функция прогноза погоды скоро будет добавлена! А пока что: ожидается хорошее настроение!")

# /news
@bot.message_handler(commands=["news"])
def news_handler(message):
    bot.send_message(message.chat.id,
                     "Функция новостей в разработке! Главная новость: команда отлично справляется!")

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