import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils.phrase_manager import PhraseManager
from config import ADMINS

# Инициализация менеджеров фраз
text_phrase_manager = PhraseManager("text")
image_phrase_manager = PhraseManager("image")

# Состояния для диалога
WAITING_FOR_ADD_PHRASE = 1
WAITING_FOR_REMOVE_PHRASE = 2
WAITING_FOR_ADD_IMAGE_WORD = 3
WAITING_FOR_REMOVE_IMAGE_WORD = 4

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
/add_image_word - Добавить запрещенное слово или сочетание слов для картинок
/remove_image_word - Удалить запрещенное слово или сочетание слов для картинок
/list_phrases - Показать все запрещенные фразы и слова
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

async def add_image_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление новых запрещенных слов для картинок"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    await update.message.reply_text("🖼 Пожалуйста, введите слово или сочетание слов для добавления в список запрещенных на картинках:")
    context.user_data['state'] = WAITING_FOR_ADD_IMAGE_WORD

async def remove_image_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление запрещенных слов для картинок"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    await update.message.reply_text("🗑 Пожалуйста, введите слово или сочетание слов для удаления из списка запрещенных на картинках:")
    context.user_data['state'] = WAITING_FOR_REMOVE_IMAGE_WORD

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений для диалога добавления/удаления фраз"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    state = context.user_data.get('state')
    text = update.message.text.strip()
    
    if state == WAITING_FOR_ADD_PHRASE:
        if text_phrase_manager.add_phrase(text):
            await update.message.reply_text(f"✅ Фраза \"{text}\" добавлена в список запрещенных.")
            logging.info(f"Админ {user.username} добавил фразу: {text}")
        else:
            await update.message.reply_text(f"❌ Фраза \"{text}\" уже есть в списке.")
        context.user_data['state'] = None
        
    elif state == WAITING_FOR_REMOVE_PHRASE:
        if text_phrase_manager.remove_phrase(text):
            await update.message.reply_text(f"✅ Фраза \"{text}\" удалена из списка запрещенных.")
            logging.info(f"Админ {user.username} удалил фразу: {text}")
        else:
            await update.message.reply_text(f"❌ Фраза \"{text}\" не найдена в списке.")
        context.user_data['state'] = None
        
    elif state == WAITING_FOR_ADD_IMAGE_WORD:
        if image_phrase_manager.add_phrase(text):
            await update.message.reply_text(f"✅ Слово(-а) \"{text}\" добавлено(-ы) в список запрещенных на картинках.")
            logging.info(f"Админ {user.username} добавил слово(-а) для картинок: {text}")
        else:
            await update.message.reply_text(f"❌ Слово(-а) \"{text}\" уже есть в списке запрещенных на картинках.")
        context.user_data['state'] = None
        
    elif state == WAITING_FOR_REMOVE_IMAGE_WORD:
        if image_phrase_manager.remove_phrase(text):
            await update.message.reply_text(f"✅ Слово(-а) \"{text}\" удалено(-ы) из списка запрещенных на картинках.")
            logging.info(f"Админ {user.username} удалил слово(-а) для картинок: {text}")
        else:
            await update.message.reply_text(f"❌ Слово(-а) \"{text}\" не найдено в списке запрещенных на картинках.")
        context.user_data['state'] = None
        
async def list_phrases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение списка всех запрещенных фраз и слов"""
    user = update.effective_user
    
    if not is_admin(user):
        await update.message.reply_text("❌ У Вас нет прав для выполнения этой команды.")
        return
        
    text_phrases = text_phrase_manager.get_phrases()
    image_words = image_phrase_manager.get_phrases()
    
    if not text_phrases and not image_words:
        await update.message.reply_text("📝 Списки запрещенных фраз и слов пусты.")
        return
    
    response = "📝 Списки запрещенных фраз и слов:\n\n"
    
    if text_phrases:
        response += "🔤 Запрещенные текстовые фразы:\n"
        response += "\n".join([f"• {phrase}" for phrase in text_phrases]) + "\n\n"
    
    if image_words:
        response += "🖼 Запрещенные слова на картинках:\n"
        response += "\n".join([f"• {word}" for word in image_words])
    
    # Разбиваем сообщение если оно слишком длинное
    if len(response) > 4096:
        parts = []
        current_part = ""
        
        lines = response.split('\n')
        for line in lines:
            if len(current_part) + len(line) + 1 < 4096:
                current_part += line + '\n'
            else:
                parts.append(current_part)
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part)
        
        for part in parts:
            await update.message.reply_text(part)
    else:
        await update.message.reply_text(response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    user = update.effective_user
    
    if is_admin(user):
        await update.message.reply_text(
            "Доступные команды:\n\n"
            "/add_phrase - Добавить запрещенную фразу\n"
            "/remove_phrase - Удалить запрещенную фразу из списка\n"
            "/add_image_word - Добавить запрещенное слово или сочетание слов для картинок\n"
            "/remove_image_word - Удалить запрещенное слово или сочетание слов для картинок\n"
            "/list_phrases - Показать все запрещенные фразы и слова\n"
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
        CommandHandler("add_image_word", add_image_word, filters=private_filter),
        CommandHandler("remove_image_word", remove_image_word, filters=private_filter),
        CommandHandler("list_phrases", list_phrases, filters=private_filter),
        CommandHandler("help", help_command, filters=private_filter),
        CommandHandler("cancel", cancel, filters=filters.ChatType.PRIVATE),
        MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_text),
    ]
