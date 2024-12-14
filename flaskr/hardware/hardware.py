import sys
sys.path.insert(0, "/opt/clay/clay_golem")
print(sys.path)
from flaskr.hardware.hardware_base import HardwareLamp, HardwareRelay,HardwareSensorOnRelayBoard
from flaskr.hardware.hardware_collection import HardwareCollection
from flask import current_app, g
from typing import Any


# global_hardware_collection = HardwareCollection()
# empty hardware container


def init_hardware(app):
    """
    """
    print("INIT HARDWARE")

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
    exp_ext_temp = HardwareSensorOnRelayBoard(
        device_id=105,
        name="exp_ext_temp",
        description="DHT11 temp outside experimental plants volume",
        family="ext_temp",
        ip_addr="10.10.0.5"
    )
    exp_ext_hum = HardwareSensorOnRelayBoard(
        device_id=106,
        name="exp_ext_hum",
        description="DHT11 humidity outside experimental plants volume",
        family="ext_hum",
        ip_addr="10.10.0.5"
    )
    exp_int_temp = HardwareSensorOnRelayBoard(
        device_id=107,
        name="exp_int_temp",
        description="DHT22 temp inside experimental plants volume",
        family="int_temp",
        ip_addr="10.10.0.5"
    )
    exp_int_hum = HardwareSensorOnRelayBoard(
        device_id=108,
        name="exp_int_hum",
        description="DHT22 hum inside experimental plants volume",
        family="int_hum",
        ip_addr="10.10.0.5"
    )
    exp_roots_temp = HardwareSensorOnRelayBoard(
        device_id=109,
        name="exp_roots_temp",
        description="DS18B20 temp inside experimental roots module",
        family="roots_temp",
        ip_addr="10.10.0.5"
    )


    with app.app_context():
        current_app.global_hardware_collection = HardwareCollection(
            app,
            hardware_dict={
                100: lamp0,
                101: relay0,
                102: relay1,
                103: relay2,
                104: relay3,
                105: exp_ext_temp,
                106: exp_ext_hum,
                107: exp_int_temp,
                108: exp_int_hum,
                109: exp_roots_temp
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
        # TODO: remove sqlite writing here, we will write to sqlite only when state update polling
        current_app.global_hardware_collection.save_measurement_to_sqlite(device_id)
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
    # init_hardware()
    # handle_command(1, "")
    pass
