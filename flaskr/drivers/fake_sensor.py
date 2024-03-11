import time
from random import randint


class FakeSensorDriver:
    """
    Randomly can send incorrect result or raise error  (for test purposes)
    """
    def __init__(self, name):
        self.temperature = 25.0  # Default temperature in Celsius
        self.params = {}  # List of dicts to store sensor parameters
        self.is_running = False  # Sensor running state
        self.name = name
        if randint(0, 5) == 1:
            raise ValueError("no data from sensor")
        time.sleep(1)

    def get_temperature(self):
        """
        Simulates getting the current temperature from the sensor.

        Returns:
            float: The current temperature.
        """
        # Simulate temperature reading logic
        time.sleep(0.5)
        if randint(0, 5) == 3:
            raise ValueError("no data from sensor")
        elif randint(0, 5) == 2:
            return -1000
        else:
            return self.temperature + randint(-5, 5)

    def set_params(self, params):
        """
        Sets the parameters for the sensor.

        Args:
            params (dict): A dictionary of parameters to be set for the sensor.
        """
        time.sleep(0.5)
        if randint(0, 5) == 5:
            raise ValueError("no data from sensor")
        self.params.update(params)
        # Simulate setting sensor parameters logic

    def start(self):
        """
        Starts the sensor operation.
        """
        time.sleep(0.5)
        if randint(0, 5) == 1:
            raise ValueError("no data from sensor")
        self.is_running = True
        # Simulate sensor start logic

    def stop(self):
        """
        Stops the sensor operation.
        """
        time.sleep(0.5)
        if randint(0, 5) == 0:
            raise ValueError("no data from sensor")
        self.is_running = False
        # Simulate sensor stop logic

    def reboot(self):
        """
        Reboots the sensor.
        """
        # Simulate reboot logic, including stopping and restarting the sensor
        self.stop()
        # Simulate any necessary reboot operations here
        self.start()


if __name__ == "__main__":
    # Example usage
    sensor_driver = FakeSensorDriver(name="temp_sensor_1")
    sensor_driver.set_params({'sampling_rate': 1.0})  # Set sensor sampling rate to 1 Hz
    sensor_driver.start()
    print(f"Sensor running: {sensor_driver.is_running}")
    print(f"Current temperature: {sensor_driver.get_temperature()}°C")
    sensor_driver.stop()
    print(f"Sensor running: {sensor_driver.is_running}")
    sensor_driver.reboot()
    print(f"Sensor running: {sensor_driver.is_running}")