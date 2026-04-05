class UrgencyClassifier:

    def __init__(self):
        self.previous_values = {}

    def classify(self, device_id, gas_value):

        previous = self.previous_values.get(device_id, gas_value)
        change = gas_value - previous

        self.previous_values[device_id] = gas_value

        # classification logic

        if gas_value >= 80 or change >= 25:
            return "CRITICAL"

        elif gas_value >= 60 or change >= 15:
            return "WARNING"

        else:
            return "NORMAL"