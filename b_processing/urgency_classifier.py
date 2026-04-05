import joblib
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

class UrgencyClassifier:

    def __init__(self):
        self.previous_values = {}

        self.model = joblib.load("b_processing/urgency_model.pkl")
        self.scaler = joblib.load("b_processing/scaler.pkl")

    def classify(self, device_id, sensor_values):

        # 🔥 SCALE FIRST (MANDATORY)
        scaled_input = self.scaler.transform([sensor_values])

        urgency = self.model.predict(scaled_input)[0]

        if urgency == 2:
            return "CRITICAL"
        elif urgency == 1:
            return "WARNING"
        else:
            return "NORMAL"
        
    def classify_with_confidence(self, device_id, sensor_values):

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
