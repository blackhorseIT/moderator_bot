import logging
import io
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden
from utils.phrase_manager import PhraseManager
from utils.chat_actions import delete_message, ban_user
from config import TESSERACT_PATH

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    print("Предупреждение: Tesseract не найден. Распознавание текста с картинок отключено.")

# Инициализация менеджеров фраз
text_phrase_manager = PhraseManager("text")
image_phrase_manager = PhraseManager("image")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщения в группах"""
    message = update.effective_message
    user = message.from_user
    chat = update.effective_chat
    
    # Логируем тип сообщения для отладки
    message_type = "текст"
    if message.photo:
        message_type = "фото"
    elif message.document:
        message_type = "документ"
    elif message.video:
        message_type = "видео"
    elif message.audio:
        message_type = "аудио"
    elif message.voice:
        message_type = "голосовое"
    elif message.sticker:
        message_type = "стикер"
    elif message.animation:
        message_type = "анимация"
    
    logging.info(f"Получено сообщение типа: {message_type}")
    
    # Проверяем права пользователя
    try:
        member = await chat.get_member(user.id)
        if member.status in ['administrator', 'creator']:
            return
    except BadRequest as e:
        if "User not found" in str(e) or "Chat not found" in str(e):
            logging.warning(f"Пользователь {user.id} или чат {chat.id} не найден")
        else:
            logging.error(f"Ошибка проверки прав пользователя {user.id}: {e}")
        return
    except Forbidden as e:
        logging.error(f"Доступ запрещен при проверке прав пользователя {user.id}: {e}")
        return
    except Exception as e:
        logging.error(f"Неизвестная ошибка при проверки прав пользователя {user.id}: {e}")
        return

    # Проверка изображений
    is_image = await is_image_message(message)
    
    if is_image:
        logging.info(f"Обнаружено изображение, начинаем проверку OCR")
        banned_found = await check_image_for_banned_words(message, context)
        if banned_found:
            await handle_restricted_message(message, chat, user, context, "изображение")

    # Проверка текстовых сообщений
    text = message.text or message.caption
    
    if text:
        text_lower = text.lower()
        for phrase in text_phrase_manager.get_phrases():
            if phrase.lower() in text_lower:
                await handle_restricted_message(message, chat, user, context, "текст")
                return

async def is_image_message(message):
    """Определяет, является ли сообщение изображением"""
    # Проверяем фото
    if message.photo:
        logging.info(f"Сообщение содержит фото: {len(message.photo)} элементов")
        return True
    
    # Проверяем документ с изображением
    if message.document:
        mime_type = getattr(message.document, 'mime_type', '')
        file_name = getattr(message.document, 'file_name', '').lower()
        
        logging.info(f"Документ: MIME-type={mime_type}, file_name={file_name}")
        
        # Проверяем MIME-type
        if mime_type and mime_type.startswith('image/'):
            return True
            
        # Проверяем расширение файла (на случай, если MIME-type не установлен)
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff')
        if file_name and any(file_name.endswith(ext) for ext in image_extensions):
            return True
    
    # Проверяем, есть ли медиагруппа (альбом изображений)
    if message.media_group_id:
        logging.info(f"Сообщение является частью медиагруппы: {message.media_group_id}")
        # Проверяем, есть ли фото в медиагруппе
        if message.photo:
            return True
    
    return False

async def check_image_for_banned_words(message, context):
    """Проверяет изображение на наличие запрещенных слов с помощью OCR"""
    try:
        # Получаем файл изображения
        if message.photo:
            # Берем самое большое изображение (последний элемент в списке)
            file_id = message.photo[-1].file_id
            logging.info(f"Обрабатываем фото с file_id: {file_id}")
        elif message.document:
            file_id = message.document.file_id
            logging.info(f"Обрабатываем документ с file_id: {file_id}")
        else:
            logging.warning("Неизвестный тип изображения")
            return False
            
        file = await context.bot.get_file(file_id)
        logging.info(f"Получили файл: {file.file_path}")
        
        # Скачиваем изображение в память
        image_bytes = io.BytesIO()
        await file.download_to_memory(out=image_bytes)
        image_bytes.seek(0)
        
        # Открываем изображение с PIL
        try:
            image = Image.open(image_bytes)
            logging.info(f"Изображение открыто: {image.size}, формат: {image.format}")
        except Exception as e:
            logging.error(f"Ошибка открытия изображения: {e}")
            return False
        
        # Используем tesseract для распознавания текста
        try:
            extracted_text = pytesseract.image_to_string(image, lang='rus+eng')
            logging.info(f"Распознанный текст с изображения: {extracted_text}")
        except Exception as e:
            logging.error(f"Ошибка OCR: {e}")
            return False
            
        extracted_text_lower = extracted_text.lower()
        
        # Проверяем каждую строку из запрещенных слов для изображений
        banned_image_phrases = image_phrase_manager.get_phrases()
        logging.info(f"Запрещенные фразы для изображений: {banned_image_phrases}")
        
        for phrase_line in banned_image_phrases:
            # Разбиваем строку на отдельные слова
            words_in_phrase = phrase_line.lower().split()
            
            # Пропускаем пустые строки
            if not words_in_phrase:
                continue
                
            # Проверяем, что все слова из строки присутствуют в распознанном тексте
            if all(word in extracted_text_lower for word in words_in_phrase):
                logging.info(f"Найдено запрещенное сочетание слов в изображении: {phrase_line}")
                return True
                
        logging.info("Запрещенных сочетаний слов в изображении не найдено")
        return False
        
    except Exception as e:
        logging.error(f"Ошибка при обработке изображения: {e}")
        return False

async def handle_restricted_message(message, chat, user, context, content_type="контент"):
    """Обрабатывает сообщение с запрещенной фразой"""
    username = f"@{user.username}" if user.username else user.first_name
    
    # Баним пользователя
    ban_success = await ban_user(chat, user)
    
    # Удаляем сообщение
    delete_success = await delete_message(message, chat, user)
    
    # Логируем результат
    log_message = f"Обнаружен запрещенный {content_type} от {username}"
    
    if delete_success and ban_success:
        logging.info(f"{log_message} - полностью обработан (бан + удаление)")
    else:
        logging.warning(f"{log_message} - частично обработан (удаление: {delete_success}, бан: {ban_success})")
