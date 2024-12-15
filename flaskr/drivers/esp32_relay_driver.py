import requests
import json
from typing import Union, Tuple, Dict, Any
from flaskr.drivers.base_driver import BaseDriver

class ESP32RelayDriver(BaseDriver):
    """
    Driver for ESP32 relay based on API from https://github.com/houseofbigseals/esp32_relay
    """
    def __init__(self, host, name="relay_1"):
        """
        Args:
            host (str): IP address or hostname of ESP32 (example: '10.10.0.7' or 'esp32_relay_4.local')
            name (str): Name identifier for the relay
        """
        super().__init__(host, name)
        self.SENSOR_ERROR_VALUE = -255  # Значение, означающее что датчик не установлен или сломан

    def get_info(self):
        """Get state of all relays and sensors"""
        try:
            response = requests.get(f"{self.base_url}/info", timeout=5)
            self.logger.debug(f"Got info response: {response.json()}")
            if response.status_code == 200:
                return response.json()
                # it returns giant dict, see https://github.com/houseofbigseals/esp32_relay
            self.logger.warning(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error getting info: {str(e)}", exc_info=True)
        return None

    def get_sensor_value(self, sensor_type):
        """
        Get specific sensor value
        Args:
            sensor_type (str): One of: ext_temp, ext_hum, int_temp, int_hum, roots_temp
        """
        try:
            response = requests.get(f"{self.base_url}/{sensor_type}", timeout=5)
            self.logger.debug(f"Got sensor value response: {response.text}")
            if response.status_code == 200:
                value = float(response.text)
                if value == self.SENSOR_ERROR_VALUE:
                    self.logger.warning(f"Sensor error value received for {sensor_type}")
                    return None
                return value
            self.logger.warning(f"Unexpected status code for sensor {sensor_type}: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error getting sensor value for {sensor_type}: {str(e)}", exc_info=True)
        return None

    def set_relay_state(self, channel: int, state: Union[bool, int]) -> Tuple[bool, str]:
        """
        Set relay state
        Args:
            channel (int): Channel number (must be an integer)
            state (Union[bool, int]): State to set (True/False or 1/0)
        Returns:
            Tuple[bool, str]: (success, message)
        """
        headers: Dict[str, str] = {'Content-Type': 'application/json'}
        
        # Проверка, что channel является целым числом
        if not isinstance(channel, int):
            self.logger.error(f"Invalid channel type: {type(channel)}. Must be an integer.")
            raise ValueError("Channel must be an integer.")
        
        # Преобразуем bool в int если нужно
        if isinstance(state, bool):
            state_value = 1 if state else 0
        elif isinstance(state, int) and state in [0, 1]:
            state_value = state
        else:
            self.logger.error(f"Invalid state value: {state}. Must be 0 or 1.", exc_info=True)
            raise ValueError("State must be either 0 or 1.")
        
        data: Dict[str, Any] = {
            "channel": channel,
            "state": state_value
        }
        
        try:
            self.logger.debug(f"Setting relay state: channel={channel}, state={state_value}")
            response = requests.post(
                f"{self.base_url}/relay",
                headers=headers,
                data=json.dumps(data),
                timeout = 5
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
                self.logger.warning(f"Error setting relay state: {result}")
                return False, result
            
            if "SUCCESS" in result:
                self.logger.info(f"Successfully set relay state: channel={channel}, state={state_value}")
                return True, result
            
            self.logger.warning(f"Unexpected response when setting relay state: {result}")
            return False, f"Неожиданный ответ: {result}"
            
        except Exception as e:
            self.logger.error(f"Error setting relay state: {str(e)}", exc_info=True)
            return False, f"Ошибка запроса: {str(e)}"

    def reset_device(self):
        """Force reset the device"""
        headers = {'Content-Type': 'text/html'}
        try:
            self.logger.info("Attempting to reset the device")
            response = requests.post(
                f"{self.base_url}/reset",
                headers=headers,
                data='force_reset',
                timeout=5
            )
            if response.status_code == 200:
                self.logger.info("Device reset successful")
                return True
            self.logger.warning(f"Device reset failed with status code: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error during device reset: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    lamp1 = ESP32RelayDriver("esp32_relay_5.local", name="relay5")  # ("10.10.0.12")
    # print(lamp1.get_info())
    # print(lamp1.set_relay_state(0, 9))
