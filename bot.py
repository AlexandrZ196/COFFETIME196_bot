import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- Конфигурация ---
# Токен берется из переменных окружения Bothost
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# ID чата администратора
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '-1001234567890')  # Замените на ваш

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
TYPING_FEEDBACK, TYPING_SUGGESTION = range(2)

# --- Клавиатуры ---
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("Оставить отзыв ✍️"), KeyboardButton("Пожелание/Идея 💡")],
        [KeyboardButton("Поделиться фото 📸"), KeyboardButton("Новинки 🆕")],
        [KeyboardButton("Обратная связь 📞")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_text = (
        f"Привет, {user.first_name}! 👋\n"
        f"Добро пожаловать в нашу кофейню!\n"
        "Чем могу помочь? Выбери опцию ниже:"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())

async def show_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_text = (
        "☕️ <b>Наши новинки:</b>\n\n"
        "• <b>Кленовый Раф</b> - нежный и сладкий!\n"
        "• <b>Сироп 'Соленая карамель'</b> - теперь в вашем кофе!\n"
        "• <b>Веганское миндальное печенье</b> - новое пополнение!\n\n"
        "Следи за обновлениями! 😉"
    )
    await update.message.reply_text(news_text, parse_mode='HTML')

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        "<b>Обратная связь:</b>\n\n"
        "Если нужна помощь с заказом или срочный вопрос:\n\n"
        "📞 <b>Телефон:</b> +7 (XXX) XXX-XX-XX\n"
        "✉️ <b>Почта:</b> coffee@mycoffee.ru\n"
        "🏠 <b>Адрес:</b> ул. Кофейная, д. 1"
    )
    await update.message.reply_text(contact_text, parse_mode='HTML')

# --- Обработка сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Оставить отзыв ✍️":
        await update.message.reply_text(
            "Пожалуйста, напиши свой отзыв. Мы очень ценим твое мнение!",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Отмена 🔙")]], resize_keyboard=True)
        )
        return TYPING_FEEDBACK

    elif text == "Пожелание/Идея 💡":
        await update.message.reply_text(
            "Расскажи, что мы можем улучшить? Жду твою идею!",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Отмена 🔙")]], resize_keyboard=True)
        )
        return TYPING_SUGGESTION

    elif text == "Поделиться фото 📸":
        await update.message.reply_text(
            "Присылай свое фото! Мы с радостью опубликуем самые интересные фото у себя в сторис! 📸",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Отмена 🔙")]], resize_keyboard=True)
        )

    elif text == "Новинки 🆕":
        await show_news(update, context)

    elif text == "Обратная связь 📞":
        await show_contacts(update, context)

    elif text == "Отмена 🔙":
        await update.message.reply_text("Главное меню:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END

    else:
        await forward_to_admin(update, context, message_type="📨 Прочее сообщение")
        await update.message.reply_text("Спасибо за сообщение! Мы его получили.", reply_markup=main_menu_keyboard())

    return ConversationHandler.END

async def received_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_feedback = update.message.text
    user = update.message.from_user

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📝 <b>Новый отзыв</b> от @{user.username or 'N/A'} (ID: {user.id}):\n\n{user_feedback}",
        parse_mode='HTML'
    )

    await update.message.reply_text("Большое спасибо за твой отзыв! 💚", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def received_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_suggestion = update.message.text
    user = update.message.from_user

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"💡 <b>Новое пожелание/идея</b> от @{user.username or 'N/A'} (ID: {user.id}):\n\n{user_suggestion}",
        parse_mode='HTML'
    )

    await update.message.reply_text("Супер! Спасибо за идею! Мы обязательно её рассмотрим. 🔥", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    caption = update.message.caption or "Без описания"

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_file.file_id,
        caption=f"📸 <b>Новое фото</b> от @{user.username or 'N/A'} (ID: {user.id}):\n{caption}",
        parse_mode='HTML'
    )

    await update.message.reply_text("Вау, крутое фото! Спасибо, что делишься с нами! 🤩", reply_markup=main_menu_keyboard())

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, message_type="Сообщение"):
    user = update.message.from_user
    text = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"{message_type} от @{user.username or 'N/A'} (ID: {user.id}):\n\n{text}",
        parse_mode='HTML'
    )

# Команда для получения ID чата (уберите после настройки)
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"ID этого чата: <code>{chat_id}</code>", parse_mode='HTML')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        ],
        states={
            TYPING_FEEDBACK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_feedback)
            ],
            TYPING_SUGGESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_suggestion)
            ],
        },
        fallbacks=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("^Отмена 🔙$"), start)
        ],
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chat_id", get_chat_id))  # Удалите после настройки
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчик ошибок
    application.add_error_handler(error)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()