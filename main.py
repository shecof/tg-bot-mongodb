import telebot
from telebot import types
from pymongo import MongoClient
import pymongo

#Подключаем пароли и БД
f = open('/Users/dmitriy/Desktop/My Python Projects/inputs.txt','r')
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
category_btn = []

cur_stage = 0
c_stage = 0

# Добавляем все значения таблицы в массив
for x in category_db.find():
    category_name.append(x['name'])
    category_btn.append(x['btn'])

# Обработчик /start
@bot.message_handler(commands=["start"])
def start(message, res=False):
	markup=types.ReplyKeyboardMarkup(resize_keyboard=True)

	# Каркас будущих кнопок
	btn1 = types.KeyboardButton("Меню")
	btn2 = types.KeyboardButton("Корзина")
	btn3 = types.KeyboardButton("Акции")
	btn4 = types.KeyboardButton("Поддержка")
	markup.add(btn3,btn1,btn2,btn4)

	# Отправить приветствие
	bot.send_message(message.chat.id, 'Бот работает', reply_markup=markup)

# Обработчик /stop
@bot.message_handler(commands=["stop"])
def stop(message, res=False):
	bot.send_message(message.chat.id, 'Кнопки удалены', reply_markup=types.ReplyKeyboardRemove())



# Обработчик текста
@bot.message_handler(content_types=['text'])

# Нажатие по кнопке Меню
def inline_key(a):
	if a.text == "Меню":
		inlinemenu = types.InlineKeyboardMarkup()

		# Используя наименование категорий формируем кнопки name = btn.text, category = callback
		i = 0
		for x in category_name:
			btn = types.InlineKeyboardButton(x, callback_data=category_btn[i])
			inlinemenu.add(btn)
			i+=1
	# Отправляем пустую фотку с нашими кнопками (найти как можно изменять сообщение с добавлением фотки, не прикрепляя фотки)
	bot.send_photo(a.chat.id, "https://i.imgur.com/KWRQcAA.png",caption="Выберите категорию:",reply_markup=inlinemenu)


# Callback
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	if call.data == category_btn[cur_stage]:
		# Считаем, сколько всего элементов в массиве для вывода stage
		stage = str(cur_stage+1) + "/" + str(len(category_name))

		global c_stage
		c_stage = cur_stage+1

		# Формируем кнопки
		inlinemenu = types.InlineKeyboardMarkup()
		nextbtn = types.InlineKeyboardButton(text='Далее',callback_data=category_btn[c_stage])
		stage = types.InlineKeyboardButton(text=stage,callback_data='empty') # Пустой callback
		inlinemenu.add(nextbtn,stage)

		# Редактируем сообщение с фоткой
		bot.edit_message_media(types.InputMediaPhoto('https://orderapp-static.burgerking.ru/x256/mobile_image/8ef47102331d33496fcd9fb3efcc2072.png'),call.message.chat.id, call.message.message_id)
		bot.edit_message_caption(category_name[cur_stage],call.message.chat.id, call.message.message_id,reply_markup=inlinemenu)
    
	elif call.data == category_btn[c_stage]:
		# Считаем, сколько всего элементов в массиве для вывода stage
		stage = str(c_stage+1) + "/" + str(len(category_name))

		global cur_stage
		cur_stage = c_stage+1

		# Формируем кнопки
		inlinemenu = types.InlineKeyboardMarkup()
		nextbtn = types.InlineKeyboardButton(text='Далее',callback_data=category_btn[cur_stage])
		stage = types.InlineKeyboardButton(text=stage,callback_data='empty') # Пустой callback
		inlinemenu.add(nextbtn,stage)

		# Редактируем сообщение с фоткой
		bot.edit_message_media(types.InputMediaPhoto('https://orderapp-static.burgerking.ru/x256/mobile_image/8ef47102331d33496fcd9fb3efcc2072.png'),call.message.chat.id, call.message.message_id)
		bot.edit_message_caption(category_name[cur_stage],call.message.chat.id, call.message.message_id,reply_markup=inlinemenu)

# Телеграм отправка
bot.polling(none_stop=True, interval=0)