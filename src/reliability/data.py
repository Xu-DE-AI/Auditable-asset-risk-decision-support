from datetime import datetime, timezone
import numpy as np
import pandas as pd

def generate_demo_data(rows: int = 6000, seed: int = 23) -> pd.DataFrame:
    if rows < 500:
        raise ValueError("rows must be at least 500 for temporal evaluation")
    rng = np.random.default_rng(seed)
    ids = np.array([f"PUMP-{i:03d}" for i in range(max(12, min(100, rows // 40)))])
    assets = rng.choice(ids, rows)
    timestamps = pd.date_range(datetime(2024, 1, 1, tzinfo=timezone.utc), periods=rows, freq="15min")
    vibration = np.clip(rng.lognormal(1.1, .45, rows), .1, 30)
    temperature = np.clip(rng.normal(68, 9, rows) + vibration * .45, -10, 160)
    pressure = np.clip(rng.normal(9, 1.7, rows), .1, 40)
    current = np.clip(rng.normal(38, 6, rows) + vibration * .6, .1, 120)
    hours = np.maximum(np.linspace(500, 50000, rows) + rng.normal(0, 100, rows), 0)
    latent = -5.2 + .15*vibration + .018*np.maximum(temperature-65, 0)
    latent += .00004*np.maximum(hours-20000, 0) + .012*np.maximum(current-38, 0)
    p = 1 / (1 + np.exp(-latent))
    return pd.DataFrame({"asset_id":assets,"observed_at":timestamps,"vibration_rms":vibration,
        "temperature_c":temperature,"pressure_bar":pressure,"motor_current_a":current,
        "operating_hours":hours,"failure_within_horizon":rng.binomial(1,p)})
