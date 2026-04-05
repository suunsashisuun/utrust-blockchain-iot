import numpy as np
import random
import joblib
import warnings
import os
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

class GasSensorModel:


    def __init__(self, device_id, base_level, risk_factor):
        self.device_id = device_id
        self.base_level = base_level
        self.risk_factor = risk_factor


        # ---------------------------
        # LOAD FEATURE DISTRIBUTION (SAFE PATH)
        # ---------------------------
        base_path = os.path.join(os.path.dirname(__file__), "..", "b_processing")


        try:
            self.feature_means = joblib.load(os.path.join(base_path, "feature_means.pkl"))
            self.feature_stds = joblib.load(os.path.join(base_path, "feature_stds.pkl"))
        except Exception as e:
            raise RuntimeError(f"Failed to load feature stats: {e}")


        # ---------------------------
        # INITIAL STATE (PERSISTENT)
        # ---------------------------
        self.current_values = np.random.normal(
            self.feature_means,
            self.feature_stds
        )


    # ---------------------------
    # GENERATE SENSOR READING
    # ---------------------------
    def generate_reading(self):


        # ---------------------------
        # TEMPORAL CONTINUITY (KEY FIX)
        # ---------------------------
        drift = np.random.normal(0, self.feature_stds * 0.1)
        self.current_values += drift


        # ---------------------------
        # CONTROLLED RISK MODES
        # ---------------------------
        mode = random.random()


        if mode < 0.4:
            multiplier = 0.5    # NORMAL
        elif mode < 0.75:
            multiplier = 1.2    # WARNING
        else:
            multiplier = 2.0    # CRITICAL


        values = self.current_values * multiplier


        # ---------------------------
        # SMALL NOISE
        # ---------------------------
        noise = np.random.normal(0, self.feature_stds * 0.05)
        values += noise


        # ---------------------------
        # RANDOM SPIKE (RARE EVENT)
        # ---------------------------
        if random.random() < self.risk_factor:
            spike = np.random.normal(0, self.feature_stds * 0.3)
            values += spike

        # ---------------------------
        # CLAMP VALUES 
        # ---------------------------
        values = np.clip(values, 0, None)

        return values
