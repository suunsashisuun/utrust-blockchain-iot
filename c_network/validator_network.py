from c_network.validator import Validator


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

