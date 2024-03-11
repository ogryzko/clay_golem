import os

from flask import Flask, render_template, jsonify, request
from . import db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # main page with all controls
    @app.route('/')
    def index():
        return render_template('index.html', devices=db.devices)

    # relay toggling route
    @app.route('/toggle-relay', methods=['POST'])
    def toggle_relay():
        relayId = request.args.get('relayId')  # Retrieve deviceId from query string
        print(relayId)
        new_states = db.get_device_states()
        if relayId in new_states:
            # Toggle the device state
            new_states[relayId] = 'On' if new_states[relayId] == 'Off' else 'Off'
            # Return the new state as JSON
            return jsonify(state=new_states[relayId])
        else:
            # Return an error if the deviceId is not found
            return jsonify(error="Device not found"), 404

    # led lamp controls
    @app.route('/control-leds', methods=['POST'])
    def control_leds():

        #sdfdsfdsf
        command, value = request.args.get('relayId')  # Retrieve deviceId from query string
        return jsonify("started")

    @app.route('/get-device-updates')
    def get_device_updates():
        # `device_states` is a big dictionary holding the state of each device
        new_states = db.get_device_states()
        return jsonify(new_states)

    db.init_app(app)

    return app
