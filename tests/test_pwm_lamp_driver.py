import pytest
from flaskr.drivers.pwm_lamp_driver import PWMLampDriver

def test_reset_device_success(requests_mock):
    """Тест успешной перезагрузки"""
    driver = PWMLampDriver(host="test.local")
    requests_mock.post(
        "http://test.local/reset",
        text="User have sent force reset command, so rebooting"
    )
    
    success, message = driver.reset_device()
    assert success is True
    assert "force reset command" in message.lower()
    assert "rebooting" in message.lower()

def test_reset_device_failure(requests_mock):
    """Тест неуспешной перезагрузки"""
    driver = PWMLampDriver(host="test.local")
    requests_mock.post(
        "http://test.local/reset",
        text="User have sent incorrect reset command, so no rebooting"
    )
    
    success, message = driver.reset_device()
    assert success is False
    assert "incorrect reset command" in message.lower()
    assert "no rebooting" in message.lower() 