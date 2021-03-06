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
subcategory_db = db["subcategory"]
items_db = db["items"]

#создаем массив наименования категорий
category_name = []
category_btn = []

#текущий этап 0, корзина пустая
stage = 0
cart = []

# Выгружаем категории
for x in category_db.find():
    category_name.append(x['name'])
    category_btn.append(x['btn'])

# Обработчик /start
@bot.message_handler(commands=["start"])
def start(message, res=False):
	markup=types.ReplyKeyboardMarkup(resize_keyboard=True)

	# Каркас будущих кнопок
	btn1 = types.KeyboardButton("Меню")
	btn2 = types.KeyboardButton("Корзина "+ str(len(cart)))
	btn3 = types.KeyboardButton("Акции")
	btn4 = types.KeyboardButton("Поддержка")
	markup.add(btn3,btn1,btn2,btn4)

	# Отправить приветствие
	bot.send_message(message.chat.id, 'Бот работает', reply_markup=markup)

# Обработчик /stop
@bot.message_handler(commands=["stop"])
def stop(message, res=False):
	bot.send_message(message.chat.id, 'Кнопки удалены', reply_markup=types.ReplyKeyboardRemove())

# Для очистки корзины
def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

# Обработчик текста
@bot.message_handler(content_types=['text'])

# Обработка кнопок
def inline_key(a):

	# Нажатие по Меню
	if a.text == "Меню":

		# Глобально обнуляем шаг и обнуляем товары
		global stage
		global items_cost
		stage = 0
		items_name = []
		items_btn = []
		items_image = []
		items_description = []
		items_weight = []
		items_cost = []
		inlinemenu = types.InlineKeyboardMarkup()

		# Используя наименование категорий формируем кнопки name = btn.text, category = callback
		i = 0
		for x in category_btn:
			btn = types.InlineKeyboardButton(category_name[i], callback_data=x)
			inlinemenu.add(btn)
			i += 1

		# Отправляем пустую фотку с нашими кнопками (найти как можно изменять сообщение с добавлением фотки, не прикрепляя фотки)
		bot.send_photo(a.chat.id, "https://i.imgur.com/KWRQcAA.png",caption="Выберите категорию:",reply_markup=inlinemenu)

	elif a.text.split()[0][0:] == "Корзина":
		#Глобально слушаем корзину и клонируем для операций вывода
		global cart
		clone_cart = cart
		count = 0 #количество одного товара

		message = [] #будущее сообщение

		bot.send_message(a.chat.id, 'Корзина')
		i = 1
		#bot.send_message(a.chat.id, '№\tНаименование\t\t\tКоличество\t\t\tСтоимость')

		# клонируем корзину во временную корзину для формирования сообщения
		lastsummary = 0
		for x in clone_cart:
			count = clone_cart.count(x)
			if count>0:
				for y in items_db.find({"name":x}):
					cost = (y['cost'])
					summary = int(count) * int(cost)
					message.append(str(i)+".\t\t" + x.ljust(22) +"\t\t"+ str(count) + " шт. x" +"\t\t" + str(cost) + " руб. = " + str(summary)+ " руб.")
					i+=1
					lastsummary += summary
			clone_cart = remove_values_from_list(clone_cart, x)
			#print ("i= "+ str(i) + " cart " +str(clone_cart))
			count = 0
		inlinemenu = types.InlineKeyboardMarkup()
		buyall = types.InlineKeyboardButton("Оформить заказ", callback_data="buyall")
		clear = types.InlineKeyboardButton("Удалить товар", callback_data="clear")
		deleteone = types.InlineKeyboardButton("Очистить корзину", callback_data="deleteone")
		inlinemenu.add(buyall)
		inlinemenu.add(clear,deleteone)

		message.append("\nИтог: " + str(lastsummary)+ " руб.")
		text = ""
		for x in message:
			text += x + "\n"
		bot.send_message(a.chat.id,text,reply_markup=inlinemenu)

