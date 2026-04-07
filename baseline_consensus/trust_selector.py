import random

class TrustSelector:

    def select_validator(self, validators):

        # 🔥 Step 1: sort by "trust-like" score
        sorted_validators = sorted(
            validators,
            key=lambda v: (v.current_load * 0.7 + v.latency * 0.3)
        )

        # 🔥 Step 2: take top-K (not just best)
        k = max(3, int(len(validators) * 0.3))
        top_k = sorted_validators[:k]

        # 🔥 Step 3: RANDOM pick inside top-K
        selected = random.choice(top_k)

        return selected.validator_id
