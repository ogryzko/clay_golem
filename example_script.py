from flaskr.drivers.esp32_relay_driver import ESP32RelayDriver
from flaskr.drivers.pwm_lamp_driver import PWMLampDriver
import json
import time
from flaskr.utils.logger import Logger

def main():
    logger = Logger.get_logger(__name__)

    relay = ESP32RelayDriver(host="10.10.0.5")
    
    try:
        # Получаем информацию об устройстве
        info = relay.get_info()
        if info is not None:
            logger.info("Информация о устройстве:")
            logger.info(json.dumps(info, indent=2, ensure_ascii=False))
        
        # Получаем значения конкретных датчиков
        sensors = ['pcb_temp', 'ext_temp']
        for sensor in sensors:
            value = relay.get_sensor_value(sensor)
            logger.info(f"{sensor}: {value}")
        
        # Переключаем реле
        success, message = relay.set_relay_state(1, 1)
        if success:
            logger.info("Реле успешно переключено: %s", message)
        else:
            logger.error("Ошибка переключения реле: %s", message)
        
    except Exception as e:
        logger.error("Произошла ошибка: %s", str(e))

    pwm_driver = PWMLampDriver(host="10.10.0.7")

    try:
        # Получаем информацию о лампе
        pwm_info = pwm_driver.get_info()
        if pwm_info:
            logger.info("Информация о лампе:")
            logger.info(json.dumps(pwm_info, indent=2, ensure_ascii=False))
        else:
            logger.warning("Не удалось получить информацию о лампе.")

        # Устанавливаем скважность для канала 0
        success, message = pwm_driver.set_pwm(channel=0, duty=75)
        if success:
            logger.info("Успешно установлена скважность на канале 0: %s", message)
        else:
            logger.error("Ошибка при установке скважности на канале 0: %s", message)

        # Устанавливаем скважность для канала 1
        success, message = pwm_driver.set_pwm(channel=1, duty=50)
        if success:
            logger.info("Успешно установлена скважность на канале 1: %s", message)
        else:
            logger.error("Ошибка при установке скважности на канале 1: %s", message)

        # Перезагружаем устройство
        success, message = pwm_driver.reset_device()
        if success:
            logger.info("Устройство успешно перезагружено.")
        else:
            logger.error("Ошибка при перезагрузке устройства: %s", message)

    except Exception as e:
        logger.error("Произошла ошибка с PWM-лампой: %s", str(e))

if __name__ == "__main__":
    main() 