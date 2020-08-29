#|------------------------ IMPORTS -------------------|
import os
import re
import logging
import asyncio
#import datetime
#from aiohttp import BasicAuth
from random import randint as ri
from time import gmtime, strftime
from aiogram.types.message import ContentTypes
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#|------------------- LOCAL MODULES ------------------|
from config import TOKEN, ADMINS_IDS, MANAGERS_GROUP_ID, BOTS_URL, HEADERS, PROXIE_URL, PROXIE_AUTH, \
    CATEGORIES_KEYBOARD, BREATH_KEYBOARD, RESPIRATORS_KEYBOARD, MASKS_KEYBOARD, \
        GOODS, SUITS_KEYBOARD, GLOVES_KEYBOARD, RESPIRATORS_LIST, MASKS_LIST, SUITS_LIST, GLOVES_LIST, \
            PRODUCT_CALLBACKS, ADD_TO_BUCKET_KEYBOARDS, EDIT_BUCKET_KEYBOARD, create_edit_keyboard, \
                EDIT_PRODUCT_KEYBOARD, PAYMENTS_PROVIDER_TOKEN, ORDER_INFO_TEXT, SHIPPING_OPTIONS, GROUP_BREATH, GROUP_CATEGORIES

from bucket import add_product_by_name, get_bucket_string, remove_from_bucket, get_product_by_number, add_product_by_number, get_bucket_for_checkout, remove_bucket
from states import OrderForm, Mailing
from users_manage import add_user, get_all_users, get_count_users

#|---------------------- CODE ------------------------|

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

storage = MemoryStorage()

bot = Bot(token=TOKEN, proxy=PROXIE_URL, proxy_auth=PROXIE_AUTH)

dp = Dispatcher(bot, storage=storage, loop=loop)

@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    """Отправляет приветственно сообщение"""
    await add_user(message.chat.id)
    text="""

Добро пожаловать в телеграмм-магазин Pro Блеск Pro Свет!

Совершайте покупки прямо в телеграмм!

Перемещайтесь между разделами товаров с помощью клавиатуры, выбирайте понравившийся товар и добавляйте в коризну, а затем в несколько незамысловатых действий оформляйте заказ!

Чтобы просмотреть подробную инструкцию по использованию,
нажмите /help.

Наш сайт http://pbps.ru
Приятных покупок!
"""
    if message.chat.id < 0:
        reply_key = GROUP_CATEGORIES
    else:
        reply_key = CATEGORIES_KEYBOARD

    await message.answer(text, reply_markup=reply_key)

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """Отправляет инструкцию"""
    text="""
Инструкция по использованию магазина:

1. Перейдите в нужную категорию товаров

2. Выберите номер продукта из предложенного списка

3. Выберите количество и добавьте продукт в корзину

4. После добавления всех необходимых товаров нажмите кнопку 'Моя корзина' и (если необходимо) нажмите 'Редактировать корзину' и настройте количество товаров

5. Затем Вы можете приступать к оформлению заказа, есть два варианта:
    а) оформление и оплата заказа через телеграмм
    б) оформление и оплата заказа через связь с менеджером магазина

6. Вновь нажмите кнопку 'Моя корзина', выберите вариант оформления заказа, который Вам ближе, и следуйте дальнейшим инструкциям

7. После оформления и оплаты заказа Вы получите квитанцию со всей информацией о заказе, если Вы выбрали заказ через менеджера, то с Вами дополнительно свяжутся для уточнения деталей.

Чтобы просмотреть это сообщение еще раз,
нажмите /help

Наш сайт http://pbps.ru
Приятных покупок!
"""
    if message.chat.id < 0:
        reply_key = GROUP_CATEGORIES
    else:
        reply_key = CATEGORIES_KEYBOARD

    await message.answer(text, reply_markup=reply_key)

@dp.message_handler(commands=['go'])
async def hidden_go(message: types.Message):
    await message.answer(".")

@dp.message_handler(commands=['cancelOrder'], state=OrderForm)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Внимание! Вы отменили оформление заказа через менеджера. Начните снова в любое время.")
    await state.reset_state()

