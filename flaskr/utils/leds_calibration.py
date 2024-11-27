import sqlite3
import click, sys, os
sys.path.insert(0, '/opt/clay/clay_golem/')
from flaskr.drivers.pwm_lamp_driver import PWMLampDriver

#print(os.getcwd())

l1 = PWMLampDriver("10.10.0.15", "exp_lamp")
l2 = PWMLampDriver("10.10.0.16", "ctrl_lamp")

import sqlite3
import click

# Global step value
STEP_VALUE = 10

# Database initialization
def init_db():
    conn = sqlite3.connect("experiment_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            point INTEGER NOT NULL,
            red_duty INTEGER NOT NULL,
            white_duty INTEGER NOT NULL,
            ppfd REAL NOT NULL,
            stand TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_value INTEGER NOT NULL
        )
        """
    )
    cursor.execute("INSERT INTO settings (step_value) VALUES (?)", (STEP_VALUE,))
    conn.commit()
    conn.close()

# Update step value
def update_step_value(step):
    conn = sqlite3.connect("experiment_data.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET step_value = ? WHERE id = 1", (step,))
    conn.commit()
    conn.close()

# Get step value
def get_step_value():
    conn = sqlite3.connect("experiment_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT step_value FROM settings WHERE id = 1")
    step = cursor.fetchone()[0]
    conn.close()
    return step

# Add measurement data
def add_measurement(point, red, white, ppfd, stand):
    conn = sqlite3.connect("experiment_data.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO measurements (point, red_duty, white_duty, ppfd, stand) VALUES (?, ?, ?, ?, ?)",
        (point, red, white, ppfd, stand),
    )
    conn.commit()
    conn.close()

# Mock function to set duty cycles
def set_duty(red, white, device):
    global l1
    if device == "exp":
        l1.set_pwm(0, white)
        l1.set_pwm(1, white)
        l1.set_pwm(2, red)
        l1.set_pwm(3, red)

    elif device == "ctr":
        l2.set_pwm(0, white)
        l2.set_pwm(1, white)
        l2.set_pwm(2, red)
        l2.set_pwm(3, red)
    print(f"Setting device '{device}' - Red: {red}%, White: {white}%")

# Perform measurements for a point
def perform_measurements(point, step, stand, start_red=0, start_white=0):
    print(f"Starting measurements for point {point} on stand '{stand}'...")
    print(f"Current step size: {step}%")
    for white in range(start_white, 101, step):
        set_duty(0, white, device=stand)
        user_input = input(f"Enter quantum meter reading for white={white}%, red=0% (or press Enter to skip): ")
        if user_input.strip() == "":
            print(f"Skipping white={white}%, red=0%.")
            continue
        try:
            ppfd = float(user_input)
            add_measurement(point, 0, white, ppfd, stand)
        except ValueError:
            print("Invalid input. Skipping this measurement.")

    for red in range(start_red, 101, step):
        set_duty(red, 0, device=stand)
        user_input = input(f"Enter quantum meter reading for red={red}%, white=0% (or press Enter to skip): ")
        if user_input.strip() == "":
            print(f"Skipping red={red}%, white=0%.")
            continue
        try:
            ppfd = float(user_input)
            add_measurement(point, red, 0, ppfd, stand)
        except ValueError:
            print("Invalid input. Skipping this measurement.")

    set_duty(0, 0, device=stand)
    print(f"Measurements for point {point} on stand '{stand}' completed.")


# CLI commands
@click.group()
def cli():
    pass

@cli.command()
def init():
    "Initialize the database."
    init_db()
    click.echo("Database initialized.")

@cli.command()
@click.option("--point", required=True, type=int, help="Point number for measurements.")
@click.option("--stand", required=True, type=click.Choice(['exp', 'ctrl']), help="Stand type (exp or ctrl).")
@click.option("--start-red", default=0, type=int, help="Start value for red duty cycle (default: 0%).")
@click.option("--start-white", default=0, type=int, help="Start value for white duty cycle (default: 0%).")
def measure(point, stand, start_red, start_white):
    "Start measurements for a specific point."
    step = get_step_value()
    perform_measurements(point, step, stand, start_red, start_white)

@cli.command()
@click.option("--point", required=True, type=int, help="Point number for measurements.")
@click.option("--red", required=True, type=int, help="Red light duty cycle (0-100%).")
@click.option("--white", required=True, type=int, help="White light duty cycle (0-100%).")
@click.option("--stand", required=True, type=click.Choice(['exp', 'ctrl']), help="Stand type (exp or ctrl).")
def add(point, red, white, ppfd, stand):
    "Add a single measurement to the database."
    set_duty(red, white, stand)
    user_input = input(f"Enter quantum meter reading for red={red}%, white=0% (or press Enter to skip): ")
    if user_input.strip() == "":
        print(f"Skipping red={red}%, white=0%.")
    else:
        ppfd = float(user_input)
        add_measurement(point, red, 0, ppfd, stand)
        click.echo(f"Measurement added for point={point}, red={red}%, white={white}%, ppfd={ppfd}, stand={stand}.")
    set_duty(0, 0, stand)

@cli.command()
@click.option("--step", default=10, type=int, help="New step size for PWM duty cycle.")
def set_step(step):
    "Set the PWM duty cycle step size."
    update_step_value(step)
    click.echo(f"Step size updated to {step}%.")

if __name__ == "__main__":
    cli()

