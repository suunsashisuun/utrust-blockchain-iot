import random

MIN_GAS = 10
MAX_GAS = 100

class GasSensorModel:
    def __init__(self, device_id, base_level, risk_factor):
        self.device_id = device_id
        self.base_level = base_level
        self.current_value = base_level
        self.risk_factor = risk_factor

    def generate_reading(self):

    # NORMAL ENVIRONMENT FLUCTUATION
        fluctuation = random.randint(-2, 2)
        self.current_value += fluctuation

    # OCCASIONAL GAS SPIKE
        if random.random() < self.risk_factor:
            self.current_value += random.randint(30, 50)

    # STRONG RECOVERY WHEN ABOVE NORMAL RANGE
        if self.current_value > self.base_level + 5:
            self.current_value -= random.randint(3, 8)

    # LIMIT RANGE
        self.current_value = max(MIN_GAS, min(self.current_value, MAX_GAS))

        return self.current_value