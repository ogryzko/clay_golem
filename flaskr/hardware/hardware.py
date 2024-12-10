import sys
sys.path.insert(0, "/opt/clay/clay_golem")
print(sys.path)
from flaskr.hardware.hardware_base import HardwareLamp, HardwareRelay
from flaskr.hardware.hardware_collection import HardwareCollection
from typing import Any


global_hardware_collection = HardwareCollection()
# empty hardware container


def init_hardware():
    """
    """
    print("INIT HARDWARE")
    global global_hardware_collection
    # TODO: read data from redis
    # TODO: if there are no data in redis, then create that data in default way and set in redis "hardware lock" on

    # for now just stubs
    lamp0 = HardwareLamp(
        device_id=100,
        name="Lamp_0",
        ip_addr="10.10.0.14"
    )
    relay0 = HardwareRelay(
        device_id=101,
        name="Relay_0",
        channel=0,
        ip_addr="10.10.0.18"
    )
    relay1 = HardwareRelay(
        device_id=102,
        name="Relay_1",
        channel=1,
        ip_addr="10.10.0.18"
    )
    relay2 = HardwareRelay(
        device_id=103,
        name="Relay_2",
        channel=2,
        ip_addr="10.10.0.18"
    )
    relay3 = HardwareRelay(
        device_id=104,
        name="Relay_3",
        channel=3,
        ip_addr="10.10.0.18"
    )
    global_hardware_collection.add(lamp0)
    global_hardware_collection.add(relay0)
    global_hardware_collection.add(relay1)
    global_hardware_collection.add(relay2)
    global_hardware_collection.add(relay3)
    print(global_hardware_collection.to_list())
    print(global_hardware_collection.get(101))
    print(global_hardware_collection.get(100))
    print(global_hardware_collection.hardware)


def handle_command(device_id: int, command: str, arg: Any):
    """ method to handle user command from web page for selected device"""
    global global_hardware_collection
    if global_hardware_collection.length() == 0:
        raise AssertionError("Hardware has not initialized yet!")

    else:
        device = global_hardware_collection.get(int(device_id))
        device.run_command(command, arg=arg)
        return True

def get_device_states():
    global global_hardware_collection
    if global_hardware_collection.length() == 0:
        raise AssertionError("Hardware has not initialized yet!")
    else:
        # TODO: in reality we will load it from redis
        # but now it is static and store in ram
        return global_hardware_collection.to_list()



if __name__ == "__main__":
    # mock call like from real server creation process
    init_hardware()
    handle_command(1, "")