@dp.message_handler(user_id=ADMINS_IDS, commands=['mailing'])
async def new_mailing(message: types.Message):
    await message.answer("Пожалуйста, введите сообщение для рассылки.")
    await Mailing.text.set()

@dp.message_handler(user_id=ADMINS_IDS, commands=['users'])
async def get_users_count(message: types.Message):
    count = await get_count_users()
    await message.answer(f"Пользователей за все время: {count}")

@dp.message_handler(user_id=ADMINS_IDS, state=Mailing.text)
async def get_mailing(message: types.Message, state: FSMContext):
    await message.answer("Начинаю рассылку сообщения.")
    await state.update_data(text=message.text)
    data = await state.get_data()
    to_mail = data.get("text")
    all_users = await get_all_users()
    for user in all_users:
        try:
            await bot.send_message(user, to_mail)
        except:
            pass

    await state.reset_state()
    await message.answer("Рассылка проведена успешно.")

@dp.message_handler(lambda message: message.chat.id < 0 and re.match(r"(?i)\где\sмне\sкупить\s(\bреспиратор|\bзащитную\sмаску|\bзащитный\sкостюм|\bзащитные\sперчатки)", message.text) != None)
async def get_group_message(message: types.Message):
    text = re.match(r"(?i)\где\sмне\sкупить\s(\bреспиратор|\bзащитную\sмаску|\bзащитный\sкостюм|\bзащитные\sперчатки)", message.text)
    product = text.group(0).split()[-1].lower()

    if product == "респиратор":
        await message.answer(RESPIRATORS_LIST, reply_markup=RESPIRATORS_KEYBOARD)
    elif product == "маску":
        await message.answer(MASKS_LIST, reply_markup=MASKS_KEYBOARD)
    elif product == "костюм":
        await message.answer(SUITS_LIST, reply_markup=SUITS_KEYBOARD)
    elif product == "перчатки":
        await message.answer(GLOVES_LIST, reply_markup=GLOVES_KEYBOARD)
    else:
        await message.answer("Посетите наш магазин! У нас много интересного!", reply_markup=GROUP_CATEGORIES)


# ---------- CATEGORIES
@dp.message_handler(lambda message: message.text.lower().startswith("защита органов дыхания"))
async def send_breath_handler(message: types.Message):
    """Отправляет защиту органов дыхания"""

    if message.chat.id < 0:
        reply_key = GROUP_BREATH
    else:
        reply_key = BREATH_KEYBOARD

    await message.answer("Выберите способ защиты дыхания:", reply_markup=reply_key)

@dp.message_handler(lambda message: message.text.lower().startswith("защитные костюмы"))
async def send_body_handler(message: types.Message):
    """Отправляет защитные костюмы"""
    await message.answer(SUITS_LIST, reply_markup=SUITS_KEYBOARD)

@dp.message_handler(lambda message: message.text.lower().startswith("защитные перчатки"))
async def send_body_handler(message: types.Message):
    """Отправляет защитные перчатки"""
    await message.answer(GLOVES_LIST, reply_markup=GLOVES_KEYBOARD)



# ---------- BREATH CATEGORIES
@dp.message_handler(lambda message: message.text.lower().startswith("респираторы 3м"))
async def send_respirators_3m_handler(message: types.Message):
    """Отправляет список респираторов"""
    await message.answer(RESPIRATORS_LIST, reply_markup=RESPIRATORS_KEYBOARD)

@dp.message_handler(lambda message: message.text.lower().startswith("тканевые многоразовые маски"))
async def send_masks_handler(message: types.Message):
    """Отправляет список масок"""
    await message.answer(MASKS_LIST, reply_markup=MASKS_KEYBOARD)



# ---------- NAVIGATION
@dp.message_handler(lambda message: message.text.lower().startswith("назад к защите органов дыхания"))
async def send_back_to_breath_handler(message: types.Message):
    """Отправляет защиту органов дыхания"""
    text = "Выберите способ защиты дыхания:"
    await message.answer(text, reply_markup=BREATH_KEYBOARD)

