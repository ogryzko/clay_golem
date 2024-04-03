import redis
import click
import subprocess
import re
from flask import current_app, g

"""
All commands here are for manual start-stop app using systemd services
"""


@click.command("start-app")
def start_app_systemd():
    """
    start web-server using systemd service
    """
    service_name = current_app.config["SYSTEMD_APP_NAME"]
    try:
        print(f"Starting {service_name}...")
        subprocess.run(['systemctl', 'start', service_name], check=True)
        print(f"{service_name} started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start {service_name}: {e}")


@click.command("start-workers")
def start_workers_systemd():
    """
    start selected in config number rq-workers using systemd template
    and start rq-scheduler using different systemd service
    """
    num_workers = current_app.config["RQ_NUM_WORKERS"]
    service_name_base = current_app.config["SYSTEMD_WORKER_NAME"]
    try:
        for i in range(1, num_workers + 1):
            service_name = f"{service_name_base}{i}"
            print(f"Starting {service_name}...")
            subprocess.run(['systemctl', 'start', service_name], check=True)
            print(f"{service_name} started.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while starting services: {e}")

    scheduler_name = current_app.config["SYSTEMD_SCHEDULER_NAME"]
    try:
        print(f"Starting {scheduler_name}...")
        subprocess.run(['systemctl', 'start', scheduler_name], check=True)
        print(f"{scheduler_name} started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start {scheduler_name}: {e}")




@click.command("stop-workers")
def stop_workers_systemd():
    """
    stop all workers and scheduler using systemd
    """
    service_name_pattern = current_app.config["SYSTEMD_WORKER_NAME"]
    try:
        # List all active systemd units
        completed_process = subprocess.run(['systemctl', 'list-units', '--no-legend', '--plain'],
                                           stdout=subprocess.PIPE, text=True, check=True)
        units = completed_process.stdout.splitlines()

        # Filter out the units that match our service name pattern
        service_pattern = re.compile(service_name_pattern)
        services_to_stop = [unit.split()[0] for unit in units if service_pattern.search(unit)]

        for service in services_to_stop:
            print(f"Stopping {service}...")
            subprocess.run(['systemctl', 'stop', service], check=True)
            print(f"{service} stopped.")

        if not services_to_stop:
            print("No services matched the pattern to stop.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while stopping services: {e}")

    scheduler_name = current_app.config["SYSTEMD_SCHEDULER_NAME"]
    try:
        print(f"Starting {scheduler_name}...")
        subprocess.run(['systemctl', 'stop', scheduler_name], check=True)
        print(f"{scheduler_name} stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop {scheduler_name}: {e}")


@click.command("stop-app")
def stop_app_systemd():
    """
    stop web server systemd service
    """
    service_name = current_app.config["SYSTEMD_APP_NAME"]
    try:
        print(f"Starting {service_name}...")
        subprocess.run(['systemctl', 'stop', service_name], check=True)
        print(f"{service_name} stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop {service_name}: {e}")


def init_systemd_handlers(app):
    app.cli.add_command(start_app_systemd)
    app.cli.add_command(stop_app_systemd)
    app.cli.add_command(start_workers_systemd)
    app.cli.add_command(stop_workers_systemd)

