from datetime import datetime
import requests


class HardwareRelay:
    """
        That class represents one channel on remote relay device, with its params and methods
        for represents
    """
    def __init__(self, name, device_id, hardware_type, description, ip_addr, localhost_name, channel):
        # Parameters
        self.name = name   # some human-readable name like "Relay 4"
        self.device_id = device_id   # absolute numeration of virtual devices in experiment devices collection (for use in db and web-page)
        self.last_time_active = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")   # store last correct operation time
        self.hardware_type = hardware_type  # string with short description of device type, like "HardwareRelay"
        self.uptime_sec = 0   # updated from db
        self.description = description   # string with short description of device purpose
        self.status = "ok"   # updated from  db or result of request
        self.last_error = ""   # updated from  db or result of request
        self.ip_addr = ip_addr   # ip addr in wireguard network like "10.10.0.7"
        self.localhost_name = localhost_name   # local addr like "esp32_relay_4.local"
        self.channel = channel  # Channel on the real relay device

        # Data
        self.state = "OFF"  # Default state

    def send_command(self, state):
        """
        General method to send an HTTP command to set the relay state.

        """
        url = f"http://{self.ip_addr}/relay"
        payload = {
            "channel": self.channel,
            "state": state
        }
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.last_time_active = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

            # Parse the response text for success or known error messages
            if "RESULT: SUCCESS" in response.text:
                self.state = "ON" if state == 1 else "OFF"
                self.last_error = ""
                self.status = "ok"
                print(f"Device {self.device_id} on channel {self.channel} set to state {self.state}")
            elif "ERROR" in response.text:
                self.last_error = response.text
                self.status = "error"
                print(f"Error setting device {self.device_id} on channel {self.channel}: {self.last_error}")
            else:
                self.last_error = "Unexpected response format"
                self.status = "error"
                print(f"Unexpected response from device {self.device_id} on channel {self.channel}: {response.text}")

        except requests.RequestException as e:
            self.last_error = str(e)
            self.status = "error"
            print(f"Request failed for device {self.device_id} on channel {self.channel}: {e}")

    def set_on(self):
        """Command to turn the device on by sending an HTTP request."""
        self.send_command(1)

    def set_off(self):
        """Command to turn the device off by sending an HTTP request."""
        self.send_command(0)

    def get_representation(self):
        """Retrieve the current status of the device as python dict."""
        return {
            "params": {
                "name": self.name,
                "device_id": self.device_id,
                "last_time_active": self.last_time_active,
                "hardware_type": self.hardware_type,
                "uptime_sec": self.uptime_sec,
                "description": self.description,
                "status": self.status,
                "last_error": self.last_error,
                "ip_addr": self.ip_addr,
                "localhost_name": self.localhost_name,
                "channel": self.channel
            },
            "commands":{
                "set_on": None,
                "set_off": None
            },
            "data": {
                "state": self.state
            }
        }


if __name__ == "__main__":
    pass
    r1 = HardwareRelay(
        name="relay1",
        device_id="35",
        hardware_type="HardwareRelay",
        description="test hardware relay",
        ip_addr="10.10.0.18",
        localhost_name="sdsdfsdf.local",
        channel=7
    )
    print(r1.set_on())
    print(r1.set_off())
