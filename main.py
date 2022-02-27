import telebot
from telebot import types
from pymongo import MongoClient
import pymongo

#Подключаем пароли и БД
f = open('inputs.txt','r')
settings = f.readlines()
f.close()

# Задаем боту ключ
bot = telebot.TeleBot(settings[0].rstrip('\n'))

# Подключаем БД
client = pymongo.MongoClient(settings[1].rstrip('\n'))

# Определяем Коллекцию и таблицу
db = client["DB"]
category_db = db["category"]

#создаем массив наименования категорий
category_name = []

# Добавляем все значения таблицы в массив
for x in category_db.find():
    category_name.append(x['name'])

# Обработчик /start
@bot.message_handler(commands=["start"])
def start(message, res=False):
	markup=types.ReplyKeyboardMarkup(resize_keyboard=True)

	i = 0
	for x in category_name:
		btnname = "button%d"% + i
		btnname = types.KeyboardButton(x)
		markup.add(btnname)
		i+=1

	bot.send_message(message.chat.id, 'Бот работает', reply_markup=markup)

# Обработчик /stop
@bot.message_handler(commands=["stop"])
def stop(message, res=False):
	bot.send_message(message.chat.id, 'Кнопки удалены', reply_markup=types.ReplyKeyboardRemove())


# Телеграм отправка
bot.polling(none_stop=True, interval=0)