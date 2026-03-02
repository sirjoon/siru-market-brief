"""
SPY Market Intelligence Brief Generator
Runs at 7:00 AM IST (pre-market) and 9:00 PM IST (end-of-day)
"""

import anthropic
import os
import sys
import datetime
import requests
import json
from pathlib import Path
from zoneinfo import ZoneInfo

# ── Config ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID", "")

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime.datetime.now(IST)
DATE_STR  = NOW.strftime("%A, %B %d, %Y")
TIME_STR  = NOW.strftime("%I:%M %p IST")
FILE_DATE = NOW.strftime("%Y-%m-%d")

# ── Prompts ───────────────────────────────────────────────────────────────────

MORNING_PROMPT = f"""You are a professional buy-side equity analyst running a morning intelligence briefing.
Today is {DATE_STR}. Current time: {TIME_STR}. US pre-market session is active.

Use your web search tool to scrape the LATEST data from these sources RIGHT NOW:
- https://www.briefing.com/general/news
- https://www.marketwatch.com/latest-news
- https://www.barchart.com/stocks/market-pulse
- https://www.tradingview.com/news/
- https://finviz.com/news.ashx
- https://earningswhispers.com/calendar

Build a dense, data-rich morning brief. No fluff. Every number must be sourced.

---

# 🌅 SPY MORNING BRIEF — {DATE_STR}
## Sentiment Score: [X/10] | [EXTREME FEAR / FEAR / NEUTRAL / GREED / EXTREME GREED]

---

## 1. OVERNIGHT CHANGES
- SPY futures: [price, % vs yesterday close]
- ES1! (S&P futures): [direction, key level]
- What macro event caused any gap up/down overnight?
- Key overnight news from Europe/Asia affecting US open
- Dollar (DXY), Gold, Oil, 10yr Yield direction

## 2. 🚨 LIFE-CHANGING CATALYST STOCKS (Pre-market movers)
Stocks with: earnings surprise >15%, FDA decision, M&A, major contract, analyst re-rating >30% PT move
Format each:
| TICKER | Catalyst | Pre-mkt % | Market Cap | Why It Matters |
Only include if catalyst is GENUINELY significant. Min 3, max 8 stocks.

## 3. 💥 MASSIVE EARNINGS SURPRISES (Last 12 hours)
Companies that beat/missed EPS by largest margin:
| TICKER | EPS Actual | EPS Est | Beat% | Rev Actual | Rev Est | Guidance | Signal |
Flag: raised guidance = 🟢, cut guidance = 🔴, in-line = 🟡

## 4. 📊 TODAY'S LEADING THEMES (Rate 1-10, Bullish/Bearish/Neutral)
For each theme state: Direction | Strength | Key datapoint
- Inflation/Fed narrative
- AI sector momentum  
- Tariff/trade developments
- Sector rotation signal
- Geopolitical risk

## 5. 🔄 SECTOR ROTATION SNAPSHOT
Which of these are showing pre-market strength vs SPY?
XLK, XLV, XLE, XLF, XLU, XLI, XLC, XLY, XLP, XLB, XLRE
Format: [TICKER] [+/-X%] [LEADING/IMPROVING/WEAKENING/LAGGING]

## 6. 📅 ECONOMIC CALENDAR TODAY
| Time (ET) | Event | Expected | Prior | Market Impact |
Flag high-impact events with ⚡

## 7. 🎯 TOP 3 SETUPS TO WATCH
| TICKER | Long/Short | Catalyst | Key Level | Stop | Target |

## 8. SENTIMENT SCORE BREAKDOWN
Score: X/10 — [Label]
Driver 1: [specific data point]
Driver 2: [specific data point]  
Driver 3: [specific data point]
vs Yesterday: [Higher/Lower/Same] — [reason]

---
Sources checked: briefing.com, marketwatch, barchart, tradingview, finviz
Generated: {TIME_STR}
"""

