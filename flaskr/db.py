import redis
import click
from flask import current_app, g
import sqlite3
from sqlite3 import Error


def get_device_states():
    """method to update flask web page data from db"""
    # lets load all devices data from redis hashes
    red = get_db()
    reconstructed_devices = []
    for device_dict in current_app.config['DEVICES']:
        # to get needed names
        dev_id = device_dict["params"]["device_id"]
        recon_device = {}   # updated dict
        # update device params from redis
        for key in device_dict.keys():
            hash_name = f"device_{dev_id}:{key}"
            recon_device[key] = red.hgetall(hash_name)
        # load it to updated list
        reconstructed_devices.append(recon_device)
    return reconstructed_devices


def get_db():
    """
    we have operational db - redis and data db - sqlite
    this method returns redis pointer
    :return:
    """
    if 'db' not in g:
        # TODO update from config in future
        g.db = redis.Redis(host='localhost', port=6379, decode_responses=True)   # mb it is important to already decode
    return g.db


def get_data_db():
    """
    we have operational db - redis and data db - sqlite
    this method returns sqlite db pointer
    :return:
    """
    if 'db' not in g:
        # TODO update from config in future
        g.db = redis.Redis(host='localhost', port=6379, decode_responses=True)   # mb it is important to already decode
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """ this method must be called only when server created or re-created, it will fully rewrite devices data """
    devices_conf_list = current_app.config['DEVICES']

    red = get_db()
    print("Deleting current redis keys to clear app state.")
    # clear all device_* data from db0
    # Pattern to match
    pattern = 'device_*'

    # Use SCAN to find keys matching the pattern
    # SCAN returns a tuple (cursor, [list of keys])
    # We start with cursor 0, and SCAN iterates until cursor returns 0 again
    cursor = '0'
    while cursor != 0:
        cursor, keys = red.scan(cursor=cursor, match=pattern, count=100)
        for key in keys:
            # Delete each key
            red.delete(key)
            print(f"Deleted key: {key}")

    print("Finished deleting keys.")

    # load data from devices config file and store it to redis
    # iterate over all fields in all devices in list
    print("Loading new redis keys from app config")
    for device_dict in devices_conf_list:
        dev_id = device_dict["params"]["device_id"]
        # Store each sub-dictionary in its own hash
        for key, val in device_dict.items():
            hash_name = f"device_{dev_id}:{key}"
            for field, value in val.items():
                red.hset(hash_name, field, value if value is not None else "")
    print("Finished loading new keys")

    # create tables in sqlite db for all devices in list

    # remove all old sql tables
    # TODO mb simply remove or rename old sqlite db file if already exists

    # create db or connection
    data_db_path = current_app.instance_path + "/" + current_app.config['DATA_DB_NAME']
    if "data_db" not in g:
        g.data_db = sqlite3.connect(
            data_db_path,  #current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # g.db.row_factory = sqlite3.Row

    # then create tables for all
    print("Loading new sql tables from app config to data db")
    for device_dict in devices_conf_list:
        dev_id = device_dict["params"]["device_id"]
        try:
            # one table contain one type of data
            # so one sensor can have multiple tables
            for d in device_dict["data"]:
                sql_create_sensor_data_table = f"""CREATE TABLE IF NOT EXISTS device_{dev_id}_{d} (
                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    datetime DATETIME NOT NULL,
                                                    value REAL NOT NULL
                                                );"""
                cursor = g.data_db.cursor()
                cursor.execute(sql_create_sensor_data_table)
        except Error as e:
            print("sqlite database fucked up somehow: {}".format(e))
    print("finished loading new sql tables from app config to data db")


@click.command('init-db')
def init_db_command():
    """Clear the existing data in redis and sqlite and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
