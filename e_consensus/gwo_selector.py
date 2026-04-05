import random
import math


class GWOSelector:

    def __init__(self, iterations=15):
        self.iterations = iterations

    # ---------------------------
    # FITNESS FUNCTION (BALANCED)
    # ---------------------------
    def fitness(self, validator, trust_scores, urgency_weight):

        trust = trust_scores.get(validator.validator_id, 0.5)

        latency_score = 1 - validator.latency
        energy_score = 1 - validator.energy

        load_penalty = validator.current_load / 10

        # HARD CAP (prevents domination) removed now becoz already soft pen is there 
        #if validator.current_load > 7:
           # return -1

        fitness = (
            0.25 * trust
            + 0.25 * latency_score
            + 0.15 * energy_score
            + 0.15 * urgency_weight
            - 0.30 * load_penalty
        )

        return fitness


    # ---------------------------
    # MAIN SELECTION
    # ---------------------------
    def select_validator(self, validators, trust_scores, urgency_weight):

        peers = validators

        if len(peers) == 0:
            return None

        # 🔥 small wolf population (stable)
        num_wolves = min(8, len(peers))
        wolves = [random.choice(peers) for _ in range(num_wolves)]

        for t in range(self.iterations):

            fitness_values = [
                (wolf, self.fitness(wolf, trust_scores, urgency_weight))
                for wolf in wolves
            ]

            fitness_values.sort(key=lambda x: x[1], reverse=True)

            alpha = fitness_values[0][0]
            beta = fitness_values[1][0] if len(peers) > 1 else alpha
            delta = fitness_values[2][0] if len(peers) > 2 else beta

            new_wolves = []

            a = 2 - (2 * t / self.iterations)

            for wolf in wolves:

                r1, r2 = random.random(), random.random()
                A1 = 2 * a * r1 - a
                C1 = 2 * r2

                r1, r2 = random.random(), random.random()
                A2 = 2 * a * r1 - a
                C2 = 2 * r2

                r1, r2 = random.random(), random.random()
                A3 = 2 * a * r1 - a
                C3 = 2 * r2

                Xi = trust_scores.get(wolf.validator_id, 0.5)
                Xa = trust_scores.get(alpha.validator_id, 0.5)
                Xb = trust_scores.get(beta.validator_id, 0.5)
                Xd = trust_scores.get(delta.validator_id, 0.5)

                D_alpha = abs(C1 * Xa - Xi)
                X1 = Xa - A1 * D_alpha

                D_beta = abs(C2 * Xb - Xi)
                X2 = Xb - A2 * D_beta

                D_delta = abs(C3 * Xd - Xi)
                X3 = Xd - A3 * D_delta

                # 🔥 add slight exploration noise (prevents early convergence)
                exploration = random.uniform(-0.05, 0.05)

                new_position = (X1 + X2 + X3) / 3 + exploration
                new_position = max(0, min(1, new_position))

                # map to closest validator in fitness space
                closest_validator = min(
                    validators,
                    key=lambda v: abs(
                        self.fitness(v, trust_scores, urgency_weight) - new_position
                    )
                )

                new_wolves.append(closest_validator)

            wolves = new_wolves

                
                
        # ---------------------------
        # FINAL SELECTION (IMPROVED)
        # ---------------------------
        final_fitness = [
            (wolf, self.fitness(wolf, trust_scores, urgency_weight))
            for wolf in wolves
        ]

        final_fitness.sort(key=lambda x: x[1], reverse=True)

        # 🔥 increase diversity
        top_k = min(6, len(final_fitness))
        top_candidates = final_fitness[:top_k]

        candidates = [v for v, f in top_candidates]

        # avoid zero/negative fitness
        weights = [max(f, 0.001) for v, f in top_candidates]

        # 🔥 SOFTMAX SELECTION (KEY FIX)
        T = 0.5  # temperature

        exp_weights = [math.exp(w / T) for w in weights]

        selected = random.choices(
            candidates,
            weights=exp_weights,
            k=1
        )[0]

        return selected.validator_id

