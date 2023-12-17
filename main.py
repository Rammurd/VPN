import logging ##НУЖНО СДЕЛАТЬ УДАЛЕНИЕ КЛЮЧЕЙ, тут примеры https://github.com/jadolg/outline-vpn-api
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import httpx
from database import add_user, update_purchase_date, get_access_key, add_access_key, get_key_text, get_server_locations


# Сюда тыкаю токен от бота
bot = Bot(token='5964693615:AAFLleTU9TTsMlwa2ApbKXLiJvm1MLUO5fg')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["🔍 Как подключить","🍌 Доступ к VPN", "🛠 Мои ключи"]
    keyboard.add(*buttons)
    await message.answer("Выберите один из вариантов:", reply_markup=keyboard)

    #Добавляю юзера в бд после кнопки START
    user_id = message.from_user.id
    username = message.from_user.username
    add_user(user_id, username)


@dp.message_handler(lambda message: message.text == '🛠 Мои ключи')
async def my_keys_command(message: types.Message):
    # Получите user_id из сообщения
    user_id = message.from_user.id

    # Получите все доступные серверные местоположения для данного user_id
    server_locations = get_server_locations(user_id)

    if server_locations:
        # Создайте инлайн-клавиатуру с динамическими кнопками на основе server_locations
        keyboard = InlineKeyboardMarkup()
        buttons = [InlineKeyboardButton(location, callback_data=f'server_location_{location}') for location in server_locations]
        keyboard.add(*buttons)

        await message.answer("Выберите серверное местоположение:", reply_markup=keyboard)
    else:
        await message.answer("У вас нет доступных серверных местоположений.")

@dp.callback_query_handler(lambda query: query.data.startswith('server_location_'))
async def handle_server_location_choice(callback_query: types.CallbackQuery):
    # Получите server_location, на который нажали, из callback_data
    server_location = callback_query.data.replace('server_location_', '')

    # Получите соответствующий key_text для server_location
    user_id = callback_query.from_user.id
    key_text = get_key_text(user_id, server_location)

    if key_text:
        await callback_query.answer()
        await bot.send_message(callback_query.from_user.id, f"Ключ для сервера {server_location}: {key_text}")
    else:
        await callback_query.answer("Ключ не найден.")



# Кнопка "🔍 Как подключить"
@dp.message_handler(lambda message: message.text == '🔍 Как подключить')
async def how_to_connect(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("💅 iOS (iPhone)", url="https://itunes.apple.com/us/app/outline-app/id1356177741"),
        types.InlineKeyboardButton("👔 MacOS (Тунеядцы)", url="https://itunes.apple.com/us/app/outline-app/id1356178125"),
        types.InlineKeyboardButton("🐧 Linux (Для психов)", url="https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/stable/Outline-Client.AppImage"),
        types.InlineKeyboardButton("🤖 Android (Не iPhone)", url="https://play.google.com/store/apps/details?id=org.outline.android.client"),
        types.InlineKeyboardButton("🚪 Windows (Компьютер)", url="https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/stable/Outline-Client.exe"),
        types.InlineKeyboardButton("🥩 Chrome (Браузер)", url="https://play.google.com/store/apps/details?id=org.outline.android.client")
    )
    await message.answer("🍙 С какого устройства будем подключаться?", reply_markup=keyboard)


# Обработка кнопки "🍌 Доступ к VPN" и отправка инвойса
@dp.message_handler(lambda message: message.text == '🍌 Доступ к VPN')
async def server_callback(message: types.Message):
    # Создаем инлайн-клавиатуру с тремя кнопками тарифов в столбце
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("1 месяц (249 рублей)", callback_data="vpn_1_month"),
        types.InlineKeyboardButton("3 месяца (660 рублей)", callback_data="vpn_3_months"),
        types.InlineKeyboardButton("6 месяцев (990 рублей)", callback_data="vpn_6_months")
    ]
    keyboard.add(*buttons)

    await message.answer("Выберите тариф доступа к VPN:", reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data.startswith('vpn_'))
async def handle_vpn_tariff(callback_query: types.CallbackQuery):
    # Получите выбранный тариф из callback_data
    tariff = callback_query.data

    # Определите цену и описание в зависимости от выбранного тарифа
    if tariff == 'vpn_1_month':
        price = 24900
        description = "Доступ к VPN на 1 месяц"
    elif tariff == 'vpn_3_months':
        price = 66000
        description = "Доступ к VPN на 3 месяца"
    elif tariff == 'vpn_6_months':
        price = 99000
        description = "Доступ к VPN на 6 месяцев"
    else:
        price = 0
        description = ""

    # Создайте инвойс с выбранным тарифом
    invoice = types.Invoice(
        title="Доступ к VPN",
        description=description,
        payload=tariff,
        provider_token="381764678:TEST:73561",
        currency="RUB",
        prices=[types.LabeledPrice(label="Руб", amount=price)]
    )

    # Отправьте инвойс пользователю
    await bot.send_invoice(callback_query.from_user.id, **invoice.to_python())

# Обработка уведомления о PreCheckoutQuery
@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Что-то пошло не так, платеж не прошел"
    )

# Обработка успешного платежа
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    # Получите номер транзакции из SuccessfulPayment
    transaction_id = message.successful_payment.provider_payment_charge_id

    # Запрос к серверу Outline для получения ключа
    outline_server_data = {
        "apiUrl": "https://81.19.137.215:55902/Gs9mTulEVDPZmGcrj8dv6w",
        "certSha256": "A786F229BE1C5D083C559D7658DD18BFAA2D00D8946C2251FA1C3BB161027AF8"
    }
    async with httpx.AsyncClient(verify=False) as client:
        url = outline_server_data["apiUrl"] + "/access-keys/"
        response = await client.post(url)

        if response.status_code == 201:
            key_data = response.json()
            print(key_data)
            key_text = key_data.get("accessUrl")

            user_id = message.from_user.id
            update_purchase_date(user_id)
            add_access_key(user_id, key_text, "FRANCE")

    #Второй сервер
    outline_server_data_1 = {
        "apiUrl":"https://95.181.173.47:53852/m7q9MYv9BxRe6Sdj5fDZgw",
        "certSha256":"8FCD1D531CD1A0AE6D30A1627FE94968D3370EFF5F435018651C47ADABAB0834"
    }
    async with httpx.AsyncClient(verify=False) as client:
        url = outline_server_data_1["apiUrl"] + "/access-keys/"
        response = await client.post(url)

        if response.status_code == 201:
            key_data = response.json()
            print(key_data)
            key_text = key_data.get("accessUrl")

            add_access_key(user_id, key_text, "USA")

        else:
            await bot.send_message(
                message.from_user.id,
                "Что-то пошло не так. Платеж прошел, но ключ не был получен."
            )

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=None)