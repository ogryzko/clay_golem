import json
from typing import List, Dict, Type, TypeVar, Union
from flaskr.hardware.hardware_base import Hardware, HardwareRelay, HardwareLamp, HardwareSBA5, HardwareHumSensor, HardwareTempSensor

class HardwareCollection:
    """

    """

    def __init__(self):
        self.hardware: Dict[int, Hardware] = {}

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


    def store_hardware_description_to_db(self):
        """ Store dict representation directly to sqlite db"""
        pass

    def load_hardware_description_from_db(self):
        """ Load dict representation directly from sqlite db"""
        pass

    # def to_json(self) -> str:
    #     """Convert the collection to a JSON string."""
    #     return json.dumps([hw.to_dict() for hw in self.hardware.values()])

    def to_list(self) -> list:
        devices_list = [hw.to_dict() for hw in self.hardware.values()]
        # it is old format, that needed for web page to generate info about devices
        # print(devices_list)
        return devices_list

    # def from_json(self, json_str: str):
    #     """Update the collection from a JSON string."""
    #     data = json.loads(json_str)
    #     for item in data:
    #         hw_class = globals()[item['type']]  # Resolve class by name
    #         hardware = hw_class.from_dict(item)
    #         self.add(hardware)

    # def __repr__(self):
    #     return f"HardwareCollection({list(self.hardware.values())})"