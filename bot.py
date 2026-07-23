import os
import asyncio
from io import BytesIO
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    BufferedInputFile
)
from aiogram.filters import Command
from wg_api import WireGuardAPI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WG_API_URL = os.getenv("WG_API_URL")
WG_PASSWORD = os.getenv("WG_PASSWORD")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
wg = WireGuardAPI(WG_API_URL, WG_PASSWORD)


def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔒 День — 25 ⭐", callback_data="buy_1day")],
        [InlineKeyboardButton(text="🔒 Неделя — 100 ⭐", callback_data="buy_7days")],
        [InlineKeyboardButton(text="🔒 Месяц — 170 ⭐", callback_data="buy_30days")],
        [InlineKeyboardButton(text="📱 Мои устройства", callback_data="my_devices")],
        [InlineKeyboardButton(text="ℹ️ О сервисе", callback_data="about")]
    ])


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🛡 Snaff — твой личный VPN за минуту\n\n"
        "• Защита в публичных сетях\n"
        "• Доступ к домашним ресурсам\n"
        "• Без сбора логов и данных\n\n"
        "Выбери тариф:",
        reply_markup=main_keyboard()
    )


@dp.callback_query(F.data == "buy_1day")
async def buy_1day(callback: types.CallbackQuery):
    await callback.message.answer_invoice(
        title="Snaff VPN — 1 день",
        description="Защищённое подключение на 24 часа",
        payload="vpn_1day",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="VPN на день", amount=25)]
    )


@dp.callback_query(F.data == "buy_7days")
async def buy_7days(callback: types.CallbackQuery):
    await callback.message.answer_invoice(
        title="Snaff VPN — 7 дней",
        description="Защищённое подключение на неделю",
        payload="vpn_7days",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="VPN на неделю", amount=100)]
    )


@dp.callback_query(F.data == "buy_30days")
async def buy_30days(callback: types.CallbackQuery):
    await callback.message.answer_invoice(
        title="Snaff VPN — 30 дней",
        description="Защищённое подключение на месяц",
        payload="vpn_30days",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="VPN на месяц", amount=170)]
    )


@dp.pre_checkout_query()
async def pre_checkout(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    await message.answer("⏳ Создаю твой защищённый канал...")

    client_data = wg.create_client(device_name=f"tg_{message.from_user.id}")

    if "error" in client_data:
        await message.answer("❌ Ошибка создания. Попробуй позже.")
        return

    config_text = client_data.get("config", "")
    qr_code_url = client_data.get("qr", "")

    await message.answer("✅ VPN готов! Вот твои данные для подключения:")

    config_file = BytesIO(config_text.encode())
    config_file.name = "snaff.conf"
    await message.answer_document(
        document=BufferedInputFile(config_file.read(), filename="wiregate.conf"),
        caption="📄 Конфигурационный файл"
    )

    if qr_code_url:
        await message.answer_photo(qr_code_url, caption="📱 Отсканируй QR-код в приложении WireGuard")

    await message.answer(
        "📲 Как подключиться:\n"
        "1. Скачай Snaff VPN из магазина приложений\n"
        "2. Нажми «+» → «Импорт из файла»\n"
        "3. Выбери скачанный конфиг\n"
        "4. Включи тумблер — готово!"
    )


@dp.callback_query(F.data == "my_devices")
async def show_devices(callback: types.CallbackQuery):
    clients = wg.get_clients()
    if not clients:
        await callback.message.answer("У тебя пока нет активных устройств")
        return

    text = "📱 Твои устройства:\n\n"
    for client in clients:
        text += f"• {client.get('name', 'Unknown')}\n"

    await callback.message.answer(text)


@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    await callback.message.answer(
        "🛡 Snaff VPN — личная кибербезопасность\n\n"
        "• Военный стандарт шифрования\n"
        "• Не храним и не собираем логи подключений\n"
        "• Сервера в РФ (соответствие 152-ФЗ)\n"
        "• Поддержка 24/7\n\n"
        "Сервис предназначен для защиты ваших личных данных в публичных сетях "
        "и удалённого доступа к личным ресурсам."
    )


async def main():
    print("🚀 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())