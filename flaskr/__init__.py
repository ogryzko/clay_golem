import os
import redis
from flask import Flask, render_template, jsonify, request
from . import db
from . import hardware
from .tasks.data_logger_cycle import update_device_data
from .tasks.ventilation_loop import ventilation_loop
from .tasks.start_tasks import init_tasks
from .systemd_handle import init_systemd_handlers


def create_app():
    # create and configure the app
    instance_path = os.path.join(os.getcwd(), "instance")   # finally
    app = Flask(__name__,  instance_path=instance_path, instance_relative_config=True)
    # app.config["RQ_DASHBOARD_REDIS_URL"] = "redis://127.0.0.1:6379"


    # print(app.instance_path)
    res = app.config.from_pyfile('config.py')
    print(f"Keys loaded from current app config: {res}")
    #rq_dashboard.web.setup_rq_connection(app)
    #app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
    # for key in app.config:
    #     print(key)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # main page with all controls
    @app.route('/')
    def index():
        return render_template('index.html', devices=db.get_device_states())

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
        try:
            # Parse the JSON data
            data = request.get_json()

            # Extract the device ID, command, and argument from the data
            device_id = data.get('device_id')
            command = data.get('command')
            arg = data.get('arg')

            # Handle the command (you would replace this with your actual command handling logic)
            success = hardware.handle_command(device_id, command, arg)

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
        # `device_states` is a big dictionary holding the state of each device
        new_states = db.get_device_states()
        return jsonify(new_states)

    # init database
    db.init_app(app)

    # init tasks
    init_tasks(app)

    # init systemd handle cli commands
    init_systemd_handlers(app)

    return app
