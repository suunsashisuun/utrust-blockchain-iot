import random


class DomainSelector:


    def __init__(self, alpha=0.3):
        # % or Fraction of validators selected for consensus
        self.alpha = alpha


    def select_domain(self, validators, trust_scores):


        # ---------------------------
        # SORT BY TRUST (SAFE ACCESS)
        # ---------------------------
        sorted_validators = sorted(
            validators,
            key=lambda v: trust_scores.get(v.validator_id, 0.5),
            reverse=True
        )


        # ---------------------------
        # DOMAIN SIZE
        # ---------------------------
        k = max(3, int(len(sorted_validators) * self.alpha))


        # ---------------------------
        # MIXED DOMAIN SELECTION
        # ---------------------------
        top_part = sorted_validators[:k // 2]


        remaining = sorted_validators[k // 2:]


        random_part = random.sample(
            remaining,
            min(len(remaining), k - len(top_part))
        )


        consensus_group = top_part + random_part


        return consensus_group
