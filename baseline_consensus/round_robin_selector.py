
class RoundRobinSelector:

    def __init__(self):
        self.index = 0

    def select_validator(self, validators):
        validator = validators[self.index % len(validators)]
        self.index += 1
        return validator.validator_id
