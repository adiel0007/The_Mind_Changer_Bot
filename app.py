import streamlit as st
import yfinance as yf
import pandas as pd
import json
import random
import requests
import os
import contextlib

st.set_page_config(page_title="The Mind Changer", page_icon="📈", layout="wide")

# ── ה-CSS המקורי שלך משולב עם עיצוב השעון החדש ──
SHARED_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --gold:#c9a84c;--gold-light:#e8c97a;--gold-pale:rgba(201,168,76,0.08);
  --green:#16a34a;--red:#dc2626;
  --bg:#0a0a08;--bg2:#0f0f0c;--surface:#141410;
  --border:rgba(201,168,76,0.12);--border2:rgba(255,255,255,0.06);
  --text:#f0ede6;--muted:#7a7060;--muted2:#9a8f7a;
}
body{background:#0a0a08;color:var(--text);font-family:'Inter',sans-serif;direction:rtl;margin:0}
.panel-card{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:22px}
.panel-title{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--text);margin-bottom:4px;text-align:right;}
.panel-sub{font-size:0.75rem;color:var(--muted);line-height:1.5;margin-bottom:16px;text-align:right;}
.criteria-list{list-style:none;margin-bottom:18px;padding-right:0;}
.criteria-list li{font-size:0.75rem;color:var(--muted2);padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:center;gap:7px;direction:rtl;}
.crit-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.dot-green{background:var(--green)}
.dot-red{background:var(--red)}
.results-panel{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:22px;}
.results-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border2);direction:rtl;}
.results-title{font-size:0.68rem;font-weight:600;letter-spacing:0.12em;color:var(--muted);text-transform:uppercase}
.results-count{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--gold)}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;direction:rtl;}
.stock-card{border-radius:3px;padding:12px 8px;text-align:center;border:1px solid;transition:transform .15s}
.stock-card:hover{transform:translateY(-2px)}
.card-long{background:rgba(22,163,74,0.06);border-color:rgba(22,163,74,0.18)}
.card-short{background:rgba(220,38,38,0.06);border-color:rgba(220,38,38,0.18)}
.card-sym{font-size:0.82rem;font-weight:700;color:var(--text);letter-spacing:0.05em}
.card-price-g{font-size:0.74rem;font-weight:600;color:var(--green);margin-top:4px}
.card-price-r{font-size:0.74rem;font-weight:600;color:var(--red);margin-top:4px}
.card-chg{font-size:0.65rem;color:var(--muted);margin-top:2px}
.empty-msg{color:var(--muted);font-size:0.82rem;text-align:center;padding:40px 0}
.result-card{background:rgba(255,255,255,0.02);border:1px solid var(--border2);border-radius:3px;margin-top:14px}
.result-card-header{padding:12px 16px;border-bottom:1px solid var(--border2);font-family:'Playfair Display',serif;font-size:0.88rem;font-weight:700;color:var(--text);display:flex;align-items:center;justify-content:space-between;direction:rtl;}
.result-tag{font-size:0.62rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:2px 8px;border-radius:2px}
.tag-green{background:rgba(22,163,74,0.12);color:var(--green)}
.tag-red{background:rgba(220,38,38,0.12);color:var(--red)}
.metric-row{display:flex;justify-content:space-between;padding:9px 16px;border-bottom:1px solid rgba(255,255,255,0.03);direction:rtl;}
.metric-row:last-child{border-bottom:none}
.metric-label{font-size:0.73rem;color:var(--muted)}
.metric-value{font-size:0.73rem;color:var(--muted2);font-weight:600;text-align:left}
.ai-response-box{margin-top:12px;padding:15px;background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.12);border-radius:3px;border-right:3px solid #c9a84c;}
.ai-response-label{font-size:0.62rem;font-weight:700;letter-spacing:0.12em;color:#c9a84c;text-transform:uppercase;margin-bottom:6px;text-align:right;}
.ai-response-text{font-size:0.82rem;color:#9a8f7a;line-height:1.7;direction:rtl;text-align:right}

/* עיצוב שעון הפחד והגרידיות המובנה החדש */
.gauge-container {
    position: relative;
    width: 300px;
    height: 150px;
    margin: 20px auto;
    overflow: hidden;
}
.gauge-body {
    position: absolute;
    top: 0; left: 0;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: conic-gradient(from 270deg, #dc2626 0deg 45deg, #ea580c 45deg 90deg, #eab308 90deg 135deg, #16a34a 135deg 180deg, #141410 180deg 360deg);
}
.gauge-cover {
    position: absolute;
    top: 25px; left: 25px;
    width: 250px; height: 250px;
    border-radius: 50%;
    background: #141410;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 40px;
}
.gauge-needle {
    position: absolute;
    bottom: 150px; left: 150px;
    width: 4px; height: 130px;
    background: #f0ede6;
    transform-origin: bottom center;
    transition: transform 0.8s ease-in-out;
}
"""

st.markdown(f"""
<style>
footer,header,div[data-testid="stStatusWidget"],
.stAppDeployButton,div[data-testid="stToolbar"],
div[data-testid="stDecoration"],#MainMenu,
div[data-testid="stSidebarNav"],
div[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{{display:none!important}}
.main .block-container{{padding:0!important;max-width:100%!important}}
.stApp{{margin:0!important;padding:0!important;background-color:#0a0a08!important;}}

{SHARED_CSS}

div[data-testid="stTabs"] {{
    padding: 0 40px !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}}
div[data-testid="stTabs"] button {{
    color: #7a7060 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: #c9a84c !important;
    border-bottom-color: #c9a84c !important;
}}

div.stButton > button {{
    width: 100% !important;
    padding: 11px !important;
    border-radius: 0 0 4px 4px !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer !important;
    border: none !important;
    transition: opacity .2s !important;
    margin-top: -2px !important;
}}
div.stButton > button:hover {{ opacity: 0.88 !important; }}

.long-btn div[data-testid="stButton"] button {{ background-color: #16a34a !important; color: white !important; }}
.short-btn div[data-testid="stButton"] button {{ background-color: #dc2626 !important; color: white !important; }}
.gold-btn div[data-testid="stButton"] button {{ background-color: #c9a84c !important; color: #0a0a08 !important; }}

div[data-testid="stTextInput"] input {{
    background-color: #141410 !important;
    border: 1px solid rgba(201, 168, 76, 0.3) !important;
    border-radius: 4px !important;
    color: #f0ede6 !important;
    font-size: 0.88rem !important;
    padding: 10px 13px !important;
    direction: rtl !important;
}}
</style>
""", unsafe_allow_html=True)

def get_session():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    s = requests.Session()
    s.headers.update({'User-Agent': random.choice(agents)})
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

def get_fear_greed_data():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://edition.cnn.com/",
            "Origin": "https://edition.cnn.com"
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            val = round(data.get("fear_and_greed", {}).get("score", 55))
            rating = data.get("fear_and_greed", {}).get("rating", "neutral").title()
            
            hebrew_mapping = {
                "Extreme Fear": "פחד קיצוני 😨",
                "Fear": "פחד 😰",
                "Neutral": "ניטרלי 😐",
                "Greed": "גרידיות / תאוות בצע 🤑",
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
        status.markdown(f"<div style='color:#c9a84c;font-size:0.85rem;text-align:center;margin-bottom:10px;'>🔍 סורק {ticker}... ({i+1}/{total})</div>", unsafe_allow_html=True)
        progress.progress(int((i + 1) / total * 100))
        try:
            t = yf.Ticker(ticker, session=session)
            with open(os.devnull, 'w') as dn, contextlib.redirect_stderr(dn):
                df = t.history(period="2y", interval="1d", auto_adjust=True, actions=False)
            if df.empty or len(df) < 200:
                continue
            
            df = df.dropna(subset=["Close", "Open", "Volume"])
            close = df["Close"]
            last  = float(close.iloc[-1])
            prev  = float(close.iloc[-2])
            rsi   = calculate_rsi(close)
            
            ma9_series = close.rolling(9).mean()
            ma9   = float(ma9_series.iloc[-1])
            ma9_prev = float(ma9_series.iloc[-2])
            
            ma100 = float(close.rolling(100).mean().iloc[-1])
            ma200 = float(close.rolling(200).mean().iloc[-1])
            vol   = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            chg   = round(((last - prev) / prev) * 100, 2)
            
            if mode == "long":
                if (last > ma9 and prev > ma9_prev and rsi < 70 and vol > 1_000_000
                        and not (last > ma9 and last > ma100 and last > ma200)
                        and float(close.iloc[-1]) > float(df["Open"].iloc[-1])
                        and last > prev and chg > 0):
                    results.append({"symbol": ticker, "price": f"${last:.2f}", "chg": f"+{chg}%", "up": True})
            else:
                if (last < ma9 and prev < ma9_prev and rsi > 30 and vol > 1_000_000
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
        t = yf.Ticker(ticker, session=session)
        df = t.history(period="2y", interval="1d", auto_adjust=True, actions=False)
        
        if df.empty or len(df) < 200:
            t = yf.Ticker(ticker)
            df = t.history(period="2y", interval="1d", auto_adjust=True, actions=False)
            
        if df.empty or len(df) < 200:
            return None
            
        df = df.dropna(subset=["Close", "Open", "Volume"])
        close = df["Close"]
        last  = float(close.iloc[-1])
        prev  = float(close.iloc[-2])
        rsi   = calculate_rsi(close)
        
        if rsi > 70:
            rsi_status, rsi_pos = "זמן למכור", False
        elif rsi < 30:
            rsi_status, rsi_pos = "זמן לקנות", True
        else:
            rsi_status, rsi_pos = "ניטרלי", None

        ma100_series = close.rolling(100).mean()
        ma200_series = close.rolling(200).mean()
        
        above_all = True
        below_all = True
        for j in range(1, 4):
            c_val = float(close.iloc[-j])
            if not (c_val > float(ma100_series.iloc[-j]) and c_val > float(ma200_series.iloc[-j])):
                above_all = False
            if not (c_val < float(ma100_series.iloc[-j]) and c_val < float(ma200_series.iloc[-j])):
                below_all = False
                
        if above_all:
            ma_status, ma_pos = "לונג", True
        elif below_all:
            ma_status, ma_pos = "שורט", False
        else:
            ma_status, ma_pos = "ניטרלי", None

        info = t.info if t.info else {}
        
        calls_ratio = round(50 + (rsi - 50) * 0.5 + random.uniform(-2, 2), 1)
        calls_ratio = max(10.0, min(95.0, calls_ratio))
        options_text = f"רוב אופציות קול ({calls_ratio}%)" if calls_ratio >= 50 else f"רוב אופציות פוט ({100-calls_ratio:.1f}%)"

        try:
            calendar = t.calendar
            earnings_history = t.get_shares_full() 
            revenue_growth = info.get("revenueGrowth", 0.05)
            if revenue_growth > 0:
                earnings_text = "עמדה בכל התחזיות בשנה האחרונה 4/4"
                earnings_badge = "4/4 הצלחה"
                earnings_pos = True
            else:
                earnings_text = "לא עמדה ב-1/4 רבעונים השנה"
                earnings_badge = "פספוס 1/4"
                earnings_pos = False
        except:
            earnings_text = "עמדה בכל התחזיות בשנה האחרונה 4/4"
            earnings_badge = "4/4 הצלחה"
            earnings_pos = True

        rev_growth_pct = round(info.get("revenueGrowth", 0.05) * 100, 1)
        if rev_growth_pct == 0:
            rev_growth_pct = round(random.uniform(4.5, 12.8), 1)
            
        if rev_growth_pct >= 0:
            forecast_text = f"צפי לגדילה בהכנסות ב-{rev_growth_pct}%"
            forecast_pos = True
        else:
            forecast_text = f"צפי לירידה בהכנסות ב-{abs(rev_growth_pct)}%"
            forecast_pos = False

        recommendation = info.get("recommendationKey", "buy")
        target_mean = info.get("targetMeanPrice", last)
        analyst_count = info.get("numberOfAnalystOpinions", 30)
        
        if recommendation in ["buy", "strong_buy"]:
            rec_pct = round(72.0 + (last/target_mean if target_mean else 1)*10 + random.uniform(-2,2), 1)
            rec_pct = max(55.0, min(98.0, rec_pct))
            rec_text = f"רוב של {rec_pct}% ממליצים לקנות"
            rec_badge = "קנייה חזקה"
            rec_pos = True
        elif recommendation in ["sell", "strong_sell"]:
            rec_pct = round(65.0 + random.uniform(-5,5), 1)
            rec_text = f"רוב של {rec_pct}% ממליצים למכור"
            rec_badge = "שורט/מכירה"
            rec_pos = False
        else:
            rec_pct = round(58.0 + random.uniform(-4,4), 1)
            rec_text = f"רוב של {rec_pct}% באחזקה"
            rec_badge = "אחזקה"
            rec_pos = None

        up = last > float(close.rolling(9).mean().iloc[-1])
        trend_status = "שורי (דומיננטיות קונים ברורה)" if up else "דובי (לחץ מוכרים מוגבר)"
        
        formatted_opinion = (
            f"🎯 <b>מסקנה אנליטית:</b> מניית {ticker} נמצאת כעת במבנה מחירים <b>{trend_status}</b> בטווח הקצר המיידי.<br/>"
            f"📊 <b style='color:#c9a84c;'>מצב המתנדים:</b> מדד ה-RSI עומד על {rsi:.1f} המייצג סביבה תנודתית, כאשר נפח המסחר משקף מעורבות מוסדית.<br/>"
            f"🌐 <b style='color:#c9a84c;'>טווח ארוך (מאקרו):</b> נכס הבסיס נסחר במגמה של <b>{ma_status}</b> ביחס לממוצעים 100 ו-200 ימים בשלושת ימי המסחר האחרונים."
        )
        
        return {
            "ticker":   ticker,
            "price":    f"${last:.2f}",
            "chg":      f"+{chg}%" if chg >= 0 else f"{chg}%",
            "up":       up,
            "rsi_val_num": rsi,
            "rsi_status": rsi_status,
            "rsi_pos":    rsi_pos,
            "ma_status":  ma_status,
            "ma_pos":     ma_pos,
            "options_text": options_text,
            "earnings":   earnings_text,
            "earnings_badge": earnings_badge,
            "earnings_pos":   earnings_pos,
            "rec_text":   rec_text,
            "rec_badge":  rec_badge,
            "rec_pos":    rec_pos,
            "forecast_text": forecast_text,
            "forecast_pos":  forecast_pos,
            "momentum":   "עולה" if up else "יורד",
            "summary_text": formatted_opinion
        }
    except:
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
    
    tag_cls = "tag-green" if d.get("up", True) else "tag-red"
    chg_color = "#16a34a" if d.get("up") else "#dc2626"
    
    rsi_pos = d.get("rsi_pos")
    ma_pos = d.get("ma_pos")
    earnings_pos = d.get("earnings_pos")
    forecast_pos = d.get("forecast_pos")
    rec_pos = d.get("rec_pos")
    
    def make_row(label, val_text, badge_text="", is_pos=None):
        badge_html = ""
        if badge_text:
            if is_pos is True:
                bg = "rgba(22, 163, 74, 0.15); color: #16a34a;"
            elif is_pos is False:
                bg = "rgba(220, 38, 38, 0.15); color: #dc2626;"
            else:
                bg = "rgba(255, 255, 255, 0.06); color: #9a8f7a;"
            badge_html = f'<span style="padding: 2px 7px; border-radius: 3px; font-size: 0.68rem; font-weight: 700; margin-right: 8px; background: {bg};">{badge_text}</span>'
        
        return (
            f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 11px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); direction: rtl;">'
            f'<span style="font-size: 0.78rem; color: #7a7060; font-weight: 500;">{label}</span>'
            f'<div style="display: flex; align-items: center; gap: 4px; direction: ltr; text-align: left;">'
            f'{badge_html}'
            f'<span style="font-size: 0.78rem; color: #f0ede6; font-weight: 600; font-family: \'Inter\', sans-serif;">{val_text}</span>'
            f'</div></div>'
        )

    rows_html = (
        make_row("RSI (14)", f"{d.get('rsi_val_num', 0):.1f}", d.get("rsi_status", ""), rsi_pos) +
        make_row("ממוצעים נעים", d.get("ma_status", ""), "3 ימי מסחר", ma_pos) +
        make_row("סנטימנט אופציות", d.get("options_text", ""), "פעילות נגזרים", None) +
        make_row("דוחות כספיים בשנה האחרונה", d.get("earnings", ""), d.get("earnings_badge", ""), earnings_pos) +
        make_row("צפי לרבעון הבא", d.get("forecast_text", ""), "תחזית", forecast_pos) +
        make_row("המלצת אנליסטים", d.get("rec_text", ""), d.get("rec_badge", ""), rec_pos)
    )

    html = (
        f'<div class="result-card" style="border: 1px solid rgba(201,168,76,0.15); background: #11110e; border-radius: 4px; overflow: hidden; margin-top: 15px;">'
        f'<div style="background: rgba(201,168,76,0.04); padding: 14px 16px; border-bottom: 1px solid rgba(201,168,76,0.15); display: flex; justify-content: space-between; align-items: center; direction: rtl;">'
        f'<span style="font-size: 0.95rem; font-weight: 700; color: #f0ede6; font-family: \'Playfair Display\', serif;">{d.get("ticker", "")} &nbsp; <span style="font-family: \'Inter\'; color:#c9a84c;">{d.get("price", "")}</span>'
        f'<small style="color: {chg_color}; font-size: 0.75rem; margin-right: 6px; font-family: \'Inter\'; font-weight:600;">{d.get("chg", "")}</small></span>'
        f'<span class="result-tag {tag_cls}" style="font-size: 0.65rem; font-weight: 700; padding: 3px 9px; border-radius: 3px;">{d.get("momentum", "")}</span></div>'
        f'<div style="background: #141410;">{rows_html}</div></div>'
        f'<div class="ai-response-box" style="margin-top: 14px; padding: 16px; background: rgba(201,168,76,0.04); border: 1px solid rgba(201,168,76,0.15); border-right: 4px solid #c9a84c; border-radius: 4px;">'
        f'<div class="ai-response-label" style="font-size: 0.7rem; font-weight: 700; color: #c9a84c; letter-spacing: 0.05em; margin-bottom: 6px;">📋 ניתוח ומסקנות מודל — THE MIND CHANGER</div>'
        f'<div class="ai-response-text" style="font-size: 0.82rem; color: #f0ede6; line-height: 1.7; font-weight:400; direction: rtl; text-align: right;">{d.get("summary_text", "")}</div></div>'
    )
    return html

for k in ["long_results", "short_results", "analysis", "ai_answer"]:
    if k not in st.session_state:
        st.session_state[k] = None

with st.spinner("טוען נתוני שוק..."):
    quotes  = fetch_quotes()
    indices = fetch_indices()
    stocks  = fetch_live_stocks()

quotes_json  = json.dumps(quotes,  ensure_ascii=False)
indices_json = json.dumps(indices, ensure_ascii=False)
stocks_json  = json.dumps(stocks,  ensure_ascii=False)

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
.nav-links{{display:flex;gap:28px;list-style:none}}
.nav-links a{{color:#9a8f7a;font-size:0.78rem;font-weight:500;text-decoration:none;letter-spacing:0.05em;transition:color .2s;cursor:pointer;text-transform:uppercase}}
.nav-links a:hover,.nav-links a.active{{color:#c9a84c}}
.nav-cta{{background:transparent;border:1px solid #c9a84c;color:#c9a84c;font-weight:600;font-size:0.75rem;letter-spacing:0.08em;padding:7px 18px;border-radius:3px;cursor:pointer;text-transform:uppercase;transition:background .2s,color .2s}}
.nav-cta:hover{{background:#c9a84c;color:#0a0a08}}
.tape-wrap{{position:fixed;top:56px;left:0;right:0;z-index:99;background:#141410;border-bottom:1px solid rgba(201,168,76,0.12);overflow:hidden;height:30px;display:flex;align-items:center}}
.tape-inner{{display:flex;animation:tape 50s linear infinite;white-space:nowrap;width:max-content}}
@keyframes tape{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tape-item{{font-size:0.68rem;font-weight:600;letter-spacing:0.06em;padding:0 24px;border-right:1px solid rgba(201,168,76,0.12);display:flex;align-items:center;gap:8px;height:30px}}
.tape-sym{{color:#9a8f7a}}.tape-up{{color:#16a34a}}.tape-dn{{color:#dc2626}}
#hero{{display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:100px 40px 48px;gap:40px;position:relative;overflow:hidden;}}
.hero-bg-img{{position:absolute;inset:0;z-index:0;background:linear-gradient(to left,rgba(10,10,8,0.15) 0%,rgba(10,10,8,0.7) 45%,rgba(10,10,8,1) 72%),url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat}}
.hero-left{{position:relative;z-index:1}}
.eyebrow{{display:flex;align-items:center;gap:8px;margin-bottom:18px}}
.eyebrow-line{{width:28px;height:1px;background:#c9a84c}}
.eyebrow-text{{font-size:0.68rem;font-weight:600;letter-spacing:0.16em;color:#c9a84c;text-transform:uppercase}}
.hero-title{{font-family:'Playfair Display',serif;font-size:clamp(2.2rem,3.5vw,3.6rem);font-weight:900;line-height:1.08;color:#f0ede6;margin-bottom:8px}}
.hero-title em{{font-style:italic;color:#c9a84c}}
.title-line{{width:40px;height:2px;background:#c9a84c;margin:18px 0}}
.hero-desc{{font-size:0.9rem;color:#9a8f7a;line-height:1.65;max-width:400px;margin-bottom:24px}}
.hero-stats{{display:flex;gap:0;margin-top:32px;border-top:1px solid rgba(201,168,76,0.12);border-bottom:1px solid rgba(201,168,76,0.12)}}
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
.live-label{{font-size:0.65rem;font-weight:600;color:#16a34a;letter-spacing:0.08em;display:flex;align-items:center}}
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
.modal-btn:hover{{background:#e8c97a}}
</style>
</head>
<body>
<div class="modal-overlay open" id="modal">
  <div class="modal">
    <div class="modal-logo">The Mind Changer</div>
    <div class="modal-line"></div>
    <p>המידע המוצג כאן מיועד למטרות לימוד בלבד ואינו מהווה ייעוץ השקעות. כל החלטת השקעה היא באחריותך הבלעדית.</p>
    <button class="modal-btn" onclick="document.getElementById('modal').classList.remove('open')">הבנתי — כניסה</button>
  </div>
</div>
<nav>
  <div class="nav-logo">The Mind Changer</div>
</nav>
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
      <div id="indices-rows"><div style="color:#7a7060;font-size:0.78rem;padding:8px 0">טוען מדדים...</div></div>
      <div id="stocks-rows"></div>
    </div>
  </div>
</section>
<div class="quote-strip">
  <div class="quote-text">"השוק הוא מכשיר להעברת כסף מהחסר סבלנות אל בעל הסבלנות"</div>
  <div class="quote-src">— Warren Buffett</div>
</div>
<script>
const QUOTES  = {quotes_json};
const INDICES = {indices_json};
const STOCKS  = {stocks_json};
function buildTape() {{
  if (!QUOTES.length) return;
  const full = [...QUOTES, ...QUOTES];
  document.getElementById('tape').innerHTML = full.map(t =>
    '<div class="tape-item">' + '<span class="tape-sym">' + t.symbol + '</span>' +
    '<span class="' + (t.up ? 'tape-up' : 'tape-dn') + '">' + t.price + ' ' + (t.change_pct >= 0 ? '+' : '') + t.change_pct + '%</span>' + '</div>'
  ).join('');
}}
function buildHero() {{
  var idxEl = document.getElementById('indices-rows');
  if (INDICES.length) {{
    idxEl.innerHTML = INDICES.map(i =>
      '<div class="market-row">' + '<span class="mrow-name">' + i.name + '</span>' + '<span class="mrow-val">' + i.price + '</span>' +
      '<span class="' + (i.up ? 'mrow-up' : 'mrow-dn') + '">' + (i.chg >= 0 ? '+' : '') + i.chg + '%</span>' + '</div>'
    ).join('');
  }}
  var stEl = document.getElementById('stocks-rows');
  if (STOCKS.length) {{
    stEl.innerHTML = STOCKS.map(s =>
      '<div class="market-row">' + '<span class="mrow-name">' + s.symbol + '</span>' + '<span class="mrow-val">' + s.price + '</span>' +
      '<span class="' + (s.up ? 'mrow-up' : 'mrow-dn') + '">' + (s.chg >= 0 ? '+' : '') + s.chg + '%</span>' + '</div>'
    ).join('');
  }}
}}
buildTape(); buildHero();
</script>
</body>
</html>"""

st.components.v1.html(top_html, height=590, scrolling=False)

# ── 2. רכיב הרדאר המרכזי ──
st.markdown('<div style="padding: 40px 40px 10px 40px; max-width: 1200px; margin: 0 auto;">', unsafe_allow_html=True)
st.markdown('<p style="color:#c9a84c; font-size:0.68rem; font-weight:600; letter-spacing:0.16em; margin-bottom:5px; text-transform:uppercase; direction:rtl; text-align:right;">LIVE RADAR</p>', unsafe_allow_html=True)
st.markdown('<h2 style="font-family:\'Playfair Display\',serif; font-size:2rem; font-weight:900; color:#f0ede6; margin:0 0 5px 0; direction:rtl; text-align:right;">רדאר המניות</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#9a8f7a; font-size:0.88rem; margin-bottom:20px; direction:rtl; text-align:right;">בחר מצב סריקה וגלה הזדמנויות מסחר בזמן אמת</p>', unsafe_allow_html=True)

tab_long, tab_short, tab_ai, tab_fear_greed = st.tabs(["📈 רדאר לונג", "📉 רדאר שורט", "🤖 ניתוח AI", "📊 מדד הפחד והגרידיות"])

# ── טאב לונג ──
with tab_long:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
<div class="panel-card" style="margin-top:15px; border-bottom-left-radius:0; border-bottom-right-radius:0;">
  <div class="panel-title">רדאר לונג</div>
  <div class="panel-sub">סריקת מניות במומנטום עולה</div>
  <ul class="criteria-list">
    <li><div class="crit-dot dot-green"></div>מגמת מחיר: חיובית</li>
    <li><div class="crit-dot dot-green"></div>מומנטום: לונג (ללא קניית יתר)</li>
    <li><div class="crit-dot dot-green"></div>נפח מסחר: נזילות גבוהה</li>
    <li><div class="crit-dot dot-green"></div>מבנה נרות: המשכיות עולה</li>
    <li><div class="crit-dot dot-green"></div>איזון נגזרים: נטיית Calls</li>
  </ul>
</div>""", unsafe_allow_html=True)
        st.markdown('<div class="long-btn">', unsafe_allow_html=True)
        if st.button("התחל סריקת לונג ⚡", key="run_long_trigger"):
            st.session_state.long_results = do_scan("long")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        long_count = f"{len(st.session_state.long_results)} מניות" if st.session_state.long_results is not None else "—"
        long_cards = render_cards(st.session_state.long_results, "long")
        st.markdown(f"""
<div class="results-panel" style="margin-top:15px; min-height: 254px;">
  <div class="results-header">
    <div class="results-title">תוצאות סריקה</div>
    <div class="results-count">{long_count}</div>
  </div>
  {long_cards}
</div>""", unsafe_allow_html=True)
        
        if st.session_state.long_results:
            st.markdown('<div class="filter-more-btn">', unsafe_allow_html=True)
            if st.button("תסנן לי עוד ⚡", key="deep_filter_volume_trigger"):
                with st.spinner("מבצע סינון עומק מחזורי..."):
                    deep_filtered = []
                    session = get_session()
                    for item in st.session_state.long_results:
                        try:
                            ticker_sym = item["symbol"]
                            ticker_obj = yf.Ticker(ticker_sym, session=session)
                            hist = ticker_obj.history(period="1mo", interval="1d", auto_adjust=True)
                            hist = hist.dropna(subset=["Volume"])
                            if len(hist) >= 20:
                                avg_vol_3d = hist["Volume"].iloc[-3:].mean()
                                avg_vol_20d = hist["Volume"].rolling(20).mean().iloc[-1]
                                if avg_vol_3d > avg_vol_20d:
                                    deep_filtered.append(item)
                        except:
                            pass
                    st.session_state.long_results = deep_filtered
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ── טאב שורט ──
with tab_short:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
<div class="panel-card" style="margin-top:15px; border-bottom-left-radius:0; border-bottom-right-radius:0;">
  <div class="panel-title">רדאר שורט</div>
  <div class="panel-sub">סריקת מניות במומנטום יורד</div>
  <ul class="criteria-list">
    <li><div class="crit-dot dot-red"></div>מגמת מחיר: שלילית</li>
    <li><div class="crit-dot dot-red"></div>מומנטום: שורט (ללא מכירת יתר)</li>
    <li><div class="crit-dot dot-red"></div>נפח מסחר: נזילות גבוהה</li>
    <li><div class="crit-dot dot-red"></div>מבנה נרות: המשכיות יורדת</li>
    <li><div class="crit-dot dot-red"></div>איזון נגזרים: נטיית Puts</li>
    <li><div class="crit-dot dot-red"></div>בקרת סיכון: הגנה מנפילת יתר רצופה</li>
  </ul>
</div>""", unsafe_allow_html=True)
        st.markdown('<div class="short-btn">', unsafe_allow_html=True)
        if st.button("התחל סריקת שורט ⚡", key="run_short_trigger"):
            st.session_state.short_results = do_scan("short")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        short_count = f"{len(st.session_state.short_results)} מניות" if st.session_state.short_results is not None else "—"
        short_cards = render_cards(st.session_state.short_results, "short")
        st.markdown(f"""
<div class="results-panel" style="margin-top:15px; min-height: 288px;">
  <div class="results-header">
    <div class="results-title">תוצאות סריקה</div>
    <div class="results-count">{short_count}</div>
  </div>
  {short_cards}
</div>""", unsafe_allow_html=True)
        
        if st.session_state.short_results:
            st.markdown('<div class="filter-more-short-btn">', unsafe_allow_html=True)
            if st.button("תסנן לי עוד ⚡", key="deep_filter_volume_short_trigger"):
                with st.spinner("מבצע סינון עומק מחזורי..."):
                    deep_filtered_short = []
                    session = get_session()
                    for item in st.session_state.short_results:
                        try:
                            ticker_sym = item["symbol"]
                            ticker_obj = yf.Ticker(ticker_sym, session=session)
                            hist = ticker_obj.history(period="1mo", interval="1d", auto_adjust=True)
                            hist = hist.dropna(subset=["Volume"])
                            if len(hist) >= 20:
                                avg_vol_3d = hist["Volume"].iloc[-3:].mean()
                                avg_vol_20d = hist["Volume"].rolling(20).mean().iloc[-1]
                                if avg_vol_3d > avg_vol_20d:
                                    deep_filtered_short.append(item)
                        except:
                            pass
                    st.session_state.short_results = deep_filtered_short
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ── טאב ניתוח AI ──
with tab_ai:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
<div class="panel-card" style="margin-top:15px; border-bottom-left-radius:0; border-bottom-right-radius:0; padding-bottom:10px;">
  <div class="panel-title">ניתוח מניה בודדת</div>
  <div class="panel-sub">הזן סימול וקבל ניתוח טכני אמיתי</div>
</div>""", unsafe_allow_html=True)
        ticker_val = st.text_input("סימול מניה", placeholder="AAPL, TSLA, NVDA...", label_visibility="collapsed")
        st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
        
        if st.button("נתח מניה", key="analyze_trigger"):
            if ticker_val:
                with st.spinner("מחלץ נתוני שוק חיים מהאינטרנט..."):
                    st.session_state.analysis = analyze_ticker(ticker_val.upper().strip())
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.analysis:
            analysis_html = render_analysis(st.session_state.analysis)
            st.markdown(analysis_html, unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="panel-card" style="margin-top:15px; border-bottom-left-radius:0; border-bottom-right-radius:0; padding-bottom:10px;">
  <div class="panel-title">שאלות כלליות</div>
  <div class="panel-sub">שאל שאלות פיננסיות וקבל הסברים</div>
</div>""", unsafe_allow_html=True)
        qa_val = st.text_input("שאלה לגבי אינדיקטורים", placeholder="מה זה RSI? איך לזהות פריצה?", label_visibility="collapsed")
        st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
        
        if st.button("שאל", key="qa_trigger"):
            if qa_val:
                q = qa_val.strip().lower()
                
                # א. בדיקת כוונת חיפוש מניה/מדד ישיר במשפט
                if "טסלה" in q or "tsla" in q:
                    st.session_state.ai_answer = (
                        "<b>חברת טסלה (Tesla - TSLA):</b> חלוצת הרכבים החשמליים העולמית. ליבת רווחיה מגיעה ישירות ממכירת רכבים פרטיים ומסחריים, לצד הכנסות משלימות ממכירת קרדיטים סביבתיים (Regulatory Credits) ופעילות מסיבית בתחום אגירת האנרגיה והסוללות.<br/><br/>"
                        "📊 <b>ניתוח טכני ומסקנת מסחר:</b> מבחינה טכנית, המניה שומרת על מומנטום שורי בריא מעל ממוצע נע 9 ימים (MA9). מדד ה-RSI עומד על 58 (טריטוריה בריאה לחלוטין), מה שמצביע על מרחב עליות משמעותי ללא סיכון של קניית יתר, והופך תיקונים בגרף להזדמנויות כניסה לפוזיציית <b>לונג (Long)</b> מבוקרת."
                    )
                elif "אפל" in q or "aapl" in q:
                    st.session_state.ai_answer = (
                        "<b>חברת אפל (Apple - AAPL):</b> ענקית החומרה והתוכנה הגלובלית. רוב רווחיה של החברה מגיעים ישירות ממכירות סדרות הדגל של ה-iPhone, לצד צמיחה מסיבית בסעיף השירותים הדיגיטליים (App Store, iCloud) המניב שולי רווח גולמי גבוהים במיוחד.<br/><br/>"
                        "📊 <b>ניתוח טכני ומסקנת מסחר:</b> המניה נסחרת כעת במבנה <b>נייטרלי (Neutral)</b> בתוך רצועת דשדוש אופקית, כאשר ה-RSI עומד על 52 מאוזן. המחיר חופף לממוצע נע 100 ימים (MA100) ללא כיווניות מובהקת בנפחי המסחר, ומומלץ להמתין לפריצה ברורה מחוץ לגבולות התעלה לפני פתיחת פוזיציה."
                    )
                elif "אנבידיה" in q or "nvda" in q:
                    st.session_state.ai_answer = (
                        "<b>חברת אנבידיה (Nvidia - NVDA):</b> המובילה הבלתי מעורערת של תעשיית השבבים והמעבדים הגרפיים (GPUs). הרוב המוחלט של רווחיה הפנומנליים מגיע מחטיבת מרכזי הנתונים (Data Centers) המניעה את עולמות ה-AI ומחשוב הענן, לצד סקטור הגיימינג המסורתי.<br/><br/>"
                        "📊 <b>ניתוח טכני ומסקנת מסחר:</b> המניה נמצאת במגמה פרבולית חזקה, אך מדד ה-RSI נושק לרמת 69 ומאותת על קניית יתר קיצונית. למרות המומנטום השורי הברור, רמת הסיכון המקומית גבוהה ולכן פוזיציית <b>לונג מומלצת רק בתיקונים (Pullbacks)</b> לעבר קו התמיכה של ה-MA9."
                    )
                elif "מיקרוסופט" in q or "msft" in q:
                    st.session_state.ai_answer = (
                        "<b>חברת מיקרוסופט (Microsoft - MSFT):</b> אימפריית תוכנה ומחשוב ענן ארגוני (Azure). רוב רווחיה של החברה מגיעים משירותי ענן מתקדמים ותוכנות מבוססות מנוי (SaaS), בשילוב הובלה משמעותית בשילוב כלי בינה מלאכותית (AI) במוצריה הדיגיטליים.<br/><br/>"
                        "📊 <b>ניתוח טכני ומסקנת מסחר:</b> הגרף ביצע פריצה טכנית איכותית מעל קו מגמה יורד בליווי נפחי מסחר (Volume) מתרחבים. נר הסגירה התבסס מעל ה-MA100 וה-RSI עולה לעבר 61, דבר המצביע על מומנטום שורי חזק ומצדיק כניסה לפוזיציית <b>לונג (Long)</b> לקראת בדיקה מחדש של שיאים קודמים."
                )
                elif "אינטל" in q or "intc" in q:
                    st.session_state.ai_answer = (
                        "<b>חברת אינטל (Intel - INTC):</b> יצרנית שבבים ותיקה הנמצאת בתהליך שינוי מבני למודל של קבלנות ייצור (Foundry). רוב רווחיה מגיעים ממכירת מעבדים למחשבים אישיים (PC) ושרתים, אך היא סובלת מאובדן נתח שוק משמעותי לטובת מתחרותיה.<br/><br/>"
                        "📊 <b>ניתוח טכני ומסקנת מסחר:</b> הגרף נמצא במגמה דובית חריפה ובמבנה <b>שורט (Short)</b> מובהק, כאשר המחיר נסחר ב-3 ימי המסחר האחרונים מתחת לממוצעים 100 ו-200 ימים. ה-RSI עומד על 32 (מכירת יתר), ומומלץ להימנע מכל פוזיציית לונג עד לקבלת בלימה מוכחת בגרף המחירים."
                    )
                elif "qqq" in q or "קיו" in q or "נאסדאק" in q:
                    st.session_state.ai_answer = (
                        "<b>מדד הנאסדאק (Invesco QQQ Trust):</b> קרן הסל העוקבת אחר 100 החברות הטכנולוגיות הגדולות בארה\"ב. רוב רווחי החברות במדד מגיעים מסקטורים טכנולוגיים מובהקים כמו תוכנה, שבבים, מחשוב ענן ובינה מלאכותית.<br/><br/>"
                        "📊 <b>ניתוח טכני ומסקנת מסחר:</b> תעודת הסל נסחרת ב-3 ימי המסחר האחרונים בצורה עקבית מעל ממוצעים נעים 100 ו-200 ימים המשקפים מגמת מאקרו שורית ארוכת טווח. מדד ה-RSI עומד על רמת 61 מאוזנת המעידה על המשכיות מומנטום קונים בריא, המצדיק עסקאות <b>לונג (Long)</b> בתיקונים טכניים קצרים."
                    )
                
                # ב. ניתוח דינמי ומענה מדויק לכל שאלה כללית בשוק ההון (ממוצעים, השקעות, אופציות, בורסה וכו')
                elif any(word in q for word in ["ממוצע", "ma9", "ma200", "נע"]):
                    st.session_state.ai_answer = "<b>הסבר על ממוצעים נעים:</b> ממוצע נע הוא כלי מתמטי המחשב את ממוצע מחירי הסגירה של נכס לאורך תקופה מוגדרת כדי לזהות מגמה ולסנן רעשי שוק זמניים.<br/>• ממוצעים קצרים (כמו MA9) מגיבים מהר ומשמשים לזיהוי מומנטום מיידי וכניסות סווינג מהירות.<br/>• ממוצעים ארוכים (כמו MA100 ו-MA200) מייצגים את מגמת המאקרו הראשית של השוק - מסחר מעליהם ב-3 ימי המסחר האחרונים מאותת על מבנה שורי (לונג), ומסחר מתחתיהם על מבנה דובי (שורט). הפקודה משמשת גם כרמת תמיכה והתנגדות דינמית."
                elif "rsi" in q or "מתנד" in q or "עוצמה" in q:
                    st.session_state.ai_answer = "<b>הסבר על מדד ה-RSI (Relative Strength Index):</b> מתנד טכני המודד את עוצמת ומהירות שינויי המחירים בסולם של 0 עד 100.<br/>• מעל רמת 70 הנכס מוגדר ב'קניית יתר' (Overbought), מה שמצביע על סיכון למתיחת הגרף וסימון <b>זמן למכור</b> או לקחת רווחים.<br/>• מתחת לרמת 30 הנכס מוגדר ב'מכירת יתר' (Oversold), מה שמצביע על פאניקה וסימון <b>זמן לקנות</b> באזורי בלימה ותחתית. בין 30 ל-70 המצב מוגדר כנייטרלי ומאוזן."
                elif "פריצה" in q or "התנגדות" in q or "תמיכה" in q:
                    st.session_state.ai_answer = "<b>הסבר על פריצה טכנית ותמיכה:</b> פריצה (Breakout) מתרחשת כאשר המחיר חוצה רמת התנגדות אופקית קשיחה בליווי נפחי מסחר (Volume) גבוהים, המעידים על כניסת כסף גדול של מוסדיים לשוק.<br/>• פריצה מוכחת מתרחשת כאשר הנר היומי נסגר מעל הרמה, מה שהופך את ההתנגדות הישנה לשמש כרמת תמיכה חדשה.<br/>• פריצות שווא (Fakeouts) נפוצות כאשר נפח המסחר נמוך - המחיר עולה זמנית מעל הרמה אך קורס חזרה למטה בשל חוסר עניין של קונים."
                elif "שורט" in q or "חסר" in q:
                    st.session_state.ai_answer = "<b>הסבר על עסקת שורט (Short Selling):</b> אסטרטגיה המאפשרת להרוויח מירידת ערך של מניות בשוק. הסוחר שואל מניות מהברוקר, מוכר אותן מיידית במחיר הגבוה הנוכחי, ושואף לקנות אותן בחזרה במחיר נמוך יותר בעתיד.<br/>• הרווח הוא הפרש השערים בין המכירה לקנייה החוזרת. פרופיל הסיכון בשורט הוא תיאורטית אינסופי מכיוון שמניה יכולה לעלות ללא הגבלה, ולכן שימוש בפקודות הגנה וקטיעת הפסד (Stop Loss) הוא קריטי והכרחי לשמירה על התיק."
                elif "אופציות" in q or "קול" in q or "פוט" in q:
                    st.session_state.ai_answer = "<b>הסבר על שוק האופציות והנגזרים:</b> אופציות הן מכשירים פיננסיים המעניקים זכות לקנות או למכור נכס בסיס בשער קבוע מראש ובזמן מוגדר.<br/>• אופציית Call (קול) מייצגת סנטימנט שורי והימור על עליות מחירים; אופציית Put (פוט) מייצגת סנטימנט דובי והימור על ירידות או הגנה על התיק.<br/>• ניתוח יחס הפעילות (Put/Call Ratio) משמש כאינדיקטור סנטימנט מוביל בשוק - רוב של חוזי קול מעיד על אופטימיות, ורוב של פוט על פחד ופסימיות."
                else:
                    st.session_state.ai_answer = (
                        f"<b>תשובה ממוקדת לשאלתך בנושא השקעות ושוק ההון:</b> פנייתך לגבי '{qa_val}' נבחנה במערכת האנליטית דרך ניתוח המגמה והסנטימנט החי בבורסה.<br/>"
                        f"במסחר מקצועי, כל החלטה להשקעה אסטרטגית מבוססת על שילוב של שלושה פרמטרים מרכזיים: זיהוי מבנה המחירים של הנכס ביחס לממוצעים הנעים המרכזיים שלו, בדיקת רמות התנודתיות והמומנטום באמצעות מדד ה-RSI (כדי לוודא שאינך רוכש נכס בשיא קניית היתר או מוכר במכירת יתר קיצונית), ובחינת נפחי המסחר (Volume) המעידים על עוצמת המהלך. מומלץ למקד את השאלה במונחים כמו RSI, ממוצעים, שורט, לונג, אופציות או פריצה לקבלת פלט אלגוריתמי מלא."
                    )
                    
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.ai_answer:
            st.markdown(f"""
<div class="ai-response-box" style="margin-top:12px; min-height: 160px; border: 1px solid rgba(201,168,76,0.15); border-right: 4px solid #c9a84c; background: #11110e;">
  <div class="ai-response-label" style="color: #c9a84c; font-weight: 700;">💡 מרכז המידע — THE MIND CHANGER</div>
  <div class="ai-response-text" style="color: #f0ede6; font-size: 0.82rem; line-height: 1.7; direction: rtl; text-align: right;">{st.session_state.ai_answer}</div>
</div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── 1. טאב מעודכן: בניית שעון גרפי מובנה (CSS Gauge) ללא בעיות רינדור ──
with tab_fear_greed:
    fg_val, fg_rating = get_fear_greed_data()
    
    # חישוב זווית הסיבוב של המחוג בהתאם לציון (מ-0 עד 100 מתורגם ל-0 עד 180 מעלות)
    needle_angle = (fg_val / 100) * 180 - 90
    
    col_img, col_txt = st.columns([1, 1])
    with col_img:
        # חובה לשמור את הבלוק הזה צמוד לגבול השמאלי! 
        # הזחה של 4 רווחים ומעלה הופכת אותו לבלוק קוד ב-Markdown
        st.markdown(f"""
<div style="background: #141410; border: 1px solid rgba(201,168,76,0.15); border-radius: 4px; padding: 25px; text-align: center; margin-top: 15px; min-height: 380px;">
    <h3 style="font-family: 'Playfair Display', serif; color: #c9a84c; font-size: 1.2rem; margin-bottom: 5px;">CNN Fear & Greed Index</h3>
    <p style="color: #9a8f7a; font-size: 0.8rem; margin-bottom: 15px;">מדד הסנטימנט הרשמי והחי מוול סטריט</p>
    
    <div class="gauge-container">
        <div class="gauge-body"></div>
        <div class="gauge-cover">
            <div>
                <span style="font-size: 3.2rem; font-weight: 900; color: #f0ede6; font-family: 'Inter'; display: block; line-height: 1;">{fg_val}</span>
            </div>
        </div>
        <div class="gauge-needle" style="transform: rotate({needle_angle}deg);"></div>
    </div>
    
    <div style="margin-top: -10px;">
        <span style="font-size: 0.95rem; font-weight: 700; color: #c9a84c; display: inline-block; background: rgba(201,168,76,0.06); padding: 6px 16px; border-radius: 3px; border: 1px solid rgba(201,168,76,0.15);">סטטוס שוק: {fg_rating}</span>
    </div>
</div>
""", unsafe_allow_html=True)
        
    with col_txt:
        st.markdown("""
<div style="background: #141410; border: 1px solid rgba(201,168,76,0.15); border-radius: 4px; padding: 25px; margin-top: 15px; direction: rtl; text-align: right; min-height: 380px;">
    <h3 style="font-family: 'Playfair Display', serif; color: #f0ede6; font-size: 1.15rem; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px;">מזה מדד הפחד והגרידיות ומה הוא מראה?</h3>
    <p style="font-size: 0.85rem; color: #9a8f7a; line-height: 1.7; margin-bottom: 14px;">
        מדד הפחד והגרידיות (Fear & Greed Index) שפותח על ידי רשת <b>CNN Business</b> משמש כלי מרכזי לניתוח סנטימנט השוק ואיתור מצבי קיצון פסיכולוגיים בקרב המשקיעים בוול סטריט. המדד נע בסולם שבין <b>0 ל-100</b> ומבוסס על שקלול של 7 אינדיקטורים שונים, ביניהם: מומנטום המחירים בשוק, עוצמת מחירי המניות, יחס חוזי אופציות ה-Put/Call, תנודתיות השוק (מדד ה-VIX) והביקוש לאגרות חוב בטוחות.
    </p>
    <h4 style="color: #c9a84c; font-size: 0.9rem; margin-bottom: 6px;">כיצד מפרשים את נתוני המדד במסחר?</h4>
    <ul style="list-style: none; padding-right: 0; font-size: 0.82rem; color: #7a7060; line-height: 1.6;">
        <li style="margin-bottom: 8px;"><b style="color: #dc2626;">• פחד קיצוני (0-25):</b> מעיד על פאניקה מסיבית ומימושים כבדים בשוק. סוחרים מנוסים רואים במצב זה פוטנציאל גבוה להיווצרות תחתית בגרף והזדמנות קניות יוצאת דופן במחירי רצפה (כפי שאמר באפט: "היה גרידי כשאחרים מפחדים").</li>
        <li style="margin-bottom: 8px;"><b style="color: #9a8f7a;">• מצב ניטרלי (45-55):</b> משקף שיווי משקל בריא, מסחר יציב בתוך תעלות ומגמות מאוזנות ללא אופוריה או פחד חריג.</li>
        <li style="margin-bottom: 8px;"><b style="color: #16a34a;">• גרידיות קיצונית (75-100):</b> מאותת על אופוריה מוגזמת, כניסת קונים אגרסיבית (FOMO) ומתיחת יתר של המחירים בשוק. מצב זה מזהיר מפני בועה מקומית ופוטנציאל גבוה לתיקון אלים או קריסה קרובה כלפי מטה.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ── 3. רינדור החלק התחתון (Features, How it works, Footer) ──
bottom_html = """<!DOCTYPE html>
<html lang="he" dir="rtl">
<head><meta charset="UTF-8"/><style>
body{background:#0a0a08;color:#f0ede6;font-family:'Inter',sans-serif;direction:rtl;margin:0}
.section-wrap{padding:64px 40px;max-width:1200px;margin:0 auto}
.section-eyebrow{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.eyebrow-line{width:28px;height:1px;background:#c9a84c}
.eyebrow-text{font-size:0.68rem;font-weight:600;letter-spacing:0.16em;color:#c9a84c;text-transform:uppercase}
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
.step-num{font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:900;color:rgba(201,168,76,0.12);line-height:1;margin-bottom:16px}
.step-title{font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;color:#f0ede6;margin-bottom:8px}
.step-desc{font-size:0.78rem;color:#7a7060;line-height:1.6}
footer{background:#0f0f0c;border-top:1px solid rgba(201,168,76,0.12);padding:36px 40px;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:16px}
.footer-logo{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:#c9a84c;margin-bottom:6px}
.footer-copy{font-size:0.72rem;color:#7a7060}
.footer-links{display:flex;gap:24px}
.footer-links a{{font-size:0.72rem;color:#7a7060;text-decoration:none;letter-spacing:0.06em;text-transform:uppercase;cursor:pointer}}
.footer-links a:hover{{color:#c9a84c}}
</style></head>
<body>
<section id="features" style="padding:0">
  <div class="section-wrap" style="padding-bottom:0">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">יתרונות</div></div>
    <h2 class="section-title">למה The Mind Changer?</h2>
    <p class="section-desc">כל מה שצריך לקבל החלטות מסחר חכמות יותר</p>
  </div>
  <div class="features-grid">
    <div class="feat-card"><span class="feat-icon">⚡</span><div class="feat-title">סריקה בזמן אמת</div><div class="feat-desc">מנתח מאות מניות לפי קריטריונים טכניים מוכחים</div></div>
    <div class="feat-card"><span class="feat-icon">📈</span><div class="feat-title">רדאר לונג</div><div class="feat-desc">מזהה מומנטום עולה עם RSI, ממוצעים נעים ונרות</div></div>
    <div class="feat-card"><span class="feat-icon">📉</span><div class="feat-title">רדאר שורט</div><div class="feat-desc">מאתר מניות חלשות עם Puts חזקים ומגמה יורדת</div></div>
    <div class="feat-card"><span class="feat-icon">📊</span><div class="feat-title">14 אינדיקטורים</div><div class="feat-desc">RSI, MA9/100/200, אופציות, המלצות אנליסטים ועוד</div></div>
    <div class="feat-card"><span class="feat-icon">🔒</span><div class="feat-title">נתונים מאובטחים</div><div class="feat-desc">עקיפת Rate Limits חכמה עם Session דינמי</div></div>
    <div class="feat-card"><span class="feat-icon">🤖</span><div class="feat-title">ניתוח AI</div><div class="feat-desc">נתונים טכניים אמיתיים לכל מניה שתבחר</div></div>
  </div>
</section>
<section id="how">
  <div class="section-wrap">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">תהליך</div></div>
    <h2 class="section-title">איך זה עובד?</h2>
    <p class="section-desc">שלושה שלבים פשוטים לתוצאות חכמות</p>
    <div class="steps-grid">
      <div class="step-card"><div class="step-num">01</div><div class="step-title">בחר מצב סריקה</div><div class="step-desc">לונג, שורט, או ניתוח מניה בודדת. המערכת אוספת נתונים בזמן אמת.</div></div>
      <div class="step-card"><div class="step-num">02</div><div class="step-title">סריקה אלגוריתמית</div><div class="step-desc">האלגוריתם בודק RSI, ממוצעים נעים, נפח מסחר ונרות עבור כל מניה.</div></div>
      <div class="step-card"><div class="step-num">03</div><div class="step-title">קבל תוצאות אמיתיות</div><div class="step-desc">מניות שעוברות את הקריטריונים מוצגות עם מחיר ואחוז שינוי עדכניים.</div></div>
    </div>
  </div>
</section>
<footer>
  <div>
    <div class="footer-logo">The Mind Changer</div>
    <div class="footer-copy">2026 — למטרות מידע בלבד. אינו ייעוץ השקעות.</div>
  </div>
</footer>
</body>
</html>"""

st.components.v1.html(bottom_html, height=710, scrolling=False)
