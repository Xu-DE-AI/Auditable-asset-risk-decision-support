import pandas as pd
from reliability.features import build_features, MODEL_FEATURES

def test_features_keep_caller_order_and_exclude_label():
    f=pd.DataFrame([
      {"asset_id":"A","observed_at":"2025-01-02T00:00:00Z","vibration_rms":4,"temperature_c":70,"pressure_bar":9,"motor_current_a":40,"operating_hours":10,"failure_within_horizon":1},
      {"asset_id":"A","observed_at":"2025-01-01T00:00:00Z","vibration_rms":2,"temperature_c":65,"pressure_bar":9,"motor_current_a":38,"operating_hours":9,"failure_within_horizon":0}])
    x=build_features(f)
    assert list(x.columns)==MODEL_FEATURES
    assert x.iloc[0]["vibration_delta"]==2
    assert "failure_within_horizon" not in x
