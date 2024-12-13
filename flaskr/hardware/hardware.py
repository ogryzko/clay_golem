import sys
sys.path.insert(0, "/opt/clay/clay_golem")
print(sys.path)
from flaskr.hardware.hardware_base import HardwareLamp, HardwareRelay
from flaskr.hardware.hardware_collection import HardwareCollection
from flask import current_app, g
from typing import Any


# global_hardware_collection = HardwareCollection()
# empty hardware container


def init_hardware(app):
    """
    """
    print("INIT HARDWARE")


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
    # is dependency injection is cool?
    with app.app_context():
        current_app.global_hardware_collection = HardwareCollection(
            app,
            hardware_dict={
                100: lamp0,
                101: relay0,
                102: relay1,
                103: relay2,
                104: relay3
            }
        )

        # g.global_hardware_collection.add(lamp0)
        # g.global_hardware_collection.add(relay0)
        # g.global_hardware_collection.add(relay1)
        # g.global_hardware_collection.add(relay2)
        # g.global_hardware_collection.add(relay3)

        # first time store that user-defined hardware collection to redis
        current_app.global_hardware_collection.store_hardware_description_to_redis()



def handle_command(device_id: int, command: str, arg: Any):
    """ method to handle user command from web page for selected device"""
    # global global_hardware_collection
    if current_app.global_hardware_collection.length() == 0:
        raise AssertionError("Hardware has not initialized yet!")

    else:
        device = current_app.global_hardware_collection.get(int(device_id))
        device.run_command(command, arg=arg)
        current_app.global_hardware_collection.store_one_device_update_to_redis(device_id)
        return True

def get_device_states():
    # global global_hardware_collection
    if current_app.global_hardware_collection.length() == 0:
        raise AssertionError("Hardware has not initialized yet!")
    else:
        # print(current_app.global_hardware_collection.load_hardware_description_from_redis())
        return current_app.global_hardware_collection.load_hardware_description_from_redis()



if __name__ == "__main__":
    # mock call like from real server creation process
    init_hardware()
    # handle_command(1, "")
