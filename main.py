import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
import httpx
from database import add_user, update_purchase_date, get_user_data


# Сюда тыкаю токен от бота
bot = Bot(token='5964693615:AAFLleTU9TTsMlwa2ApbKXLiJvm1MLUO5fg')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["🔍 Как подключить","🍌 Доступ к VPN"]
    keyboard.add(*buttons)
    await message.answer("Выберите один из вариантов:", reply_markup=keyboard)

    #Добавляю юзера в бд после кнопки START
    user_id = message.from_user.id
    username = message.from_user.username
    add_user(user_id, username)


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
    # Создайте инвойс и отправьте его пользователю
    invoice = types.Invoice(
        title="YourTitle",
        description="YourDescription",
        payload="YourPayload",
        provider_token="381764678:TEST:73561",
        currency="RUB",
        prices=[types.LabeledPrice(label="Руб", amount=9900)]
    )

    await bot.send_invoice(
        message.from_user.id,
        **invoice.to_python()
    )
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
            if key_text:
                await bot.send_message(message.from_user.id,
                                       f"1. Не тупи\n2. Нажми на непонятный текст снизу\n3. Вставь в ключ в приложение\n```{key_text}#VPN_Франция🥖(t.me/ryyad)```\np.s\nПриложение можно скачать по кнопке в меню (🔍 Как подключить)",
                                       parse_mode=types.ParseMode.MARKDOWN)
                user_id = message.from_user.id
                update_purchase_date(user_id)

        else:
            await bot.send_message(
                message.from_user.id,
                "Что-то пошло не так. Платеж прошел, но ключ не был получен."
            )

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=None)