import random
class DomainSelector:

    def __init__(self, alpha=0.3):
        self.alpha = alpha  # % of validators to select

    def select_domain(self, validators, trust_scores):

        # sort by trust
        sorted_validators = sorted(
            validators,
            key=lambda v: trust_scores[v.validator_id],
            reverse=True
        )

        k = max(3, int(len(sorted_validators) * self.alpha))

        # ---------------------------
        # 🔥 MIXED DOMAIN (KEY FIX)
        # ---------------------------

        top_part = sorted_validators[:k//2]

        remaining = sorted_validators[k//2:]
        random_part = random.sample(
            remaining,
            min(len(remaining), k - len(top_part))
        )

        consensus_group = top_part + random_part

        return consensus_group

