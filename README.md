# markets-lab

Automated daily research log on ASX and Hong Kong markets: 21 trackers, a website, a newsletter, a podcast,
social posts and short videos, with **one Approve button** before anything public goes out.
Built by Adam Lam. General information only, not financial advice.

## What happens every weekday at 7 pm Sydney
1. **build** (automatic): runs `trackers/`, writes notes and charts, builds the website pages, newsletter, podcast script and audio,
   social posts and a 20-second vertical video. Uploads datasets to Kaggle, Hugging Face and the Google Sheet (data only).
2. **publish** (waits for you): your phone gets "Review pending deployment" in the GitHub app. Open the run summary to read the drafts
   (full preview: the `drafts` artifact, `out/preview.html`). Tap **Approve and deploy** to post everything, or **Reject** to post nothing.
3. **pages**: the website goes live at `https://<username>.github.io/markets-lab`.

Trackers with nothing new that day are skipped. A tracker that errors is skipped and listed in the summary; the rest still run.

## One-time setup (about a day)
1. **Create a public repo** called `markets-lab` on GitHub and upload this folder (GitHub > Add file > Upload files, or `git push`).
2. **Edit `config.yaml`**: replace every `YOUR-...` value (GitHub username, Kaggle and Hugging Face usernames, SEC contact email).
3. **Turn on Pages**: Settings > Pages > Source: **GitHub Actions**.
4. **Create the Approve button**: Settings > Environments > New environment `publish` > tick **Required reviewers** > add yourself > Save.
5. **Install the GitHub mobile app** and turn on notifications for deployment reviews.
6. **Add secrets** (Settings > Secrets and variables > Actions > New repository secret). Each is optional; anything missing is skipped.

| Secret | Where to get it | Used for |
|---|---|---|
| `AI_API_KEY` | console.anthropic.com (set a monthly spend limit) | Written notes; without it notes are plain facts |
| `POSTIZ_API_KEY` | postiz.com > Settings > Developers > Public API | LinkedIn, Threads, X, Instagram, TikTok, YouTube |
| `NEWSLETTER_API_KEY` | buttondown.com > Settings > API (or Ghost Admin API key `id:secret`) | Daily newsletter |
| `KAGGLE_USERNAME`, `KAGGLE_KEY` | kaggle.com > Settings > Create New Token | Kaggle dataset |
| `HF_TOKEN` | huggingface.co > Settings > Access Tokens (write) | HF dataset and monthly model |
| `GOOGLE_SERVICE_ACCOUNT` | Google Cloud > service account > JSON key (paste whole JSON); share the Sheet with its email | Google Sheet for Tableau Public and Power BI |
| `NUMERAI_PUBLIC_ID`, `NUMERAI_SECRET_KEY` | numer.ai > Account > API keys (upload-only scope) | Numerai submissions |

   Variables (same page, Variables tab): `HF_MODEL_REPO` (e.g. `yourname/finance-headline-sentiment`), `NUMERAI_MODEL_NAME`.
7. **Connect social accounts in Postiz** (Instagram must be a Business or Creator account linked to a Facebook Page), then copy each
   account's integration ID into `config.yaml > postiz > integrations`. Check `GET /integration-settings/<id>` for each platform and
   adjust `SETTINGS` in `publishers/postiz.py` (YouTube title and privacy, TikTok posting method).
8. **Test**: Actions > daily > Run workflow > demo = 1. Approve it, then check every channel. Then run once with demo = 0.
9. **Podcast**: after the first approved run, submit `https://<username>.github.io/markets-lab/podcast.xml` once to Spotify for Creators
   and Apple Podcasts Connect.

## Feeds you add yourself (check each site's terms first)
- `announcement_feeds`: RSS of ASX announcements you are allowed to read automatically. Feeds trackers 11 to 15.
- `news_feeds`: market headline RSS for the sentiment index (18).
- `job_feeds`: graduate job RSS for the jobs board (19). Posts link out, never copy ads.
- `economic_calendar`: add RBA and ABS dates as they are announced (9).
- `hk_nav_csv_urls`: issuer NAV files, if you want premium/discount (8).

## Other platforms in this repo
- `app/streamlit_app.py`: ETF screener and DCF calculator. Streamlit Community Cloud > New app > this repo > that file.
  Change `RAW` to your username. Refreshes itself from the daily data.
- **Tableau Public and Power BI**: connect to the Google Sheet the build updates (Tableau: tick "keep data in sync"; Power BI: publish to web, scheduled refresh).
- `hf/train_sentiment.py` + `monthly_model.yml`: retrains a finance sentiment model on the 1st of each month and pushes it to Hugging Face.
- `numerai/numerai_model.py` + `numerai.yml`: run once with mode = train, then it submits Tuesday to Saturday. **Never stake NMR.**
- `qc/forward_test_strategy.py`: paste into QuantConnect, backtest, deploy to paper trading.
- `pkg/` + `pypi.yml`: the `asx-shorts` package. Set up trusted publishing on pypi.org (project name `asx-shorts`, check it is free),
  create an environment `pypi`, then push a tag `v0.1.0`.
- `assistant/instructions.md`: paste into a custom GPT or Poe bot.

## Still manual (no posting API, or must be your own work)
TradingView ideas and indicator, Good Judgment Open forecasts, SSRN uploads, open-source pull requests, Gumroad listing (once),
Myfxbook (connect an MT5 **demo** account; you type the investor password), monthly flagship projects.

## Rules built in
Every page, post, chart and video carries "General information only, not financial advice". AI notes are told never to recommend
buying or selling. The forward test is paper only and every signal is committed before the next session. No confidential employer data.

## Run locally
```
pip install -r requirements.txt
DEMO=1 python build_all.py      # synthetic data, no keys needed
python build_all.py             # live data
```
