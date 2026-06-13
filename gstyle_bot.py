import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "BU_YERGA_TOKENINGIZNI_QOYING"

logging.basicConfig(level=logging.INFO)

# Conversation states
ASK_NAME, ASK_PHONE, ASK_MODEL, ASK_SIZE = range(4)

CATALOG = """
👟 *G.Style.uz Katalog*

*Nike:*
• Air Force 1 — 850,000 so'm
• Air Max 270 — 950,000 so'm
• Dunk Low — 900,000 so'm

*Adidas:*
• Samba — 800,000 so'm
• Gazelle — 750,000 so'm
• NMD R1 — 950,000 so'm

*New Balance:*
• 574 — 700,000 so'm
• 990 — 1,100,000 so'm

*Jordan:*
• Air Jordan 1 Retro — 1,200,000 so'm
• Jordan 4 — 1,300,000 so'm

📦 Yetkazib berish: Toshkent bo'ylab bepul!
"""

INFO = """
📍 *G.Style.uz haqida*

📌 Manzil: Toshkent sh., (Instagram: @G.style.uz)
⏰ Ish vaqti: 10:00 — 21:00 (har kuni)
📱 Instagram: @G.style.uz
📞 Telefon: +998 90 000 00 00

✅ 100% original krossovkalar
🚚 Toshkent bo'ylab yetkazib berish
💳 Naqd va karta orqali to'lov
"""

def main_menu():
    keyboard = [
        [InlineKeyboardButton("👟 Katalog va narxlar", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Buyurtma berish", callback_data="order")],
        [InlineKeyboardButton("📍 Manzil va ish vaqti", callback_data="info")],
        [InlineKeyboardButton("❓ Savol berish", callback_data="question")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👟 *G.Style.uz ga xush kelibsiz!*\n\nOriginal krossovkalar do'koni\n\nQuyidagilardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        await query.message.reply_text(CATALOG, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bosh menyu", callback_data="menu")]]))

    elif query.data == "info":
        await query.message.reply_text(INFO, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bosh menyu", callback_data="menu")]]))

    elif query.data == "order":
        await query.message.reply_text("📝 *Buyurtma berish*\n\nIsmingizni kiriting:", parse_mode="Markdown")
        return ASK_NAME

    elif query.data == "question":
        await query.message.reply_text("❓ Savolingizni yozing, tez orada javob beramiz!\n\n(Yozib yuboring 👇)")

    elif query.data == "menu":
        await query.message.reply_text("Bosh menyu:", reply_markup=main_menu())

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Rahmat, {update.message.text}! 📞 Telefon raqamingizni kiriting:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("👟 Qaysi model krossovka kerak? (masalan: Nike Air Force 1):")
    return ASK_MODEL

async def ask_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['model'] = update.message.text
    await update.message.reply_text("📏 O'lcham (razmer) kiriting (masalan: 42):")
    return ASK_SIZE

async def ask_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['size'] = update.message.text
    name = context.user_data['name']
    phone = context.user_data['phone']
    model = context.user_data['model']
    size = context.user_data['size']

    summary = f"""✅ *Buyurtmangiz qabul qilindi!*

👤 Ism: {name}
📞 Telefon: {phone}
👟 Model: {model}
📏 O'lcham: {size}

Tez orada siz bilan bog'lanamiz! 🙏"""

    await update.message.reply_text(summary, parse_mode="Markdown", reply_markup=main_menu())

    # Admin ga xabar yuborish (o'zingizning Telegram ID ni qo'ying)
    # await context.bot.send_message(chat_id=ADMIN_ID, text=f"Yangi buyurtma!\n{summary}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.", reply_markup=main_menu())
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Savolingiz uchun rahmat! Tez orada javob beramiz 🙏\n\nYoki bosh menyuga qayting:",
        reply_markup=main_menu()
    )

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
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
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
