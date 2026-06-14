import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

TOKEN = os.environ.get("TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

ASK_NAME, ASK_PHONE, ASK_MODEL, ASK_SIZE = range(4)

CATALOG = (
    "👟 *G.Style.uz Katalog*\n\n"
    "*Nike:*\n• Air Force 1\n• Air Max 270\n• Dunk Low\n\n"
    "*Adidas:*\n• Samba\n• Gazelle\n• NMD R1\n\n"
    "*New Balance:*\n• 574\n• 990\n\n"
    "*Jordan:*\n• Air Jordan 1 Retro\n• Jordan 4\n\n"
    "Narx va mavjudlik uchun buyurtma bering!"
)

INFO = (
    "📍 *G.Style.uz haqida*\n\n"
    "📌 Instagram: @G.style.uz\n"
    "⏰ Ish vaqti: 10:00 - 21:00\n"
    "📞 Telefon: +998 87 901 85 85\n\n"
    "✅ 100% original krossovkalar\n"
    "🚚 Toshkent boylab yetkazib berish"
)

def main_menu():
    keyboard = [
        [InlineKeyboardButton("👟 Katalog", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order")],
        [InlineKeyboardButton("📍 Manzil va ish vaqti", callback_data="info")],
        [InlineKeyboardButton("❓ Savol berish", callback_data="question")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👟 *G.Style.uz ga xush kelibsiz!*\n\nOriginal krossovkalar dokoni\n\nQuyidagilardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        await query.message.reply_text(
            CATALOG, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]]))
    elif query.data == "info":
        await query.message.reply_text(
            INFO, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]]))
    elif query.data == "order":
        await query.message.reply_text("Ismingizni kiriting:")
        return ASK_NAME
    elif query.data == "question":
        await query.message.reply_text("Savolingizni yozing, tez orada javob beramiz!")
    elif query.data == "menu":
        await query.message.reply_text("Bosh menyu:", reply_markup=main_menu())

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Qaysi model krossovka kerak?")
    return ASK_MODEL

async def ask_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["model"] = update.message.text
    await update.message.reply_text("Razmer kiriting (masalan: 42):")
    return ASK_SIZE

async def ask_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["size"] = update.message.text
    msg = (
        "✅ *Buyurtma qabul qilindi!*\n\n"
        f"👤 Ism: {context.user_data['name']}\n"
        f"📞 Telefon: {context.user_data['phone']}\n"
        f"👟 Model: {context.user_data['model']}\n"
        f"📏 Razmer: {context.user_data['size']}\n\n"
        "Tez orada boglanamiz!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.", reply_markup=main_menu())
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Savolingiz uchun rahmat! Tez orada javob beramiz.", reply_markup=main_menu())

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^order$")],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_model)],
            ASK_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_size)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    print("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
