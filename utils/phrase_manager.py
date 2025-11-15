import os
from config import PHRASES_FILE

class PhraseManager:
    def __init__(self):
        self.phrases_file = PHRASES_FILE
        self.banned_phrases = self.load_banned_phrases()

    def load_banned_phrases(self):
        """Загрузка запрещенных фраз из файла"""        
        with open(self.phrases_file, 'r', encoding='utf-8') as f:
            phrases = [line.strip() for line in f if line.strip()]
            return phrases

    def save_banned_phrases(self, phrases):
        """Сохранение фраз в файл"""
        with open(self.phrases_file, 'w', encoding='utf-8') as f:
            for phrase in phrases:
                f.write(phrase + '\n')
        self.banned_phrases = phrases

    def add_phrase(self, phrase):
        """Добавление новой фразы"""
        normalized_phrase = phrase.strip()
        # Проверяем без учета регистра
        if not any(normalized_phrase.lower() == existing.lower() 
                   for existing in self.banned_phrases):
            self.banned_phrases.append(normalized_phrase)
            self.save_banned_phrases(self.banned_phrases)
            return True
        return False

    def remove_phrase(self, phrase):
        """Удаление фразы"""
        if phrase in self.banned_phrases:
            self.banned_phrases.remove(phrase)
            self.save_banned_phrases(self.banned_phrases)
            return True  # Фраза успешно удалена
        return False  # Фразы не было в списке

    def get_phrases(self):
        """Получение списка запрещенных фраз"""
        return self.banned_phrases.copy()