@dp.message_handler(lambda message: message.text.lower().startswith("назад на главную"))
async def send_back_to_main_handler(message: types.Message):
    """Отправляет все категории"""
    text = "Выберите способ защиты:"

    if message.chat.id < 0:
        reply_key = GROUP_CATEGORIES
    else:
        reply_key = CATEGORIES_KEYBOARD

    await message.answer(text, reply_markup=reply_key)



# ---------- GOODS CHOOSING
@dp.callback_query_handler(lambda callback_query: True)
async def goods_query_handler(callback_query: types.CallbackQuery):
    """Отправляет информацию о товаре"""
    if callback_query.data in GOODS['categories']['breath_care']['respiratirs_3m'].keys():
        
        if callback_query.message.chat.id < 0:
            reply_key = None
        else:
            reply_key = ADD_TO_BUCKET_KEYBOARDS[callback_query.data]
        
        await callback_query.message.answer(GOODS['categories']['breath_care']['respiratirs_3m'][callback_query.data], reply_markup=reply_key)

    elif callback_query.data in GOODS['categories']['breath_care']['masks'].keys():
        
        if callback_query.message.chat.id < 0:
            reply_key = None
        else:
            reply_key = ADD_TO_BUCKET_KEYBOARDS[callback_query.data]

        await callback_query.message.answer(GOODS['categories']['breath_care']['masks'][callback_query.data], reply_markup=reply_key)

    elif callback_query.data in GOODS['categories']['body_care'].keys():

        if callback_query.message.chat.id < 0:
            reply_key = None
        else:
            reply_key = ADD_TO_BUCKET_KEYBOARDS[callback_query.data]

        await callback_query.message.answer(GOODS['categories']['body_care'][callback_query.data], reply_markup=reply_key)

    elif callback_query.data in GOODS['categories']['hand_care'].keys():

        if callback_query.message.chat.id < 0:
            reply_key = None
        else:
            reply_key = ADD_TO_BUCKET_KEYBOARDS[callback_query.data]
    
        await callback_query.message.answer(GOODS['categories']['hand_care'][callback_query.data], reply_markup=reply_key)

    elif callback_query.data.endswith("product_by_name"):

        amount = callback_query.data.split("_")[1]
        name = "_".join(callback_query.data.split("_")[2:4])

        await add_product_by_name(callback_query.message.chat.id, PRODUCT_CALLBACKS[name][0], PRODUCT_CALLBACKS[name][1], int(amount) )
        await callback_query.message.answer(f"Продукт {PRODUCT_CALLBACKS[name][0]} был успешно добавлен в корзину в количестве {amount}")

    elif callback_query.data == "edit_bucket":

        await callback_query.message.answer("Выберите номер продукта для редактирования количества:", reply_markup=create_edit_keyboard(callback_query.message.chat.id))

    elif callback_query.data.startswith("edit") and callback_query.data.endswith("product_in_bucket"):

        num_of_product = callback_query.data.split("_")[1]

        res = get_product_by_number(callback_query.message.chat.id, int(num_of_product))

        if res != None:
            await callback_query.message.answer(res, reply_markup=EDIT_PRODUCT_KEYBOARD)

        else:
            await callback_query.message.answer("При выборе продукта для редактирования произошла ошибка.")

    elif callback_query.data.endswith("product_by_number"):

        to_do = callback_query.data.split("_")[0]
        number_of_product = callback_query.message.text.split()[3][0]
       
        amount = callback_query.data.split("_")[1]
    
        text = "При редактирование продукта произошла ошибка."

        if to_do == "delete":

            if amount == "all":
                res = remove_from_bucket(callback_query.message.chat.id, int(number_of_product), 0, True)
                if res:
                    text = "Продукт был успешно удален из корзины."
            else:
                res = remove_from_bucket(callback_query.message.chat.id, int(number_of_product), int(amount), False)
                if res:
                    text = "Количество выбранного продукта было успешно изменено."

        elif to_do == "add":

            res = add_product_by_number(callback_query.message.chat.id, int(number_of_product), int(amount))
            if res:
                text = "Количество выбранного продукта было успешно изменено."

        await callback_query.message.answer(text)

    elif callback_query.data == "checkout_escvair":

        description, prices = get_bucket_for_checkout(callback_query.message.chat.id)

        await bot.send_invoice(callback_query.message.chat.id, 
                           title='Итоговая корзина',
                           description=description,
                           provider_token=PAYMENTS_PROVIDER_TOKEN,
                           currency='rub',
                           photo_url='https://telegra.ph/file/d08ff863531f10bf2ea4b.jpg',
                           photo_height=512,  # !=0/None or picture won't be shown
                           photo_width=512,
                           photo_size=512,
                           is_flexible=True,  # True If you need to set up Shipping Fee
                           prices=prices,
                           start_parameter='result-bucket-checkout',
                           payload='ИТОГОВАЯ КОРЗИНА')

        await callback_query.message.answer("Заказ был успешно сформирован, пожалуйста, нажмите на кнопку 'Заплатить ...' в сообщении выше, введите все необходимые данные и оплатите Ваш заказ.\n\nСейчас Ваша корзина пуста, если захотите приобрести что-то еще - Вы знаете что делать!")

    elif callback_query.data == "checkout_menedger":

        await callback_query.message.answer("Для оформления заказа необходимы некоторые данные. Пожалуйста, внимательно ответьте на следующие несколько сообщений. Введенные данные не будут храниться где-либо и не будут переданы третьим лицам и поступят сразу к менеджеру для оформления заказа.")
        await callback_query.message.answer("Введите Вашу фамилию имя и отчество:\nДля отмены нажмите /cancelOrder")
        await OrderForm.name.set()

    elif callback_query.data == "back_to_breath":

        if callback_query.message.chat.id < 0:
            reply_key = GROUP_BREATH
        else:
            reply_key = BREATH_KEYBOARD

        await callback_query.message.answer("Выберите способ защиты дыхания:", reply_markup=reply_key)

    elif callback_query.data == "back_to_main":
        
        if callback_query.message.chat.id < 0:
            reply_key = GROUP_CATEGORIES
        else:
            reply_key = CATEGORIES_KEYBOARD
        
        await callback_query.message.answer("Выберите способ защиты:", reply_markup=reply_key)

    else:

        await callback_query.message.answer("Выберите продукт из списка:")

