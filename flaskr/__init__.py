import os
import redis
from flask import Flask, render_template, jsonify, request
from . import db
from .tasks.data_logger_cycle import update_device_data
from .tasks.ventilation_loop import ventilation_loop
#from .tasks.start_tasks import init_tasks
#from .systemd_handle import init_systemd_handlers
from .hardware.hardware import init_hardware, handle_command, get_device_states


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
        devices = get_device_states()
        return render_template('index.html', devices=devices)

    # обработчик для эксперимента
    @app.route('/handle-experiment', methods=['POST'])
    def handle_experiment():
        try:
            # Получаем данные из JSON-запроса
            data = request.get_json()
            
            # Здесь должна быть логика обработки эксперимента
            # Например, можно вызвать соответствующую функцию из модуля hardware
            
            # Заглушка для демонстрации
            result = {"status": "success", "message": "Эксперимент успешно обработан"}
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
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
            success = handle_command(device_id, command, arg)

            # Return a success response
            if success:
                return jsonify({'status': 'ok'}), 200
            else:
                return jsonify({'status': 'error', 'error': 'Failed to handle command'}), 500
        except Exception as e:
            # Return an error response if something goes wrong
            return jsonify({'status': 'error', 'error': str(e)}), 500


    @app.route('/get-device-updates')
    def get_device_updates():
        # `device_states` is a big list with dictionaries holding the state of each device
        new_states = get_device_states()
        return jsonify(new_states)

    # init database
    db.init_app(app)

    # init hardware high level handlers
    init_hardware()

    # init tasks
    #init_tasks(app)

    # init systemd handle cli commands
    #init_systemd_handlers(app)

    return app
