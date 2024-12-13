
import redis
from flask import current_app, g
import time
import sqlite3
from datetime import datetime

# from flaskr.hardware.hardware import global_hardware_collection
from flaskr.hardware.hardware import HardwareCollection

# def update_device_data():
#     for h in g.global_hardware_collection.hardware:
#         h.



# def update_device_data(config, db_path, device_name):
#     """
#     main goal - to get actual devices state info from hardware and store it to redis
#     """
#     device_dict = config[device_name]
#     rhost = config['REDIS_HOST']
#     rport = config["REDIS_PORT"]
#     qname = config["QUEUE"]
#     red = redis.Redis(host=rhost, port=rport, decode_responses=True)
#     queue_ = rq.Queue(connection=red, name=qname)
#
#     esp_ip_addr = config['ESP_IP_ADDR']
#     esp_auth_login = config['ESP_AUTH_LOGIN']
#     esp_auth_pass = config['ESP_AUTH_PASS']
#     conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
#     cursor = conn.cursor()
#     # dev_id = device_dict["params"]["device_id"]
#     # d =
#     # table_name = f"device_{dev_id}_{d}"
#     # insert_sql = "INSERT INTO sensor_data (sensor_name, datetime, value) VALUES (?, ?, ?)"
#
#     # esphome relay
#     if device_dict["params"]["family"] == "esphome_switch":
#         rel = esphome_driver.ESPHomeDeviceDriver(esp_ip_addr, "switch",
#                            device_dict["params"]["esphome_name"], esp_auth_login, esp_auth_pass)
#         d_id = device_dict["params"]["device_id"]
#         # try to call real hardware
#         try:
#             status = rel.get()  # get is all method for our esphome devices via web-api
#             # success result - (200, {'id': 'switch-kolos-3_relay1', 'value': False, 'state': 'OFF'})
#             if status[0] == 200:
#                 # push data to sqlite data db
#                 insert_sql = f"INSERT INTO device_{d_id}_state (datetime, value) VALUES (?, ?)"
#                 cursor.execute(insert_sql, (datetime.now(), int(status[1]["value"])))
#                 conn.commit()
#
#                 # push it to redis
#                 red.hset(f"device_{d_id}:data", "state", status[1]["state"])
#                 red.hset(f"device_{d_id}:params", "last_time_active",
#                          datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#                 red.hset(f"device_{d_id}:params", "status", "ok")
#             else:
#                 # mb store errors in logs in future
#                 red.hset(f"device_{d_id}:params", "status", "error")
#                 red.hset(f"device_{d_id}:params", "last_error",
#                          f"esphome web api status {status[0]}")
#
#         except Exception as e:
#             red.hset(f"device_{d_id}:params", "status", "error")
#             red.hset(f"device_{d_id}:params", "last_error", e.__str__() +
#                      datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#
#     if device_dict["params"]["family"] == "esphome_dht22":
#         # we need make two web api calls - for humidity and for temperature
#         dht_hum = esphome_driver.ESPHomeDeviceDriver(esp_ip_addr, "sensor",
#                            device_dict["params"]["esphome_name"] + "hum", esp_auth_login, esp_auth_pass)
#         dht_temp = esphome_driver.ESPHomeDeviceDriver(esp_ip_addr, "sensor",
#                            device_dict["params"]["esphome_name"] + "temp", esp_auth_login, esp_auth_pass)
#         d_id = device_dict["params"]["device_id"]
#         # try to call real hardware
#         try:
#             status = dht_hum.get()  # get is all method for our esphome devices via web-api
#             # success result - (200, {'id': 'sensor-kolos-3_dht_internal_temp', 'value': 26.3, 'state': '26.3 °C'})
#             if status[0] == 200:
#                 # push data to sqlite data db
#                 insert_sql = f"INSERT INTO device_{d_id}_humidity (datetime, value) VALUES (?, ?)"
#                 cursor.execute(insert_sql, (datetime.now(), int(status[1]["value"])))
#                 conn.commit()
#
#                 # push it to redis
#                 red.hset(f"device_{d_id}:data", "humidity", status[1]["value"])
#                 red.hset(f"device_{d_id}:params", "last_time_active",
#                          datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#                 red.hset(f"device_{d_id}:params", "status", "ok")
#             else:
#                 red.hset(f"device_{d_id}:params", "status", "error")
#                 red.hset(f"device_{d_id}:params", "last_error",
#                          f"esphome web api status {status[0]}")
#         except Exception as e:
#             red.hset(f"device_{d_id}:params", "status", "error")
#             red.hset(f"device_{d_id}:params", "last_error", e.__str__() +
#                      datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#
#         try:
#             status = dht_temp.get()  # get is all method for our esphome devices via web-api
#             # success result - (200, {'id': 'sensor-kolos-3_dht_internal_temp', 'value': 26.3, 'state': '26.3 °C'})
#             if status[0] == 200:
#                 # push data to sqlite data db
#                 insert_sql = f"INSERT INTO device_{d_id}_temperature (datetime, value) VALUES (?, ?)"
#                 cursor.execute(insert_sql, (datetime.now(), int(status[1]["value"])))
#                 conn.commit()
#
#                 # push it to redis
#                 red.hset(f"device_{d_id}:data", "temperature", status[1]["value"])
#                 red.hset(f"device_{d_id}:params", "last_time_active",
#                          datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#                 red.hset(f"device_{d_id}:params", "status", "ok")
#             else:
#                 red.hset(f"device_{d_id}:params", "status", "error")
#                 red.hset(f"device_{d_id}:params", "last_error",
#                          f"esphome web api status {status[0]}")
#         except Exception as e:
#             red.hset(f"device_{d_id}:params", "status", "error")
#             red.hset(f"device_{d_id}:params", "last_error", e.__str__() +
#                      datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#
#     # esphome ds18b20
#     if device_dict["params"]["family"] == "esphome_ds18b20":
#         # we need make two web api calls - for humidity and for temperature
#         ds18b20 = esphome_driver.ESPHomeDeviceDriver(esp_ip_addr, "sensor",
#                            device_dict["params"]["esphome_name"], esp_auth_login, esp_auth_pass)
#         d_id = device_dict["params"]["device_id"]
#         # try to call real hardware
#         try:
#             status = ds18b20.get()  # get is all method for our esphome devices via web-api
#             # success result - (200, {'id': 'sensor-kolos-3_dht_internal_temp', 'value': 26.3, 'state': '26.3 °C'})
#             if status[0] == 200:
#                 # push data to sqlite data db
#                 insert_sql = f"INSERT INTO device_{d_id}_temperature (datetime, value) VALUES (?, ?)"
#                 cursor.execute(insert_sql, (datetime.now(), int(status[1]["value"])))
#                 conn.commit()
#
#                 # push it to redis
#                 red.hset(f"device_{d_id}:data", "temperature", status[1]["value"])
#                 red.hset(f"device_{d_id}:params", "last_time_active",
#                          datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#                 red.hset(f"device_{d_id}:params", "status", "ok")
#             else:
#                 red.hset(f"device_{d_id}:params", "status", "error")
#                 red.hset(f"device_{d_id}:params", "last_error",
#                          f"esphome web api status {status[0]}")
#         except Exception as e:
#             red.hset(f"device_{d_id}:params", "status", "error")
#             red.hset(f"device_{d_id}:params", "last_error", e.__str__() +
#                      datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#
#     # schedule itself again
#     time.sleep(1)
#     queue_.enqueue(update_device_data, config, db_path, device_name)

