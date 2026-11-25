"""Numerai tournament model. 'train' downloads training data and fits LightGBM on the small feature set;
'submit' predicts the live round and uploads. Never stake NMR. Dataset version names change: check numer.ai/data."""
import os, sys, json, pandas as pd
from numerapi import NumerAPI
napi = NumerAPI(os.environ.get("NUMERAI_PUBLIC_ID"), os.environ.get("NUMERAI_SECRET_KEY"))
# newest dataset version that has features, train and live files (v6.0 as of Nov 2026)
_vs = sorted({d.split("/")[0] for d in napi.list_datasets() if d.endswith("live.parquet") and d.startswith("v")}, key=lambda v: [int(x) for x in v[1:].split(".")])
V = os.environ.get("NUMERAI_DATA_VERSION") or _vs[-1]; print("Numerai dataset version", V)
mode = sys.argv[1] if len(sys.argv) > 1 else "submit"
napi.download_dataset(f"{V}/features.json", "numerai/features.json")
feats = json.load(open("numerai/features.json"))["feature_sets"]["small"]
import lightgbm as lgb
def prep(df):
    """v6 stores some features as non-numeric types; convert to numbers (category codes as fallback)."""
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            num = pd.to_numeric(df[c].astype(str), errors="coerce")
            df[c] = num if num.notna().mean() > 0.9 else df[c].astype("category").cat.codes
    return df.astype("float32")
if mode == "train":
    napi.download_dataset(f"{V}/train.parquet", "/tmp/train.parquet")
    import pyarrow.parquet as pq
    names = pq.read_schema("/tmp/train.parquet").names
    era = next((c for c in ("era", "date", "era_date") if c in names), None)      # v6 renamed the era column
    tgt = "target" if "target" in names else next(c for c in names if c.startswith("target"))
    print("columns used:", era, tgt, len(feats), "features")
    tr = pd.read_parquet("/tmp/train.parquet", columns=([era] if era else []) + [tgt] + feats).rename(columns={tgt: "target"})
    tr = tr[tr[era].isin(tr[era].unique()[::4])] if era else tr.iloc[::4]   # every 4th era keeps memory low
    tr = tr.dropna(subset=["target"])
    m = lgb.LGBMRegressor(n_estimators=2000, learning_rate=0.01, max_depth=5, num_leaves=31, colsample_bytree=0.1)
    m.fit(prep(tr[feats]), tr["target"].astype("float32")); m.booster_.save_model("numerai/model.txt"); print("trained")
else:
    if not os.path.exists("numerai/model.txt"): sys.exit("Run once with mode=train first")
    napi.download_dataset(f"{V}/live.parquet", "/tmp/live.parquet")
    import pyarrow.parquet as pq
    idc = next((c for c in ("id", "numerai_ticker") if c in pq.read_schema("/tmp/live.parquet").names), None)
    live = pd.read_parquet("/tmp/live.parquet", columns=feats + ([idc] if idc else []))
    if idc: live = live.set_index(idc)          # v6 files carry the row id as a column
    preds = lgb.Booster(model_file="numerai/model.txt").predict(prep(live[feats]))
    out = pd.Series(preds, index=live.index).rank(pct=True).to_frame("prediction"); out.to_csv("/tmp/preds.csv")
    models = {k.lower(): v for k, v in napi.get_models().items()}
    mid = models[os.environ["NUMERAI_MODEL_NAME"].lower()]
    print(napi.upload_predictions("/tmp/preds.csv", model_id=mid))
