import json
import redis
from typing import List, Dict, Type, TypeVar, Union
from flaskr.hardware.hardware_base import Hardware, HardwareRelay, HardwareLamp, HardwareSBA5, HardwareHumSensor, HardwareTempSensor
from flask import current_app, g
from flaskr.db import get_db, get_data_db
from flaskr.utils.logger import Logger

class HardwareCollection:
    """

    """

    def __init__(self, app, hardware_dict: Dict[int, Hardware]=None):
        """
        NOTE:
        we cannot load descriptions from redis if devices were not loaded to dict before !
        but we can add or remove device in work process
        """
        with app.app_context():
            self.hardware: Dict[int, Hardware] = hardware_dict if hardware_dict else {}
            self.redis_client = get_db()
            self.logger = Logger.get_logger(f"{self.__class__.__name__}")
            # check if there is already working devices or we are first instance, ie if redis is empty
            if self.redis_client.set("global_hardware_lock:", "locked", nx=True, ex=10):
                # we set lock here for 10 seconds, because all flask instances must start in one time
                # so after 10 second some stupid instance can update all operational data to default values
                # that`s the life
                # so
                self.logger.info("we are the first flask instance and we need to store our hardware params")
                self.store_hardware_description_to_redis()
            else:
                self.logger.info("we are NOT the first flask instance,so just load data from db")
                self.load_hardware_description_from_redis()

    def add(self, hardware: Hardware):
        """Add a hardware object to the collection."""
        self.hardware[hardware.params["device_id"]] = hardware

    def length(self):
        """ Returns number of devices in collection"""
        return len(self.hardware)

    def remove(self, hardware_id: int):
        """Remove a hardware object from the collection."""
        self.hardware.pop(hardware_id, None)

    def get(self, hardware_id: int) -> Union[Hardware, None]:
        """Retrieve a hardware object by its ID."""
        # print(self.hardware[hardware_id].to_dict())
        return self.hardware[hardware_id]

    def __iter__(self):
        """Allow iteration over the hardware objects."""
        return iter(self.hardware.values())

    def update_all_hardware_info(self):
        """
         update info for all devices and store to redis
         that method can be long, so call it in different thread
        """
        for h_id in self.hardware:
            self.hardware[h_id].get_info()
            self.logger.debug(self.hardware[h_id].to_dict())
            self.store_one_device_update_to_redis(h_id)
        #self.store_hardware_description_to_redis()

    def store_one_device_update_to_redis(self, dev_id):
        """ just store state of device with dev_id to redis"""
        key_prefix = f"device:{dev_id}"
        # Save each dictionary as a JSON string in Redis
        self.redis_client.set(f"{key_prefix}:params", json.dumps(self.hardware[dev_id].params))
        self.redis_client.set(f"{key_prefix}:commands", json.dumps(self.hardware[dev_id].commands))
        self.redis_client.set(f"{key_prefix}:data", json.dumps(self.hardware[dev_id].data))

    def store_hardware_description_to_redis(self):
        """ Store dict representation directly to redis db for whole collection"""
        for h_id in self.hardware:
            # if self.hardware[h_id].get_info():
            key_prefix = f"device:{h_id}"
            # Save each dictionary as a JSON string in Redis
            self.redis_client.set(f"{key_prefix}:params", json.dumps(self.hardware[h_id].params))
            self.redis_client.set(f"{key_prefix}:commands", json.dumps(self.hardware[h_id].commands))
            self.redis_client.set(f"{key_prefix}:data", json.dumps(self.hardware[h_id].data))

    def load_hardware_description_from_redis(self):
        """ Load dict representation directly from redis db"""
        # TODO: we can generate devices from unique prefixes in redis
        for h_id in self.hardware:
            key_prefix = f"device:{h_id}"

            # Load each dictionary from Redis
            params_json = self.redis_client.get(f"{key_prefix}:params")
            commands_json = self.redis_client.get(f"{key_prefix}:commands")
            data_json = self.redis_client.get(f"{key_prefix}:data")

            if params_json:
                self.hardware[h_id].params = json.loads(params_json)
            if commands_json:
                self.hardware[h_id].commands = json.loads(commands_json)
            if data_json:
                self.hardware[h_id].data = json.loads(data_json)

        return self.to_list()

    # def to_json(self) -> str:
    #     """Convert the collection to a JSON string."""
    #     return json.dumps([hw.to_dict() for hw in self.hardware.values()])

    def to_list(self) -> list:
        devices_list = [hw.to_dict() for hw in self.hardware.values()]
        # it is old format, that needed for web page to generate info about devices
        # print(devices_list)
        return devices_list



if __name__ == "__main__":
    # Initialize Redis client
    pass
    # def from_json(self, json_str: str):
    #     """Update the collection from a JSON string."""
    #     data = json.loads(json_str)
    #     for item in data:
    #         hw_class = globals()[item['type']]  # Resolve class by name
    #         hardware = hw_class.from_dict(item)
    #         self.add(hardware)

    # def __repr__(self):
    #     return f"HardwareCollection({list(self.hardware.values())})"