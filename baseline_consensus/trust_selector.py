class TrustSelector:

    def select_validator(self, validators):

        # select validator with minimum load
        best = min(validators, key=lambda v: v.current_load)

        return best.validator_id
