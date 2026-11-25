"""Trains a small finance-headline sentiment model (TF-IDF + logistic regression) and pushes it to Hugging Face.
Training data: zeroshot/twitter-financial-news-sentiment (labels 0 bearish, 1 bullish, 2 neutral). Check its licence on the dataset page."""
import os, json, joblib, datetime as dt
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
ds = load_dataset("zeroshot/twitter-financial-news-sentiment")
tr, va = ds["train"], ds["validation"]
model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True), LogisticRegression(max_iter=2000, class_weight="balanced"))
model.fit(tr["text"], tr["label"])
rep = classification_report(va["label"], model.predict(va["text"]), target_names=["bearish", "bullish", "neutral"], output_dict=True)
os.makedirs("hf/out", exist_ok=True); joblib.dump(model, "hf/out/model.joblib")
card = f"""---
license: mit
tags: [finance, sentiment, sklearn]
---
# Finance headline sentiment (TF-IDF + logistic regression)
Retrained monthly by GitHub Actions in markets-lab. Last trained {dt.date.today()}.
Validation accuracy: {rep['accuracy']:.3f}. Macro F1: {rep['macro avg']['f1-score']:.3f}.
Labels: 0 bearish, 1 bullish, 2 neutral. Trained on zeroshot/twitter-financial-news-sentiment.
Limits: short English headlines only; not investment advice.
"""
open("hf/out/README.md", "w").write(card); json.dump(rep, open("hf/out/metrics.json", "w"), indent=1)
repo = os.environ.get("HF_MODEL_REPO")
if os.environ.get("HF_TOKEN") and repo:
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"]); api.create_repo(repo, exist_ok=True)
    api.upload_folder(folder_path="hf/out", repo_id=repo, commit_message=f"Monthly retrain {dt.date.today()}")
print(card)
