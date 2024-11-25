import requests
import json
from typing import Union, Tuple, Dict, Any

class ESP32RelayDriver:
    """
    Driver for ESP32 relay based on API from https://github.com/houseofbigseals/esp32_relay
    """
    def __init__(self, host, name="relay_1"):
        """
        Args:
            host (str): IP address or hostname of ESP32 (example: '10.10.0.7' or 'esp32_relay_4.local')
            name (str): Name identifier for the relay
        """
        self.host = host
        self.name = name
        self.base_url = f"http://{host}"
        self.SENSOR_ERROR_VALUE = -255  # Значение, означающее что датчик не установлен или сломан

    def get_info(self):
        """Get state of all relays and sensors"""
        response = requests.get(f"{self.base_url}/info")
        if response.status_code == 200:
            return response.json()
        return None

    def get_sensor_value(self, sensor_type):
        """
        Get specific sensor value
        Args:
            sensor_type (str): One of: ext_temp, ext_hum, int_temp, int_hum, roots_temp
        """
        response = requests.get(f"{self.base_url}/{sensor_type}")
        if response.status_code == 200:
            value = float(response.text)
            if value == self.SENSOR_ERROR_VALUE:
                return None
            return value
        return None

    def set_relay_state(self, channel: Union[str, int], state: Union[bool, int]) -> Tuple[bool, str]:
        """
        Set relay state
        Args:
            channel (Union[str, int]): Channel name or number (ch1, ch2, etc. or 1, 2)
            state (Union[bool, int]): State to set (True/False or 1/0)
        Returns:
            Tuple[bool, str]: (success, message)
        """
        headers: Dict[str, str] = {'Content-Type': 'application/json'}
        
        # Преобразуем bool в int если нужно
        state_value = 1 if state in [True, 1] else 0
        
        data: Dict[str, Any] = {
            "channel": channel,
            "state": state_value
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/relay",
                headers=headers,
                data=json.dumps(data)
            )
            
            result: str = response.text.strip()
            
            # Проверяем все возможные ошибки
            error_messages = [
                "ERROR Failed to parse JSON",
                "ERROR Invalid channel type",
                "ERROR Invalid state type",
                "ERROR invalid params!"
            ]
            
            if any(error in result for error in error_messages):
                return False, result
            
            if "SUCCESS" in result:
                return True, result
            
            return False, f"Неожиданный ответ: {result}"
            
        except Exception as e:
            return False, f"Ошибка запроса: {str(e)}"

    def reset_device(self):
        """Force reset the device"""
        headers = {'Content-Type': 'text/html'}
        response = requests.post(
            f"{self.base_url}/reset",
            headers=headers,
            data='force_reset'
        )
        return response.status_code == 200