from c_network.validator import Validator

class ValidatorNetwork:
    """
    Manages a network of validators.


    Responsibilities:
    - Initialize validators
    - Provide access to validator list
    - Retrieve validator by ID
    """


    def __init__(self, num_validators=50):


        # ---------------------------
        # INITIALIZE VALIDATORS
        # ---------------------------
        self.validators = []


        for index in range(num_validators):
            validator = Validator(f"validator_{index + 1}")
            self.validators.append(validator)


    # ---------------------------
    # GET ALL VALIDATORS
    # ---------------------------
    def get_validators(self):
        return self.validators


    # ---------------------------
    # GET VALIDATOR BY ID
    # ---------------------------
    def get_validator_by_id(self, validator_id):


        for validator in self.validators:
            if validator.validator_id == validator_id:
                return validator


        return None
