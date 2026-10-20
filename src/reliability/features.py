import pandas as pd
RAW_FEATURES=["vibration_rms","temperature_c","pressure_bar","motor_current_a","operating_hours"]
MODEL_FEATURES=RAW_FEATURES+["vibration_delta","temperature_delta","current_delta",
                             "vibration_roll_mean","temperature_roll_mean"]

def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    required={"asset_id","observed_at",*RAW_FEATURES}
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    work=frame.copy()
    work["_pos"]=range(len(work))
    work["observed_at"]=pd.to_datetime(work["observed_at"],utc=True)
    work=work.sort_values(["asset_id","observed_at","_pos"],kind="stable")
    grouped=work.groupby("asset_id",sort=False)
    work["vibration_delta"]=grouped["vibration_rms"].diff().fillna(0)
    work["temperature_delta"]=grouped["temperature_c"].diff().fillna(0)
    work["current_delta"]=grouped["motor_current_a"].diff().fillna(0)
    work["vibration_roll_mean"]=grouped["vibration_rms"].transform(lambda s:s.rolling(8,min_periods=1).mean())
    work["temperature_roll_mean"]=grouped["temperature_c"].transform(lambda s:s.rolling(8,min_periods=1).mean())
    work=work.sort_values("_pos",kind="stable")
    out=work[MODEL_FEATURES].replace([float("inf"),float("-inf")],0).fillna(0)
    out.index=frame.index
    return out
