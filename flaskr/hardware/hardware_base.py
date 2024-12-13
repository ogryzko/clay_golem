import json
from abc import ABC, abstractmethod
from typing import List, Dict, Type, TypeVar, Union
from datetime import datetime
from flaskr.drivers import pwm_lamp_driver, esp32_relay_driver
from flaskr.utils.logger import Logger
T = TypeVar('T', bound='Hardware')

# Base class for hardware objects
class Hardware(ABC):
    def __init__(
            self,
            device_id: int,
            name: str,
            params: Dict = None
            ):

        self.params = params  if params else dict()  # i dont want to check it for now
        self.params["device_id"] = device_id
        self.params["name"] = name
        # logger
        self.logger = Logger.get_logger(f"{self.__class__.__name__}_{self.params["name"]}")
        # Default hardware cannot keep any commands or data, so initialize as empty dicts
        self.commands = dict()
        self.data = dict()

    def to_dict(self) -> Dict:
        """Convert object to a dictionary representation."""
        return {
            "params": self.params,
            "commands": self.commands,
            "data": self.data,
        }

    @abstractmethod
    def run_command(self, command, arg):    # ONLY ONE ARG for simplicity?
        """
        I do not want to make some remote call, it is very unsafe
        So lets every child class implements it itself manually
        """
        pass

    @abstractmethod
    def get_info(self):
        """
        get info about state of that particular device
        """
        pass

    # @classmethod
    # def from_dict(cls: Type[T], data: Dict) -> T:
    #     """Create object from a dictionary representation."""
    #     # TODO: change to be more abstract
    #     instance = cls(
    #         device_id=data["params"]["device_id"],
    #         name=data["params"]["name"],
    #         last_time_active=data["params"]["last_time_active"],
    #         dev_type=data["params"]["dev_type"],
    #         uptime_sec=data["params"]["uptime_sec"],
    #         description=data["params"]["description"],
    #         status=data["params"]["status"],
    #         last_error=data["params"]["last_error"],
    #     )
    #     instance.commands = data.get("commands", {})
    #     instance.data = data.get("data", {})
    #     return instance

    def __repr__(self):
        return f"({json.dumps(self.to_dict(), indent=2)})"



# Derived classes for specific hardware