EVENING_PROMPT = f"""You are a hedge fund daily PnL analyst. Market closed approximately 1.5 hours ago.
Today is {DATE_STR}. Current time: {TIME_STR}.

Use your web search tool to pull end-of-day data from:
- https://www.briefing.com/general/news
- https://www.marketwatch.com/latest-news
- https://www.barrons.com/market-data
- https://wsj.com/markets
- https://www.barchart.com/stocks/market-pulse
- https://finviz.com/news.ashx

Build a sharp EOD debrief. Call out what surprised you. Flag divergences between morning thesis and actual price action.

---

# 🌆 SPY EVENING DEBRIEF — {DATE_STR}
## EOD Sentiment Score: [X/10] | [Label] | vs Morning: [↑/↓/→]

---

## 1. HOW THE DAY PLAYED OUT
- SPY: Open [X] → High [X] → Low [X] → Close [X] ([+/-]%)
- Volume vs 20-day avg: [Heavy/Normal/Light] ([X]M shares)
- VIX close: [X] ([+/-]% change)
- Intraday narrative: [1-2 sentences on what drove price action]

## 2. 🏆 BIGGEST MOVERS TODAY
Top 5 Winners:
| TICKER | % Gain | Volume vs Avg | Catalyst |

Top 5 Losers:
| TICKER | % Loss | Volume vs Avg | Catalyst |

## 3. 🚨 LIFE-CHANGING NEWS THAT BROKE TODAY
Stocks that moved >10% on significant catalysts:
| TICKER | Event Type | % Move | Follow-Through Potential | Tradeable? |
Event types: FDA_APPROVAL / M&A / EARNINGS / GUIDANCE / LEGAL / MACRO

## 4. 💥 EARNINGS SURPRISE SCORECARD
If earnings were reported today:
| TICKER | EPS Beat% | Rev Beat% | Guidance | Stock Reaction | PED Setup? |
Beat rate today vs 73% historical average: [X%]
Guidance raise/cut ratio: [X raises : X cuts]

## 5. 📊 MORNING THESIS CHECK
For each theme from the morning brief — did it play out?
| Theme | Morning Call | Actual | CONFIRMED/REVERSED/MIXED | Key Observation |

## 6. 🔄 SECTOR ROTATION FINAL READING
| Sector | EOD % | vs SPY | Quadrant Signal |
Strongest rotation INTO: [sector]
Strongest rotation OUT OF: [sector]

## 7. 🌙 OVERNIGHT RISK FACTORS
Earnings after close today (key names and consensus estimates):
Fed speakers tonight/tomorrow:
International data overnight (ECB, BOJ, China PMI, etc):
Geopolitical flash points:

## 8. 📋 TOMORROW'S WATCHLIST
| TICKER | Setup Type | Catalyst | Entry Zone | Risk Level |
Based on: tonight's earnings catalyst, technical setup, news flow

## 9. SENTIMENT SCORE CHANGE
Morning: [X]/10 | EOD: [Y]/10 | Change: [↑ Improved / ↓ Deteriorated / → Stable]
Primary reason for change: [1 sentence]
What surprised most: [1 sentence]

---
Sources checked: briefing.com, barrons, wsj, marketwatch, barchart
Generated: {TIME_STR}
"""

