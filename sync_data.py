"""Runs WITHOUT approval (data only, no public wording): Kaggle and Hugging Face dataset versions, Google Sheet for Tableau/Power BI."""
import os, sys, glob, shutil, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.core import CFG, DATA, TODAY
import pandas as pd
EXP = os.path.join(DATA, "export"); os.makedirs(EXP, exist_ok=True)
for p in glob.glob(os.path.join(DATA, "*.csv")): shutil.copy(p, EXP)
log = []
if os.environ.get("KAGGLE_KEY") and "YOUR-" not in CFG["kaggle_dataset"]:
    json.dump({"title": "ASX Markets Lab daily", "id": CFG["kaggle_dataset"], "licenses": [{"name": "CC-BY-SA-4.0"}]}, open(os.path.join(EXP, "dataset-metadata.json"), "w"))
    r = subprocess.run(["kaggle", "datasets", "version", "-p", EXP, "-m", f"Daily update {TODAY}"], capture_output=True, text=True)
    if r.returncode != 0: r = subprocess.run(["kaggle", "datasets", "create", "-p", EXP, "--public"], capture_output=True, text=True)   # first run: dataset does not exist yet
    log.append("kaggle: " + (r.stdout + r.stderr)[-200:])
if os.environ.get("HF_TOKEN") and "YOUR-" not in CFG["hf_dataset"]:
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"]); api.create_repo(CFG["hf_dataset"], repo_type="dataset", exist_ok=True)
    api.upload_folder(folder_path=EXP, repo_id=CFG["hf_dataset"], repo_type="dataset", commit_message=f"Daily update {TODAY}", allow_patterns=["*.csv"]); log.append("hf: uploaded")
if os.environ.get("GOOGLE_SERVICE_ACCOUNT") and CFG.get("google_sheet_id"):
    import gspread
    gc = gspread.service_account_from_dict(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])); sh = gc.open_by_key(CFG["google_sheet_id"])
    for name in ("core_etf_prices.csv", "t07_sectors.csv", "t02_yields.csv"):
        p = os.path.join(DATA, name)
        if not os.path.exists(p): continue
        df = pd.read_csv(p).fillna(""); title = name[:-4]
        try: ws = sh.worksheet(title)
        except gspread.WorksheetNotFound: ws = sh.add_worksheet(title, rows=1000, cols=30)
        ws.clear(); ws.update([df.columns.tolist()] + df.astype(str).values.tolist())
    log.append("google sheet: updated")
print("\n".join(log) or "no data destinations configured yet")
