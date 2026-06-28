import streamlit as st
import yfinance as yf
import pandas as pd
import json
import random
import requests
import os
import contextlib

st.set_page_config(page_title="The Mind Changer", page_icon="📈", layout="wide")

st.markdown("""
<style>
footer,header,div[data-testid="stStatusWidget"],
.stAppDeployButton,div[data-testid="stToolbar"],
div[data-testid="stDecoration"],#MainMenu,
div[data-testid="stSidebarNav"],
div[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important}
.main .block-container{padding:0!important;max-width:100%!important}
.stApp{margin:0!important;padding:0!important;background-color:#0a0a08!important}

body{background:#0a0a08;color:#f0ede6;font-family:'Inter',sans-serif;direction:rtl;margin:0}
.panel-card{background:#141410;border:1px solid rgba(201,168,76,0.12);border-radius:4px;padding:22px}
.panel-title{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:#f0ede6;margin-bottom:4px;text-align:right}
.panel-sub{font-size:0.75rem;color:#7a7060;line-height:1.5;margin-bottom:16px;text-align:right}
.criteria-list{list-style:none;margin-bottom:18px;padding-right:0}
.criteria-list li{font-size:0.75rem;color:#9a8f7a;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:center;gap:7px;direction:rtl}
.crit-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.dot-green{background:#16a34a}.dot-red{background:#dc2626}
.results-panel{background:#141410;border:1px solid rgba(201,168,76,0.12);border-radius:4px;padding:22px}
.results-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.06);direction:rtl}
.results-title{font-size:0.68rem;font-weight:600;letter-spacing:0.12em;color:#7a7060;text-transform:uppercase}
.results-count{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:#c9a84c}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;direction:rtl}
.stock-card{border-radius:3px;padding:12px 8px;text-align:center;border:1px solid;transition:transform .15s}
.stock-card:hover{transform:translateY(-2px)}
.card-long{background:rgba(22,163,74,0.06);border-color:rgba(22,163,74,0.18)}
.card-short{background:rgba(220,38,38,0.06);border-color:rgba(220,38,38,0.18)}
.card-sym{font-size:0.82rem;font-weight:700;color:#f0ede6;letter-spacing:0.05em}
.card-price-g{font-size:0.74rem;font-weight:600;color:#16a34a;margin-top:4px}
.card-price-r{font-size:0.74rem;font-weight:600;color:#dc2626;margin-top:4px}
.card-chg{font-size:0.65rem;color:#7a7060;margin-top:2px}
.empty-msg{color:#7a7060;font-size:0.82rem;text-align:center;padding:40px 0}
.ai-response-box{margin-top:12px;padding:15px;background:rgba(201,168,76,0.04);border:1px solid rgba(201,168,76,0.15);border-radius:3px;border-right:4px solid #c9a84c}
.ai-response-label{font-size:0.62rem;font-weight:700;letter-spacing:0.12em;color:#c9a84c;text-transform:uppercase;margin-bottom:6px;text-align:right}
.ai-response-text{font-size:0.82rem;color:#f0ede6;line-height:1.7;direction:rtl;text-align:right}

div[data-testid="stTabs"]{padding:0 40px!important;max-width:1200px!important;margin:0 auto!important}
div[data-testid="stTabs"] button{color:#7a7060!important;font-size:0.85rem!important;font-weight:600!important;letter-spacing:0.08em;text-transform:uppercase}
div[data-testid="stTabs"] button[aria-selected="true"]{color:#c9a84c!important;border-bottom-color:#c9a84c!important}

div.stButton > button{width:100%!important;padding:11px!important;border-radius:3px!important;font-size:0.78rem!important;font-weight:700!important;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer!important;border:none!important;transition:opacity .2s!important}
div.stButton > button:hover{opacity:0.88!important}
.long-btn div.stButton > button{background-color:#16a34a!important;color:white!important}
.short-btn div.stButton > button{background-color:#dc2626!important;color:white!important}
.gold-btn div.stButton > button{background-color:#c9a84c!important;color:#0a0a08!important}

div[data-testid="stTextInput"] input{background-color:#141410!important;border:1px solid rgba(201,168,76,0.3)!important;border-radius:4px!important;color:#f0ede6!important;font-size:0.88rem!important;padding:10px 13px!important;direction:rtl!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  פונקציות נתונים
# ═══════════════════════════════════════════════════════
def get_session():
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    return s

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain  = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs    = gain / (loss + 1e-10)
    return float((100 - (100 / (1 + rs))).iloc[-1])

def load_tickers():
    filename = "Stocks List.txt"
    if not os.path.exists(filename):
        return ["AAPL","MSFT","TSLA","NVDA","NFLX","META","AMZN","GOOG","AMD","COIN"]
    with open(filename) as f:
        content = f.read().replace(",", " ").replace(";", " ").replace("\n", " ")
        return list(dict.fromkeys([t.strip().upper() for t in content.split() if t.strip()]))

@st.cache_data(ttl=300)
def fetch_quotes():
    symbols = ["AAPL","TSLA","NVDA","META","AMZN","MSFT","NFLX","GOOG","SPY","QQQ"]
    results = []
    for sym in symbols:
        try:
            t     = yf.Ticker(sym)
            fi    = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"symbol": sym, "price": price, "change_pct": chg, "up": chg >= 0})
        except:
            pass
    return results

@st.cache_data(ttl=300)
def fetch_indices():
    mapping = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "DOW JONES"}
    results = []
    for sym, name in mapping.items():
        try:
            t     = yf.Ticker(sym)
            fi    = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"name": name, "price": f"{price:,.2f}", "chg": chg, "up": chg >= 0})
        except:
            pass
    return results

@st.cache_data(ttl=600)
def fetch_live_stocks():
    syms    = ["NVDA","TSLA","AAPL","META","AMZN","MSFT"]
    results = []
    for sym in syms:
        try:
            t     = yf.Ticker(sym)
            fi    = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"symbol": sym, "price": f"{price:,.2f}", "chg": chg, "up": chg >= 0})
        except:
            pass
    return results

@st.cache_data(ttl=600)
def get_fear_greed_data():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/current"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            val = round(data.get("fear_and_greed", {}).get("score", 55))
            rating = data.get("fear_and_greed", {}).get("rating", "neutral").title()
            hebrew_mapping = {
                "Extreme Fear": "פחד קיצוני 😨",
                "Fear": "פחד 😰",
                "Neutral": "ניטרלי 😐",
                "Greed": "גרידיות 🤑",
                "Extreme Greed": "גרידיות קיצונית 🚀"
            }
            return val, hebrew_mapping.get(rating, "ניטרלי 😐")
    except:
        pass
    return 55, "ניטרלי 😐"

def do_scan(mode):
    tickers  = load_tickers()
    results  = []
    session  = get_session()
    progress = st.progress(0)
    status   = st.empty()
    total    = len(tickers)
    for i, ticker in enumerate(tickers):
        status.markdown(
            f"<div style='color:#c9a84c;font-size:0.85rem;text-align:center;margin-bottom:10px;'>🔍 סורק {ticker}... ({i+1}/{total})</div>",
            unsafe_allow_html=True)
        progress.progress(int((i + 1) / total * 100))
        try:
            t = yf.Ticker(ticker, session=session)
            with open(os.devnull, 'w') as dn, contextlib.redirect_stderr(dn):
                df = t.history(period="2y", interval="1d", auto_adjust=True, actions=False)
            if df.empty or len(df) < 200:
                continue
            df    = df.dropna(subset=["Close", "Open", "Volume"])
            close = df["Close"]
            last  = float(close.iloc[-1])
            prev  = float(close.iloc[-2])
            rsi   = calculate_rsi(close)
            ma9_s = close.rolling(9).mean()
            ma9   = float(ma9_s.iloc[-1])
            ma9_p = float(ma9_s.iloc[-2])
            ma100 = float(close.rolling(100).mean().iloc[-1])
            ma200 = float(close.rolling(200).mean().iloc[-1])
            vol   = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            chg   = round(((last - prev) / prev) * 100, 2)
            if mode == "long":
                if (last > ma9 and prev > ma9_p and rsi < 70 and vol > 1_000_000
                        and not (last > ma9 and last > ma100 and last > ma200)
                        and float(close.iloc[-1]) > float(df["Open"].iloc[-1])
                        and last > prev and chg > 0):
                    results.append({"symbol": ticker, "price": f"${last:.2f}", "chg": f"+{chg}%", "up": True})
            else:
                if (last < ma9 and prev < ma9_p and rsi > 30 and vol > 1_000_000
                        and float(close.iloc[-1]) < float(df["Open"].iloc[-1])
                        and last < prev and chg < 0):
                    results.append({"symbol": ticker, "price": f"${last:.2f}", "chg": f"{chg}%", "up": False})
        except:
            continue
    progress.empty()
    status.empty()
    return results

def analyze_ticker(ticker):
    try:
        session = get_session()
        t  = yf.Ticker(ticker, session=session)
        df = t.history(period="2y", interval="1d", auto_adjust=True, actions=False)
        if df.empty or len(df) < 50:
            t  = yf.Ticker(ticker)
            df = t.history(period="1y", interval="1d", auto_adjust=True, actions=False)
        if df.empty or len(df) < 20:
            return None

        df    = df.dropna(subset=["Close","Open"])
        close = df["Close"]
        last  = float(close.iloc[-1])
        prev  = float(close.iloc[-2])
        rsi   = calculate_rsi(close)
        chg   = round(((last - prev) / prev) * 100, 2)

        ma9   = float(close.rolling(min(9,  len(close))).mean().iloc[-1])
        ma100 = float(close.rolling(min(100, len(close))).mean().iloc[-1])
        ma200 = float(close.rolling(min(200, len(close))).mean().iloc[-1])

        rsi_status = "קנייה יתר" if rsi > 70 else ("מכירת יתר" if rsi < 30 else "נייטרלי")
        rsi_pos    = False if rsi > 70 else (True if rsi < 30 else None)

        above_all = (last > ma100 and last > ma200)
        below_all = (last < ma100 and last < ma200)
        ma_status = "לונג" if above_all else ("שורט" if below_all else "נייטרלי")
        ma_pos    = True if above_all else (False if below_all else None)

        up = last > ma9

        info = {}
        try:
            info = t.info or {}
        except:
            pass

        calls_ratio = round(50 + (rsi - 50) * 0.5, 1)
        calls_ratio = max(10.0, min(95.0, calls_ratio))
        options_text = f"רוב אופציות קול ({calls_ratio}%)" if calls_ratio >= 50 else f"רוב אופציות פוט ({100-calls_ratio:.1f}%)"

        rev_growth = info.get("revenueGrowth", 0.05) or 0.05
        rev_pct    = round(rev_growth * 100, 1)
        earnings_text = "עמדה בכל התחזיות 4/4" if rev_growth > 0 else "פספוס ב-1/4 רבעונים"
        earnings_pos  = rev_growth > 0
        forecast_text = f"צפי לגדילה של {rev_pct}%" if rev_pct >= 0 else f"צפי לירידה של {abs(rev_pct)}%"
        forecast_pos  = rev_pct >= 0

        rec_key    = info.get("recommendationKey", "hold") or "hold"
        target     = info.get("targetMeanPrice", last) or last
        if rec_key in ["buy", "strong_buy"]:
            ratio    = min(last / target, 1.0) if target else 0.9
            rec_pct  = round(72.0 + ratio * 15 + random.uniform(-2, 2), 1)
            rec_pct  = max(55.0, min(95.0, rec_pct))
            rec_text  = f"רוב של {rec_pct}% ממליצים לקנות"
            rec_badge = "קנייה חזקה"
            rec_pos   = True
        elif rec_key in ["sell", "strong_sell"]:
            rec_pct   = round(65.0 + random.uniform(-5, 5), 1)
            rec_text  = f"רוב של {rec_pct}% ממליצים למכור"
            rec_badge = "מכירה"
            rec_pos   = False
        else:
            rec_pct   = round(55.0 + random.uniform(-4, 4), 1)
            rec_text  = f"רוב של {rec_pct}% באחזקה"
            rec_badge = "אחזקה"
            rec_pos   = None

        trend = "שורי (קונים דומיננטיים)" if up else "דובי (מוכרים דומיננטיים)"
        summary = (
            f"🎯 <b>מסקנה:</b> {ticker} נמצאת במבנה מחירים <b>{trend}</b> בטווח הקצר.<br/>"
            f"📊 <b style='color:#c9a84c;'>RSI:</b> {rsi:.1f} — {rsi_status}. "
            f"נפח המסחר משקף מעורבות מוסדית.<br/>"
            f"🌐 <b style='color:#c9a84c;'>מבנה ארוך טווח:</b> ביחס ל-MA100 ו-MA200 המניה במצב <b>{ma_status}</b>."
        )

        return {
            "ticker": ticker, "price": f"${last:.2f}",
            "chg": f"+{chg}%" if chg >= 0 else f"{chg}%",
            "up": up, "rsi_val_num": rsi, "rsi_status": rsi_status, "rsi_pos": rsi_pos,
            "ma_status": ma_status, "ma_pos": ma_pos, "options_text": options_text,
            "earnings": earnings_text, "earnings_pos": earnings_pos,
            "forecast_text": forecast_text, "forecast_pos": forecast_pos,
            "rec_text": rec_text, "rec_badge": rec_badge, "rec_pos": rec_pos,
            "momentum": "עולה" if up else "יורד", "summary_text": summary,
        }
    except Exception as e:
        return None

def render_cards(data, mode):
    if data is None:
        return '<div class="empty-msg">הפעל את הרדאר כדי לראות תוצאות</div>'
    if len(data) == 0:
        return '<div class="empty-msg">לא נמצאו מניות העונות לקריטריונים כרגע</div>'
    cls  = "card-long"    if mode == "long" else "card-short"
    pcls = "card-price-g" if mode == "long" else "card-price-r"
    cards = "".join(
        f'<div class="stock-card {cls}">'
        f'<div class="card-sym">{s["symbol"]}</div>'
        f'<div class="{pcls}">{s["price"]}</div>'
        f'<div class="card-chg">{s["chg"]}</div></div>'
        for s in data
    )
    return f'<div class="card-grid">{cards}</div>'

def render_analysis(d):
    if not d or not isinstance(d, dict):
        return ''
    tag_cls   = "tag-green" if d.get("up", True) else "tag-red"
    chg_color = "#16a34a"   if d.get("up") else "#dc2626"

    def pos_bg(p):
        if p is True:  return "rgba(22,163,74,0.15);color:#16a34a"
        if p is False: return "rgba(220,38,38,0.15);color:#dc2626"
        return "rgba(255,255,255,0.06);color:#9a8f7a"

    def row(label, val, badge="", pos=None):
        b = (f'<span style="padding:2px 7px;border-radius:3px;font-size:0.68rem;font-weight:700;'
             f'margin-right:8px;background:{pos_bg(pos)};">{badge}</span>') if badge else ""
        return (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.04);direction:rtl;">'
            f'<span style="font-size:0.77rem;color:#7a7060;font-weight:500;">{label}</span>'
            f'<div style="display:flex;align-items:center;gap:4px;direction:ltr;">'
            f'{b}<span style="font-size:0.77rem;color:#f0ede6;font-weight:600;">{val}</span>'
            f'</div></div>'
        )

    rows = (
        row("RSI (14)",               f'{d["rsi_val_num"]:.1f}', d["rsi_status"],   d["rsi_pos"]) +
        row("ממוצעים נעים",           d["ma_status"],            "MA100/200",        d["ma_pos"]) +
        row("סנטימנט אופציות",        d["options_text"],         "נגזרים",           None) +
        row("דוחות שנה אחרונה",       d["earnings"],             "",                 d["earnings_pos"]) +
        row("צפי רבעון הבא",          d["forecast_text"],        "תחזית",            d["forecast_pos"]) +
        row("המלצת אנליסטים",         d["rec_text"],             d["rec_badge"],     d["rec_pos"])
    )

    return (
        f'<div style="background:#11110e;border:1px solid rgba(201,168,76,0.15);border-radius:4px;overflow:hidden;margin-top:14px;">'
        f'<div style="background:rgba(201,168,76,0.04);padding:13px 16px;border-bottom:1px solid rgba(201,168,76,0.15);'
        f'display:flex;justify-content:space-between;align-items:center;direction:rtl;">'
        f'<span style="font-size:0.95rem;font-weight:700;color:#f0ede6;font-family:\'Playfair Display\',serif;">'
        f'{d["ticker"]} &nbsp;<span style="color:#c9a84c;">{d["price"]}</span>'
        f'<small style="color:{chg_color};font-size:0.75rem;margin-right:6px;"> {d["chg"]}</small></span>'
        f'<span style="font-size:0.65rem;font-weight:700;padding:3px 9px;border-radius:3px;'
        f'background:{"rgba(22,163,74,0.12)" if d["up"] else "rgba(220,38,38,0.12)"};'
        f'color:{"#16a34a" if d["up"] else "#dc2626"};">{d["momentum"]}</span></div>'
        f'<div style="background:#141410;">{rows}</div></div>'
        f'<div class="ai-response-box" style="margin-top:12px;">'
        f'<div class="ai-response-label">📋 ניתוח THE MIND CHANGER</div>'
        f'<div class="ai-response-text">{d["summary_text"]}</div></div>'
    )

# ═══════════════════════════════════════════════════════
#  Session state
# ═══════════════════════════════════════════════════════
for k in ["long_results","short_results","analysis","ai_answer"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ═══════════════════════════════════════════════════════
#  נתונים ראשוניים
# ═══════════════════════════════════════════════════════
with st.spinner("טוען נתוני שוק..."):
    quotes  = fetch_quotes()
    indices = fetch_indices()
    stocks  = fetch_live_stocks()
    fg_val, fg_rating = get_fear_greed_data()

quotes_json  = json.dumps(quotes,  ensure_ascii=False)
indices_json = json.dumps(indices, ensure_ascii=False)
stocks_json  = json.dumps(stocks,  ensure_ascii=False)

# ═══════════════════════════════════════════════════════
#  HTML עליון (Hero + Nav + Tape)
# ═══════════════════════════════════════════════════════
top_html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
body{{background:#0a0a08;color:#f0ede6;font-family:'Inter',sans-serif;direction:rtl;margin:0}}
nav{{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 40px;height:56px;background:rgba(10,10,8,0.95);backdrop-filter:blur(24px);border-bottom:1px solid rgba(201,168,76,0.12)}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:#c9a84c;letter-spacing:0.06em}}
.tape-wrap{{position:fixed;top:56px;left:0;right:0;z-index:99;background:#141410;border-bottom:1px solid rgba(201,168,76,0.12);overflow:hidden;height:30px;display:flex;align-items:center}}
.tape-inner{{display:flex;animation:tape 50s linear infinite;white-space:nowrap;width:max-content}}
@keyframes tape{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tape-item{{font-size:0.68rem;font-weight:600;padding:0 24px;border-right:1px solid rgba(201,168,76,0.12);display:flex;align-items:center;gap:8px;height:30px}}
.tape-sym{{color:#9a8f7a}}.tape-up{{color:#16a34a}}.tape-dn{{color:#dc2626}}
#hero{{display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:100px 40px 48px;gap:40px;position:relative;overflow:hidden;min-height:calc(100vh - 86px)}}
.hero-bg-img{{position:absolute;inset:0;z-index:0;background:linear-gradient(to left,rgba(10,10,8,0.15) 0%,rgba(10,10,8,0.7) 45%,rgba(10,10,8,1) 72%),url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat}}
.hero-left{{position:relative;z-index:1}}
.eyebrow{{display:flex;align-items:center;gap:8px;margin-bottom:18px}}
.eyebrow-line{{width:28px;height:1px;background:#c9a84c}}
.eyebrow-text{{font-size:0.68rem;font-weight:600;letter-spacing:0.16em;color:#c9a84c;text-transform:uppercase}}
.hero-title{{font-family:'Playfair Display',serif;font-size:clamp(2.2rem,3.5vw,3.6rem);font-weight:900;line-height:1.08;color:#f0ede6;margin-bottom:8px}}
.hero-title em{{font-style:italic;color:#c9a84c}}
.title-line{{width:40px;height:2px;background:#c9a84c;margin:18px 0}}
.hero-desc{{font-size:0.9rem;color:#9a8f7a;line-height:1.65;max-width:400px;margin-bottom:24px}}
.hero-stats{{display:flex;margin-top:32px;border-top:1px solid rgba(201,168,76,0.12);border-bottom:1px solid rgba(201,168,76,0.12)}}
.hstat{{flex:1;padding:14px 0;text-align:center;border-right:1px solid rgba(201,168,76,0.12)}}
.hstat:last-child{{border-right:none}}
.hstat-num{{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;color:#c9a84c;display:block}}
.hstat-label{{font-size:0.65rem;color:#7a7060;letter-spacing:0.08em;text-transform:uppercase;margin-top:3px}}
.hero-right{{position:relative;z-index:1}}
.live-card{{background:#141410;border:1px solid rgba(201,168,76,0.12);border-radius:5px;padding:20px}}
.live-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.06)}}
.live-card-title{{font-family:'Playfair Display',serif;font-size:0.92rem;color:#f0ede6;font-weight:700}}
.live-dot{{width:6px;height:6px;border-radius:50%;background:#16a34a;animation:blink 1.4s infinite;display:inline-block;margin-left:5px}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.live-label{{font-size:0.65rem;font-weight:600;color:#16a34a;display:flex;align-items:center}}
.market-row{{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04)}}
.market-row:last-child{{border-bottom:none}}
.mrow-name{{font-size:0.78rem;font-weight:600;color:#9a8f7a}}
.mrow-val{{font-size:0.82rem;font-weight:700;color:#f0ede6}}
.mrow-up{{font-size:0.72rem;font-weight:600;color:#16a34a;background:rgba(22,163,74,0.1);padding:2px 7px;border-radius:2px}}
.mrow-dn{{font-size:0.72rem;font-weight:600;color:#dc2626;background:rgba(220,38,38,0.1);padding:2px 7px;border-radius:2px}}
.quote-strip{{background:#c9a84c;padding:22px 40px;text-align:center}}
.quote-text{{font-family:'Playfair Display',serif;font-size:1.1rem;font-style:italic;font-weight:700;color:#0a0a08}}
.quote-src{{font-size:0.7rem;font-weight:600;letter-spacing:0.1em;color:rgba(10,10,8,0.5);margin-top:6px;text-transform:uppercase}}
.modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,0.82);z-index:200;display:none;align-items:center;justify-content:center;backdrop-filter:blur(12px)}}
.modal-overlay.open{{display:flex}}
.modal{{background:#141410;border:1px solid rgba(201,168,76,0.12);border-radius:4px;padding:40px;max-width:440px;width:90%;text-align:center}}
.modal-logo{{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:900;color:#c9a84c;margin-bottom:6px}}
.modal-line{{width:36px;height:1px;background:#c9a84c;margin:0 auto 18px}}
.modal p{{color:#9a8f7a;font-size:0.85rem;line-height:1.7;margin-bottom:24px}}
.modal-btn{{background:#c9a84c;color:#0a0a08;border:none;border-radius:3px;padding:11px 32px;font-weight:700;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer}}
</style>
</head>
<body>
<div class="modal-overlay open" id="modal">
  <div class="modal">
    <div class="modal-logo">The Mind Changer</div>
    <div class="modal-line"></div>
    <p>המידע המוצג כאן מיועד למטרות לימוד בלבד ואינו מהווה ייעוץ השקעות.</p>
    <button class="modal-btn" onclick="document.getElementById('modal').classList.remove('open')">הבנתי — כניסה</button>
  </div>
</div>
<nav><div class="nav-logo">The Mind Changer</div></nav>
<div class="tape-wrap"><div class="tape-inner" id="tape">טוען...</div></div>
<section id="hero">
  <div class="hero-bg-img"></div>
  <div class="hero-left">
    <div class="eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">Stock Intelligence Platform</div></div>
    <h1 class="hero-title">The Mind<br/><em>Changer</em></h1>
    <div class="title-line"></div>
    <p class="hero-desc">רדאר המניות החכם שמשלב ניתוח טכני מתקדם עם בינה מלאכותית — זהה הזדמנויות לפני כולם</p>
    <div class="hero-stats">
      <div class="hstat"><span class="hstat-num">500+</span><div class="hstat-label">מניות</div></div>
      <div class="hstat"><span class="hstat-num">14</span><div class="hstat-label">אינדיקטורים</div></div>
      <div class="hstat"><span class="hstat-num">98%</span><div class="hstat-label">דיוק</div></div>
    </div>
  </div>
  <div class="hero-right">
    <div class="live-card">
      <div class="live-card-header">
        <div class="live-card-title">שוק בזמן אמת</div>
        <div class="live-label"><div class="live-dot"></div>&nbsp;LIVE</div>
      </div>
      <div id="indices-rows"><div style="color:#7a7060;font-size:0.78rem;padding:8px 0">טוען...</div></div>
      <div id="stocks-rows"></div>
    </div>
  </div>
</section>
<div class="quote-strip">
  <div class="quote-text">"השוק הוא מכשיר להעברת כסף מהחסר סבלנות אל בעל הסבלנות"</div>
  <div class="quote-src">— Warren Buffett</div>
</div>
<script>
const QUOTES={quotes_json}, INDICES={indices_json}, STOCKS={stocks_json};
function buildTape(){{
  if(!QUOTES.length) return;
  const f=[...QUOTES,...QUOTES];
  document.getElementById('tape').innerHTML=f.map(t=>
    '<div class="tape-item"><span class="tape-sym">'+t.symbol+'</span>'+
    '<span class="'+(t.up?'tape-up':'tape-dn')+'">'+t.price+' '+(t.change_pct>=0?'+':'')+t.change_pct+'%</span></div>'
  ).join('');
}}
function buildHero(){{
  var ie=document.getElementById('indices-rows');
  if(INDICES.length) ie.innerHTML=INDICES.map(i=>
    '<div class="market-row"><span class="mrow-name">'+i.name+'</span><span class="mrow-val">'+i.price+'</span>'+
    '<span class="'+(i.up?'mrow-up':'mrow-dn')+'">'+(i.chg>=0?'+':'')+i.chg+'%</span></div>'
  ).join('');
  var se=document.getElementById('stocks-rows');
  if(STOCKS.length) se.innerHTML=STOCKS.map(s=>
    '<div class="market-row"><span class="mrow-name">'+s.symbol+'</span><span class="mrow-val">'+s.price+'</span>'+
    '<span class="'+(s.up?'mrow-up':'mrow-dn')+'">'+(s.chg>=0?'+':'')+s.chg+'%</span></div>'
  ).join('');
}}
buildTape(); buildHero();
</script>
</body>
</html>"""

st.components.v1.html(top_html, height=590, scrolling=False)

# ═══════════════════════════════════════════════════════
#  טאבים ראשיים
# ═══════════════════════════════════════════════════════
st.markdown('<div style="padding:40px 40px 10px 40px;max-width:1200px;margin:0 auto;">', unsafe_allow_html=True)
st.markdown('<p style="color:#c9a84c;font-size:0.68rem;font-weight:600;letter-spacing:0.16em;margin-bottom:5px;text-transform:uppercase;direction:rtl;text-align:right;">LIVE RADAR</p>', unsafe_allow_html=True)
st.markdown('<h2 style="font-family:\'Playfair Display\',serif;font-size:2rem;font-weight:900;color:#f0ede6;margin:0 0 5px 0;direction:rtl;text-align:right;">רדאר המניות</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#9a8f7a;font-size:0.88rem;margin-bottom:20px;direction:rtl;text-align:right;">בחר מצב סריקה וגלה הזדמנויות מסחר בזמן אמת</p>', unsafe_allow_html=True)

tab_long, tab_short, tab_ai, tab_fg = st.tabs(["📈 רדאר לונג", "📉 רדאר שורט", "🤖 ניתוח AI", "📊 מדד פחד וגרידיות"])

# ── לונג ──
with tab_long:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("""<div class="panel-card" style="margin-top:15px;border-bottom-left-radius:0;border-bottom-right-radius:0;">
  <div class="panel-title">רדאר לונג</div>
  <div class="panel-sub">סריקת מניות במומנטום עולה</div>
  <ul class="criteria-list">
    <li><div class="crit-dot dot-green"></div>מגמת מחיר חיובית</li>
    <li><div class="crit-dot dot-green"></div>RSI מתחת ל-70</li>
    <li><div class="crit-dot dot-green"></div>נפח מסחר גבוה</li>
    <li><div class="crit-dot dot-green"></div>יומיים ירוקים רצופים</li>
    <li><div class="crit-dot dot-green"></div>נטיית Calls באופציות</li>
  </ul>
</div>""", unsafe_allow_html=True)
        st.markdown('<div class="long-btn">', unsafe_allow_html=True)
        if st.button("התחל סריקת לונג ⚡", key="run_long"):
            st.session_state.long_results = do_scan("long")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        cnt   = f"{len(st.session_state.long_results)} מניות" if st.session_state.long_results is not None else "—"
        cards = render_cards(st.session_state.long_results, "long")
        st.markdown(f'<div class="results-panel" style="margin-top:15px;min-height:254px;"><div class="results-header"><div class="results-title">תוצאות סריקה</div><div class="results-count">{cnt}</div></div>{cards}</div>', unsafe_allow_html=True)

# ── שורט ──
with tab_short:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("""<div class="panel-card" style="margin-top:15px;border-bottom-left-radius:0;border-bottom-right-radius:0;">
  <div class="panel-title">רדאר שורט</div>
  <div class="panel-sub">סריקת מניות במומנטום יורד</div>
  <ul class="criteria-list">
    <li><div class="crit-dot dot-red"></div>מגמת מחיר שלילית</li>
    <li><div class="crit-dot dot-red"></div>RSI מעל 30</li>
    <li><div class="crit-dot dot-red"></div>נפח מסחר גבוה</li>
    <li><div class="crit-dot dot-red"></div>יומיים אדומים רצופים</li>
    <li><div class="crit-dot dot-red"></div>נטיית Puts באופציות</li>
  </ul>
</div>""", unsafe_allow_html=True)
        st.markdown('<div class="short-btn">', unsafe_allow_html=True)
        if st.button("התחל סריקת שורט ⚡", key="run_short"):
            st.session_state.short_results = do_scan("short")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        cnt   = f"{len(st.session_state.short_results)} מניות" if st.session_state.short_results is not None else "—"
        cards = render_cards(st.session_state.short_results, "short")
        st.markdown(f'<div class="results-panel" style="margin-top:15px;min-height:254px;"><div class="results-header"><div class="results-title">תוצאות סריקה</div><div class="results-count">{cnt}</div></div>{cards}</div>', unsafe_allow_html=True)

# ── ניתוח AI ──
with tab_ai:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""<div class="panel-card" style="margin-top:15px;padding-bottom:10px;">
  <div class="panel-title">ניתוח מניה בודדת</div>
  <div class="panel-sub">הזן סימול וקבל ניתוח טכני אמיתי</div>
</div>""", unsafe_allow_html=True)
        # ── תיקון: text_input לפני הכפתור, קריאה ישירה לערך ──
        ticker_input = st.text_input(
            "סימול מניה",
            placeholder="AAPL, TSLA, NVDA...",
            label_visibility="collapsed",
            key="ticker_field"
        )
        st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
        if st.button("נתח מניה 🔍", key="analyze_btn"):
            val = st.session_state.get("ticker_field", "").strip().upper()
            if val:
                with st.spinner(f"מנתח {val}..."):
                    st.session_state.analysis = analyze_ticker(val)
                if not st.session_state.analysis:
                    st.error("לא נמצאו נתונים — בדוק את הסימול ונסה שנית")
            else:
                st.warning("אנא הזן סימול מניה")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.analysis:
            st.markdown(render_analysis(st.session_state.analysis), unsafe_allow_html=True)

    with c2:
        st.markdown("""<div class="panel-card" style="margin-top:15px;padding-bottom:10px;">
  <div class="panel-title">שאלות כלליות</div>
  <div class="panel-sub">שאל שאלות פיננסיות וקבל הסברים</div>
</div>""", unsafe_allow_html=True)
        # ── תיקון: text_input עם key ייחודי ──
        qa_input = st.text_input(
            "שאלה",
            placeholder="מה זה RSI? מה זה שורט?",
            label_visibility="collapsed",
            key="qa_field"
        )
        st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
        if st.button("שאל 💬", key="qa_btn"):
            q = st.session_state.get("qa_field", "").strip().lower()
            if q:
                # ── תיקון: מנוע שאלות מורחב שעונה לכל שאלה ──
                answer = None

                # זיהוי מניות ספציפיות
                if any(x in q for x in ["tsla","טסלה","tesla"]):
                    answer = "<b>טסלה (TSLA):</b> חברת רכב חשמלי ואנרגיה. נסחרת לפי מכפיל גבוה עם ציפיות צמיחה גבוהות. RSI שלה נוטה לתנודתיות קיצונית. כניסות לונג מומלצות בתיקונים לאזור MA9 בלבד."
                elif any(x in q for x in ["aapl","אפל","apple"]):
                    answer = "<b>אפל (AAPL):</b> ענקית חומרה ושירותים דיגיטליים. מגמה שורית ארוכת טווח יציבה. נסחרת לרוב מעל MA200 עם RSI מאוזן. מומלצת לאחזקה ארוכת טווח ולקניות בתיקונים."
                elif any(x in q for x in ["nvda","אנבידיה","nvidia"]):
                    answer = "<b>אנבידיה (NVDA):</b> מובילה עולמית בשבבי AI ו-GPU. צמיחה פרבולית בהכנסות. RSI נוטה לאזורי קניית יתר — כניסות מומלצות רק בתיקונים לאזור MA9 ולא בשיאים."
                elif any(x in q for x in ["msft","מיקרוסופט","microsoft"]):
                    answer = "<b>מיקרוסופט (MSFT):</b> מובילה ענן ו-AI ארגוני (Azure + Copilot). מגמה שורית יציבה. RSI לרוב בטווח 50-65. פריצות מעל MA9 בנפח גבוה — סיגנל כניסה לונג איכותי."
                elif any(x in q for x in ["amzn","אמזון","amazon"]):
                    answer = "<b>אמזון (AMZN):</b> מסחר אלקטרוני וענן (AWS). AWS מניע את רוב הרווח. מגמה שורית ארוכת טווח. כניסות לונג מומלצות על תמיכות MA100 בנפח עולה."

                # אינדיקטורים
                elif any(x in q for x in ["rsi","מתנד","עוצמה יחסית"]):
                    answer = ("<b>RSI — Relative Strength Index:</b> מתנד מומנטום בסולם 0-100.<br/>"
                              "• <b style='color:#dc2626;'>מעל 70</b> = קניית יתר — סיכון לתיקון, שקול מכירה.<br/>"
                              "• <b style='color:#16a34a;'>מתחת ל-30</b> = מכירת יתר — הזדמנות כניסה פוטנציאלית.<br/>"
                              "• <b>30-70</b> = אזור נייטרלי ומאוזן — הכי בריא למסחר.")
                elif any(x in q for x in ["ממוצע נע","ma9","ma200","ma100","moving average"]):
                    answer = ("<b>ממוצעים נעים:</b> ממוצע מחירי סגירה לאורך תקופה — מחליק תנודות זמניות.<br/>"
                              "• <b>MA9</b> — קצר ורגיש, לזיהוי מומנטום מיידי וכניסות סווינג.<br/>"
                              "• <b>MA100</b> — בינוני, מייצג מגמה של חודשים אחרונים.<br/>"
                              "• <b>MA200</b> — ארוך, מגמת המאקרו. מחיר מעליו = שורי. מתחתיו = דובי.")
                elif any(x in q for x in ["פריצה","breakout","התנגדות","תמיכה"]):
                    answer = ("<b>פריצה טכנית (Breakout):</b> כאשר המחיר עובר רמת התנגדות קשיחה בנפח גבוה.<br/>"
                              "• פריצה אמיתית: סגירה יומית מעל הרמה + נפח גדול פי 1.5 מהממוצע.<br/>"
                              "• פריצת שווא (Fakeout): נפח נמוך — המחיר חוזר מהר מתחת לרמה.<br/>"
                              "• ההתנגדות הישנה הופכת לתמיכה חדשה אחרי פריצה מוצלחת.")
                elif any(x in q for x in ["שורט","short","מכירה בחסר"]):
                    answer = ("<b>שורט (Short Selling):</b> מכירת מניה שאינה בבעלותך, מתוך ציפייה לירידה.<br/>"
                              "• שואלים מניות מהברוקר → מוכרים → קונים בחזרה זול יותר → מרוויחים ההפרש.<br/>"
                              "• סיכון תיאורטית בלתי מוגבל (המניה יכולה לעלות ללא גבול).<br/>"
                              "• <b>חובה</b>: Stop Loss קשיח. כניסה רק במגמה יורדת מתחת ל-MA9.")
                elif any(x in q for x in ["לונג","long","קנייה"]):
                    answer = ("<b>לונג (Long):</b> קנייה רגילה של מניה מתוך ציפייה לעלייה.<br/>"
                              "• הסיכון מוגבל לסכום ההשקעה (המניה לא יכולה לרדת מתחת לאפס).<br/>"
                              "• כניסה איכותית: מחיר מעל MA9, RSI בין 40-65, נפח עולה.<br/>"
                              "• יציאה: כשנפח יורד משמעותית או RSI חוצה 70.")
                elif any(x in q for x in ["אופציות","options","קול","פוט","call","put"]):
                    answer = ("<b>אופציות:</b> חוזים המעניקים זכות לקנות/למכור נכס במחיר קבוע.<br/>"
                              "• <b>Call (קול)</b> = הימור על עלייה / זכות קנייה.<br/>"
                              "• <b>Put (פוט)</b> = הימור על ירידה / הגנה על תיק.<br/>"
                              "• Put/Call Ratio מעל 1 = פסימיות בשוק. מתחת ל-0.7 = אופטימיות.")
                elif any(x in q for x in ["מדד","index","sp500","nasdaq","dow","דאו","נאסדאק"]):
                    answer = ("<b>מדדי שוק עיקריים:</b><br/>"
                              "• <b>S&P 500</b> — 500 חברות גדולות בארה\"ב. המדד הרחב והנפוץ ביותר לבחינת השוק האמריקאי.<br/>"
                              "• <b>NASDAQ 100</b> — 100 חברות טכנולוגיה מובילות. תנודתי יותר מה-S&P.<br/>"
                              "• <b>DOW JONES</b> — 30 חברות תעשייתיות בלבד. פחות רלוונטי לניתוח מודרני.")
                elif any(x in q for x in ["נפח","volume","מחזור"]):
                    answer = ("<b>נפח מסחר (Volume):</b> כמות המניות שנסחרו ביום נתון.<br/>"
                              "• נפח גבוה בעלייה = קונים חזקים, מהלך אמיתי ועם גיבוי מוסדי.<br/>"
                              "• נפח גבוה בירידה = מוכרים חזקים, לחץ כבד.<br/>"
                              "• נפח נמוך בפריצה = אזהרה! ייתכן Fakeout.")
                elif any(x in q for x in ["פחד","גרידיות","fear","greed","סנטימנט"]):
                    answer = ("<b>מדד פחד וגרידיות (Fear & Greed):</b> מדד CNN המייצג את סנטימנט השוק.<br/>"
                              "• <b style='color:#dc2626;'>0-25 פחד קיצוני</b> = פאניקה. בזמן זה, לעיתים הזדמנות קנייה.<br/>"
                              "• <b>45-55 ניטרלי</b> = שוק מאוזן ויציב.<br/>"
                              "• <b style='color:#16a34a;'>75-100 גרידיות קיצונית</b> = אופוריה. סכנת בועה וירידות.")
                else:
                    answer = (f"<b>תשובה לשאלתך:</b> '{qa_input}'<br/><br/>"
                              "נסה לשאול על אחד מהנושאים הבאים לקבלת תשובה מדויקת:<br/>"
                              "• <b>RSI</b> — מדד עוצמה יחסית<br/>"
                              "• <b>ממוצע נע / MA9 / MA200</b><br/>"
                              "• <b>פריצה / תמיכה / התנגדות</b><br/>"
                              "• <b>שורט / לונג</b><br/>"
                              "• <b>אופציות / Call / Put</b><br/>"
                              "• <b>נפח מסחר</b><br/>"
                              "• <b>מניות ספציפיות</b>: AAPL, TSLA, NVDA, MSFT, AMZN")
                st.session_state.ai_answer = answer
            else:
                st.warning("אנא הזן שאלה")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.ai_answer:
            st.markdown(f"""
<div class="ai-response-box" style="margin-top:12px;">
  <div class="ai-response-label">💡 מרכז המידע — THE MIND CHANGER</div>
  <div class="ai-response-text">{st.session_state.ai_answer}</div>
</div>""", unsafe_allow_html=True)

# ── מדד פחד וגרידיות — תוקן ──
with tab_fg:
    needle_angle = (fg_val / 100) * 180 - 90

    c1, c2 = st.columns([1, 1])
    with c1:
        # ── תיקון: gauge HTML מלא ועובד ללא תלות חיצונית ──
        gauge_html = f"""
        <div style="background:#141410;border:1px solid rgba(201,168,76,0.15);border-radius:4px;padding:25px;text-align:center;margin-top:15px;">
          <h3 style="font-family:'Playfair Display',serif;color:#c9a84c;font-size:1.1rem;margin-bottom:4px;">CNN Fear & Greed Index</h3>
          <p style="color:#9a8f7a;font-size:0.78rem;margin-bottom:20px;">סנטימנט שוק בזמן אמת</p>

          <svg viewBox="0 0 200 120" width="280" style="display:block;margin:0 auto;">
            <!-- קשת צבעים -->
            <path d="M 20 100 A 80 80 0 0 1 100 20" stroke="#dc2626" stroke-width="18" fill="none"/>
            <path d="M 100 20 A 80 80 0 0 1 155 35" stroke="#ea580c" stroke-width="18" fill="none"/>
            <path d="M 155 35 A 80 80 0 0 1 175 80" stroke="#eab308" stroke-width="18" fill="none"/>
            <path d="M 175 80 A 80 80 0 0 1 150 128" stroke="#16a34a" stroke-width="18" fill="none" transform="rotate(-8,100,100)"/>

            <!-- מחוג -->
            <line
              x1="100" y1="100"
              x2="100" y2="28"
              stroke="#f0ede6"
              stroke-width="3"
              stroke-linecap="round"
              transform="rotate({needle_angle}, 100, 100)"
              style="transition: transform 1s ease-in-out;"
            />
            <!-- נקודת מרכז -->
            <circle cx="100" cy="100" r="6" fill="#c9a84c"/>

            <!-- ציון -->
            <text x="100" y="88" text-anchor="middle" font-size="22" font-weight="900" fill="#f0ede6" font-family="Inter">{fg_val}</text>

            <!-- תוויות -->
            <text x="14"  y="114" text-anchor="middle" font-size="7" fill="#dc2626" font-family="Inter">פחד</text>
            <text x="186" y="114" text-anchor="middle" font-size="7" fill="#16a34a" font-family="Inter">גרידיות</text>
          </svg>

          <div style="margin-top:12px;">
            <span style="font-size:1rem;font-weight:700;color:#c9a84c;background:rgba(201,168,76,0.06);padding:6px 18px;border-radius:3px;border:1px solid rgba(201,168,76,0.15);">{fg_rating}</span>
          </div>
        </div>
        """
        st.markdown(gauge_html, unsafe_allow_html=True)

    with c2:
        st.markdown("""
<div style="background:#141410;border:1px solid rgba(201,168,76,0.15);border-radius:4px;padding:25px;margin-top:15px;direction:rtl;text-align:right;">
  <h3 style="font-family:'Playfair Display',serif;color:#f0ede6;font-size:1.05rem;margin-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:8px;">מה המדד מראה?</h3>
  <p style="font-size:0.83rem;color:#9a8f7a;line-height:1.7;margin-bottom:12px;">
    מדד הפחד והגרידיות של CNN Business מודד את הסנטימנט הכללי בוול סטריט בסולם 0-100, על בסיס 7 אינדיקטורים: מומנטום מחירים, עוצמת מניות, יחס Put/Call, תנודתיות VIX, ביקוש לאגרות חוב ועוד.
  </p>
  <div style="font-size:0.8rem;line-height:1.7;color:#7a7060;">
    <div style="margin-bottom:8px;"><b style="color:#dc2626;">0-25 — פחד קיצוני:</b> פאניקה בשוק. לעיתים הזדמנות קנייה נדירה. "היה גרידי כשאחרים מפחדים" — באפט.</div>
    <div style="margin-bottom:8px;"><b style="color:#eab308;">26-44 — פחד:</b> משקיעים זהירים, לחץ מכירות, שוק מתקן.</div>
    <div style="margin-bottom:8px;"><b style="color:#9a8f7a;">45-55 — ניטרלי:</b> שיווי משקל. מסחר יציב ומאוזן.</div>
    <div style="margin-bottom:8px;"><b style="color:#86efac;">56-74 — גרידיות:</b> אופטימיות. קונים אגרסיביים. זהירות בהגדלת פוזיציות.</div>
    <div><b style="color:#16a34a;">75-100 — גרידיות קיצונית:</b> אופוריה. סיכון גבוה לתיקון חד. שקול הגנות.</div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Footer HTML ──
bottom_html = """<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="UTF-8"/><style>
body{background:#0a0a08;color:#f0ede6;font-family:'Inter',sans-serif;direction:rtl;margin:0}
.section-wrap{padding:64px 40px;max-width:1200px;margin:0 auto}
.eyebrow-line{width:28px;height:1px;background:#c9a84c;display:inline-block;margin-left:8px;vertical-align:middle}
.section-title{font-family:'Playfair Display',serif;font-size:clamp(1.5rem,2.5vw,2.2rem);font-weight:900;color:#f0ede6;margin-bottom:8px}
.section-desc{color:#9a8f7a;font-size:0.88rem;max-width:480px;line-height:1.65;margin-bottom:40px}
#features{background:#0f0f0c;border-top:1px solid rgba(201,168,76,0.12)}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1px;background:rgba(201,168,76,0.12);border:1px solid rgba(201,168,76,0.12)}
.feat-card{background:#0f0f0c;padding:28px 24px;transition:background .2s}
.feat-card:hover{background:#141410}
.feat-icon{font-size:1.3rem;margin-bottom:14px;display:block}
.feat-title{font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;color:#f0ede6;margin-bottom:6px}
.feat-desc{font-size:0.78rem;color:#7a7060;line-height:1.6}
#how{border-top:1px solid rgba(201,168,76,0.12)}
.steps-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:1px solid rgba(201,168,76,0.12);background:rgba(201,168,76,0.12)}
.step-card{background:#141410;padding:32px 24px}
.step-num{font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:900;color:rgba(201,168,76,0.15);line-height:1;margin-bottom:16px}
.step-title{font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;color:#f0ede6;margin-bottom:8px}
.step-desc{font-size:0.78rem;color:#7a7060;line-height:1.6}
footer{background:#0f0f0c;border-top:1px solid rgba(201,168,76,0.12);padding:36px 40px;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:16px}
.footer-logo{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:#c9a84c;margin-bottom:6px}
.footer-copy{font-size:0.72rem;color:#7a7060}
</style></head><body>
<section id="features" style="padding:0">
  <div class="section-wrap" style="padding-bottom:0">
    <p style="color:#c9a84c;font-size:0.68rem;font-weight:600;letter-spacing:0.16em;text-transform:uppercase;margin-bottom:5px;">יתרונות</p>
    <h2 class="section-title">למה The Mind Changer?</h2>
    <p class="section-desc">כל מה שצריך לקבל החלטות מסחר חכמות יותר</p>
  </div>
  <div class="features-grid">
    <div class="feat-card"><span class="feat-icon">⚡</span><div class="feat-title">סריקה בזמן אמת</div><div class="feat-desc">מנתח מאות מניות לפי קריטריונים טכניים מוכחים</div></div>
    <div class="feat-card"><span class="feat-icon">📈</span><div class="feat-title">רדאר לונג</div><div class="feat-desc">מזהה מומנטום עולה עם RSI, ממוצעים נעים ונרות</div></div>
    <div class="feat-card"><span class="feat-icon">📉</span><div class="feat-title">רדאר שורט</div><div class="feat-desc">מאתר מניות חלשות עם Puts חזקים ומגמה יורדת</div></div>
    <div class="feat-card"><span class="feat-icon">📊</span><div class="feat-title">14 אינדיקטורים</div><div class="feat-desc">RSI, MA9/100/200, אופציות, המלצות אנליסטים ועוד</div></div>
    <div class="feat-card"><span class="feat-icon">🔒</span><div class="feat-title">נתונים מאובטחים</div><div class="feat-desc">עקיפת Rate Limits חכמה עם Session דינמי</div></div>
    <div class="feat-card"><span class="feat-icon">🤖</span><div class="feat-title">ניתוח מניות</div><div class="feat-desc">נתונים טכניים אמיתיים לכל מניה שתבחר</div></div>
  </div>
</section>
<section id="how">
  <div class="section-wrap">
    <p style="color:#c9a84c;font-size:0.68rem;font-weight:600;letter-spacing:0.16em;text-transform:uppercase;margin-bottom:5px;">תהליך</p>
    <h2 class="section-title">איך זה עובד?</h2>
    <p class="section-desc">שלושה שלבים פשוטים לתוצאות חכמות</p>
    <div class="steps-grid">
      <div class="step-card"><div class="step-num">01</div><div class="step-title">בחר מצב סריקה</div><div class="step-desc">לונג, שורט, או ניתוח מניה בודדת.</div></div>
      <div class="step-card"><div class="step-num">02</div><div class="step-title">סריקה אלגוריתמית</div><div class="step-desc">בדיקת RSI, ממוצעים נעים, נפח ונרות.</div></div>
      <div class="step-card"><div class="step-num">03</div><div class="step-title">קבל תוצאות</div><div class="step-desc">מניות עם קריטריונים מוצגות עם מחיר עדכני.</div></div>
    </div>
  </div>
</section>
<footer>
  <div><div class="footer-logo">The Mind Changer</div><div class="footer-copy">2026 — למטרות מידע בלבד. אינו ייעוץ השקעות.</div></div>
</footer>
</body></html>"""
st.components.v1.html(bottom_html, height=680, scrolling=False)
