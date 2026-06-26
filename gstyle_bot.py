import logging
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import os

TELEGRAM_TOKEN = os.environ.get("TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MANAGER_USERNAME = "@SamandarGayratovic"
INSTAGRAM_URL = "https://www.instagram.com/g.style.uz"
KATALOG_URL = "https://t.me/g_style_uz"
MANZIL = "Chirchiq bazar, TSUM, 2-proxod"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""You are AI assistant of G-Style shoe store in Chirchiq, Uzbekistan.
Store address: Chirchiq bazar, TSUM, 2-proxod.
We sell: Nike, Adidas, New Balance and other brand sneakers.

IMPORTANT RULES:
- If user writes in Uzbek - respond in Uzbek
- If user writes in Russian - respond in Russian
- If user writes in English - respond in English
- Be friendly and professional
- For catalog: recommend visiting our Telegram channel t.me/g_style_uz
- For Instagram: instagram.com/g.style.uz
- For price or availability questions: recommend contacting manager @SamandarGayratovic
- Working hours: 9:00 - 21:00""",
)

user_chats = {}


def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("👟 Katalog", url=KATALOG_URL),
         InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_URL)],
        [InlineKeyboardButton("📍 Manzil", callback_data="manzil"),
         InlineKeyboardButton("👨‍💼 Menejer", callback_data="manager")],
        [InlineKeyboardButton("💬 Savol berish", callback_data="ask")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_chats[user.id] = model.start_chat(history=[])
    await update.message.reply_text(
        f"👟 G-Style ga xush kelibsiz, {user.first_name}!\n\n"
        "Добро пожаловать в G-Style!\n\n"
        "Chirchiq bazar, TSUM, 2-proxod\n"
        "Ish vaqti: 9:00 - 21:00\n\n"
        "Quyidagi menyudan tanlang yoki savol yozing 👇",
        reply_markup=get_main_keyboard(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "manager":
        await query.message.reply_text(
            f"👨‍💼 Menejer: {MANAGER_USERNAME}\n"
            f"Менеджер: {MANAGER_USERNAME}\n\n"
            "Ish vaqti / Время работы: 9:00 - 21:00",
            reply_markup=get_main_keyboard(),
        )
    elif query.data == "manzil":
        await query.message.reply_text(
            f"📍 Manzil: {MANZIL}\n"
            f"Адрес: {MANZIL}",
            reply_markup=get_main_keyboard(),
        )
    elif query.data == "ask":
        await query.message.reply_text(
            "✍️ Savolingizni yozing / Напишите ваш вопрос:",
            reply_markup=get_main_keyboard(),
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = user_chats[user_id].send_message(update.message.text)
        await update.message.reply_text(response.text, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text(
            f"Texnik xato. Menejer: {MANAGER_USERNAME}\n"
            f"Техническая ошибка. Менеджер: {MANAGER_USERNAME}",
            reply_markup=get_main_keyboard(),
        )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
