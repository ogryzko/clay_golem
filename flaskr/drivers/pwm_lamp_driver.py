import requests
import json
from typing import Optional, Tuple, Dict, Union
from flaskr.drivers.base_driver import BaseDriver

class PWMLampDriver(BaseDriver):
    def __init__(self, host: str, name: str = "unnamed"):
        """
        Инициализация драйвера PWM-лампы
        Args:
            host (str): IP-адрес или hostname устройства (например, '10.10.0.7' или 'esp32_pwm_lamp_0.local')
        """
        super().__init__(host, name)
    
    def get_info(self) -> Optional[Dict]:
        """Получение информации о состоянии всех каналов и температуре"""
        try:
            response = requests.get(f"{self.base_url}/info", timeout=5)
            self.logger.debug(f"Got info response: {response.json()}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting info: {str(e)}", exc_info=True)
            return None
    
    def set_pwm(self, channel: int, duty: int) -> Tuple[bool, str]:
        """
        Установка скважности ШИМ для канала
        Args:
            channel (int): номер канала (0-3)
            duty (int): скважность ШИМ (0-100)
        Returns:
            tuple: (успех операции, текст ответа)
        """
        # Проверка, что channel является целым числом
        if not isinstance(channel, int):
            self.logger.error("Invalid channel type: %s. Channel must be an integer.", type(channel))
            raise ValueError("Channel must be an integer.")
        
        # Проверка, что duty является целым числом
        if not isinstance(duty, int):
            self.logger.error("Invalid duty type: %s. Duty must be an integer.", type(duty))
            raise ValueError("Duty must be an integer.")
        
        # Проверка диапазона значений
        if not (0 <= channel <= 3):
            self.logger.error("Invalid channel value: %d. Channel must be between 0 and 3.", channel)
            raise ValueError("Channel must be between 0 and 3.")
        
        if not (0 <= duty <= 100):
            self.logger.error("Invalid duty value: %d. Duty must be between 0 and 100.", duty)
            raise ValueError("Duty must be between 0 and 100.")
        
        headers = {'Content-Type': 'application/json'}
        data = {"channel": channel, "duty": duty}
        
        try:
            self.logger.debug(f"Setting PWM: channel={channel}, duty={duty}")
            response = requests.post(
                f"{self.base_url}/pwm",
                headers=headers,
                data=json.dumps(data),
                timeout=5
            )
            
            result = response.text.strip()
            
            if "SUCCESS" in result:
                self.logger.info(f"Successfully set PWM: channel={channel}, duty={duty}")
                return True, result
            self.logger.warning(f"Failed to set PWM: {result}")
            return False, result
            
        except Exception as e:
            self.logger.error(f"Error setting PWM: {str(e)}", exc_info=True)
            return False, f"Ошибка запроса: {str(e)}"
    
    def reset_device(self) -> Tuple[bool, str]:
        """
        Перезагрузка устройства
        Returns:
            Tuple[bool, str]: (успех операции, текст ответа)
                success: True если устройство перезагружается, False в противном случае
                message: Сообщение от устройства
        """
        headers: Dict[str, str] = {'Content-Type': 'text/html'}
        try:
            self.logger.info("Attempting device reset")
            response: requests.Response = requests.post(
                f"{self.base_url}/reset",
                headers=headers,
                data='force_reset',
                timeout=5
            )
            result: str = response.text.strip()
            
            if "force reset command" in result.lower() and "rebooting" in result.lower():
                self.logger.info("Device reset successful")
                return True, result
            self.logger.warning(f"Device reset failed: {result}")
            return False, result
            
        except Exception as e:
            self.logger.error(f"Error during device reset: {str(e)}", exc_info=True)
            return False, f"Ошибка запроса: {str(e)}" 


if __name__ == "__main__":
    lamp1 = PWMLampDriver("10.10.0.14")
    print(lamp1.get_info())
    print(lamp1.set_pwm(0, 0))
    print(lamp1.set_pwm(1, 0))

