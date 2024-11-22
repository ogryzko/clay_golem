import pytest
import requests
from unittest.mock import Mock
import requests_mock
from flaskr.drivers.esp32_relay_driver import ESP32RelayDriver

@pytest.fixture
def relay():
    """Фикстура для создания экземпляра драйвера"""
    return ESP32RelayDriver(host="test.local")

@pytest.fixture
def mock_requests():
    """Фикстура для мокирования HTTP-запросов"""
    with requests_mock.Mocker() as m:
        yield m

def test_init():
    """Тест инициализации драйвера"""
    relay = ESP32RelayDriver(host="test.local", name="test_relay")
    assert relay.host == "test.local"
    assert relay.name == "test_relay"
    assert relay.base_url == "http://test.local"
    assert relay.SENSOR_ERROR_VALUE == -255

def test_get_info_success(relay, mock_requests):
    """Тест успешного получения информации"""
    expected_data = {
        "ch0": 0,
        "ch1": 1,
        "ch2": 1,
        "ch3": 0,
        "pcb_temp": -255,
        "roots_temp": -255,
        "ext_temp": -255,
        "ext_hum": -255,
        "int_temp": -255,
        "int_hum": -255,
        "uptime": 132
    }
    mock_requests.get("http://test.local/info", json=expected_data)
    
    result = relay.get_info()
    assert result == expected_data

def test_get_info_failure(relay, mock_requests):
    """Тест неудачного получения информации"""
    mock_requests.get("http://test.local/info", status_code=500)
    result = relay.get_info()
    assert result is None

def test_get_sensor_value_success(relay, mock_requests):
    """Тест успешного получения значения датчика"""
    mock_requests.get("http://test.local/ext_temp", text="25.5")
    result = relay.get_sensor_value("ext_temp")
    assert result == 25.5

def test_get_sensor_value_error(relay, mock_requests):
    """Тест получения ошибочного значения датчика (-255)"""
    mock_requests.get("http://test.local/ext_temp", text="-255")
    result = relay.get_sensor_value("ext_temp")
    assert result is None

def test_get_sensor_value_failure(relay, mock_requests):
    """Тест неудачного получения значения датчика"""
    mock_requests.get("http://test.local/ext_temp", status_code=500)
    result = relay.get_sensor_value("ext_temp")
    assert result is None

def test_set_relay_state_success(relay, mock_requests):
    """Тест успешной установки состояния реле"""
    mock_requests.post("http://test.local/relay", status_code=200)
    result = relay.set_relay_state(1, 1)
    assert result is True
    
    # Проверяем правильность отправленных данных
    last_request = mock_requests.last_request
    assert last_request.json() == {"channel": 1, "state": 1}
    assert last_request.headers["Content-Type"] == "application/json"

def test_set_relay_state_failure(relay, mock_requests):
    """Тест неудачной установки состояния реле"""
    mock_requests.post("http://test.local/relay", status_code=500)
    result = relay.set_relay_state(1, 1)
    assert result is False

def test_reset_device_success(relay, mock_requests):
    """Тест успешного сброса устройства"""
    mock_requests.post("http://test.local/reset", status_code=200)
    result = relay.reset_device()
    assert result is True
    
    # Проверяем правильность отправленных данных
    last_request = mock_requests.last_request
    assert last_request.text == "force_reset"
    assert last_request.headers["Content-Type"] == "text/html"

def test_reset_device_failure(relay, mock_requests):
    """Тест неудачного сброса устройства"""
    mock_requests.post("http://test.local/reset", status_code=500)
    result = relay.reset_device()
    assert result is False

def test_network_error(relay):
    """Тест обработки сетевых ошибок"""
    # Тестируем все методы на случай сетевой ошибки
    with pytest.raises(requests.exceptions.ConnectionError):
        relay.get_info()
    
    with pytest.raises(requests.exceptions.ConnectionError):
        relay.get_sensor_value("ext_temp")
    
    with pytest.raises(requests.exceptions.ConnectionError):
        relay.set_relay_state(1, 1)
    
    with pytest.raises(requests.exceptions.ConnectionError):
        relay.reset_device() 