import redis
import rq
import time
import datetime
from flask import current_app, g
from ..drivers.esphome_driver import ESPHomeDeviceDriver


# TODO add errors handling and logging for each operation, because now it will die silently
def ventilation_loop(rhost, rport, qname):
    """
    we must start at each time divided by 5 minutes
    :param rhost:
    :param rport:
    :param qname:
    :return:
    """

    red = redis.Redis(host=rhost, port=rport, decode_responses=True)
    queue_ = rq.Queue(connection=red, name=qname)

    esp_ip_addr = current_app.config['ESP_IP_ADDR']
    esp_auth_login = current_app.config['ESP_AUTH_LOGIN']
    esp_auth_pass = current_app.config['ESP_AUTH_PASS']

    # create web api drivers
    valve_out = ESPHomeDeviceDriver(esp_ip_addr, "switch",
                                    "kolos-3_relay3", esp_auth_login, esp_auth_pass)
    valve_in = ESPHomeDeviceDriver(esp_ip_addr, "switch",
                                    "kolos-3_relay4", esp_auth_login, esp_auth_pass)
    pump_out = ESPHomeDeviceDriver(esp_ip_addr, "switch",
                                  "kolos-3_relay1", esp_auth_login, esp_auth_pass)
    pump_in = ESPHomeDeviceDriver(esp_ip_addr, "switch",
                                  "kolos-3_relay2", esp_auth_login, esp_auth_pass)

    try:
        # lets open valves
        valve_out.post_no_params("turn_on")  # turn_on, turn_off and toggle
        valve_in.post_no_params("turn_on")  # turn_on, turn_off and toggle
        time.sleep(5)  # wait when valves fully open
        # start ventilation
        pump_out.post_no_params("turn_on")  # turn_on, turn_off and toggle
        pump_in.post_no_params("turn_on")  # turn_on, turn_off and toggle
        time.sleep(115)  # ventilation time  TODO it is too much for rq, max 180 sec of sleeping
        # stop ventilation
        pump_out.post_no_params("turn_off")  # turn_on, turn_off and toggle
        pump_in.post_no_params("turn_off")  # turn_on, turn_off and toggle
        valve_out.post_no_params("turn_off")  # turn_on, turn_off and toggle
        valve_in.post_no_params("turn_off")  # turn_on, turn_off and toggle

    except Exception as e:
        # log something or make emergency call
        raise ValueError("fufufufufufufu")


    # Calculate the next run time
    now = datetime.datetime.now()
    now = now.replace(second=0, microsecond=0)
    next_run_minute = ((now.minute // 15) + 1) * 15
    delta_minutes = next_run_minute - now.minute
    next_run_time = now + datetime.timedelta(minutes=delta_minutes)

    # if next_run_minute == 0:  # Handle day rollover
    #     next_run_time += datetime.timedelta(hours=1)

    # schedule itself again
    queue_.enqueue_at(next_run_time, ventilation_loop, rhost, rport, qname)


if __name__ == "__main__":
    pass
    now = datetime.datetime(2024, 3, 31, 23, 57, 54, 720267)
    now = datetime.datetime.now()
    now = now.replace(second=0, microsecond=0)
    next_run_minute = ((now.minute // 6) + 1) * 6
    delta_minutes = next_run_minute - now.minute
    next_run_time = now + datetime.timedelta(minutes=delta_minutes)
    print(f"Scheduling next run at {next_run_time}")