@dp.shipping_query_handler(lambda query: True)
async def shipping(shipping_query: types.ShippingQuery):
    await bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=SHIPPING_OPTIONS,
                                    error_message="Ошибка! При выборе способа доставки произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message="Ошибка! При оплате Вашего заказ произошла ошибка, пожалуйста, попробуйте позже.")


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    remove_bucket(message.chat.id)
    await bot.send_message(message.chat.id,
                           'Поздравляем! Оплата прошла успешно! Ваш заказ `{} {}`'
                           ' будет доставлен как можно скорее. Вы можете посмотреть квитанцию о заказе, нажав на кнопку "Посмотреть квитанцию" в сообщении выше.'
                           '\n\nСейчас Ваша корзина пуста, если захотите приобрести что-то еще - Вы знаете что делать!'.format(
                               message.successful_payment.total_amount / 100, message.successful_payment.currency),
                           parse_mode='Markdown')

@dp.message_handler(state=OrderForm.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer("Теперь выберите номер варианта доставки из списка ниже\n( пожалуйста, отправьте только номер варианта, например, 2 )\nДля отмены нажмите /cancelOrder")
    await message.answer("""
1. Самовывоз - Сходня
2. Самовывоз - Путилково
3. Доставка в пределах МКАД - 500р
4. Доставка за МКАД - 700р
5. Доставка курьером - нужно будет уточнить детали у менеджера\nДля отмены нажмите /cancelOrder""")
    await OrderForm.shipping.set()

@dp.message_handler(state=OrderForm.shipping)
async def get_ship(message: types.Message, state: FSMContext):
    
    options = {
        1: "Самовывоз - Сходня",
        2: "Самовывоз - Путилково",
        3: "Доставка в пределах МКАД - 500р",
        4: "Доставка за МКАД - 700р",
        5: "Доставка курьером"
    }

    if message.text.isdigit():
        if int(message.text) in range(1, 6):
            await state.update_data(shipping=options[int(message.text)])
            await message.answer("Теперь введите Ваш полный адрес Город, улица, номер дома, номер квартиры и почтовый индекс\n( пожалуйста, вводите адрес внимательно - изменить его можно будет только через менеджера! ):\nДля отмены нажмите /cancelOrder")
            await OrderForm.address.set()

        else:
            await message.answer("Пожалуйста, введите корректный номер варианта доставки.\nДля отмены нажмите /cancelOrder")
            await OrderForm.shipping.set()
    else:
        await message.answer("Пожалуйста, введите корректный номер варианта доставки.\nДля отмены нажмите /cancelOrder")
        await OrderForm.shipping.set()

@dp.message_handler(state=OrderForm.address)
async def get_address(message: types.Message, state: FSMContext):

    address = message.text

    await state.update_data(address=address)
    await message.answer("Теперь введите Ваш номер телефона:\nДля отмены нажмите /cancelOrder")
    await OrderForm.phone_number.set()

@dp.message_handler(state=OrderForm.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):

    phone = message.text

    await state.update_data(phone_number=phone)
    await message.answer("Теперь введите Вашу электронную почту:\nДля отмены нажмите /cancelOrder")
    await OrderForm.mail.set()

@dp.message_handler(state=OrderForm.mail)
async def get_mail(message: types.Message, state: FSMContext):

    mail = message.text

    await state.update_data(mail=mail)

    await message.answer("Теперь введите Ваш никнейм в телеграмме\n( чтобы узнать его, перейдите в свой профиль и найдите там надпись Имя пользователя - начинается со знака @ ):\nДля отмены нажмите /cancelOrder")

    await OrderForm.nickname.set()

@dp.message_handler(state=OrderForm.nickname)
async def get_nickname(message: types.Message, state: FSMContext):

    nickname = message.text

    if nickname.startswith("@"):

        await state.update_data(nickname=nickname)

        bucket_info = get_bucket_string(message.chat.id)
        remove_bucket(message.chat.id)
        order_number = str(ri(0, 9999))
        order_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        data = await state.get_data()
        name = data.get("name")
        ship = data.get("shipping")
        address = data.get("address")
        phone = data.get("phone_number")
        mail = data.get("mail")
        nick = data.get("nickname")

        result = f"""
=============================
Квитанция по заказу номер {order_number} от {order_time}:
{bucket_info}
-----------------------------
Имя: {name}
Доставка: {ship}
Адрес: {address}
Номер телефона: {phone}
Электр. почта: {mail}
Никнейм: {nick}
=============================
    """
        await state.reset_state(with_data=False)
        await message.answer(result)
        await message.answer("Поздравляем! Ваш заказ был успешно сформирован! В скором времени с Вами свяжется менеджер для уточнения деталей. Спасибо за Ваш заказ!")
        await bot.send_message(MANAGERS_GROUP_ID, result)
    
    else:

        await message.answer("Пожалуйста, введите Ваш корректный никнем в телеграмме.\nДля отмены нажмите /cancelOrder")
        await OrderForm.nickname.set()


@dp.message_handler(lambda message: message.text.lower().startswith("моя корзина"))
async def send_bucket_handler(message: types.Message):
    """Отправляет корзину заказа"""
    result = get_bucket_string(message.chat.id)
    if result != None:
        await message.answer(result, reply_markup=EDIT_BUCKET_KEYBOARD)

    else:

        await message.answer("Корзина пуста, выберите необходимый продукт и добавьте его в корзину в требуемом количестве.")




@dp.message_handler()
async def everything_else_handler(message: types.Message):
    """Обрабатывает прочие сообщения"""
    await message.answer("Пожалуйста, выберите продукт или категорию")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)