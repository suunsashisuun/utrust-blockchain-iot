import time


class Transaction:

    def __init__(self, tx_id, device_id, sensor_value, urgency):

        self.tx_id = tx_id
        self.device_id = device_id
        self.sensor_value = sensor_value
        self.urgency = urgency
        self.timestamp = time.time()

    def to_dict(self):

        return {
            "tx_id": self.tx_id,
            "device_id": self.device_id,
            "sensor_value": self.sensor_value,
            "urgency": self.urgency,
            "timestamp": self.timestamp
        }