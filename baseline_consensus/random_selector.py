import random

class RandomSelector:

    def select_validator(self, validators):
        return random.choice(validators).validator_id
