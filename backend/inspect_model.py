import joblib
import os

MODEL_FILE = "health_model.pkl"

def check_model():
    print("--- 🔍 MODEL INSPECTION ---")
    
    if not os.path.exists(MODEL_FILE):
        print(f"❌ No model found at '{MODEL_FILE}'")
        return

    try:
        # Load the model
        model = joblib.load(MODEL_FILE)
        print(f"✅ Model loaded successfully!")
        print(f"   Type: {type(model)}")
        print(f"   Trees in forest: {model.n_estimators}")
        print(f"   Features expected: {model.n_features_in_}")
        print("   The brain is ready for predictions.")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")

if __name__ == "__main__":
    check_model()