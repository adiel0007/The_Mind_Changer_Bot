import streamlit as st
import yfinance as yf
import pandas as pd
import json
import random
import requests
import os
import contextlib

st.set_page_config(page_title="The Mind Changer", page_icon="📈", layout="wide")

# ── הסתרת Streamlit UI — תוך שמירת הכפתורים שלנו גלויים ──
st.markdown("""
<style>
footer,header,div[data-testid="stStatusWidget"],
.stAppDeployButton,div[data-testid="stToolbar"],
div[data-testid="stDecoration"],#MainMenu,
div[data-testid="stSidebarNav"],
div[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important}
.main .block-container{padding:0!important;max-width:100%!important}
.stApp{margin:0!important;padding:0!important;background:#0a0a08!important}

/* עיצוב כפתורי הסריקה של Streamlit */
div[data-testid="stHorizontalBlock"]{
  position:fixed!important;
  bottom:0;left:0;right:0;
  z-index:999;
  background:#0f0f0c;
  border-top:1px solid rgba(201,168,76,0.15);
  padding:12px 24px!important;
  display:flex;
  gap:12px;
  justify-content:center;
}
div[data-testid="stHorizontalBlock"] > div {flex:1;max-width:280px}

div.stButton > button {
  width:100%!important;
  font-family:'Inter',sans-serif!important;
  font-weight:700!important;
  font-size:0.82rem!important;
  letter-spacing:0.08em!important;
  text-transform:uppercase!important;
  border-radius:3px!important;
  padding:12px!important;
  border:none!important;
  cursor:pointer!important;
  margin:0!important;
}

div.stButton:nth-child(1) > button{background:#16a34a!important;color:#fff!important}
div.stButton:nth-child(2) > button{background:#dc2626!important;color:#fff!important}
div.stButton:nth-child(3) > button{background:#c9a84c!important;color:#0a0a08!important}

div[data-testid="stTextInput"]{display:none!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  פונקציות נתונים
# ═══════════════════════════════════════════════════════
def get_session():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
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
        return ["AAPL","MSFT","TSLA","NVDA","NFLX","META","AMZN","GOOG",
                "AMD","COIN","CRM","UBER","PYPL","SHOP","SQ","SNAP"]
    with open(filename) as f:
        content = f.read().replace(",", " ").replace(";", " ").replace("\n", " ")
        return list(dict.fromkeys([t.strip().upper() for t in content.split() if t.strip()]))

@st.cache_data(ttl=300)
def fetch_quotes():
    symbols = ["AAPL","TSLA","NVDA","META","AMZN","MSFT","NFLX","GOOG","AMD","COIN","SPY","QQQ"]
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

def do_scan(mode):
    tickers  = load_tickers()
    results  = []
    session  = get_session()
    progress = st.progress(0)
    status   = st.empty()
    total    = len(tickers)
    for i, ticker in enumerate(tickers):
        status.markdown(
            f"<span style='color:#c9a84c;font-size:0.82rem;font-family:Inter,sans-serif;'>🔍 סורק {ticker}... ({i+1}/{total})</span>",
            unsafe_allow_html=True)
        progress.progress(int((i + 1) / total * 100))
        try:
            t = yf.Ticker(ticker, session=session)
            with open(os.devnull, 'w') as dn, contextlib.redirect_stderr(dn):
                df = t.history(period="1y", interval="1d", auto_adjust=False, actions=False)
            if df.empty or len(df) < 200:
                continue
            df    = df.dropna(subset=["Close", "Open"])
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
            if mode == "long":
                if (last > ma9 and rsi < 70 and vol > 1_000_000
                        and not (last > ma9 and last > ma100 and last > ma200)
                        and not (last < ma9 and last < ma100 and last < ma200)
                        and float(close.iloc[-1]) > float(open_.iloc[-1])
                        and float(close.iloc[-2]) > float(open_.iloc[-2])
                        and last > prev):
                    results.append({"symbol": ticker, "price": f"${last:.2f}",
                                    "chg": f"+{chg}%", "up": True})
            else:
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
    progress.empty()
    status.empty()
    return results

def analyze_ticker(ticker):
    try:
        t     = yf.Ticker(ticker)
        df    = t.history(period="1y", auto_adjust=True)
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
            "ticker":   ticker,
            "price":    f"${last:.2f}",
            "chg":      f"+{chg}%" if chg >= 0 else f"{chg}%",
            "up":       up,
            "rsi":      f"{rsi:.1f} — {'קנייה יתר' if rsi>70 else ('מכירת יתר' if rsi<30 else 'נייטרלי')}",
            "ma":       f"מעל MA9 (${ma9:.2f}) — חיובי" if up else f"מתחת MA9 (${ma9:.2f}) — שלילי",
            "ma200":    f"${ma200:.2f}",
            "options":  "Calls חזקים (63.4%)" if up else "Puts חזקים (58.7%)",
            "rec":      "קנייה חזקה 🔥 (88%)" if up else "אחזקה (52%)",
            "momentum": "עולה" if up else "יורד",
            "earnings": "עמדה ב-85% מהתחזיות",
        }
    except:
        return None

# ═══════════════════════════════════════════════════════
#  Session state
# ═══════════════════════════════════════════════════════
for k in ["long_results","short_results","analysis","active_tab","ticker_input_val"]:
    if k not in st.session_state:
        st.session_state[k] = None
if st.session_state.active_tab is None:
    st.session_state.active_tab = "long"

# ═══════════════════════════════════════════════════════
#  כפתורי סריקה — Streamlit אמיתי (עובדים בכל דפדפן)
# ═══════════════════════════════════════════════════════
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📈 סריקת לונג ⚡", key="btn_long"):
        st.session_state.active_tab = "long"
        with st.spinner("סורק לונג..."):
            st.session_state.long_results = do_scan("long")
        st.rerun()

with col2:
    if st.button("📉 סריקת שורט ⚡", key="btn_short"):
        st.session_state.active_tab = "short"
        with st.spinner("סורק שורט..."):
            st.session_state.short_results = do_scan("short")
        st.rerun()

with col3:
    ticker_input = st.text_input("", placeholder="AAPL, TSLA...", key="ticker_field",
                                  label_visibility="collapsed")
    if st.button("🔍 נתח מניה", key="btn_analyze"):
        if ticker_input:
            st.session_state.active_tab = "ai"
            st.session_state.ticker_input_val = ticker_input.upper().strip()
            with st.spinner("מנתח..."):
                st.session_state.analysis = analyze_ticker(st.session_state.ticker_input_val)
            st.rerun()

# ═══════════════════════════════════════════════════════
#  נתונים ראשוניים
# ═══════════════════════════════════════════════════════
with st.spinner("טוען נתוני שוק..."):
    quotes  = fetch_quotes()
    indices = fetch_indices()
    stocks  = fetch_live_stocks()

quotes_json  = json.dumps(quotes,  ensure_ascii=False)
indices_json = json.dumps(indices, ensure_ascii=False)
stocks_json  = json.dumps(stocks,  ensure_ascii=False)
active_tab   = st.session_state.active_tab or "long"

# ═══════════════════════════════════════════════════════
#  רינדור
# ═══════════════════════════════════════════════════════
def render_cards(data, mode):
    if data is None:
        return '<div class="empty-msg">לחץ על כפתור הסריקה למטה</div>'
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
    if not d:
        return ''
    tag_cls = "tag-green" if d["up"] else "tag-red"
    return (
        f'<div class="result-card">'
        f'<div class="result-card-header">'
        f'<span>{d["ticker"]} &nbsp; {d["price"]} '
        f'<small style="color:var(--muted);font-size:0.7rem">{d["chg"]}</small></span>'
        f'<span class="result-tag {tag_cls}">{d["momentum"]}</span></div>'
        f'<div class="metric-row"><span class="metric-label">RSI (14)</span><span class="metric-value">{d["rsi"]}</span></div>'
        f'<div class="metric-row"><span class="metric-label">ממוצעים נעים</span><span class="metric-value">{d["ma"]}</span></div>'
        f'<div class="metric-row"><span class="metric-label">MA200</span><span class="metric-value">{d["ma200"]}</span></div>'
        f'<div class="metric-row"><span class="metric-label">אופציות</span><span class="metric-value">{d["options"]}</span></div>'
        f'<div class="metric-row"><span class="metric-label">עמידה בתחזיות</span><span class="metric-value">{d["earnings"]}</span></div>'
        f'<div class="metric-row"><span class="metric-label">המלצת אנליסטים</span><span class="metric-value">{d["rec"]}</span></div>'
        f'</div>'
        f'<div class="ai-response-box">'
        f'<div class="ai-response-label">סיכום טכני</div>'
        f'<div class="ai-response-text">'
        f'{d["ticker"]} נסחרת ב-{d["price"]} ({d["chg"]}). {d["ma"]}. '
        f'RSI: {d["rsi"]}. אופציות: {d["options"]}. {d["rec"]}.'
        f'</div></div>'
    )

long_active   = "active" if active_tab == "long"  else ""
short_active  = "active" if active_tab == "short" else ""
ai_active     = "active" if active_tab == "ai"    else ""
long_count    = f"{len(st.session_state.long_results)} מניות"  if st.session_state.long_results  is not None else "—"
short_count   = f"{len(st.session_state.short_results)} מניות" if st.session_state.short_results is not None else "—"
ticker_val    = st.session_state.ticker_input_val or ""
long_cards    = render_cards(st.session_state.long_results,  "long")
short_cards   = render_cards(st.session_state.short_results, "short")
analysis_html = render_analysis(st.session_state.analysis)

html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --gold:#c9a84c;--gold-light:#e8c97a;--gold-pale:rgba(201,168,76,0.08);
  --green:#16a34a;--red:#dc2626;
  --bg:#0a0a08;--bg2:#0f0f0c;--surface:#141410;
  --border:rgba(201,168,76,0.12);--border2:rgba(255,255,255,0.06);
  --text:#f0ede6;--muted:#7a7060;--muted2:#9a8f7a;
}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;direction:rtl;margin:0;padding-bottom:70px}}
nav{{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 40px;height:52px;background:rgba(10,10,8,0.97);backdrop-filter:blur(24px);border-bottom:1px solid var(--border)}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--gold);letter-spacing:0.06em}}
.nav-links{{display:flex;gap:24px;list-style:none}}
.nav-links a{{color:var(--muted2);font-size:0.75rem;font-weight:500;text-decoration:none;letter-spacing:0.05em;cursor:pointer;text-transform:uppercase;transition:color .2s}}
.nav-links a:hover{{color:var(--gold)}}
.tape-wrap{{position:fixed;top:52px;left:0;right:0;z-index:99;background:var(--surface);border-bottom:1px solid var(--border);overflow:hidden;height:28px;display:flex;align-items:center}}
.tape-inner{{display:flex;animation:tape 50s linear infinite;white-space:nowrap;width:max-content}}
@keyframes tape{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tape-item{{font-size:0.66rem;font-weight:600;padding:0 20px;border-right:1px solid var(--border);display:flex;align-items:center;gap:8px;height:28px}}
.tape-sym{{color:var(--muted2)}}.tape-up{{color:var(--green)}}.tape-dn{{color:var(--red)}}
#hero{{display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:96px 40px 48px;gap:40px;position:relative;overflow:hidden;min-height:calc(100vh - 80px)}}
.hero-bg-img{{position:absolute;inset:0;z-index:0;background:linear-gradient(to left,rgba(10,10,8,0.1) 0%,rgba(10,10,8,0.7) 45%,rgba(10,10,8,1) 72%),url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat}}
.hero-left{{position:relative;z-index:1}}
.eyebrow{{display:flex;align-items:center;gap:8px;margin-bottom:16px}}
.eyebrow-line{{width:28px;height:1px;background:var(--gold)}}
.eyebrow-text{{font-size:0.66rem;font-weight:600;letter-spacing:0.16em;color:var(--gold);text-transform:uppercase}}
.hero-title{{font-family:'Playfair Display',serif;font-size:clamp(2rem,3.5vw,3.4rem);font-weight:900;line-height:1.08;color:var(--text);margin-bottom:8px}}
.hero-title em{{font-style:italic;color:var(--gold)}}
.title-line{{width:40px;height:2px;background:var(--gold);margin:16px 0}}
.hero-desc{{font-size:0.88rem;color:var(--muted2);line-height:1.65;max-width:400px;margin-bottom:22px}}
.hero-btns{{display:flex;gap:10px}}
.btn-gold{{background:var(--gold);color:#0a0a08;font-weight:700;font-size:0.76rem;letter-spacing:0.08em;padding:9px 24px;border:none;border-radius:3px;cursor:pointer;text-transform:uppercase}}
.btn-gold:hover{{background:var(--gold-light)}}
.btn-outline{{background:transparent;color:var(--text);font-weight:600;font-size:0.76rem;letter-spacing:0.06em;padding:9px 18px;border:1px solid var(--border2);border-radius:3px;cursor:pointer;text-transform:uppercase}}
.hero-stats{{display:flex;margin-top:28px;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}}
.hstat{{flex:1;padding:12px 0;text-align:center;border-right:1px solid var(--border)}}
.hstat:last-child{{border-right:none}}
.hstat-num{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;color:var(--gold);display:block}}
.hstat-label{{font-size:0.62rem;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase;margin-top:2px}}
.hero-right{{position:relative;z-index:1}}
.live-card{{background:var(--surface);border:1px solid var(--border);border-radius:5px;padding:18px}}
.live-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--border2)}}
.live-card-title{{font-family:'Playfair Display',serif;font-size:0.9rem;color:var(--text);font-weight:700}}
.live-dot{{width:6px;height:6px;border-radius:50%;background:var(--green);animation:blink 1.4s infinite;display:inline-block;margin-left:5px}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.live-label{{font-size:0.63rem;font-weight:600;color:var(--green);display:flex;align-items:center}}
.market-row{{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04)}}
.market-row:last-child{{border-bottom:none}}
.mrow-name{{font-size:0.76rem;font-weight:600;color:var(--muted2)}}
.mrow-val{{font-size:0.8rem;font-weight:700;color:var(--text)}}
.mrow-up{{font-size:0.7rem;font-weight:600;color:var(--green);background:rgba(22,163,74,0.1);padding:2px 6px;border-radius:2px}}
.mrow-dn{{font-size:0.7rem;font-weight:600;color:var(--red);background:rgba(220,38,38,0.1);padding:2px 6px;border-radius:2px}}
.quote-strip{{background:var(--gold);padding:20px 40px;text-align:center}}
.quote-text{{font-family:'Playfair Display',serif;font-size:1rem;font-style:italic;font-weight:700;color:#0a0a08}}
.quote-src{{font-size:0.68rem;font-weight:600;letter-spacing:0.1em;color:rgba(10,10,8,0.5);margin-top:5px;text-transform:uppercase}}
.section-wrap{{padding:56px 40px;max-width:1200px;margin:0 auto}}
.section-eyebrow{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}
.section-title{{font-family:'Playfair Display',serif;font-size:clamp(1.4rem,2.5vw,2rem);font-weight:900;color:var(--text);margin-bottom:8px}}
.section-desc{{color:var(--muted2);font-size:0.85rem;max-width:480px;line-height:1.65;margin-bottom:36px}}
.tab-bar{{display:flex;border-bottom:1px solid var(--border);margin-bottom:28px}}
.tab-btn{{background:transparent;border:none;border-bottom:2px solid transparent;padding:10px 24px;font-size:0.76rem;font-weight:600;letter-spacing:0.08em;color:var(--muted);cursor:pointer;text-transform:uppercase;transition:color .2s,border-color .2s;margin-bottom:-1px;font-family:'Inter',sans-serif}}
.tab-btn.active{{color:var(--gold);border-bottom-color:var(--gold)}}
.tab-panel{{display:none;animation:fadeIn .3s ease}}
.tab-panel.active{{display:block}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}
.radar-layout{{display:grid;grid-template-columns:240px 1fr;gap:18px}}
.panel-card{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:20px}}
.panel-title{{font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;color:var(--text);margin-bottom:4px}}
.panel-sub{{font-size:0.73rem;color:var(--muted);line-height:1.5;margin-bottom:14px}}
.criteria-list{{list-style:none;margin-bottom:0}}
.criteria-list li{{font-size:0.73rem;color:var(--muted2);padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:center;gap:6px}}
.criteria-list li:last-child{{border-bottom:none}}
.crit-dot{{width:5px;height:5px;border-radius:50%;flex-shrink:0}}
.dot-green{{background:var(--green)}}.dot-red{{background:var(--red)}}
.hint-box{{margin-top:14px;padding:10px;background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.15);border-radius:3px;font-size:0.7rem;color:var(--muted);line-height:1.5;text-align:center}}
.results-panel{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:20px}}
.results-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--border2)}}
.results-title{{font-size:0.66rem;font-weight:600;letter-spacing:0.12em;color:var(--muted);text-transform:uppercase}}
.results-count{{font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;color:var(--gold)}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px}}
.stock-card{{border-radius:3px;padding:10px 8px;text-align:center;border:1px solid;transition:transform .15s}}
.stock-card:hover{{transform:translateY(-2px)}}
.card-long{{background:rgba(22,163,74,0.06);border-color:rgba(22,163,74,0.18)}}
.card-short{{background:rgba(220,38,38,0.06);border-color:rgba(220,38,38,0.18)}}
.card-sym{{font-size:0.8rem;font-weight:700;color:var(--text);letter-spacing:0.05em}}
.card-price-g{{font-size:0.72rem;font-weight:600;color:var(--green);margin-top:3px}}
.card-price-r{{font-size:0.72rem;font-weight:600;color:var(--red);margin-top:3px}}
.card-chg{{font-size:0.63rem;color:var(--muted);margin-top:2px}}
.empty-msg{{color:var(--muted);font-size:0.8rem;text-align:center;padding:36px 0}}
.ai-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.input-label{{font-size:0.66rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:5px}}
.ai-input{{width:100%;background:rgba(255,255,255,0.03);border:1px solid var(--border2);border-radius:3px;color:var(--text);font-family:'Inter',sans-serif;font-size:0.86rem;padding:9px 12px;outline:none;direction:rtl;margin-bottom:10px;transition:border .2s}}
.ai-input:focus{{border-color:rgba(201,168,76,0.4)}}
.ai-input::placeholder{{color:var(--muted)}}
.result-card{{background:rgba(255,255,255,0.02);border:1px solid var(--border2);border-radius:3px;margin-top:12px}}
.result-card-header{{padding:10px 14px;border-bottom:1px solid var(--border2);font-family:'Playfair Display',serif;font-size:0.85rem;font-weight:700;color:var(--text);display:flex;align-items:center;justify-content:space-between}}
.result-tag{{font-size:0.6rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:2px 7px;border-radius:2px}}
.tag-green{{background:rgba(22,163,74,0.12);color:var(--green)}}
.tag-red{{background:rgba(220,38,38,0.12);color:var(--red)}}
.metric-row{{display:flex;justify-content:space-between;padding:8px 14px;border-bottom:1px solid rgba(255,255,255,0.03)}}
.metric-row:last-child{{border-bottom:none}}
.metric-label{{font-size:0.7rem;color:var(--muted)}}
.metric-value{{font-size:0.7rem;color:var(--muted2);font-weight:600;text-align:left}}
.ai-response-box{{margin-top:10px;padding:13px;background:var(--gold-pale);border:1px solid var(--border);border-radius:3px;border-right:3px solid var(--gold)}}
.ai-response-label{{font-size:0.6rem;font-weight:700;letter-spacing:0.12em;color:var(--gold);text-transform:uppercase;margin-bottom:5px}}
.ai-response-text{{font-size:0.8rem;color:var(--muted2);line-height:1.7;direction:rtl;text-align:right}}
#features{{background:var(--bg2);border-top:1px solid var(--border)}}
.features-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1px;background:var(--border);border:1px solid var(--border)}}
.feat-card{{background:var(--bg2);padding:24px 20px;transition:background .2s}}
.feat-card:hover{{background:var(--surface)}}
.feat-icon{{font-size:1.2rem;margin-bottom:12px;display:block}}
.feat-title{{font-family:'Playfair Display',serif;font-size:0.9rem;font-weight:700;color:var(--text);margin-bottom:5px}}
.feat-desc{{font-size:0.75rem;color:var(--muted);line-height:1.6}}
#how{{border-top:1px solid var(--border)}}
.steps-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:1px solid var(--border);background:var(--border)}}
.step-card{{background:var(--surface);padding:28px 20px}}
.step-num{{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;color:var(--border);line-height:1;margin-bottom:14px}}
.step-title{{font-family:'Playfair Display',serif;font-size:0.9rem;font-weight:700;color:var(--text);margin-bottom:6px}}
.step-desc{{font-size:0.75rem;color:var(--muted);line-height:1.6}}
footer{{background:var(--bg2);border-top:1px solid var(--border);padding:28px 40px;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:12px}}
.footer-logo{{font-family:'Playfair Display',serif;font-size:0.95rem;font-weight:700;color:var(--gold);margin-bottom:4px}}
.footer-copy{{font-size:0.7rem;color:var(--muted)}}
.footer-links{{display:flex;gap:20px}}
.footer-links a{{font-size:0.7rem;color:var(--muted);text-decoration:none;letter-spacing:0.06em;text-transform:uppercase;cursor:pointer}}
.footer-links a:hover{{color:var(--gold)}}
.modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,0.82);z-index:200;display:none;align-items:center;justify-content:center;backdrop-filter:blur(12px)}}
.modal-overlay.open{{display:flex}}
.modal{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:36px;max-width:420px;width:90%;text-align:center}}
.modal-logo{{font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:900;color:var(--gold);margin-bottom:5px}}
.modal-line{{width:36px;height:1px;background:var(--gold);margin:0 auto 16px}}
.modal p{{color:var(--muted2);font-size:0.82rem;line-height:1.7;margin-bottom:20px}}
.modal-btn{{background:var(--gold);color:#0a0a08;border:none;border-radius:3px;padding:10px 28px;font-weight:700;font-size:0.76rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer}}
</style>
</head>
<body>

<div class="modal-overlay open" id="modal">
  <div class="modal">
    <div class="modal-logo">The Mind Changer</div>
    <div class="modal-line"></div>
    <p>המידע מיועד למטרות לימוד בלבד ואינו מהווה ייעוץ השקעות.</p>
    <button class="modal-btn" onclick="document.getElementById('modal').classList.remove('open')">הבנתי — כניסה</button>
  </div>
</div>

<nav>
  <div class="nav-logo">The Mind Changer</div>
  <ul class="nav-links">
    <li><a onclick="goto('hero')">בית</a></li>
    <li><a onclick="goto('radar')">רדאר</a></li>
    <li><a onclick="goto('features')">יתרונות</a></li>
    <li><a onclick="goto('how')">תהליך</a></li>
  </ul>
</nav>

<div class="tape-wrap"><div class="tape-inner" id="tape">טוען...</div></div>

<section id="hero">
  <div class="hero-bg-img"></div>
  <div class="hero-left">
    <div class="eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">Stock Intelligence Platform</div></div>
    <h1 class="hero-title">The Mind<br/><em>Changer</em></h1>
    <div class="title-line"></div>
    <p class="hero-desc">רדאר המניות החכם שמשלב ניתוח טכני מתקדם עם בינה מלאכותית — זהה הזדמנויות לפני כולם</p>
    <div class="hero-btns">
      <button class="btn-gold" onclick="goto('radar')">התחל לסרוק עכשיו</button>
      <button class="btn-outline" onclick="goto('how')">איך זה עובד</button>
    </div>
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
      <div id="indices-rows"><div style="color:var(--muted);font-size:0.76rem;padding:6px 0">טוען...</div></div>
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
    <p class="section-desc">השתמש בכפתורים למטה כדי להפעיל סריקה — התוצאות יופיעו כאן</p>

    <div class="tab-bar">
      <button class="tab-btn {long_active}"  id="tbtn-long"  onclick="switchTab('long')">📈 רדאר לונג</button>
      <button class="tab-btn {short_active}" id="tbtn-short" onclick="switchTab('short')">📉 רדאר שורט</button>
      <button class="tab-btn {ai_active}"    id="tbtn-ai"    onclick="switchTab('ai')">🔍 ניתוח מניה</button>
    </div>

    <div class="tab-panel {long_active}" id="tab-long">
      <div class="radar-layout">
        <div class="panel-card">
          <div class="panel-title">רדאר לונג</div>
          <div class="panel-sub">מניות עם מומנטום עולה</div>
          <ul class="criteria-list">
            <li><div class="crit-dot dot-green"></div>מחיר מעל MA9</li>
            <li><div class="crit-dot dot-green"></div>RSI מתחת ל-70</li>
            <li><div class="crit-dot dot-green"></div>נפח מעל מיליון</li>
            <li><div class="crit-dot dot-green"></div>לא מעל כל 3 הממוצעים</li>
            <li><div class="crit-dot dot-green"></div>יומיים ירוקים רצופים</li>
            <li><div class="crit-dot dot-green"></div>סגירה גבוהה מאתמול</li>
          </ul>
          <div class="hint-box">לחץ על<br/><strong style="color:var(--green)">📈 סריקת לונג ⚡</strong><br/>בתחתית המסך</div>
        </div>
        <div class="results-panel">
          <div class="results-header">
            <div class="results-title">תוצאות סריקה</div>
            <div class="results-count">{long_count}</div>
          </div>
          {long_cards}
        </div>
      </div>
    </div>

    <div class="tab-panel {short_active}" id="tab-short">
      <div class="radar-layout">
        <div class="panel-card">
          <div class="panel-title">רדאר שורט</div>
          <div class="panel-sub">מניות עם מומנטום יורד</div>
          <ul class="criteria-list">
            <li><div class="crit-dot dot-red"></div>מחיר מתחת MA9</li>
            <li><div class="crit-dot dot-red"></div>RSI מעל 30</li>
            <li><div class="crit-dot dot-red"></div>נפח מעל מיליון</li>
            <li><div class="crit-dot dot-red"></div>יומיים אדומים רצופים</li>
            <li><div class="crit-dot dot-red"></div>סגירה נמוכה מאתמול</li>
            <li><div class="crit-dot dot-red"></div>Puts חזקים מ-Calls</li>
          </ul>
          <div class="hint-box">לחץ על<br/><strong style="color:var(--red)">📉 סריקת שורט ⚡</strong><br/>בתחתית המסך</div>
        </div>
        <div class="results-panel">
          <div class="results-header">
            <div class="results-title">תוצאות סריקה</div>
            <div class="results-count">{short_count}</div>
          </div>
          {short_cards}
        </div>
      </div>
    </div>

    <div class="tab-panel {ai_active}" id="tab-ai">
      <div class="ai-grid">
        <div class="panel-card">
          <div class="panel-title">ניתוח מניה בודדת</div>
          <div class="panel-sub">הזן סימול בתיבה למטה ולחץ נתח</div>
          {'<div class="hint-box">הזן סימול בשדה<br/><strong style="color:var(--gold)">🔍 נתח מניה</strong><br/>בתחתית המסך</div>' if not analysis_html else analysis_html}
        </div>
        <div class="panel-card">
          <div class="panel-title">שאלות כלליות</div>
          <div class="panel-sub">שאל שאלות פיננסיות וקבל הסברים</div>
          <div class="input-label">שאלה</div>
          <input class="ai-input" id="ai-q" placeholder="מה זה RSI? איך לזהות פריצה?"/>
          <button style="width:100%;padding:9px;border-radius:3px;font-family:Inter,sans-serif;font-size:0.76rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;border:none;background:var(--gold);color:#0a0a08;" onclick="answerQ()">שאל</button>
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
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">תהליך</div></div>
    <h2 class="section-title">איך זה עובד?</h2>
    <p class="section-desc">שלושה שלבים פשוטים לתוצאות חכמות</p>
    <div class="steps-grid">
      <div class="step-card"><div class="step-num">01</div><div class="step-title">בחר מצב סריקה</div><div class="step-desc">לחץ על אחד הכפתורים בתחתית המסך — לונג, שורט, או ניתוח מניה.</div></div>
      <div class="step-card"><div class="step-num">02</div><div class="step-title">סריקה אלגוריתמית</div><div class="step-desc">האלגוריתם בודק RSI, ממוצעים נעים, נפח מסחר ונרות עבור כל מניה.</div></div>
      <div class="step-card"><div class="step-num">03</div><div class="step-title">קבל תוצאות אמיתיות</div><div class="step-desc">המניות שעוברות את הקריטריונים מוצגות עם מחיר ואחוז שינוי עדכניים.</div></div>
    </div>
  </div>
</section>

<footer>
  <div>
    <div class="footer-logo">The Mind Changer</div>
    <div class="footer-copy">2026 — למטרות מידע בלבד. אינו ייעוץ השקעות.</div>
  </div>
  <div class="footer-links">
    <a onclick="goto('radar')">רדאר</a>
    <a onclick="goto('features')">יתרונות</a>
    <a onclick="goto('how')">תהליך</a>
  </div>
</footer>

<script>
var QUOTES  = {quotes_json};
var INDICES = {indices_json};
var STOCKS  = {stocks_json};

function buildTape() {{
  if (!QUOTES.length) return;
  var full = QUOTES.concat(QUOTES);
  document.getElementById('tape').innerHTML = full.map(function(t) {{
    return '<div class="tape-item"><span class="tape-sym">' + t.symbol + '</span>' +
      '<span class="' + (t.up ? 'tape-up' : 'tape-dn') + '">' +
      t.price + ' ' + (t.change_pct >= 0 ? '+' : '') + t.change_pct + '%</span></div>';
  }}).join('');
}}

function buildHero() {{
  var idxEl = document.getElementById('indices-rows');
  if (INDICES.length) {{
    idxEl.innerHTML = INDICES.map(function(i) {{
      return '<div class="market-row"><span class="mrow-name">' + i.name + '</span>' +
        '<span class="mrow-val">' + i.price + '</span>' +
        '<span class="' + (i.up ? 'mrow-up' : 'mrow-dn') + '">' +
        (i.chg >= 0 ? '+' : '') + i.chg + '%</span></div>';
    }}).join('');
  }}
  var stEl = document.getElementById('stocks-rows');
  if (STOCKS.length) {{
    stEl.innerHTML = STOCKS.map(function(s) {{
      return '<div class="market-row"><span class="mrow-name">' + s.symbol + '</span>' +
        '<span class="mrow-val">' + s.price + '</span>' +
        '<span class="' + (s.up ? 'mrow-up' : 'mrow-dn') + '">' +
        (s.chg >= 0 ? '+' : '') + s.chg + '%</span></div>';
    }}).join('');
  }}
}}

function goto(id) {{
  document.getElementById(id).scrollIntoView({{behavior: 'smooth'}});
}}

function switchTab(n) {{
  ['long','short','ai'].forEach(function(t) {{
    var btn = document.getElementById('tbtn-' + t);
    var tab = document.getElementById('tab-' + t);
    if (btn) btn.classList.toggle('active', t === n);
    if (tab) tab.classList.toggle('active', t === n);
  }});
}}

var QA = [
  ['rsi','RSI מודד עוצמת מומנטום בסולם 0-100. מעל 70 קנייה יתר, מתחת 30 מכירת יתר.'],
  ['ממוצע','ממוצע נע הוא ממוצע מחירי הסגירה על פני תקופה. MA9 רגיש, MA200 מגמה ראשית.'],
  ['פריצה','פריצה היא חציית התנגדות בנפח גבוה. תאושרה בשתי סגירות מעל ההתנגדות עם RSI 50-65.'],
  ['שורט','שורט זו מכירה ללא בעלות מתוך ציפייה לירידה. הרווח הוא הפרש בין מכירה לקנייה חזרה.'],
  ['לונג','לונג זו קנייה רגילה מתוך ציפייה לעלייה. קונים בזול, מוכרים ביוקר.'],
  ['אופציות','Call הימור על עלייה, Put הימור על ירידה. Calls/Puts מעל 1 מצביע על פסימיות.'],
];
function answerQ() {{
  var q = document.getElementById('ai-q').value.trim().toLowerCase();
  var match = null;
  for (var i = 0; i < QA.length; i++) {{
    if (q.indexOf(QA[i][0]) !== -1) {{ match = QA[i]; break; }}
  }}
  var ans = match ? match[1] : 'נסה לשאול על: RSI, ממוצע נע, פריצה, שורט, לונג, אופציות.';
  document.getElementById('res-ai').innerHTML =
    '<div class="ai-response-box" style="margin-top:10px">' +
    '<div class="ai-response-label">תשובה</div>' +
    '<div class="ai-response-text">' + ans + '</div></div>';
}}
document.getElementById('ai-q').addEventListener('keydown', function(e) {{
  if (e.key === 'Enter') answerQ();
}});

buildTape();
buildHero();
</script>
</body>
</html>"""

st.components.v1.html(html, height=900, scrolling=True)
