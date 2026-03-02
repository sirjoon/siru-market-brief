# 📊 SPY Market Intelligence Brief
> Automated daily briefings delivered to Telegram — 7 AM & 9 PM IST

## What You Get

| Time | Brief | Contents |
|------|-------|----------|
| 7:00 AM IST | Pre-Market | Overnight changes, catalyst stocks, earnings surprises, sector rotation, sentiment score |
| 9:00 PM IST | End-of-Day | Day recap, winners/losers, thesis check, tomorrow's watchlist |
| On-demand | Catalyst Scan | Life-changing news, earnings monsters, unusual options flow |

---

## ⚡ Setup in 4 Steps (20 minutes total)

### Step 1 — Create the GitHub Repo

```bash
# Option A: Use GitHub CLI
gh repo create siru-market-brief --private --clone
cd siru-market-brief

# Option B: Manual
# Go to github.com → New Repository → Name: siru-market-brief → Private → Create
# Then: git clone https://github.com/YOUR_USERNAME/siru-market-brief
```

Copy all files from this zip into the repo folder.

```bash
git add .
git commit -m "initial setup"
git push origin main
```

---

### Step 2 — Get Your Telegram Bot (10 minutes)

1. Open Telegram → search **@BotFather** → `/start`
2. Send `/newbot` → follow prompts → give it a name like `SiruMarketBrief`
3. BotFather gives you a **TOKEN** like `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxx`
4. Start a chat with your new bot → send `/start`
5. Get your **CHAT_ID**:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   Look for `"chat":{"id": 123456789}` — that number is your CHAT_ID

---

### Step 3 — Add GitHub Secrets

Go to your repo on GitHub:
`Settings → Secrets and variables → Actions → New repository secret`

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com |
| `TELEGRAM_TOKEN` | The token from BotFather |
| `TELEGRAM_CHAT_ID` | Your numeric chat ID |

---

### Step 4 — Enable Actions & Test

1. Go to your repo → **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. Click **"SPY Market Intelligence Brief"** → **"Run workflow"** → select `morning` → **Run**
4. Watch it execute (takes 2–3 minutes)
5. Check your Telegram — the brief should arrive!

---

## 📁 Repo Structure

```
siru-market-brief/
├── .github/
│   └── workflows/
│       └── market-brief.yml     ← GitHub Actions schedule
├── src/
│   └── brief_generator.py       ← Main script with all 3 prompts
├── briefs/                      ← Auto-generated (gitignored initially)
│   ├── 2026-03-01_morning.md
│   ├── 2026-03-01_evening.md
│   └── ...
├── requirements.txt
└── README.md
```

---

## 🕐 Schedule

| Cron | UTC | IST | Brief |
|------|-----|-----|-------|
| `30 1 * * 1-5`  | 01:30 UTC | 07:00 AM | Morning pre-market |
| `30 15 * * 1-5` | 15:30 UTC | 09:00 PM | Evening end-of-day |

Runs Monday–Friday only. No weekends.

---

## 🔧 Running Manually

**From GitHub UI:**
Actions → SPY Market Intelligence Brief → Run workflow → Choose type → Run

**From terminal (local test):**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export TELEGRAM_TOKEN="7123..."
export TELEGRAM_CHAT_ID="123456789"

python src/brief_generator.py morning
python src/brief_generator.py evening
python src/brief_generator.py catalyst
```

---

## 💰 Cost Estimate

| Usage | Tokens/run | Cost/run | Monthly (44 runs) |
|-------|-----------|----------|-------------------|
| Morning brief | ~6,000 | ~$0.06 | ~$2.64 |
| Evening brief | ~6,000 | ~$0.06 | ~$2.64 |
| **Total** | | | **~$5.28/month** |

Uses `claude-opus-4-6` with web search. Adjust to `claude-sonnet-4-6` to halve costs.

---

## 🚀 Upgrade Path

Once this is running cleanly for 2 weeks:

1. **Add catalyst screener** — run at 11 AM IST (US market open +30 min)
2. **Add options flow alert** — unusual activity scan at 2 PM IST
3. **Build the HTML dashboard** — connect to your existing RRG + sentiment dashboard
4. **Add sector rotation alert** — Telegram push when any sector changes RRG quadrant
5. **Weekly Sunday report** — full week review + next week setup

---

## ❓ Troubleshooting

**Workflow doesn't trigger at scheduled time:**
GitHub Actions cron can be delayed 5–15 min. Also, repos with no activity for 60 days 
have schedules disabled — just push a commit to re-enable.

**Telegram message not arriving:**
- Verify you sent `/start` to your bot first
- Double-check CHAT_ID (it's a number, not your username)
- Check the Actions log for the error message

**API key error:**
- Verify secret name is exactly `ANTHROPIC_API_KEY` (no spaces)
- Check your Anthropic console has billing enabled

**Brief quality is poor:**
The prompts in `brief_generator.py` are tunable. Adjust the sources list, 
add/remove sections, change the tone. Re-run manually to test immediately.
