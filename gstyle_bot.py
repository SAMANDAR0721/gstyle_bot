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
MANZIL_URL = "https://yandex.ru/maps/-/CTU5JImT"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""You are AI assistant of G-Style sneaker store.
Store address: Chirchiq bazar, TSUM, 2-proxod.
We sell Nike, Adidas, New Balance and other brand sneakers.
Working hours: 9:00 - 21:00.
Manager: @SamandarGayratovic

IMPORTANT: Always respond in the same language the user writes in.
- Uzbek message -> Uzbek reply
- Russian message -> Russian reply
- English message -> English reply

You can help with: sneaker models, sizes, brands, availability.
For price or order:
