import os
import redis
import rq
from flask import Flask, render_template, jsonify, request
from . import db
from . import hardware
from .tasks.data_logger_cycle import update_device_data
from .tasks.ventilation_loop import ventilation_loop
from .tasks.start_tasks import init_tasks


def create_app():
    # create and configure the app
    instance_path = os.path.join(os.getcwd(), "instance")   # finally
    app = Flask(__name__,  instance_path=instance_path, instance_relative_config=True)
    # print(app.instance_path)
    res = app.config.from_pyfile('config.py')
    print(f"Keys loaded from current app config: {res}")
    for key in app.config:
        print(key)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # main page with all controls
    @app.route('/')
    def index():
        return render_template('index.html', devices=db.get_device_states())

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

    return app
