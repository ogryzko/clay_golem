import os
import time
import threading

from flask import Flask, render_template, jsonify, request, current_app
from . import db
from .db import get_db
#from .tasks.data_logger_cycle import update_device_data
from .tasks.ventilation_loop import ventilation_loop
from .tasks.update_data_task import state_update_worker
from .tasks.ventilation_task import VentilationTaskThread
from .hardware.hardware_config import init_hardware
from .utils.logger import Logger



def create_app():
    # create and configure the app
    instance_path = os.path.join(os.getcwd(), "instance")   # finally
    print(instance_path)
    app = Flask(__name__,  instance_path=instance_path, instance_relative_config=True)

    # print(app.instance_path)
    res = app.config.from_pyfile('config.py')
    print(f"Keys loaded from current app config: {res}")

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # main page with all controls
    @app.route('/')
    def index():
        with app_context:
            devices = current_app.global_hardware_collection.get_device_states()
            return render_template('index.html', devices=devices)

    # обработчик для эксперимента
    @app.route('/handle-experiment', methods=['POST'])
    def handle_experiment():
        try:
            # Получаем данные из JSON-запроса
            data = request.get_json()
            task_id = str(data.get('task_name')) # must be string like worker:ventilation, or worker:search, etc
            command = str(data.get('command'))
            arg = data.get('arg')  # can be int or string
            if arg:
                arg = int(arg)
            # Здесь должна быть логика обработки эксперимента
            # Например, можно вызвать соответствующую функцию из модуля hardware
            
            # Handle the command
            with app_context:
                success = current_app.global_hardware_collection.handle_task_command(task_id, command, arg)

                # Получаем данные о задаче вентиляции
                redis_client = get_db()
                task_data = VentilationTaskThread.read_task_data(get_db(), task_id)

            # Return a success response
            if success:
                return jsonify({'status': 'ok', 'task_data': task_data}), 200
            else:
                return jsonify({'status': 'error', 'error': 'Failed to handle task command'}), 500
        except Exception as e:
            app.logger.error(f"Ошибка в обработчике /handle-experiment: {str(e)}", exc_info=True)
            # Return an error response if something goes wrong
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # handler user commands for all devices
    @app.route('/handle-request', methods=['POST'])
    def handle_request():
        # TODO: do we need to send error responses from low-level devices to wep app ?
        try:
            # Parse the JSON data
            data = request.get_json()

            # Extract the device ID, command, and argument from the data
            # and convert it to correct formats
            device_id = int(data.get('device_id'))
            command = str(data.get('command'))
            arg = data.get('arg')
            if arg:
                arg = int(arg)

            # Handle the command
            with app_context:
                success = current_app.global_hardware_collection.handle_command(device_id, command, arg)

            # Return a success response
            if success:
                return jsonify({'status': 'ok'}), 200
            else:
                return jsonify({'status': 'error', 'error': 'Failed to handle command'}), 500
        except Exception as e:
            app.logger.error(f"Ошибка в обработчике /handle-request: {str(e)}", exc_info=True)
            # Return an error response if something goes wrong
            return jsonify({'status': 'error', 'error': str(e)}), 500


    @app.route('/get-device-updates')
    def get_device_updates():
        # `device_states` is a big list with dictionaries holding the state of each device
        with app_context:
            new_states = current_app.global_hardware_collection.get_device_states()
            return jsonify(new_states)

    # at first - init database
    db.init_app(app)

    # then - init hardware high level handlers
    # on that step we got ref to HardwareCollection object in current_app
    app_context = app.app_context()
    with app_context:
        current_app.global_hardware_collection = init_hardware(app_context)

    # init tasks

    app_context = app.app_context()
    # start data updating thread
    # TODO: make one thread for each device? It will make updating much faster
    update_thread = threading.Thread(target=state_update_worker, args=(app_context,), daemon=True)
    # update_thread.start()
    with app_context:
        current_app.update_thread = update_thread

    # start ventilation task thread
    vent_task = VentilationTaskThread(app_context, name="worker:ventilation")
    # vent_task.start()

    with app_context:
        current_app.vent_task = vent_task

    # add task names to hardware collection
    # and start them all
    with app_context:
        current_app.global_hardware_collection.tasks.append(current_app.vent_task.params["name"])
        print(current_app.global_hardware_collection.tasks)
    update_thread.start()
    print("update thread started")
    vent_task.start()
    print("vent_task started")


    # init systemd handle cli commands
    #init_systemd_handlers(app)

    return app
