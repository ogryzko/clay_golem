import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

class Logger:
    @staticmethod
    def get_logger(name: str):
        logger = logging.getLogger(name)
        if not logger.handlers:
            # Указываем статичный путь к директории логов
            logs_dir = '/opt/clay/clay_golem/logs'
            # Проверяем, есть ли права на запись в указанную директорию
            if not os.access(logs_dir, os.W_OK):
                logs_dir = './logs'  # Переход на локальную директорию logs
                if not os.path.exists(logs_dir):
                    os.makedirs(logs_dir)

            # Создаем обработчик для ошибок
            error_handler = TimedRotatingFileHandler(
                os.path.join(logs_dir, f'error_{datetime.now().strftime("%Y-%m-%d")}.log'),
                when='midnight',
                interval=1,
                backupCount=7  # Хранить 7 дней логов
            )
            error_handler.setLevel(logging.ERROR)
            error_formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s',
                                                 datefmt='%Y-%m-%d %H:%M:%S')
            error_handler.setFormatter(error_formatter)
            logger.addHandler(error_handler)

            # Создаем обработчик для предупреждений
            warning_handler = TimedRotatingFileHandler(
                os.path.join(logs_dir, f'warning_{datetime.now().strftime("%Y-%m-%d")}.log'),
                when='midnight',
                interval=1,
                backupCount=7
            )
            warning_handler.setLevel(logging.WARNING)
            warning_handler.setFormatter(error_formatter)  # Можно использовать тот же формат
            logger.addHandler(warning_handler)

            # Создаем обработчик для информационных сообщений
            info_handler = TimedRotatingFileHandler(
                os.path.join(logs_dir, f'info_{datetime.now().strftime("%Y-%m-%d")}.log'),
                when='midnight',
                interval=1,
                backupCount=7
            )
            info_handler.setLevel(logging.INFO)
            info_handler.setFormatter(error_formatter)
            logger.addHandler(info_handler)

            # Создаем обработчик для отладочной информации
            debug_handler = TimedRotatingFileHandler(
                os.path.join(logs_dir, f'debug_{datetime.now().strftime("%Y-%m-%d")}.log'),
                when='midnight',
                interval=1,
                backupCount=7
            )
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(error_formatter)
            logger.addHandler(debug_handler)

            # Устанавливаем уровень логирования на DEBUG, чтобы все сообщения записывались
            logger.setLevel(logging.DEBUG)

        return logger 