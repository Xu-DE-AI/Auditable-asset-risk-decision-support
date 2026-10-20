from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .features import MODEL_FEATURES, build_features

def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def train_and_evaluate(frame: pd.DataFrame, output_dir: str|Path) -> dict:
    if "failure_within_horizon" not in frame: raise ValueError("label column is required")
    ordered=frame.copy()
    ordered["observed_at"]=pd.to_datetime(ordered["observed_at"],utc=True)
    ordered=ordered.sort_values("observed_at",kind="stable").reset_index(drop=True)
    n=len(ordered); a=int(n*.65); b=int(n*.82)
    if a<100 or b<=a or n-b<50: raise ValueError("Insufficient rows for temporal split")
    X=build_features(ordered); y=ordered["failure_within_horizon"].astype(int)
    if y.nunique()!=2: raise ValueError("Both classes are required")
    baseline=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,class_weight="balanced"))
    candidate=HistGradientBoostingClassifier(max_iter=120,learning_rate=.08,max_leaf_nodes=15,
                                             l2_regularization=1,random_state=17)
    baseline.fit(X.iloc[:a],y.iloc[:a]); candidate.fit(X.iloc[:a],y.iloc[:a])
    # Model selection is based only on validation data; the final test set is never used to choose.
    val_y=y.iloc[a:b]
    baseline_val=baseline.predict_proba(X.iloc[a:b])[:,1]
    candidate_val=candidate.predict_proba(X.iloc[a:b])[:,1]
    baseline_val_ap=float(average_precision_score(val_y,baseline_val))
    candidate_val_ap=float(average_precision_score(val_y,candidate_val))
    selected, selected_name = (candidate,"hist-gradient-boosting") if candidate_val_ap >= baseline_val_ap else (baseline,"logistic-baseline")
    val_probs=selected.predict_proba(X.iloc[a:b])[:,1]
    thresholds=np.linspace(.05,.95,91)
    threshold=min(((float(t),float(recall_score(val_y,val_probs>=t,zero_division=0))) for t in thresholds),
                  key=lambda x:(abs(x[1]-.75),-x[0]))[0]
    test_X=X.iloc[b:]; test_y=y.iloc[b:]
    selected_probs=selected.predict_proba(test_X)[:,1]
    baseline_probs=baseline.predict_proba(test_X)[:,1]
    metrics={"test_rows":int(len(test_y)),"positive_rate":float(test_y.mean()),
      "selected_model_average_precision":float(average_precision_score(test_y,selected_probs)),
      "baseline_average_precision":float(average_precision_score(test_y,baseline_probs)),
      "selected_model_roc_auc":float(roc_auc_score(test_y,selected_probs)),
      "selected_model_recall_at_validation_threshold":float(recall_score(test_y,selected_probs>=threshold,zero_division=0)),
      "validation_candidate_average_precision":candidate_val_ap,
      "validation_baseline_average_precision":baseline_val_ap,
      "selected_model":selected_name,"decision_threshold":float(threshold)}
    if not all(np.isfinite(v) for v in metrics.values() if isinstance(v,(int,float))):
        raise ValueError("Non-finite evaluation metrics")
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); path=out/"asset_risk_model.joblib"
    bundle={"model":selected,"feature_columns":MODEL_FEATURES,"threshold":threshold,
      "model_version":f"{selected_name}-1.0.0","trained_at":datetime.now(timezone.utc).isoformat(),
      "training_rows":a,"evaluation_method":"chronological_train_validation_test",
      "validation_model_selection":"selected by validation average precision against logistic baseline"}
    joblib.dump(bundle,path)
    manifest={"model_version":bundle["model_version"],"trained_at":bundle["trained_at"],
      "dataset_rows":n,"metrics":metrics,"artifact_sha256":_sha256(path),
      "note":"Synthetic demo data is not evidence of operational performance."}
    (out/"evaluation.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest

def load_model(path: str|Path) -> dict:
    bundle=joblib.load(path)
    if not isinstance(bundle,dict) or not {"model","feature_columns","threshold","model_version"}<=bundle.keys():
        raise ValueError("Model artifact contract mismatch")
    if list(bundle["feature_columns"])!=MODEL_FEATURES: raise ValueError("Feature contract mismatch")
    if not 0<float(bundle["threshold"])<1: raise ValueError("Invalid threshold")
    return bundle