CATALYST_PROMPT = f"""You are a catalyst-driven equity screener. Today is {DATE_STR}.

Search the web RIGHT NOW for stocks matching these criteria in the last 24 hours.
Search: site:briefing.com earnings, barchart gaps today, marketwatch stocks movers, 
        finviz news today, unusualwhales flow, earningswhispers today

---

# 🔍 CATALYST SCREENER — {DATE_STR}

## CATEGORY A: EARNINGS MONSTERS (EPS beat >20% OR Rev beat >15%)
| TICKER | EPS Actual vs Est | Rev Actual vs Est | Guidance | Reaction % | Grade |
Grade: A+ (massive beat + raised guide), A (beat + raised), B (beat), C (in-line), F (miss)

## CATEGORY B: LIFE-CHANGING NEWS
| TICKER | Event | Details | % Move | Market Cap | Float | Short Interest | Risk |
Events: FDA approval, Phase 3 result, Major M&A, Patent, DOJ/SEC, CEO change

## CATEGORY C: UNUSUAL OPTIONS ACTIVITY
Search unusualwhales.com and barchart unusual options for today
| TICKER | Strike | Expiry | Premium | Bullish/Bearish | Rationale |
Only include blocks > $250K notional

## CATEGORY D: SHORT CANDIDATES (Negative catalysts)
| TICKER | Event | Miss% | Guidance Cut | Technical Break | Short Setup Score /10 |

## SUMMARY RANKING (Top 10 overall by opportunity score)
Rank all findings by: Catalyst Quality × Magnitude × Timing × Risk/Reward
| Rank | TICKER | Category | Signal | Urgency | Action |

Generated: {TIME_STR}
"""


# ── Core functions ─────────────────────────────────────────────────────────────

def run_brief(brief_type: str) -> str:
    """Call Claude API with web search enabled."""
    print(f"\n{'='*60}")
    print(f"  Running {brief_type.upper()} brief | {TIME_STR}")
    print(f"{'='*60}\n")

    if brief_type == "morning":
        prompt = MORNING_PROMPT
    elif brief_type == "evening":
        prompt = EVENING_PROMPT
    elif brief_type == "catalyst":
        prompt = CATALYST_PROMPT
    else:
        raise ValueError(f"Unknown brief type: {brief_type}")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
        }],
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract text from response (may include tool_use blocks)
    output_parts = []
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            output_parts.append(block.text)

    result = "\n".join(output_parts)
    print(f"✅ Brief generated ({len(result)} chars)")
    return result


def save_brief(content: str, brief_type: str) -> str:
    """Save brief to dated markdown file."""
    briefs_dir = Path("briefs")
    briefs_dir.mkdir(exist_ok=True)

    filename = f"{FILE_DATE}_{brief_type}.md"
    filepath = briefs_dir / filename

    header = f"---\ndate: {FILE_DATE}\ntype: {brief_type}\ngenerated: {TIME_STR}\n---\n\n"
    with open(filepath, "w") as f:
        f.write(header + content)

    print(f"💾 Saved: {filepath}")
    return str(filepath)


def send_telegram(content: str, brief_type: str):
    """Send brief to Telegram in chunks (4096 char limit)."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram not configured — skipping notification")
        return

    emoji_map = {
        "morning":  "🌅",
        "evening":  "🌆",
        "catalyst": "🔍"
    }
    emoji = emoji_map.get(brief_type, "📊")

    header = f"{emoji} *SPY {brief_type.upper()} BRIEF* — {DATE_STR}\n\n"
    full_message = header + content

    # Split into 4000-char chunks at newline boundaries
    chunks = []
    current = ""
    for line in full_message.split("\n"):
        if len(current) + len(line) + 1 > 4000:
            chunks.append(current)
            current = line + "\n"
        else:
            current += line + "\n"
    if current:
        chunks.append(current)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    for i, chunk in enumerate(chunks):
        part_label = f"\n\n_(part {i+1}/{len(chunks)})_" if len(chunks) > 1 else ""
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk + part_label,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }
        resp = requests.post(url, data=payload, timeout=30)
        if resp.status_code == 200:
            print(f"📱 Telegram chunk {i+1}/{len(chunks)} sent")
        else:
            print(f"❌ Telegram error: {resp.status_code} — {resp.text[:200]}")


def main():
    brief_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    print(f"\n🚀 Starting {brief_type} brief generation...")
    print(f"   Date: {DATE_STR}")
    print(f"   Time: {TIME_STR}")

    content  = run_brief(brief_type)
    filepath = save_brief(content, brief_type)
    send_telegram(content, brief_type)

    print(f"\n✅ Done! Brief saved to {filepath}")


if __name__ == "__main__":
    main()
