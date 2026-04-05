import random


class GWOSelector:

    def __init__(self, iterations=10):
        self.iterations = iterations

    def fitness(self, validator, trust_scores, urgency_weight):

        trust = trust_scores.get(validator.validator_id, 0.5)

        latency_score = 1 - validator.latency
        energy_score = 1 - validator.energy

        fitness = (
            0.5 * trust
            + 0.25 * latency_score
            + 0.15 * energy_score
            + 0.10 * urgency_weight
        )

        return fitness


    def select_validator(self, validators, trust_scores, urgency_weight):

        peers = validators

        # initialize wolves randomly
        num_wolves = max(5, len(peers) * 2)
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

                # adaptive exploration
                exploration_strength = 0.1 * (1 - t / self.iterations)
                exploration = random.uniform(-exploration_strength, exploration_strength)

                new_position = (X1 + X2 + X3) / 3 + exploration
                new_position = max(0, min(1, new_position))

                # map to closest validator using fitness space
                closest_validator = min(
                    validators,
                    key=lambda v: abs(
                        self.fitness(v, trust_scores, urgency_weight) - new_position
                    )
                )

                new_wolves.append(closest_validator)

            wolves = new_wolves

        # final evaluation
        final_fitness = [
            (wolf, self.fitness(wolf, trust_scores, urgency_weight))
            for wolf in wolves
        ]

        final_fitness.sort(key=lambda x: x[1], reverse=True)

        # probabilistic selection among top candidates
        top_candidates = final_fitness[:3]

        validators = [v for v, f in top_candidates]
        weights = [f for v, f in top_candidates]

        selected = random.choices(validators, weights=weights, k=1)[0]

        return selected.validator_id