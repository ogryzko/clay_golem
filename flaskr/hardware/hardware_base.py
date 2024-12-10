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

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> T:
        """Create object from a dictionary representation."""
        # TODO: change to be more abstract
        instance = cls(
            device_id=data["params"]["device_id"],
            name=data["params"]["name"],
            last_time_active=data["params"]["last_time_active"],
            dev_type=data["params"]["dev_type"],
            uptime_sec=data["params"]["uptime_sec"],
            description=data["params"]["description"],
            status=data["params"]["status"],
            last_error=data["params"]["last_error"],
        )
        instance.commands = data.get("commands", {})
        instance.data = data.get("data", {})
        return instance

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
        self.params["last_time_active"] = last_time_active
        self.params["type"] = type
        self.params["uptime_sec"] = uptime_sec
        self.params["description"] = description
        self.params["status"] = status
        self.params["last_error"] = last_error
        self.params["ip_addr"] = ip_addr
        self.params["channel"] = channel
        # let`s set commands to represent them on web-page
        self.commands["set_on"] = None
        self.commands["set_off"] = None
        # let`s set data param represent it on web-page
        self.data["state"] = "OFF"
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

    def _set_relay_state(self, state: int):
        """
        private method to set relay state
        """
        try:
            # TODO: here we really make http request to device using low-level driver
            #self.driver.set_relay_state(self.params["channel"], 1)
            #self.params["status"] = "on"
            #print(f"{self.params['name']} (ID: {self.params['device_id']}) is now ON.")
            pass  # it is stubbed for now
            self.data["state"] = "ON" if state else "OFF"
            self.params["status"] = "ok"  # must be "ok", any other statuses will be parsed as error
            return
        except Exception as e:
            self.logger.error(e)
            self.params["last_error"] = str(e)
            self.params["status"] = "Error"
            pass


    def turn_on(self):
        """Turning relay on."""
        self.logger.info("turning relay ON")
        self._set_relay_state(1)


    def turn_off(self):
        """Turning relay off."""
        self.logger.info("turning relay OFF")
        self._set_relay_state(0)

    def reset(self):
        """Software way to reset device"""
        self.logger.info("Reset relay")
        pass

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
        self.params["last_time_active"] = last_time_active
        self.params["type"] = type
        self.params["uptime_sec"] = uptime_sec
        self.params["description"] = description
        self.params["status"] = status
        self.params["last_error"] = last_error
        self.params["ip_addr"] = ip_addr
        # let`s set data param represent it on web-page
        self.data["red_pwm"] = 0
        self.data["white_pwm"] = 0
        # let`s set commands to represent them on web-page
        self.commands["set_red"] = "int"
        self.commands["set_white"] = "int"
        self.commands["reset"] = None

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
        self.data["red_pwm"] = pwm
        self.params["status"] = "ok" # must be "ok", any other statuses will be parsed as error
        self.logger.info(f"Set red: {pwm}")
        pass

    def set_white(self, pwm: int):
        self.data["white_pwm"] = pwm
        self.params["status"] = "ok"  # must be "ok", any other statuses will be parsed as error
        self.logger.info(f"Set white: {pwm}")
        pass

    def reset(self):
        self.logger.info(f"Reset lamp")
        pass


class HardwareSBA5(Hardware):
    pass

class HardwareHumSensor(Hardware):
    pass

class HardwareTempSensor(Hardware):
    pass


if __name__ == "__main__":
    pass