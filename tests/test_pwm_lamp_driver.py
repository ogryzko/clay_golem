import pytest
from flaskr.drivers.pwm_lamp_driver import PWMLampDriver

@pytest.fixture
def pwm_driver():
    """Создание экземпляра PWMLampDriver для тестов"""
    return PWMLampDriver(host="test.local")

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

def test_get_info_success(requests_mock):
    """Тест успешного получения информации"""
    driver = PWMLampDriver(host="test.local")
    mock_response = {
        "pcb_temp": 35.5,
        "ch0_pwm": 50,
        "ch1_pwm": 75,
        "ch2_pwm": 0,
        "ch3_pwm": 100
    }
    
    requests_mock.get(
        "http://test.local/info",
        json=mock_response
    )
    
    info = driver.get_info()
    assert info == mock_response
    assert info["pcb_temp"] == 35.5
    assert info["ch0_pwm"] == 50

def test_get_info_failure(requests_mock):
    """Тест неуспешного получения информации"""
    driver = PWMLampDriver(host="test.local")
    requests_mock.get(
        "http://test.local/info",
        status_code=500
    )
    
    info = driver.get_info()
    assert info is None

def test_set_pwm_success(requests_mock):
    """Тест успешной установки PWM"""
    driver = PWMLampDriver(host="test.local")
    requests_mock.post(
        "http://test.local/pwm",
        text="SUCCESS: Channel 0 set to 75%"
    )
    
    success, message = driver.set_pwm(channel=0, duty=75)
    assert success is True
    assert "SUCCESS" in message

def test_set_pwm_invalid_params(pwm_driver):
    """Тест установки PWM с некорректными параметрами"""
    
    # Тест некорректного канала
    with pytest.raises(ValueError, match="Channel must be between 0 and 3."):
        pwm_driver.set_pwm(channel=5, duty=50)  # channel вне диапазона

    # Тест некорректного значения duty
    with pytest.raises(ValueError, match="Duty must be between 0 and 100."):
        pwm_driver.set_pwm(channel=0, duty=150)  # duty вне диапазона

    # Тест некорректного типа канала
    with pytest.raises(ValueError, match="Channel must be an integer."):
        pwm_driver.set_pwm(channel="invalid_channel", duty=50)  # channel как строка

    # Тест некорректного типа duty
    with pytest.raises(ValueError, match="Duty must be an integer."):
        pwm_driver.set_pwm(channel=0, duty="invalid_duty")  # duty как строка

def test_set_pwm_failure(requests_mock):
    """Тест неуспешной установки PWM"""
    driver = PWMLampDriver(host="test.local")
    requests_mock.post(
        "http://test.local/pwm",
        text="ERROR: Invalid channel"
    )
    
    success, message = driver.set_pwm(channel=0, duty=50)
    assert success is False
    assert "ERROR" in message

def test_set_pwm_invalid_channel(pwm_driver):
    """Тест неудачной попытки установки скважности с неверным каналом"""
    with pytest.raises(ValueError, match="Channel must be an integer."):
        pwm_driver.set_pwm("invalid_channel", 50)  # channel как строка

    with pytest.raises(ValueError, match="Channel must be between 0 and 3."):
        pwm_driver.set_pwm(5, 50)  # channel вне диапазона

def test_set_pwm_invalid_duty(pwm_driver):
    """Тест неудачной попытки установки скважности с неверным значением duty"""
    with pytest.raises(ValueError, match="Duty must be an integer."):
        pwm_driver.set_pwm(0, "invalid_duty")  # duty как строка

    with pytest.raises(ValueError, match="Duty must be between 0 and 100."):
        pwm_driver.set_pwm(0, 150)  # duty вне диапазона 