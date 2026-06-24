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
    system_instruction="""Siz G-Style do'konining AI yordamchisisiz.
G-Style — Toshkentdagi zamonaviy krossovka do'koni.
Qoidalar:
- Faqat o'zbek va rus tillarida javob bering
- Mijoz qaysi tilda yozsa, shu tilda javob bering
- Krossovkalar, yetkazib berish, o'lchamlar haqida savollar
- Har doim do'stona va professional bo'ling
- Katalogni ko'rish uchun Instagram profilimizni tavsiya qiling
- Narx yoki mavjudlik so'ralsa, menejer bilan bog'lanishni tavsiya qiling
- Nike, Adidas, New Balance va boshqa brendlar haqida ma'lumot bera olasiz""",
)

user_chats: dict = {}


def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛍 Katalog (Instagram)", url=INSTAGRAM_URL)],
        [InlineKeyboardButton("👨‍💼 Menejer bilan bog'lanish", callback_data="manager")],
        [InlineKeyboardButton("💬 Savol berish", callback_data="ask")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_chats[user.id] = model.start_chat(history=[])
    await update.message.reply_text(
        f"👟 *G-Style botiga xush kelibsiz, {user.first_name}!*\n\n"
        "Zamonaviy krossovkalar do'koniga xush kelibsiz.\n"
        "Sizga qanday yordam bera olaman?\n\n"
        "👇 Quyidagi menyudan tanlang yoki savol yozing:",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "manager":
        await query.message.reply_text(
            f"👨‍💼 *Menejer bilan bog'lanish*\n\nTelegram: {MANAGER_USERNAME}\n\nIsh vaqti: 9:00 — 21:00",
            parse_mode="Markdown",
        )
    elif query.data == "ask":
        await query.message.reply_text("✍️ Savolingizni yozing — javob beraman!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = user_chats[user_id].send_message(update.message.text)
        await update.message.reply_text(response.text, reply_markup=get_main_keyboard())
    except Exception as e:
