from flaskr.drivers.esp32_relay_driver import ESP32RelayDriver
import json
import time

def main():
    relay = ESP32RelayDriver(host="10.10.0.5")
    
    try:
        # Получаем информацию об устройстве
        info = relay.get_info()
        if info is not None:
            print("Информация о устройстве:")
            print(json.dumps(info, indent=2, ensure_ascii=False))
        
        # Получаем значения конкретных датчиков
        sensors = ['pcb_temp', 'ext_temp']
        for sensor in sensors:
            value = relay.get_sensor_value(sensor)
            print(f"{sensor}: {value}")
        
        # Переключаем реле
        success, message = relay.set_relay_state(1, 1)
        if success:
            print(f"Реле успешно переключено: {message}")
        else:
            print(f"Ошибка переключения реле: {message}")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main() 