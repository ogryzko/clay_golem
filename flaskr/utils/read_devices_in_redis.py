import redis
import json

def load_devices_from_redis(redis_client, start_id, end_id):
    """
    Load hierarchical data for devices from Redis.

    Args:
        redis_client: Redis client instance.
        start_id (int): Start of the device ID range.
        end_id (int): End of the device ID range.

    Returns:
        dict: A dictionary containing the data for all devices.
    """
    devices = {}

    for device_id in range(start_id, end_id + 1):
        device_key_prefix = f"device:{device_id}"

        # Fetch params, commands, and data for each device
        params_json = redis_client.get(f"{device_key_prefix}:params")
        commands_json = redis_client.get(f"{device_key_prefix}:commands")
        data_json = redis_client.get(f"{device_key_prefix}:data")

        # Build a hierarchical structure
        devices[device_id] = {
            "params": json.loads(params_json) if params_json else None,
            "commands": json.loads(commands_json) if commands_json else None,
            "data": json.loads(data_json) if data_json else None,
        }

    return devices

if __name__ == "__main__":
    # Initialize Redis client
    redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    # Load data for devices from ID 100 to 105
    devices_data = load_devices_from_redis(redis_client, start_id=100, end_id=115)

    # Print the hierarchical data
    for device_id, device_data in devices_data.items():
        print(f"Device {device_id}:")
        print("  Params:", device_data["params"])
        print("  Commands:", device_data["commands"])
        print("  Data:", device_data["data"])