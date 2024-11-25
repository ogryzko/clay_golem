from flaskr.tasks.data_logger_cycle import update_device_data
from . import db
import redis
import rq
from flask import current_app


def init_hardware():
    """ """
    pass


def handle_command(device_id, command, arg):
    """ method to handle user command from web page for selected device"""
    #TBD
    return True