import random

def gwo_select_validator(trust_scores: dict) -> str:
    weighted_scores = {}
    for peer, score in trust_scores.items():
        exploration_factor = random.uniform(0, 0.1)
        weighted_scores[peer] = score + exploration_factor

    selected_peer = max(weighted_scores, key=lambda peer: weighted_scores[peer])
    return selected_peer