import logging
import os
from datetime import datetime

class Logger:
    @staticmethod
    def get_logger(name: str):
        logger = logging.getLogger(name)
        if not logger.handlers:
            # Создаем директорию logs если её нет
            logs_dir = 'logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Создаем файловый обработчик
            log_file = os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y-%m-%d")}.log')
            file_handler = logging.FileHandler(log_file)
            
            # Создаем консольный обработчик
            console_handler = logging.StreamHandler()
            
            # Настраиваем форматирование
            formatter = logging.Formatter('%(levelname)s-%(asctime)s-%(name)s-%(message)s',
                                       datefmt='%Y-%m-%d-%H:%M:%S')
            
            # Применяем форматирование к обоим обработчикам
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Добавляем оба обработчика
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(logging.INFO)
            
        return logger 