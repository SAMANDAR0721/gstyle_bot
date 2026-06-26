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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""Siz G-Style dokoni AI yordamchisisiz.
G-Style - Toshkentdagi zamonaviy krossovka dokoni.
Qoidalar:
- Faqat uzbek va rus tillarida javob bering
- Mijoz qaysi tilda yozsa, shu tilda javob bering
- Krossovkalar, yetkazib berish, olchamlar haqida savollar
- Har doim dostona va professional boling
- Katalogni korish uchun Instagram profilimizni tavsiya qiling
- Narx yoki mavjudlik soralsa, menejer bilan boglanishni tavsiya qiling""",
)

user_chats = {}


def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Katalog (Instagram)", url=INSTAGRAM_URL)],
        [InlineKeyboardButton("Menejer bilan boglanish", callback_data="manager")],
        [InlineKeyboardButton("Savol berish", callback_data="ask")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_chats[user.id] = model.start_chat(history=[])
    await update.message.reply_text(
        f"G-Style botiga xush kelibsiz, {user.first_name}!\n\n"
        "Zamonaviy krossovkalar dokoniga xush kelibsiz.\n"
        "Sizga qanday yordam bera olaman?\n\n"
        "Quyidagi menyudan tanlang yoki savol yozing:",
        reply_markup=get_main_keyboard(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "manager":
        await query.message.reply_text(
            f"Menejer bilan boglanish\n\nTelegram: {MANAGER_USERNAME}\n\nIsh vaqti: 9:00 - 21:00"
        )
    elif query.data == "ask":
        await query.message.reply_text("Savolingizni yozing - javob beraman!")


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
            f"Texnik xato. Menejer bilan boganing: {MANAGER_USERNAME}",
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
