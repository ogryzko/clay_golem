import redis
import rq
import time
import datetime
from datetime import timedelta
import traceback
# from flask import current_app, g
from ..drivers.esphome_driver import ESPHomeDeviceDriver


def calculate_next_loop_time(period):
    """ period - minutes """
    now = datetime.datetime.now()
    now = now.replace(second=0, microsecond=0)
    next_run_minute = ((now.minute // period) + 1) * period
    delta_minutes = next_run_minute - now.minute
    next_run_time = now + datetime.timedelta(minutes=delta_minutes)
    return next_run_time


def stop_ventilation(config):
    """
    Just turn off all vent system and thats all
    :param config:
    """
    rhost = config['REDIS_HOST']
    rport = config["REDIS_PORT"]
    red = redis.Redis(host=rhost, port=rport, decode_responses=True)
    # queue_ = rq.Queue(connection=red, name=qname)

    esp_ip_addr = config['ESP_IP_ADDR']
    esp_auth_login = config['ESP_AUTH_LOGIN']
    esp_auth_pass = config['ESP_AUTH_PASS']

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
        pump_out.post_no_params("turn_off")  # turn_on, turn_off and toggle
        pump_in.post_no_params("turn_off")  # turn_on, turn_off and toggle
        valve_out.post_no_params("turn_off")  # turn_on, turn_off and toggle
        valve_in.post_no_params("turn_off")  # turn_on, turn_off and toggle

    except Exception as e:
        # log something or make emergency call
        failure_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") # Store the timestamp of the failure
        }
        # Use the job params to create a unique key for the failure
        job_id = rq.get_current_job().id
        failure_key = f"job_failure:stop_ventilation_{job_id}"
        red.hset(failure_key, mapping=failure_info)


# TODO add errors handling and logging for each operation, because now it will die silently
def ventilation_loop(config):
    """
    we must start at each time divided by measure_cycle_time (minutes)
    :param config:
    :return:
    """
    vent_time = config["EXPERIMENT"]["ventilation"]["vent_time"]
    measure_cycle_time = config["EXPERIMENT"]["ventilation"]["measure_cycle_time"]
    rhost = config['REDIS_HOST']
    rport = config["REDIS_PORT"]
    qname = config["QUEUE"]
    red = redis.Redis(host=rhost, port=rport, decode_responses=True)
    queue_ = rq.Queue(connection=red, name=qname)

    esp_ip_addr = config['ESP_IP_ADDR']
    esp_auth_login = config['ESP_AUTH_LOGIN']
    esp_auth_pass = config['ESP_AUTH_PASS']

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
        # time.sleep(115)  # ventilation time  TODO it is too much for rq, max 180 sec of sleeping

    except Exception as e:
        # log something or make emergency call
        # log something or make emergency call
        failure_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") # Store the timestamp of the failure
        }
        # Use the job params to create a unique key for the failure
        job_id = rq.get_current_job().id
        failure_key = f"job_failure:start_ventilation_{job_id}"
        red.hset(failure_key, mapping=failure_info)

    finally:
        # in each situation lets try to enqueue next ventilation job
        # enqueue stop of ventilation
        queue_.enqueue_in(timedelta(seconds=vent_time), stop_ventilation, config)
        # Calculate the next run time
        next_run_time = calculate_next_loop_time(measure_cycle_time)
        # schedule itself again
        queue_.enqueue_at(next_run_time, ventilation_loop,config)



if __name__ == "__main__":
    pass
    now = datetime.datetime(2024, 3, 31, 23, 57, 54, 720267)
    now = datetime.datetime.now()
    now = now.replace(second=0, microsecond=0)
    next_run_minute = ((now.minute // 15) + 1) * 15
    delta_minutes = next_run_minute - now.minute
    next_run_time = now + datetime.timedelta(minutes=delta_minutes)
    print(f"Scheduling next run at {next_run_time}")