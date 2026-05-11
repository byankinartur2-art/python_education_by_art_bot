import telebot
import os

TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой первый бот 🤖")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Напиши мне любое сообщение, и я отвечу тем же!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

print("Бот запущен и работает...")
bot.infinity_polling()
