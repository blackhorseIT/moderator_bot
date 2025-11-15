import logging
from config import setup_logging, TOKEN
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from handlers.message_handlers import delete_message
from handlers.command_handlers import get_command_handlers

def main():
    """Запуск бота"""
    try:
        # Настройка логирования
        setup_logging()
        
        # Создаем приложение
        application = Application.builder().token(TOKEN).build()

        # Добавляем обработчики команд
        command_handlers = get_command_handlers()
        for handler in command_handlers:
            application.add_handler(handler)
            logging.info(f"Добавлен обработчик команды: {handler}")
        
        # Добавляем обработчик сообщений для групп
        application.add_handler(MessageHandler(
            filters.TEXT | filters.CAPTION,
            delete_message
        ))
        
        print("Бот запущен...")
        print("Для остановки нажмите Ctrl+C")
        
        # Запускаем бота
        application.run_polling(
            drop_pending_updates=True,  # Игнорировать накопившиеся обновления
            allowed_updates=['message', 'edited_message', 'callback_query']
        )
        
    except Exception as e:
        logging.error(f"Ошибка запуска бота: {e}")
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == '__main__':
    main()
