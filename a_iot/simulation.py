import numpy as np
import random
import joblib
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

NUM_FEATURES = 128


class GasSensorModel:

    def __init__(self, device_id, base_level, risk_factor):
        self.device_id = device_id
        self.base_level = base_level
        self.risk_factor = risk_factor

        # 🔥 Load real dataset stats
        self.feature_means = joblib.load("b_processing/feature_means.pkl")
        self.feature_stds = joblib.load("b_processing/feature_stds.pkl")

        # Initialize correctly
        self.current_values = np.random.normal(
            self.feature_means,
            self.feature_stds
        )

    def generate_reading(self):

        # ---------------------------
        # BASE REALISTIC SAMPLE
        # ---------------------------
        self.current_values = np.random.normal(
            self.feature_means,
            self.feature_stds
        )

        # ---------------------------
        # CONTROLLED RISK LEVEL
        # ---------------------------
        mode = random.random()

        if mode < 0.4:
            multiplier = 0.4   # NORMAL
        elif mode < 0.75:
            multiplier = 1.0   # WARNING
        else:
            multiplier = 2.0   # CRITICAL

        self.current_values *= multiplier

        # ---------------------------
        # SMALL NOISE
        # ---------------------------
        noise = np.random.normal(0, self.feature_stds * 0.05)
        self.current_values += noise

        # ---------------------------
        # OPTIONAL EXTRA SPIKE
        # ---------------------------
        if random.random() < self.risk_factor:
            spike = np.random.normal(0, self.feature_stds * 0.3)
            self.current_values += spike

        return self.current_values