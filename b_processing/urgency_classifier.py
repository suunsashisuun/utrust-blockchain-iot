import joblib
import warnings
import os
from sklearn.exceptions import InconsistentVersionWarning


warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

class UrgencyClassifier:


    def __init__(self):
        self.previous_values = {}

        # ---------------------------
        # SAFE MODEL LOADING
        # ---------------------------
        base_path = os.path.dirname(__file__)


        try:
            self.model = joblib.load(os.path.join(base_path, "urgency_model.pkl"))
            self.scaler = joblib.load(os.path.join(base_path, "scaler.pkl"))
        except Exception as e:
            raise RuntimeError(f"Failed to load ML model: {e}")


    # ---------------------------
    # CORE PREDICTION
    # ---------------------------
    def _predict(self, sensor_values):
        scaled_input = self.scaler.transform([sensor_values])


        pred = self.model.predict(scaled_input)[0]
        probs = self.model.predict_proba(scaled_input)[0]


        confidence = float(max(probs))


        if pred == 2:
            urgency = "CRITICAL"
        elif pred == 1:
            urgency = "WARNING"
        else:
            urgency = "NORMAL"


        return urgency, confidence


    # ---------------------------
    # BASIC CLASSIFICATION
    # ---------------------------
    def classify(self, device_id, sensor_values):
        urgency, _ = self._predict(sensor_values)
        return urgency


    # ---------------------------
    # CLASSIFICATION WITH CONFIDENCE
    # ---------------------------
    def classify_with_confidence(self, device_id, sensor_values):
        return self._predict(sensor_values)
