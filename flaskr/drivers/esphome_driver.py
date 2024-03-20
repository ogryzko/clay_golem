
import requests
from requests.auth import HTTPBasicAuth


class ESPHomeDeviceDriver:
    """
    simple driver to retrieve data from ESPHome powered esp32 device using rest web-api
    https://esphome.io/web-api/
    to get data we need create ID from device name (read link), then send get or post with http auth credentials
    to url like 'http://10.10.0.7/sensor/kolos-3_dht_internal_temp'
    NOTE: ID for rest api will be generated only from name, even if you have dedicated ID field in esphome config
    for this instance.

    """
    def __init__(self, ip_addr, type, name, auth_login, auth_pass):
        self.url = "http://" + ip_addr + "/" + type + "/" + name
        self.auth_login = auth_login
        self.auth_pass = auth_pass

    def get(self):
        """
        simply send get to device url and return status code and response
        :return:
        """
        response = requests.get(self.url, auth=HTTPBasicAuth(self.auth_login, self.auth_pass))
        if response.status_code == 200:
            data = response.json()
        else:
            data = {}
        return response.status_code, data

    def post_no_params(self, command):
        """
        just append command to url as mentioned in https://esphome.io/web-api/#switch
        :param command:  for switch - turn_on, turn_off and toggle
        :return:
        """
        response = requests.post(self.url + "/" + command, auth=HTTPBasicAuth(self.auth_login, self.auth_pass))
        return response.status_code, {}   # no data in switch response somehow, so just status

    def post_params(self, command, params_dict):
        """
        send post with query params
        no realized because we have no such device for now
        :param command:
        :param params_dict:
        :return:
        """
        pass


if __name__ == "__main__":
    # The URL to send the GET request to
    # url = ('http://10.10.0.7/sensor/kolos-3_dht_internal_temp')
    # dht22_k3_int = ESPHomeDeviceDriver("10.10.0.7", "sensor",
    #                            "kolos-3_dht_internal_hum", 'admin', 'rumata')
    #
    # # Send the GET request
    # print(dht22_k3_int.get())

    relay_1_k3 = ESPHomeDeviceDriver("10.10.0.7", "switch",
                               "kolos-3_relay1", 'admin', 'rumata')

    print(relay_1_k3.get())
    print(relay_1_k3.post_no_params("turn_off"))