import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.phrase_manager import PhraseManager

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет сообщения с запрещенными фразами"""
    # Создаем новый экземпляр менеджера фраз для каждого сообщения
    phrase_manager = PhraseManager()
    
    message = update.effective_message
    text = message.text or message.caption
    
    if text:
        text_lower = text.lower()
        for phrase in phrase_manager.get_phrases():
            if phrase in text_lower:
                try:
                    await message.delete()
                    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
                    logging.info(f"Удалил сообщение от {username}: {text[:50]}...")
                    
                except Exception as e:
                    logging.error(f"Ошибка удаления: {e}")
                break
