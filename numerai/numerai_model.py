"""Numerai tournament model. 'train' downloads training data and fits LightGBM on the small feature set;
'submit' predicts the live round and uploads. Never stake NMR. Dataset version names change: check numer.ai/data."""
import os, sys, json, pandas as pd
from numerapi import NumerAPI
V = os.environ.get("NUMERAI_DATA_VERSION", "v5.0")
napi = NumerAPI(os.environ.get("NUMERAI_PUBLIC_ID"), os.environ.get("NUMERAI_SECRET_KEY"))
mode = sys.argv[1] if len(sys.argv) > 1 else "submit"
napi.download_dataset(f"{V}/features.json", "numerai/features.json")
feats = json.load(open("numerai/features.json"))["feature_sets"]["small"]
import lightgbm as lgb
if mode == "train":
    napi.download_dataset(f"{V}/train.parquet", "/tmp/train.parquet")
    tr = pd.read_parquet("/tmp/train.parquet", columns=["era", "target"] + feats)
    tr = tr[tr["era"].isin(tr["era"].unique()[::4])]          # every 4th era keeps memory low
    m = lgb.LGBMRegressor(n_estimators=2000, learning_rate=0.01, max_depth=5, num_leaves=31, colsample_bytree=0.1)
    m.fit(tr[feats], tr["target"]); m.booster_.save_model("numerai/model.txt"); print("trained")
else:
    if not os.path.exists("numerai/model.txt"): sys.exit("Run once with mode=train first")
    napi.download_dataset(f"{V}/live.parquet", "/tmp/live.parquet")
    live = pd.read_parquet("/tmp/live.parquet", columns=feats)
    preds = lgb.Booster(model_file="numerai/model.txt").predict(live[feats])
    out = pd.Series(preds, index=live.index).rank(pct=True).to_frame("prediction"); out.to_csv("/tmp/preds.csv")
    models = {k.lower(): v for k, v in napi.get_models().items()}
    mid = models[os.environ["NUMERAI_MODEL_NAME"].lower()]
    print(napi.upload_predictions("/tmp/preds.csv", model_id=mid))
