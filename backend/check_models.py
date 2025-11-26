import pickle
import os

model_dir = "data/models"

print("Checking model files...")
print("="*50)

# Check XGBoost
xgb_path = os.path.join(model_dir, "xgboost_model.pkl")
if os.path.exists(xgb_path):
    try:
        with open(xgb_path, 'rb') as f:
            xgb = pickle.load(f)
        n_features = getattr(xgb, 'n_features_in_', 'N/A')
        print(f"✅ XGBoost: {n_features} features")
    except Exception as e:
        print(f"❌ XGBoost load failed: {e}")
else:
    print("❌ XGBoost file not found")

# Check LightGBM
lgb_path = os.path.join(model_dir, "lightgbm_model.pkl")
if os.path.exists(lgb_path):
    try:
        with open(lgb_path, 'rb') as f:
            lgb = pickle.load(f)
        n_features = getattr(lgb, 'n_features_', 'N/A')
        print(f"✅ LightGBM: {n_features} features")
    except Exception as e:
        print(f"❌ LightGBM load failed: {e}")
else:
    print("❌ LightGBM file not found")

# Check CatBoost
cat_path = os.path.join(model_dir, "catboost_model.pkl")
if os.path.exists(cat_path):
    try:
        with open(cat_path, 'rb') as f:
            cat = pickle.load(f)
        n_features = getattr(cat, 'n_features_', 'N/A')
        print(f"✅ CatBoost: {n_features} features")
    except Exception as e:
        print(f"❌ CatBoost load failed: {e}")
else:
    print("❌ CatBoost file not found")

# Check Deep NN
deep_path = os.path.join(model_dir, "deep_model.h5")
if os.path.exists(deep_path):
    try:
        from tensorflow import keras
        model = keras.models.load_model(deep_path)
        input_shape = model.input_shape
        print(f"✅ Deep NN: input shape {input_shape}")
    except Exception as e:
        print(f"❌ Deep NN load failed: {e}")
else:
    print("❌ Deep NN file not found")
