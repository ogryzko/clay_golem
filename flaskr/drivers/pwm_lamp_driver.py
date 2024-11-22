import requests
import json
from typing import Optional, Tuple, Dict, Union

class PWMLampDriver:
    def __init__(self, host: str):
        """
        Инициализация драйвера PWM-лампы
        Args:
            host (str): IP-адрес или hostname устройства (например, '10.10.0.7' или 'esp32_pwm_lamp_0.local')
        """
        self.base_url = f"http://{host}"
    
    def get_info(self) -> Optional[Dict]:
        """Получение информации о состоянии всех каналов и температуре"""
        try:
            response = requests.get(f"{self.base_url}/info")
            return response.json()
        except Exception as e:
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
        if not (0 <= channel <= 3) or not (0 <= duty <= 100):
            return False, "Некорректные параметры"
            
        headers = {'Content-Type': 'application/json'}
        data = {"channel": channel, "duty": duty}
        
        try:
            response = requests.post(
                f"{self.base_url}/pwm",
                headers=headers,
                data=json.dumps(data)
            )
            
            result = response.text.strip()
            
            if "SUCCESS" in result:
                return True, result
            return False, result
            
        except Exception as e:
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
            response: requests.Response = requests.post(
                f"{self.base_url}/reset",
                headers=headers,
                data='force_reset'
            )
            result: str = response.text.strip()
            
            if "force reset command" in result.lower() and "rebooting" in result.lower():
                return True, result
            return False, result
            
        except Exception as e:
            return False, f"Ошибка запроса: {str(e)}" 