class HardwareRelay(Hardware):
    """
    Relay high-level wrapper
    """
    def __init__(
        self,
        device_id: int, # unique id of device, to use in database and data handling
        name: str,      # human-readable name like "Relay 1"
        ip_addr: str,   # ip addr of real remote relay
        channel: int,   # channel on that relay, must be in [0-3] range
        last_time_active: str = None,
        type: str = "relay",
        uptime_sec: int = 0,
        description: str = "",
        status: str = "unknown",
        last_error: str = "",
    ):

        # Initialize the base class
        super().__init__(
            device_id=device_id,
            name=name
        )
        # it is params, and user cannot change them directly
        self.params["last_time_active"] = last_time_active
        self.params["type"]= type
        self.params["uptime_sec"] = uptime_sec
        self.params["description"] = description
        self.params["status"] = status
        self.params["last_error"] = last_error
        self.params["ip_addr"] = ip_addr
        self.params["channel"] = channel
        # let`s set commands to represent them on web-page
        self.commands["set_on"] = None
        self.commands["set_off"] = None
        self.commands["reset"] = None
        # let`s set data param represent it on web-page
        self.data["state"] = 0
        self.driver = esp32_relay_driver.ESP32RelayDriver(
            host=self.params["ip_addr"],
            name=self.params["name"]
        )

    def run_command(self, command, **args):
        """
        Manually check available commands for remote procedure calling from web page
        """
        if command == "set_on":
            self.turn_on()
        if command == "set_off":
            self.turn_off()
        if command == "reset":
            self.reset()

    def get_info(self):
        """

        """
        info_dict = self.driver.get_info()
        if info_dict:
            ch_id = "ch" + str(self.params["channel"])  # to get str like ch0 or ch2
            self.data["state"] = info_dict[ch_id]
            self.params["uptime"] = info_dict["uptime"]
            self.params["last_time_active"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            self.params["status"] = "ok"
            return True
        else:
            return False

    def _set_relay_state(self, state: int):
        """
        private method to set relay state
        """
        try:
            # Устанавливаем состояние реле через драйвер
            success, message = self.driver.set_relay_state(self.params["channel"], state)
            
            if success:
                self.data["state"] = state  # Обновляем состояние в данных
                self.params["status"] = "ok"  # Устанавливаем статус как "ok"
                self.logger.info(f"{self.params['name']} (ID: {self.params['device_id']}) is now {'ON' if state else 'OFF'}.")
            else:
                self.logger.warning(f"Failed to set relay state: {message}")
                self.params["status"] = "Error"  # Устанавливаем статус как "Error"
                self.params["last_error"] = message  # Сохраняем сообщение об ошибке
        except Exception as e:
            #TODO а так вообще бывает?
            self.logger.error(e)
            self.params["last_error"] = str(e)
            self.params["status"] = "Error"  # Устанавливаем статус как "Error"


    def turn_on(self):
        """Turning relay on."""
        self.logger.info("turning relay ON")
        self._set_relay_state(1)


    def turn_off(self):
        """Turning relay off."""
        self.logger.info("turning relay OFF")
        self._set_relay_state(0)

    def reset(self):
        """Сбросить устройство"""
        self.logger.info("Resetting relay...")
        success = self.driver.reset_device()  # Вызов метода reset_device у драйвера

        if success:
            self.params["status"] = "ok"  # Устанавливаем статус как "ok"
            self.logger.info(f"{self.params['name']} (ID: {self.params['device_id']}) has been reset successfully.")
        else:
            self.params["status"] = "Error"  # Устанавливаем статус как "Error"
            self.logger.warning(f"Failed to reset {self.params['name']} (ID: {self.params['device_id']}).")

class HardwareLamp(Hardware):
    """
    PWM lamp high-level wrapper
    """
    def __init__(
            self,
            device_id: int,  # unique id of device, to use in database and data handling
            name: str,  # human-readable name like "Lamp 1"
            ip_addr: str,  # ip addr of real remote Lamp
            last_time_active: str = None,
            type: str = "lamp",
            uptime_sec: int = 0,
            description: str = "",
            status: str = "unknown",
            last_error: str = ""
    ):
        # Initialize the base class
        super().__init__(
            device_id=device_id,
            name=name,
        )
        # params will not change
        self.params["last_time_active"] = last_time_active
        self.params["type"] = type
        self.params["uptime_sec"] = uptime_sec
        self.params["description"] = description
        self.params["status"] = status
        self.params["last_error"] = last_error
        self.params["ip_addr"] = ip_addr
        # let`s set data to represent it on web-page
        # data will change everytime
        self.data["red_pwm_1"] = 0
        self.data["red_pwm_2"] = 0
        self.data["white_pwm_1"] = 0
        self.data["white_pwm_2"] = 0
        self.data["driver_temp"] = 0
        # let`s set commands to represent them on web-page
        self.commands["set_red"] = "int"
        self.commands["set_white"] = "int"
        self.commands["reset"] = None
        # let`s create driver that makes http requests to real device
        self.driver = pwm_lamp_driver.PWMLampDriver(
            host = self.params["ip_addr"],
            name = self.params["name"]
        )

    def run_command(self, command, arg):
        """
        Manually check available commands for remote procedure calling from web page
        """
        if command == "set_red":
            self.set_red(arg)
        if command == "set_white":
            self.set_white(arg)
        if command == "reset":
            self.reset()

    def set_red(self, pwm: int):
        self.data["red_pwm_1"] = pwm
        self.data["red_pwm_2"] = pwm
        self.params["status"] = "ok" # must be "ok", any other statuses will be parsed as error
        self.logger.info(f"Set red: {pwm}")
        #self.driver.set_pwm(,pwm)

    def set_white(self, pwm: int):
        self.data["white_pwm_1"] = pwm
        self.data["white_pwm_2"] = pwm
        self.params["status"] = "ok"  # must be "ok", any other statuses will be parsed as error
        self.logger.info(f"Set white: {pwm}")
        pass

    def reset(self):
        self.logger.info(f"Reset lamp")
        
        try:
            success, message = self.driver.reset_device() 
            if success:
                self.params["status"] = "ok"  # Устанавливаем статус как "ok"
                self.logger.info(f"{self.params['name']} (ID: {self.params['device_id']}) has been reset successfully.")
            else:
                self.params["status"] = "Error"  # Устанавливаем статус как "Error"
                self.logger.warning(f"Failed to reset {self.params['name']} (ID: {self.params['device_id']}). Message: {message}")
                self.params["last_error"] = message
        except Exception as e:
                self.logger.error(e)
                self.params["last_error"] = str(e)
                self.params["status"] = "Error"  # Устанавливаем статус как "Error"


    def get_info(self):
        """

        """
        info_dict = self.driver.get_info()
        if info_dict:
            self.data["white_pwm_1"] = info_dict["ch0_pwm"]
            self.data["white_pwm_2"] = info_dict["ch1_pwm"]
            self.data["red_pwm_1"] = info_dict["ch2_pwm"]
            self.data["red_pwm_2"] = info_dict["ch3_pwm"]
            self.data["driver_temp"] = info_dict["pcb_temp"]
            self.params["uptime"] = info_dict["uptime"]
            self.params["last_time_active"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            self.params["status"] = "ok"
            return True
        else:
            self.params["status"] = "error"
            return False


class HardwareSBA5(Hardware):
    pass

class HardwareHumSensor(Hardware):
    pass

class HardwareTempSensor(Hardware):
    pass


if __name__ == "__main__":
    pass