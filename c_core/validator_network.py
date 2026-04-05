import random


class Validator:

    def __init__(self, validator_id):
        self.validator_id = validator_id
        self.trust = round(random.uniform(0.4, 0.9), 3)
        self.latency = round(random.uniform(0.1, 0.5), 3)
        self.energy = round(random.uniform(0.2, 0.8), 3)
        self.processed_transactions = 0
        self.current_load = 0


    def process_transaction(self):
        self.processed_transactions += 1
        self.current_load += 1


    def fluctuate(self):
        import random

        # simulate network condition change
        self.latency = max(0.05, min(1.0, self.latency + random.uniform(-0.05, 0.05)))
        self.energy = max(0.1, min(1.0, self.energy + random.uniform(-0.05, 0.05)))


class ValidatorNetwork:
    def __init__(self, num_validators=50):
        self.validators = []

        for i in range(num_validators):
            validator = Validator(f"validator_{i+1}")
            self.validators.append(validator)

    def get_validators(self):
        return self.validators

    def get_validator_by_id(self, validator_id):
        for v in self.validators:
            if v.validator_id == validator_id:
                return v
        return None