import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- Конфигурация ---
BOT_TOKEN = os.environ.get('8452776500:AAH29GOiUiKTLjK31KyB8c_NUilHlem3jNU')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# Проверка обязательных переменных
if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise ValueError("Не установлены BOT_TOKEN или ADMIN_CHAT_ID в переменных окружения")
/chat_id
# Конвертируем ADMIN_CHAT_ID в int
try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
except ValueError:
    raise ValueError("ADMIN_CHAT_ID должен быть числом")

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
    return ConversationHandler.END

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

# --- Обработка главного меню ---
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            "Присылай свое фото! Мы с радостью опубликуем самые интересные фото у себя в сторис! 📸"
        )

    elif text == "Новинки 🆕":
        await show_news(update, context)

    elif text == "Обратная связь 📞":
        await show_contacts(update, context)

    return ConversationHandler.END

# --- Обработка отзывов и пожеланий ---
async def received_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_feedback = update.message.text
    user = update.message.from_user

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📝 <b>Новый отзыв</b> от @{user.username or user.first_name} (ID: {user.id}):\n\n{user_feedback}",
            parse_mode='HTML'
        )
        await update.message.reply_text("Большое спасибо за твой отзыв! 💚", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка отправки отзыва: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.", reply_markup=main_menu_keyboard())
    
    return ConversationHandler.END

async def received_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_suggestion = update.message.text
    user = update.message.from_user

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"💡 <b>Новое пожелание/идея</b> от @{user.username or user.first_name} (ID: {user.id}):\n\n{user_suggestion}",
            parse_mode='HTML'
        )
        await update.message.reply_text("Супер! Спасибо за идею! Мы обязательно её рассмотрим. 🔥", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка отправки пожелания: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.", reply_markup=main_menu_keyboard())
    
    return ConversationHandler.END

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    caption = update.message.caption or "Без описания"

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=photo_file.file_id,
            caption=f"📸 <b>Новое фото</b> от @{user.username or user.first_name} (ID: {user.id}):\n{caption}",
            parse_mode='HTML'
        )
        await update.message.reply_text("Вау, крутое фото! Спасибо, что делишься с нами! 🤩", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        await update.message.reply_text("Произошла ошибка при отправке фото. Попробуйте позже.", reply_markup=main_menu_keyboard())

# Команда для получения ID чата
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"ID этого чата: <code>{chat_id}</code>", parse_mode='HTML')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню:", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        # Обработчик диалога для отзывов и пожеланий
        conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
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
                CommandHandler('cancel', cancel),
                CommandHandler('start', start),
                MessageHandler(filters.Regex('^Отмена 🔙$'), cancel)
            ],
        )

        # Добавляем обработчики в правильном порядке
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("chat_id", get_chat_id))
        application.add_handler(CommandHandler("cancel", cancel))
        application.add_handler(conv_handler)
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # Обработчик ошибок
        application.add_error_handler(error)

        # Запускаем бота
        logger.info("Бот запущен...")
        application.run_polling()

    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == '__main__':
    main()
