import logging
from telegram.error import BadRequest, Forbidden

async def delete_message(message, chat, user) -> bool:
    """Удаляет сообщение пользователя"""
    username = f"@{user.username}" if user.username else user.first_name
    
    try:
        await message.delete()
        logging.info(f"Удалил сообщение от {username} в чате {chat.id}")
        return True
        
    except BadRequest as e:
        if "Message to delete not found" in str(e):
            logging.warning(f"Сообщение уже удалено: {username}")
            return True  # Считаем успехом, так как цель достигнута
        elif "Not enough rights" in str(e):
            logging.error(f"Бот не имеет прав на удаление сообщений в чате {chat.id}")
        else:
            logging.error(f"Ошибка удаления сообщения от {username}: {e}")
        return False
    
    except Forbidden as e:
        logging.error(f"Доступ запрещен при удалении сообщения: {e}")
        return False
    
    except Exception as e:
        logging.error(f"Неизвестная ошибка при удалении сообщения: {e}")
        return False

async def ban_user(chat, user) -> bool:
    """Банит пользователя"""
    try:
        await chat.ban_member(
            user_id=user.id,
            revoke_messages=False
        )
        logging.info(f"Забанил пользователя {user.id} в чате {chat.id}")
        return True
        
    except BadRequest as e:
        error_message = str(e).lower()
        if "user is an administrator" in error_message:
            logging.warning(f"Попытка забанить администратора {user.id}")
        elif "user_not_participant" in error_message:
            logging.warning(f"Пользователь {user.id} уже вышел из чата")
        elif "not enough rights" in error_message or "chat_admin_required" in error_message:
            logging.error(f"Бот не имеет прав на бан в чате {chat.id}. Убедитесь, что бот является администратором с правом бана пользователей.")
        else:
            logging.error(f"Ошибка бана пользователя {user.id}: {e}")
        return False
    
    except Forbidden as e:
        logging.error(f"Доступ запрещен при бане пользователя {user.id}: {e}")
        return False
    
    except Exception as e:
        logging.error(f"Неизвестная ошибка при бане пользователя {user.id}: {e}")
        return False