# Callback
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

	# Первый запрос из категории
	if call.data in category_btn:
		# глобальные переменные и обнулить массивы
		global stage
		global items_btn
		global items_name
		global items_image
		global items_description
		global items_weight
		global items_cost
		items_name = []
		items_btn = []
		items_image = []
		items_description = []
		items_weight = []
		items_cost = []
		stage = -1

		#Добавить товары из категории в массив
		for x in items_db.find({"btn":call.data}):
			items_name.append(x['name'])
			items_btn.append(x['btn'])
			items_image.append(x['image'])
			items_description.append(x['description'])
			items_weight.append(x['weight'])
			items_cost.append(x['cost'])

		inlinemenu = types.InlineKeyboardMarkup()

		# Купить кнопка
		cartbtn = types.InlineKeyboardButton(text='Купить за ' + str(items_cost[0]) + " руб.", callback_data="buy" + str(stage+1))
		inlinemenu.add(cartbtn)

		# Формируем кнопки
		prevbtn = types.InlineKeyboardButton(text='Назад',callback_data=items_name[len(items_name)-1])
		quantity = types.InlineKeyboardButton(text="1" + "/" + str(len(items_name)),callback_data='empty') # Пустой callback
		nextbtn = types.InlineKeyboardButton(text='Далее',callback_data=items_name[stage+2])
		inlinemenu.add(prevbtn,quantity,nextbtn)
		stage += 1
		bot.edit_message_media(types.InputMediaPhoto(items_image[0]),call.message.chat.id, call.message.message_id)
		bot.edit_message_caption(items_name[0] + " ["+ items_weight[0] + "]" + "\n\n"+items_description[0],call.message.chat.id, call.message.message_id,reply_markup=inlinemenu)	

	# Запрос из наименования товара
	elif call.data in items_name:
		stage = items_name.index(call.data)

		#Количество товаров в кнопке
		quantity_text = str(stage+1) + "/" + str(len(items_name))

		inlinemenu = types.InlineKeyboardMarkup()
		cartbtn = types.InlineKeyboardButton(text='Купить за ' + str(items_cost[stage]) + " руб.", callback_data="buy" + str(stage))
		inlinemenu.add(cartbtn)

		#Кнопки для предпоследнего товара
		if call.data == items_name[len(items_name)-1]:
			prevbtn = types.InlineKeyboardButton(text='Назад',callback_data=items_name[stage-1])
			quantity = types.InlineKeyboardButton(text=quantity_text,callback_data='empty') # Пустой callback
			nextbtn = types.InlineKeyboardButton(text='К началу',callback_data=items_name[0])
			inlinemenu.add(prevbtn,quantity,nextbtn)
		
		#Кнопки для первого товара	
		elif call.data == items_name[0]:
			prevbtn = types.InlineKeyboardButton(text='Назад',callback_data=items_name[len(items_name)-1])
			quantity = types.InlineKeyboardButton(text=quantity_text,callback_data='empty') # Пустой callback
			nextbtn = types.InlineKeyboardButton(text='Далее',callback_data=items_name[stage+1])
			inlinemenu.add(prevbtn,quantity,nextbtn)
		
		#Кнопки для товаров	
		else:
			prevbtn = types.InlineKeyboardButton(text='Назад',callback_data=items_name[stage-1])
			quantity = types.InlineKeyboardButton(text=quantity_text,callback_data='empty') # Пустой callback
			nextbtn = types.InlineKeyboardButton(text='Далее',callback_data=items_name[stage+1])
			inlinemenu.add(prevbtn,quantity,nextbtn)
			

		bot.edit_message_media(types.InputMediaPhoto(items_image[stage]),call.message.chat.id, call.message.message_id)
		bot.edit_message_caption(items_name[stage] + " ["+ items_weight[stage] + "]" + "\n\n"+items_description[stage],call.message.chat.id, call.message.message_id,reply_markup=inlinemenu)	

	elif call.data == "buy"+str(stage):
		
		#Обновление кнопок
		markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
		btn1 = types.KeyboardButton("Меню")
		btn2 = types.KeyboardButton("Корзина "+ str(len(cart)+1))
		btn3 = types.KeyboardButton("Акции")
		btn4 = types.KeyboardButton("Поддержка")
		markup.add(btn3,btn1,btn2,btn4)

		quantity_text = str(stage+1) + "/" + str(len(items_name))

		inlinemenu = types.InlineKeyboardMarkup()


		#Кнопки для предпоследнего товара
		if stage == len(items_name)-1:
			prevbtn = types.InlineKeyboardButton(text='Назад',callback_data=items_name[stage-1])
			quantity = types.InlineKeyboardButton(text=quantity_text,callback_data='empty') # Пустой callback
			nextbtn = types.InlineKeyboardButton(text='К началу',callback_data=items_name[0])
			inlinemenu.add(prevbtn,quantity,nextbtn)
		
		#Кнопки для первого товара	
		elif stage == 0:
			prevbtn = types.InlineKeyboardButton(text='Назад',callback_data=items_name[len(items_name)-1])
			quantity = types.InlineKeyboardButton(text=quantity_text,callback_data='empty') # Пустой callback
			nextbtn = types.InlineKeyboardButton(text='Далее',callback_data=items_name[stage+1])
			inlinemenu.add(prevbtn,quantity,nextbtn)
		
		#Кнопки для товаров	
		else:
			prevbtn = types.InlineKeyboardButton(text='Назад',callback_data=items_name[stage-1])
			quantity = types.InlineKeyboardButton(text=quantity_text,callback_data='empty') # Пустой callback
			nextbtn = types.InlineKeyboardButton(text='Далее',callback_data=items_name[stage+1])
			inlinemenu.add(prevbtn,quantity,nextbtn)

		bot.send_message(call.message.chat.id, 'В корзину добавлено: '+str(items_name[stage]), reply_markup=markup)
		cart.append(items_name[stage])


# Телеграм отправка
bot.polling(none_stop=True, interval=0)