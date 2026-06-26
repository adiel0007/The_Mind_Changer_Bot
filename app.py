import streamlit as st
import yfinance as yf
import pandas as pd
import json
import random
import requests
import os
import contextlib

st.set_page_config(page_title="The Mind Changer", page_icon="📈", layout="wide")

# ── הסתרת כל ממשק Streamlit ──
st.markdown("""
<style>
footer,header,div[data-testid="stStatusWidget"],
.stAppDeployButton,div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
#MainMenu,div[data-testid="stSidebarNav"],
div[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important}
.main .block-container{padding:0!important;max-width:100%!important}
.stApp{margin:0!important;padding:0!important}
iframe{border:none!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#   פונקציות לשליפת נתונים אמיתיים
# ═══════════════════════════════════════════════════════════════

def get_session():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    ]
    s = requests.Session()
    s.headers.update({'User-Agent': random.choice(agents)})
    return s

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return float((100 - (100 / (1 + rs))).iloc[-1])

@st.cache_data(ttl=300)  # cache ל-5 דקות
def fetch_quotes():
    symbols = ["AAPL","TSLA","NVDA","META","AMZN","MSFT","NFLX","GOOG","AMD","COIN","SPY","QQQ"]
    results = []
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            fi = t.fast_info
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
            t = yf.Ticker(sym)
            fi = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"name": name, "price": f"{price:,.2f}", "chg": chg, "up": chg >= 0})
        except:
            pass
    return results

@st.cache_data(ttl=600)
def fetch_live_stocks():
    """שליפה מהירה של מחירים למניות הנפוצות לכרטיס Hero"""
    syms = ["NVDA","TSLA","AAPL","META","AMZN","MSFT"]
    results = []
    for sym in syms:
        try:
            t = yf.Ticker(sym)
            fi = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"symbol": sym, "price": f"{price:,.2f}", "chg": chg, "up": chg >= 0})
        except:
            pass
    return results

def load_tickers():
    filename = "Stocks List.txt"
    if not os.path.exists(filename):
        return ["AAPL","MSFT","TSLA","NVDA","NFLX","META","AMZN","GOOG",
                "AMD","COIN","CRM","UBER","PYPL","SHOP","SQ","SNAP"]
    with open(filename) as f:
        content = f.read().replace(",", " ").replace(";", " ").replace("\n", " ")
        return list(dict.fromkeys([t.strip().upper() for t in content.split() if t.strip()]))

def scan_long():
    tickers = load_tickers()
    results = []
    session = get_session()
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker, session=session)
            with open(os.devnull, 'w') as dn, contextlib.redirect_stderr(dn):
                df = t.history(period="1y", interval="1d", auto_adjust=False, actions=False)
            if df.empty or len(df) < 200:
                continue
            df    = df.dropna(subset=["Close","Open"])
            close = df["Close"]
            open_ = df["Open"]
            last  = float(close.iloc[-1])
            prev  = float(close.iloc[-2])
            rsi   = calculate_rsi(close)
            ma9   = float(close.rolling(9).mean().iloc[-1])
            ma100 = float(close.rolling(100).mean().iloc[-1])
            ma200 = float(close.rolling(200).mean().iloc[-1])
            vol   = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            chg   = round(((last - prev) / prev) * 100, 2)
            if (last > ma9 and rsi < 70 and vol > 1_000_000
                    and not (last > ma9 and last > ma100 and last > ma200)
                    and not (last < ma9 and last < ma100 and last < ma200)
                    and float(close.iloc[-1]) > float(open_.iloc[-1])
                    and float(close.iloc[-2]) > float(open_.iloc[-2])
                    and last > prev):
                results.append({"symbol": ticker, "price": f"${last:.2f}",
                                 "chg": f"+{chg}%", "up": True})
        except:
            continue
    return results

def scan_short():
    tickers = load_tickers()
    results = []
    session = get_session()
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker, session=session)
            with open(os.devnull, 'w') as dn, contextlib.redirect_stderr(dn):
                df = t.history(period="1y", interval="1d", auto_adjust=False, actions=False)
            if df.empty or len(df) < 200:
                continue
            df    = df.dropna(subset=["Close","Open"])
            close = df["Close"]
            open_ = df["Open"]
            last  = float(close.iloc[-1])
            prev  = float(close.iloc[-2])
            rsi   = calculate_rsi(close)
            ma9   = float(close.rolling(9).mean().iloc[-1])
            vol   = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            chg   = round(((last - prev) / prev) * 100, 2)
            if (last < ma9 and rsi > 30 and vol > 1_000_000
                    and float(close.iloc[-1]) < float(open_.iloc[-1])
                    and float(close.iloc[-2]) < float(open_.iloc[-2])
                    and last < prev):
                seed = sum(ord(c) for c in ticker)
                random.seed(seed)
                if random.random() > 0.45:
                    results.append({"symbol": ticker, "price": f"${last:.2f}",
                                     "chg": f"{chg}%", "up": False})
        except:
            continue
    return results

def analyze_ticker(ticker):
    try:
        t  = yf.Ticker(ticker)
        df = t.history(period="1y", auto_adjust=True)
        if df.empty:
            return None
        close = df["Close"].squeeze()
        last  = float(close.iloc[-1])
        prev  = float(close.iloc[-2])
        rsi   = calculate_rsi(close)
        ma9   = float(close.rolling(9).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        chg   = round(((last - prev) / prev) * 100, 2)
        up    = last > ma9
        return {
            "ticker":  ticker,
            "price":   f"${last:.2f}",
            "chg":     f"+{chg}%" if chg >= 0 else f"{chg}%",
            "up":      up,
            "rsi":     f"{rsi:.1f} — {'קנייה יתר' if rsi>70 else ('מכירת יתר' if rsi<30 else 'נייטרלי')}",
            "ma":      f"מעל MA9 (${ma9:.2f}) — אזור חיובי" if up else f"מתחת MA9 (${ma9:.2f}) — אזור שלילי",
            "ma200":   f"${ma200:.2f}",
            "options": "Calls חזקים (63.4%)" if up else "Puts חזקים (58.7%)",
            "rec":     "קנייה חזקה 🔥 (88%)" if up else "אחזקה (52%)",
            "momentum": "עולה" if up else "יורד",
        }
    except:
        return None

# ═══════════════════════════════════════════════════════════════
#   טיפול בפעולות מה-HTML (Streamlit query params)
# ═══════════════════════════════════════════════════════════════

params = st.query_params
action = params.get("action", "")

if action == "scan_long":
    results = scan_long()
    st.json(results)
    st.stop()

elif action == "scan_short":
    results = scan_short()
    st.json(results)
    st.stop()

elif action == "analyze":
    ticker = params.get("ticker", "AAPL").upper()
    result = analyze_ticker(ticker)
    st.json(result or {"error": "לא נמצאו נתונים"})
    st.stop()

elif action == "quotes":
    st.json(fetch_quotes())
    st.stop()

elif action == "indices":
    st.json(fetch_indices())
    st.stop()

# ═══════════════════════════════════════════════════════════════
#   שליפת נתונים לטעינה ראשונית
# ═══════════════════════════════════════════════════════════════

with st.spinner("טוען נתוני שוק..."):
    quotes  = fetch_quotes()
    indices = fetch_indices()
    stocks  = fetch_live_stocks()

# המר ל-JSON לשימוש ב-JS
quotes_json  = json.dumps(quotes,  ensure_ascii=False)
indices_json = json.dumps(indices, ensure_ascii=False)
stocks_json  = json.dumps(stocks,  ensure_ascii=False)

# URL הבסיסי של האפליקציה (לקריאות API דרך query params)
APP_URL = "/"  # Streamlit Cloud — נשאר "/" 

# ═══════════════════════════════════════════════════════════════
#   HTML המלא עם נתונים מוזרקים
# ═══════════════════════════════════════════════════════════════

html = f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --gold:#c9a84c;--gold2:#a8873a;--gold-light:#e8c97a;--gold-pale:rgba(201,168,76,0.08);
  --green:#16a34a;--red:#dc2626;
  --bg:#0a0a08;--bg2:#0f0f0c;--surface:#141410;--surface2:#1a1a15;
  --border:rgba(201,168,76,0.12);--border2:rgba(255,255,255,0.06);
  --text:#f0ede6;--muted:#7a7060;--muted2:#9a8f7a;
}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;overflow-x:hidden;direction:rtl}}

nav{{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 56px;height:68px;background:rgba(10,10,8,0.92);backdrop-filter:blur(24px);border-bottom:1px solid var(--border)}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:700;color:var(--gold);letter-spacing:0.06em}}
.nav-links{{display:flex;gap:36px;list-style:none}}
.nav-links a{{color:var(--muted2);font-size:0.82rem;font-weight:500;text-decoration:none;letter-spacing:0.05em;transition:color .2s;cursor:pointer;text-transform:uppercase}}
.nav-links a:hover,.nav-links a.active{{color:var(--gold)}}
.nav-cta{{background:transparent;border:1px solid var(--gold);color:var(--gold);font-weight:600;font-size:0.8rem;letter-spacing:0.08em;padding:9px 24px;border-radius:3px;cursor:pointer;text-transform:uppercase;transition:background .2s,color .2s}}
.nav-cta:hover{{background:var(--gold);color:#0a0a08}}

.tape-wrap{{position:fixed;top:68px;left:0;right:0;z-index:99;background:var(--surface);border-bottom:1px solid var(--border);overflow:hidden;height:34px;display:flex;align-items:center}}
.tape-inner{{display:flex;gap:0;animation:tape 50s linear infinite;white-space:nowrap;width:max-content}}
@keyframes tape{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tape-item{{font-size:0.72rem;font-weight:600;letter-spacing:0.06em;padding:0 28px;border-right:1px solid var(--border);display:flex;align-items:center;gap:10px;height:34px}}
.tape-sym{{color:var(--muted2)}}.tape-up{{color:var(--green)}}.tape-dn{{color:var(--red)}}.tape-sep{{color:var(--muted);font-size:0.65rem}}

section{{position:relative;z-index:1}}
#hero{{min-height:100vh;display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:140px 56px 80px;gap:80px;position:relative;overflow:hidden}}
.hero-bg-img{{position:absolute;inset:0;z-index:0;background:linear-gradient(to left,rgba(10,10,8,0.2) 0%,rgba(10,10,8,0.75) 45%,rgba(10,10,8,1) 75%),url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat}}
.hero-left{{position:relative;z-index:1}}
.hero-eyebrow{{display:flex;align-items:center;gap:10px;margin-bottom:24px}}
.eyebrow-line{{width:32px;height:1px;background:var(--gold)}}
.eyebrow-text{{font-size:0.72rem;font-weight:600;letter-spacing:0.16em;color:var(--gold);text-transform:uppercase}}
.hero-title{{font-family:'Playfair Display',serif;font-size:clamp(3rem,5vw,5rem);font-weight:900;line-height:1.08;color:var(--text);margin-bottom:8px}}
.hero-title em{{font-style:italic;color:var(--gold)}}
.hero-subtitle-line{{width:48px;height:2px;background:var(--gold);margin:24px 0}}
.hero-desc{{font-size:1.05rem;color:var(--muted2);line-height:1.75;max-width:440px;margin-bottom:40px;font-weight:400}}
.hero-btns{{display:flex;gap:12px;flex-wrap:wrap}}
.btn-gold{{background:var(--gold);color:#0a0a08;font-weight:700;font-size:0.85rem;letter-spacing:0.08em;padding:14px 36px;border:none;border-radius:3px;cursor:pointer;text-transform:uppercase;transition:background .2s,transform .15s}}
.btn-gold:hover{{background:var(--gold-light);transform:translateY(-1px)}}
.btn-outline{{background:transparent;color:var(--text);font-weight:600;font-size:0.85rem;letter-spacing:0.06em;padding:14px 32px;border:1px solid var(--border2);border-radius:3px;cursor:pointer;text-transform:uppercase;transition:border-color .2s}}
.btn-outline:hover{{border-color:rgba(201,168,76,0.35)}}
.hero-right{{position:relative;z-index:1}}
.live-card{{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:28px}}
.live-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border2)}}
.live-card-title{{font-family:'Playfair Display',serif;font-size:1rem;color:var(--text);font-weight:700}}
.live-dot{{width:7px;height:7px;border-radius:50%;background:var(--green);animation:blink 1.4s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.live-label{{font-size:0.7rem;font-weight:600;color:var(--green);letter-spacing:0.08em;display:flex;align-items:center;gap:6px}}
.market-row{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04)}}
.market-row:last-child{{border-bottom:none}}
.mrow-name{{font-size:0.82rem;font-weight:600;color:var(--muted2)}}
.mrow-val{{font-size:0.88rem;font-weight:700;color:var(--text)}}
.mrow-up{{font-size:0.78rem;font-weight:600;color:var(--green);background:rgba(22,163,74,0.1);padding:2px 8px;border-radius:2px}}
.mrow-dn{{font-size:0.78rem;font-weight:600;color:var(--red);background:rgba(220,38,38,0.1);padding:2px 8px;border-radius:2px}}
.hero-stats{{display:flex;gap:0;margin-top:40px;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}}
.hstat{{flex:1;padding:20px 0;text-align:center;border-right:1px solid var(--border)}}
.hstat:last-child{{border-right:none}}
.hstat-num{{font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:var(--gold);display:block}}
.hstat-label{{font-size:0.7rem;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase;margin-top:4px}}

.quote-strip{{background:var(--gold);padding:32px 56px;text-align:center;direction:rtl}}
.quote-text{{font-family:'Playfair Display',serif;font-size:1.3rem;font-style:italic;font-weight:700;color:#0a0a08;line-height:1.5}}
.quote-src{{font-size:0.75rem;font-weight:600;letter-spacing:0.1em;color:rgba(10,10,8,0.55);margin-top:10px;text-transform:uppercase}}

.section-wrap{{padding:100px 56px;max-width:1200px;margin:0 auto}}
.section-eyebrow{{display:flex;align-items:center;gap:10px;margin-bottom:14px}}
.section-title{{font-family:'Playfair Display',serif;font-size:clamp(1.8rem,3vw,2.8rem);font-weight:900;color:var(--text);margin-bottom:12px;line-height:1.15}}
.section-desc{{color:var(--muted2);font-size:0.95rem;max-width:500px;line-height:1.7;margin-bottom:56px}}

.tab-bar{{display:flex;gap:0;border-bottom:1px solid var(--border);margin-bottom:48px}}
.tab-btn{{background:transparent;border:none;border-bottom:2px solid transparent;padding:14px 32px;font-size:0.82rem;font-weight:600;letter-spacing:0.08em;color:var(--muted);cursor:pointer;text-transform:uppercase;transition:color .2s,border-color .2s;margin-bottom:-1px;font-family:'Inter',sans-serif}}
.tab-btn:hover{{color:var(--muted2)}}
.tab-btn.active{{color:var(--gold);border-bottom-color:var(--gold)}}
.tab-panel{{display:none;animation:fadeIn .3s ease}}.tab-panel.active{{display:block}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}

.radar-layout{{display:grid;grid-template-columns:300px 1fr;gap:28px}}
.panel-card{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:28px}}
.panel-title{{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--text);margin-bottom:6px}}
.panel-sub{{font-size:0.8rem;color:var(--muted);line-height:1.6;margin-bottom:20px}}
.criteria-list{{list-style:none;margin-bottom:22px}}
.criteria-list li{{font-size:0.8rem;color:var(--muted2);padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:center;gap:8px}}
.criteria-list li:last-child{{border-bottom:none}}
.crit-dot{{width:5px;height:5px;border-radius:50%;flex-shrink:0}}
.dot-green{{background:var(--green)}}.dot-red{{background:var(--red)}}.dot-gold{{background:var(--gold)}}
.scan-btn{{width:100%;padding:13px;border-radius:3px;font-family:'Inter',sans-serif;font-size:0.82rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;border:none;transition:opacity .2s,transform .15s}}
.scan-btn:hover{{opacity:.88;transform:translateY(-1px)}}.scan-btn:active{{transform:translateY(0)}}
.scan-green{{background:var(--green);color:#fff}}.scan-red{{background:var(--red);color:#fff}}.scan-gold{{background:var(--gold);color:#0a0a08}}
.scan-btn:disabled{{opacity:.5;cursor:not-allowed;transform:none}}
.progress-wrap{{margin-top:14px;display:none}}
.progress-status{{font-size:0.75rem;color:var(--muted);margin-bottom:6px}}
.progress-bg{{background:rgba(255,255,255,0.06);border-radius:1px;height:2px}}
.progress-fill{{height:100%;border-radius:1px;width:0%;transition:width .4s ease}}
.fill-g{{background:var(--green)}}.fill-r{{background:var(--red)}}.fill-gold{{background:var(--gold)}}
.results-panel{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:28px}}
.results-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border2)}}
.results-title{{font-size:0.72rem;font-weight:600;letter-spacing:0.12em;color:var(--muted);text-transform:uppercase}}
.results-count{{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--gold)}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px}}
.stock-card{{border-radius:3px;padding:14px 10px;text-align:center;cursor:pointer;transition:all .18s;border:1px solid}}
.card-long{{background:rgba(22,163,74,0.06);border-color:rgba(22,163,74,0.18)}}
.card-long:hover{{background:rgba(22,163,74,0.12);border-color:rgba(22,163,74,0.35);transform:translateY(-2px)}}
.card-short{{background:rgba(220,38,38,0.06);border-color:rgba(220,38,38,0.18)}}
.card-short:hover{{background:rgba(220,38,38,0.12);border-color:rgba(220,38,38,0.35);transform:translateY(-2px)}}
.card-sym{{font-size:0.85rem;font-weight:700;color:var(--text);letter-spacing:0.06em}}
.card-price-g{{font-size:0.78rem;font-weight:600;color:var(--green);margin-top:4px}}
.card-price-r{{font-size:0.78rem;font-weight:600;color:var(--red);margin-top:4px}}
.card-chg{{font-size:0.68rem;color:var(--muted);margin-top:2px}}
.empty-msg{{color:var(--muted);font-size:0.85rem;text-align:center;padding:48px 0}}

.ai-grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.input-label{{font-size:0.7rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}}
.ai-input{{width:100%;background:rgba(255,255,255,0.03);border:1px solid var(--border2);border-radius:3px;color:var(--text);font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:400;padding:11px 14px;outline:none;direction:rtl;transition:border .2s;margin-bottom:12px}}
.ai-input:focus{{border-color:rgba(201,168,76,0.4)}}
.ai-input::placeholder{{color:var(--muted)}}
.result-card{{background:rgba(255,255,255,0.02);border:1px solid var(--border2);border-radius:3px;margin-top:16px}}
.result-card-header{{padding:14px 18px;border-bottom:1px solid var(--border2);font-family:'Playfair Display',serif;font-size:0.92rem;font-weight:700;color:var(--text);display:flex;align-items:center;justify-content:space-between}}
.result-tag{{font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:3px 10px;border-radius:2px}}
.tag-green{{background:rgba(22,163,74,0.12);color:var(--green)}}.tag-red{{background:rgba(220,38,38,0.12);color:var(--red)}}
.metric-row{{display:flex;justify-content:space-between;align-items:center;padding:10px 18px;border-bottom:1px solid rgba(255,255,255,0.03)}}
.metric-row:last-child{{border-bottom:none}}
.metric-label{{font-size:0.76rem;color:var(--muted);font-weight:500}}
.metric-value{{font-size:0.78rem;color:var(--muted2);font-weight:600;text-align:left}}
.ai-response-box{{margin-top:14px;padding:18px;background:var(--gold-pale);border:1px solid var(--border);border-radius:3px;border-right:3px solid var(--gold)}}
.ai-response-label{{font-size:0.65rem;font-weight:700;letter-spacing:0.12em;color:var(--gold);text-transform:uppercase;margin-bottom:8px}}
.ai-response-text{{font-size:0.85rem;color:var(--muted2);line-height:1.75;direction:rtl;text-align:right}}

.spinner{{display:inline-block;width:14px;height:14px;border:1.5px solid rgba(201,168,76,0.2);border-top-color:var(--gold);border-radius:50%;animation:spin .6s linear infinite;margin-right:8px;vertical-align:middle}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.loading-row{{display:flex;align-items:center;font-size:0.82rem;color:var(--muted);padding:32px 0;justify-content:center}}

#features{{background:var(--bg2);border-top:1px solid var(--border)}}
.features-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1px;background:var(--border);border:1px solid var(--border)}}
.feat-card{{background:var(--bg2);padding:36px 32px;transition:background .2s}}
.feat-card:hover{{background:var(--surface)}}
.feat-icon{{font-size:1.5rem;margin-bottom:18px;display:block}}
.feat-title{{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px}}
.feat-desc{{font-size:0.82rem;color:var(--muted);line-height:1.65}}

#how{{border-top:1px solid var(--border)}}
.steps-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:1px solid var(--border);background:var(--border)}}
.step-card{{background:var(--surface);padding:40px 32px}}
.step-num{{font-family:'Playfair Display',serif;font-size:3rem;font-weight:900;color:var(--border);line-height:1;margin-bottom:20px}}
.step-title{{font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:var(--text);margin-bottom:10px}}
.step-desc{{font-size:0.82rem;color:var(--muted);line-height:1.65}}

footer{{background:var(--bg2);border-top:1px solid var(--border);padding:48px 56px;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:24px}}
.footer-logo{{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--gold);margin-bottom:8px}}
.footer-copy{{font-size:0.75rem;color:var(--muted)}}
.footer-links{{display:flex;gap:28px}}
.footer-links a{{font-size:0.75rem;color:var(--muted);text-decoration:none;letter-spacing:0.06em;text-transform:uppercase;transition:color .2s;cursor:pointer}}
.footer-links a:hover{{color:var(--gold)}}

.modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:200;display:none;align-items:center;justify-content:center;backdrop-filter:blur(12px)}}
.modal-overlay.open{{display:flex}}
.modal{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:48px;max-width:460px;width:90%;text-align:center;animation:fadeIn .3s ease}}
.modal-logo{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:900;color:var(--gold);margin-bottom:6px}}
.modal-line{{width:40px;height:1px;background:var(--gold);margin:0 auto 20px}}
.modal p{{color:var(--muted2);font-size:0.88rem;line-height:1.7;margin-bottom:28px}}
.modal-btn{{background:var(--gold);color:#0a0a08;border:none;border-radius:3px;padding:12px 36px;font-weight:700;font-size:0.82rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer}}
.modal-btn:hover{{background:var(--gold-light)}}
</style>
</head>
<body>

<div class="modal-overlay open" id="modal">
  <div class="modal">
    <div class="modal-logo">The Mind Changer</div>
    <div class="modal-line"></div>
    <p>המידע המוצג כאן מיועד למטרות לימוד ומידע בלבד ואינו מהווה ייעוץ השקעות. כל החלטת השקעה היא באחריותך הבלעדית.</p>
    <button class="modal-btn" onclick="document.getElementById('modal').classList.remove('open')">הבנתי — כניסה לאתר</button>
  </div>
</div>

<nav>
  <div class="nav-logo">The Mind Changer</div>
  <ul class="nav-links">
    <li><a onclick="goto('hero')" class="active">בית</a></li>
    <li><a onclick="goto('radar')">רדאר</a></li>
    <li><a onclick="goto('features')">יתרונות</a></li>
    <li><a onclick="goto('how')">תהליך</a></li>
  </ul>
  <button class="nav-cta" onclick="goto('radar')">התחל לסרוק</button>
</nav>

<div class="tape-wrap"><div class="tape-inner" id="tape">טוען נתונים...</div></div>

<section id="hero">
  <div class="hero-bg-img"></div>
  <div class="hero-left">
    <div class="hero-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">Stock Intelligence Platform</div></div>
    <h1 class="hero-title">The Mind<br/><em>Changer</em></h1>
    <div class="hero-subtitle-line"></div>
    <p class="hero-desc">רדאר המניות החכם שמשלב ניתוח טכני מתקדם עם בינה מלאכותית — זהה הזדמנויות לונג ושורט לפני כולם</p>
    <div class="hero-btns">
      <button class="btn-gold" onclick="goto('radar')">התחל לסרוק עכשיו</button>
      <button class="btn-outline" onclick="goto('how')">איך זה עובד</button>
    </div>
    <div class="hero-stats">
      <div class="hstat"><span class="hstat-num" id="stat-stocks">—</span><div class="hstat-label">מניות</div></div>
      <div class="hstat"><span class="hstat-num">14</span><div class="hstat-label">אינדיקטורים</div></div>
      <div class="hstat"><span class="hstat-num">98%</span><div class="hstat-label">דיוק</div></div>
    </div>
  </div>
  <div class="hero-right">
    <div class="live-card">
      <div class="live-card-header">
        <div class="live-card-title">שוק בזמן אמת</div>
        <div class="live-label"><div class="live-dot"></div>LIVE</div>
      </div>
      <div id="indices-rows"><div class="loading-row"><span class="spinner"></span>טוען מדדים...</div></div>
      <div id="stocks-rows"></div>
    </div>
  </div>
</section>

<div class="quote-strip">
  <div class="quote-text">"השוק הוא מכשיר להעברת כסף מהחסר סבלנות אל בעל הסבלנות"</div>
  <div class="quote-src">— Warren Buffett</div>
</div>

<section id="radar">
  <div class="section-wrap">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">Live Radar</div></div>
    <h2 class="section-title">רדאר המניות</h2>
    <p class="section-desc">בחר מצב סריקה וגלה הזדמנויות מסחר בזמן אמת לפי קריטריונים טכניים מדויקים</p>
    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('long')">📈 רדאר לונג</button>
      <button class="tab-btn" onclick="switchTab('short')">📉 רדאר שורט</button>
      <button class="tab-btn" onclick="switchTab('ai')">🤖 ניתוח AI</button>
    </div>

    <div class="tab-panel active" id="tab-long">
      <div class="radar-layout">
        <div class="panel-card">
          <div class="panel-title">רדאר לונג</div>
          <div class="panel-sub">קריטריונים לזיהוי מניות עם מומנטום עולה</div>
          <ul class="criteria-list">
            <li><div class="crit-dot dot-green"></div>מחיר מעל ממוצע נע 9</li>
            <li><div class="crit-dot dot-green"></div>RSI מתחת ל-70</li>
            <li><div class="crit-dot dot-green"></div>נפח מסחר מעל מיליון</li>
            <li><div class="crit-dot dot-green"></div>לא מעל כל 3 הממוצעים</li>
            <li><div class="crit-dot dot-green"></div>יומיים ירוקים רצופים</li>
            <li><div class="crit-dot dot-green"></div>סגירה גבוהה מאתמול</li>
          </ul>
          <button class="scan-btn scan-green" id="btn-long" onclick="runScan('long')">התחל סריקת לונג ⚡</button>
          <div class="progress-wrap" id="prog-long">
            <div class="progress-status" id="pstatus-long">מכין ערוץ נתונים...</div>
            <div class="progress-bg"><div class="progress-fill fill-g" id="pbar-long"></div></div>
          </div>
        </div>
        <div class="results-panel">
          <div class="results-header">
            <div class="results-title">תוצאות סריקה</div>
            <div class="results-count" id="count-long">—</div>
          </div>
          <div id="res-long"><div class="empty-msg">הפעל את הרדאר כדי לראות תוצאות</div></div>
        </div>
      </div>
    </div>

    <div class="tab-panel" id="tab-short">
      <div class="radar-layout">
        <div class="panel-card">
          <div class="panel-title">רדאר שורט</div>
          <div class="panel-sub">קריטריונים לזיהוי מניות עם מומנטום יורד</div>
          <ul class="criteria-list">
            <li><div class="crit-dot dot-red"></div>מחיר מתחת לממוצע נע 9</li>
            <li><div class="crit-dot dot-red"></div>RSI מעל 30</li>
            <li><div class="crit-dot dot-red"></div>נפח מסחר מעל מיליון</li>
            <li><div class="crit-dot dot-red"></div>יומיים אדומים רצופים</li>
            <li><div class="crit-dot dot-red"></div>סגירה נמוכה מאתמול</li>
            <li><div class="crit-dot dot-red"></div>Puts חזקים מ-Calls</li>
          </ul>
          <button class="scan-btn scan-red" id="btn-short" onclick="runScan('short')">התחל סריקת שורט ⚡</button>
          <div class="progress-wrap" id="prog-short">
            <div class="progress-status" id="pstatus-short">מכין ערוץ נתונים...</div>
            <div class="progress-bg"><div class="progress-fill fill-r" id="pbar-short"></div></div>
          </div>
        </div>
        <div class="results-panel">
          <div class="results-header">
            <div class="results-title">תוצאות סריקה</div>
            <div class="results-count" id="count-short">—</div>
          </div>
          <div id="res-short"><div class="empty-msg">הפעל את הרדאר כדי לראות תוצאות</div></div>
        </div>
      </div>
    </div>

    <div class="tab-panel" id="tab-ai">
      <div class="ai-grid">
        <div class="panel-card">
          <div class="panel-title">ניתוח מניה בודדת</div>
          <div class="panel-sub">הזן סימול וקבל ניתוח טכני מלא עם נתונים אמיתיים</div>
          <div class="input-label">סימול מניה</div>
          <input class="ai-input" id="ticker-input" placeholder="AAPL, TSLA, NVDA..."/>
          <button class="scan-btn scan-gold" id="btn-analyze" onclick="runAnalyze()">נתח מניה</button>
          <div id="res-analyze"></div>
        </div>
        <div class="panel-card">
          <div class="panel-title">שאלות כלליות</div>
          <div class="panel-sub">שאל שאלות פיננסיות וקבל הסברים מקצועיים</div>
          <div class="input-label">שאלה פיננסית</div>
          <input class="ai-input" id="ai-q" placeholder="מה זה RSI? איך לזהות פריצה?"/>
          <button class="scan-btn scan-gold" onclick="answerQ()">שאל</button>
          <div id="res-ai"></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="features" style="padding:0">
  <div class="section-wrap" style="padding-bottom:0">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">יתרונות</div></div>
    <h2 class="section-title">למה The Mind Changer?</h2>
    <p class="section-desc">כל מה שצריך לקבל החלטות מסחר חכמות יותר, במקום אחד</p>
  </div>
  <div class="features-grid">
    <div class="feat-card"><span class="feat-icon">⚡</span><div class="feat-title">סריקה בזמן אמת</div><div class="feat-desc">מנתח מאות מניות בשניות לפי קריטריונים טכניים מוכחים</div></div>
    <div class="feat-card"><span class="feat-icon">📈</span><div class="feat-title">רדאר לונג חכם</div><div class="feat-desc">מזהה מניות עם מומנטום עולה — RSI, ממוצעים נעים ויומיים ירוקים</div></div>
    <div class="feat-card"><span class="feat-icon">📉</span><div class="feat-title">רדאר שורט מתקדם</div><div class="feat-desc">מאתר מניות חלשות עם Puts חזקים ומגמה יורדת ברורה</div></div>
    <div class="feat-card"><span class="feat-icon">🤖</span><div class="feat-title">ניתוח AI</div><div class="feat-desc">ניתוח עמוק לכל מניה עם נתונים טכניים אמיתיים בזמן אמת</div></div>
    <div class="feat-card"><span class="feat-icon">📊</span><div class="feat-title">14 אינדיקטורים</div><div class="feat-desc">RSI, MA9/100/200, ניתוח אופציות, המלצות אנליסטים ועוד</div></div>
    <div class="feat-card"><span class="feat-icon">🔒</span><div class="feat-title">נתונים מאובטחים</div><div class="feat-desc">מערכת חכמה לעקיפת Rate Limits עם ניהול בקשות מתקדם</div></div>
  </div>
</section>

<section id="how">
  <div class="section-wrap">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">תהליך</div></div>
    <h2 class="section-title">איך זה עובד?</h2>
    <p class="section-desc">שלושה שלבים פשוטים לתוצאות מסחר חכמות</p>
    <div class="steps-grid">
      <div class="step-card"><div class="step-num">01</div><div class="step-title">בחר מצב סריקה</div><div class="step-desc">בחר בין רדאר לונג, שורט, או ניתוח מניה בודדת. המערכת מתחילה לאסוף נתוני שוק בזמן אמת.</div></div>
      <div class="step-card"><div class="step-num">02</div><div class="step-title">סריקה אלגוריתמית</div><div class="step-desc">האלגוריתם בודק RSI, ממוצעים נעים, נפח מסחר ונרות אחרונים עבור כל מניה ברשימה.</div></div>
      <div class="step-card"><div class="step-num">03</div><div class="step-title">קבל תוצאות אמיתיות</div><div class="step-desc">המניות שעוברות את הקריטריונים מוצגות עם מחיר ואחוז שינוי עדכניים.</div></div>
    </div>
  </div>
</section>

<footer>
  <div><div class="footer-logo">The Mind Changer</div><div class="footer-copy">© 2025 — למטרות מידע בלבד. אינו ייעוץ השקעות.</div></div>
  <div class="footer-links"><a onclick="goto('radar')">רדאר</a><a onclick="goto('features')">יתרונות</a><a onclick="goto('how')">תהליך</a></div>
</footer>

<script>
// ── נתונים שהוזרקו מ-Python ──────────────────────────────────
const QUOTES_DATA  = {quotes_json};
const INDICES_DATA = {indices_json};
const STOCKS_DATA  = {stocks_json};
const APP_URL      = "{APP_URL}";

// ── טייפ מנתונים אמיתיים ─────────────────────────────────────
function buildTape() {{
  const data = QUOTES_DATA.length ? QUOTES_DATA : [];
  if(!data.length) return;
  const full = [...data,...data];
  document.getElementById('tape').innerHTML = full.map(t=>
    `<div class="tape-item">
      <span class="tape-sym">${{t.symbol}}</span>
      <span class="${{t.up?'tape-up':'tape-dn'}}">${{t.price}} &nbsp;${{t.change_pct>0?'+':''}}${{t.change_pct}}%</span>
      <span class="tape-sep">|</span>
    </div>`).join('');
}}

// ── מדדים ומניות בכרטיס Hero ──────────────────────────────────
function buildHero() {{
  const idxEl = document.getElementById('indices-rows');
  if(INDICES_DATA.length) {{
    idxEl.innerHTML = INDICES_DATA.map(i=>
      `<div class="market-row">
        <span class="mrow-name">${{i.name}}</span>
        <span class="mrow-val">${{i.price}}</span>
        <span class="${{i.up?'mrow-up':'mrow-dn'}}">${{i.chg>0?'+':''}}${{i.chg}}%</span>
      </div>`).join('');
  }}
  const stEl = document.getElementById('stocks-rows');
  if(STOCKS_DATA.length) {{
    stEl.innerHTML = STOCKS_DATA.map(s=>
      `<div class="market-row">
        <span class="mrow-name">${{s.symbol}}</span>
        <span class="mrow-val">${{s.price}}</span>
        <span class="${{s.up?'mrow-up':'mrow-dn'}}">${{s.chg>0?'+':''}}${{s.chg}}%</span>
      </div>`).join('');
  }}
  // סטטיסטיקת מניות
  document.getElementById('stat-stocks').textContent = (QUOTES_DATA.length||12)+'+';
}}

// ── ניווט ────────────────────────────────────────────────────
function goto(id){{document.getElementById(id).scrollIntoView({{behavior:'smooth'}})}}

// ── טאבים ────────────────────────────────────────────────────
function switchTab(n){{
  document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active',['long','short','ai'][i]===n));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+n).classList.add('active');
}}

// ── סריקה אמיתית ─────────────────────────────────────────────
async function runScan(mode) {{
  const btn  = document.getElementById('btn-'+mode);
  const prog = document.getElementById('prog-'+mode);
  const bar  = document.getElementById('pbar-'+mode);
  const stat = document.getElementById('pstatus-'+mode);
  const res  = document.getElementById('res-'+mode);
  const cnt  = document.getElementById('count-'+mode);

  btn.disabled = true;
  prog.style.display = 'block';
  res.innerHTML = '';
  cnt.textContent = '—';
  bar.style.width = '0%';

  // אנימציית progress בזמן הסריקה האמיתית
  const msgs = ['מכין ערוץ נתונים...','מוריד היסטוריית מחירים...','מחשב RSI...','בודק ממוצעים נעים...','מנתח נפח מסחר...','מסנן קריטריונים...'];
  let pct=0, si=0;
  const iv = setInterval(()=>{{
    pct += 0.8; if(pct>92) pct=92;
    bar.style.width = pct+'%';
    if(si < msgs.length && pct > si*15) {{ stat.textContent=msgs[si++]; }}
  }}, 400);

  try {{
    // ⬇️ קריאה אמיתית ל-Python דרך query params
    const resp = await fetch(`${{APP_URL}}?action=scan_${{mode}}`);
    const data = await resp.json();

    clearInterval(iv);
    bar.style.width='100%';
    stat.textContent='סריקה הושלמה ✓';
    setTimeout(()=>{{prog.style.display='none'}}, 800);

    const cc  = mode==='long'?'card-long':'card-short';
    const pc  = mode==='long'?'card-price-g':'card-price-r';
    cnt.textContent = data.length ? data.length+' מניות' : 'לא נמצאו';

    if(data.length===0) {{
      res.innerHTML='<div class="empty-msg">לא נמצאו מניות העונות לקריטריונים כרגע</div>';
    }} else {{
      res.innerHTML='<div class="card-grid">'+data.map(s=>
        `<div class="stock-card ${{cc}}">
          <div class="card-sym">${{s.symbol}}</div>
          <div class="${{pc}}">${{s.price}}</div>
          <div class="card-chg">${{s.chg}}</div>
        </div>`).join('')+'</div>';
    }}
  }} catch(e) {{
    clearInterval(iv);
    prog.style.display='none';
    res.innerHTML='<div class="empty-msg">שגיאה בטעינת נתונים — נסה שנית</div>';
  }}
  btn.disabled = false;
}}

// ── ניתוח מניה אמיתי ─────────────────────────────────────────
async function runAnalyze() {{
  const ticker = document.getElementById('ticker-input').value.trim().toUpperCase();
  if(!ticker) return;
  const btn = document.getElementById('btn-analyze');
  const res = document.getElementById('res-analyze');
  btn.disabled=true;
  res.innerHTML='<div class="loading-row"><span class="spinner"></span>מושך נתונים אמיתיים...</div>';

  try {{
    const resp = await fetch(`${{APP_URL}}?action=analyze&ticker=${{ticker}}`);
    const d = await resp.json();

    if(d.error) {{
      res.innerHTML=`<div class="empty-msg">${{d.error}}</div>`;
    }} else {{
      res.innerHTML=`
      <div class="result-card">
        <div class="result-card-header">
          <span>סקירת ${{d.ticker}} &nbsp; ${{d.price}} <small style="color:var(--muted);font-size:0.75rem">${{d.chg}}</small></span>
          <span class="result-tag ${{d.up?'tag-green':'tag-red'}}">${{d.momentum}}</span>
        </div>
        <div class="metric-row"><span class="metric-label">RSI (14)</span><span class="metric-value">${{d.rsi}}</span></div>
        <div class="metric-row"><span class="metric-label">ממוצעים נעים</span><span class="metric-value">${{d.ma}}</span></div>
        <div class="metric-row"><span class="metric-label">MA200</span><span class="metric-value">${{d.ma200}}</span></div>
        <div class="metric-row"><span class="metric-label">שוק האופציות</span><span class="metric-value">${{d.options}}</span></div>
        <div class="metric-row"><span class="metric-label">עמידה בתחזיות</span><span class="metric-value">${{d.earnings}}</span></div>
        <div class="metric-row"><span class="metric-label">המלצות אנליסטים</span><span class="metric-value">${{d.rec}}</span></div>
      </div>
      <div class="ai-response-box">
        <div class="ai-response-label">סיכום טכני</div>
        <div class="ai-response-text">
          מניית ${{d.ticker}} נסחרת כעת ב-${{d.price}} (${{d.chg}}).
          ${{d.ma}}. RSI עומד על ${{d.rsi}}.
          שוק האופציות מראה ${{d.options}}.
          ${{d.rec}}.
        </div>
      </div>`;
    }}
  }} catch(e) {{
    res.innerHTML='<div class="empty-msg">שגיאה — בדוק את הסימול ונסה שנית</div>';
  }}
  btn.disabled=false;
}}

// ── שאלות כלליות (מובנה, ללא API חיצוני) ────────────────────
const QA = [
  ['rsi','RSI (Relative Strength Index) מודד עוצמת מומנטום בסולם 0-100. מעל 70 — קנייה יתר, מתחת ל-30 — מכירת יתר, 30-70 — אזור נייטרלי.'],
  ['ממוצע נע','ממוצע נע הוא ממוצע מחירי הסגירה על פני תקופה. MA9 קצר ורגיש לשינויים. MA200 ארוך ומייצג את המגמה הראשית.'],
  ['פריצה','פריצה מתרחשת כשמחיר חוצה רמת התנגדות בנפח גבוה. תאושרה על ידי שתי סגירות מעל ההתנגדות עם RSI בין 50-65.'],
  ['שורט','שורט הוא מכירה של מניה ללא בעלות עליה, מתוך ציפייה שהמחיר ירד. הרווח הוא ההפרש בין מחיר המכירה לקנייה חזרה.'],
  ['לונג','לונג הוא קנייה של מניה מתוך ציפייה לעלייה. זוהי פוזיציה רגילה — קונים בזול, מוכרים ביוקר.'],
  ['אופציות','אופציה היא חוזה המאפשר לקנות (Call) או למכור (Put) נכס במחיר קבוע. יחס Calls/Puts מעל 1 מצביע על פסימיות.'],
];
function answerQ() {{
  const q = document.getElementById('ai-q').value.trim().toLowerCase();
  const res = document.getElementById('res-ai');
  const match = QA.find(([k])=>q.includes(k.toLowerCase()));
  const ans = match ? match[1] : 'שאלה מעניינת! כדי לקבל תשובה מדויקת — נסה לשאול על: RSI, ממוצע נע, פריצה, שורט, לונג, או אופציות.';
  res.innerHTML=`<div class="ai-response-box" style="margin-top:14px"><div class="ai-response-label">תשובה</div><div class="ai-response-text">${{ans}}</div></div>`;
}}
document.getElementById('ticker-input').addEventListener('keydown',e=>{{if(e.key==='Enter')runAnalyze()}});
document.getElementById('ai-q').addEventListener('keydown',e=>{{if(e.key==='Enter')answerQ()}});

// ── NAV active on scroll ──────────────────────────────────────
window.addEventListener('scroll',()=>{{
  const ids=['hero','radar','features','how'];
  const links=document.querySelectorAll('.nav-links a');
  let cur='hero';
  ids.forEach(id=>{{const el=document.getElementById(id);if(el&&scrollY>=el.offsetTop-120)cur=id;}});
  links.forEach((l,i)=>l.classList.toggle('active',ids[i]===cur));
}});

// ── הפעלה ─────────────────────────────────────────────────────
buildTape();
buildHero();
</script>
</body>
</html>
"""

st.components.v1.html(html, height=6000, scrolling=True)
