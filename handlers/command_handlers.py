import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils.phrase_manager import PhraseManager
from config import ADMINS

# Инициализация менеджера фраз
phrase_manager = PhraseManager()

# Состояния для диалога
WAITING_FOR_ADD_PHRASE = 1
WAITING_FOR_REMOVE_PHRASE = 2

def is_admin(user):
    """Проверка, является ли пользователь администратором"""
    if not user or not user.username:
        return False
    return user.username in ADMINS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    if update.effective_chat.type == 'private':
        if is_admin(user):
            await update.message.reply_text(
"""
Привет! Я бот для модерации чатов.
Пока я умею только удалять сообщения, содержащие запрещенные фразы, слова и буквосочетания.
Но я быстро учусь и скоро появятся новые функции ;)

Доступные команды:
/add_phrase - Добавить запрещенную фразу
/remove_phrase - Удалить запрещенную фразу из списка
/list_phrases - Показать список всех запрещенных фраз
/help - Помощь
/cancel - Отмена текущей операции
"""
            )
        else:
            await update.message.reply_text(
                "Привет! У Вас нет прав для управления этим ботом.\n"
                "По всем вопросам Вы можете обратиться к @Natalya_Sunshine."
            )            

async def add_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление новой запрещенной фразы"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    await update.message.reply_text("📝 Пожалуйста, введите фразу для добавления в список запрещенных:")
    context.user_data['state'] = WAITING_FOR_ADD_PHRASE
        
async def remove_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление запрещенной фразы из списка"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    await update.message.reply_text("🗑 Пожалуйста, введите фразу для удаления из списка запрещенных:")
    context.user_data['state'] = WAITING_FOR_REMOVE_PHRASE

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений для диалога добавления/удаления фраз"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    state = context.user_data.get('state')
    phrase = update.message.text.lower()
    
    if state == WAITING_FOR_ADD_PHRASE:
        if phrase_manager.add_phrase(phrase):
            await update.message.reply_text(f"✅ Фраза \"{phrase}\" добавлена в список запрещенных.")
            logging.info(f"Админ {user.username} добавил фразу: {phrase}")
        else:
            await update.message.reply_text(f"❌ Фраза \"{phrase}\" уже есть в списке.")
        context.user_data['state'] = None
        
    elif state == WAITING_FOR_REMOVE_PHRASE:
        if phrase_manager.remove_phrase(phrase):
            await update.message.reply_text(f"✅ Фраза \"{phrase}\" удалена из списка запрещенных.")
            logging.info(f"Админ {user.username} удалил фразу: {phrase}")
        else:
            await update.message.reply_text(f"❌ Фраза \"{phrase}\" не найдена в списке.")
        context.user_data['state'] = None
        
async def list_phrases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение списка всех запрещенных фраз"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    phrases = phrase_manager.get_phrases()
    
    if not phrases:
        await update.message.reply_text("📝 Список запрещенных фраз пуст.")
    else:
        phrases_text = "📝 Список запрещенных фраз:\n\n" + "\n".join([f"• {phrase}" for phrase in phrases])
        await update.message.reply_text(phrases_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    user = update.effective_user
    
    if is_admin(user):
        await update.message.reply_text(
            "Доступные команды:\n\n"
            "/add_phrase - Добавить запрещенную фразу\n"
            "/remove_phrase - Удалить запрещенную фразу из списка\n"
            "/list_phrases - Показать список всех запрещенных фраз\n"
            "/help - Помощь\n"
            "/cancel - Отмена текущей операции\n"
        )
    else:
        await update.message.reply_text("У Вас нет прав для управления этим ботом.\n")
    await update.message.reply_text("По всем вопросам Вы можете обратиться к @Natalya_Sunshine.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена текущей операции"""
    if 'state' in context.user_data:
        context.user_data['state'] = None
        await update.message.reply_text("❌ Операция отменена.")
    
# Функция для получения обработчиков команд
def get_command_handlers():
    private_filter = filters.ChatType.PRIVATE
    return [
        CommandHandler("start", start, filters=private_filter),
        CommandHandler("add_phrase", add_phrase, filters=private_filter),
        CommandHandler("remove_phrase", remove_phrase, filters=private_filter),
        CommandHandler("list_phrases", list_phrases, filters=private_filter),
        CommandHandler("help", help_command, filters=private_filter),
        CommandHandler("cancel", cancel, filters=filters.ChatType.PRIVATE),
        MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_text),
    ]
