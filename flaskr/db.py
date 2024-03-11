import redis
import click
from flask import current_app, g
import random
from datetime import datetime

# must be stored in redis
# but for test here, as global variable
# device_states = {
#     'relay1': 'Off',
#     'relay2': 'Off',
#     'relay3': 'Off',
#     'relay4': 'Off',
#     'temp1': 23,
#     'temp2': 48,
#     'hum2': 67,
#     'temp3': 26,
#     'hum3': 56,
#     'leds_red': 100,
#     'leds_white': 120,
#     'leds_state': 'Off'
#     # Add more devices as needed
# }

# hierarchical dictionaries to store all data about in it

relay1_dict = {
    "params":
    {
        "name": "Relay 1",
        "device_id": 10,
        "last_time_active": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        "type": "relay",
        "uptime_sec": 13245,
        "description": "relay that rules air pump N1",
        "status": "error 3132"
    },
    "commands":
    {
        "set_on": None,
        "set_off": None
    },
    "data":
    {
        "state": "on"
    }
}

relay2_dict = {
    "params":
    {
        "name": "Relay 2",
        "device_id": 11,
        "last_time_active": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        "type": "relay",
        "uptime_sec": 13005,
        "description": "relay that rules air pump N2",
        "status": "ok"
    },
    "commands":
    {
        "set_on": None,
        "set_off": None

    },
    "data":
    {
        "state": "on"
    }
}

sensor1_dict = {
    "params":
    {
        "name": "DHT22 internal",
        "device_id": 12,
        "last_time_active": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        "type": "sensor",
        "uptime_sec": 15001,
        "description": "dht22 internal temp and hum data",
        "status": "ok"
    },
    "commands":
    {
        "get_temp": None,
        "get_hum": None
    },
    "data":
    {
        "humidity": 78,
        "temperature": 34,
    }
}

devices = [
    relay1_dict, relay2_dict, sensor1_dict
]


def get_device_states():
    # simulation of reading updated data from redis
    global devices
    for d in devices:
        d["params"]["last_time_active"] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        d["params"]["uptime_sec"] += 1

        if d["params"]["type"] == "relay":
            pass
            # d["data"]["state"] = "off "
        if d["params"]["type"] == "sensor":
            d["data"]["humidity"] = random.randint(50, 90)
            d["data"]["temperature"] = random.randint(20, 40)
    return devices


def get_db():
    if 'db' not in g:
        # g.db = redis.
        pass

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    # some init of redis


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
