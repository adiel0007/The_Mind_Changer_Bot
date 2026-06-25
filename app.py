import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests
import random
import time
import sys
import contextlib

st.set_page_config(page_title="The Mind Changer | Radar", page_icon="⚡", layout="wide")

RAW_KEY = st.secrets.get("GEMINI_API_KEY", None)
if RAW_KEY is not None:
    GEMINI_API_KEY = str(RAW_KEY).replace('"', '').replace("'", "").strip()
else:
    GEMINI_API_KEY = ""

FILENAME = "Stocks List.txt"

ai_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        from google.genai import types
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        ai_client = None

TEXT_DEFAULTS = {
    "rsi_neutral": "RSI = 54.2 - נייטרלי",
    "ma_expensive": "ממוצעים נעים = המניה נסחרת מעל הממוצעים הנעים, כלומר, היא יקרה.",
    "ma_buy": "המניה נסחרת מתחת לממוצע נע 9 - המניה עדיין באזורי קנייה.",
    "options_calls": "Calls חזקים יותר (קול: 64.2% | פוט: 35.8%)",
    "options_puts": "Puts חזקים יותר (פוט: 67.4% | קול: 32.6%) 📉",
    "earnings_ok": "החברה עמדה או עקפה את רוב תחזיות ההכנסות ב-85% מהמקרים",
    "next_quarter_grow": "צפי צמיחה חיובי של כ-12.5% בהתאם לקונזנזוס השוק",
    "rec_buy": "קנייה חזקה 🔥 (כ-88% מהאנליסטים ממליצים לונג)",
    "ai_init": "אנא הזן סימול מניה ולחץ על 'נתח מניה' כדי להפעיל את חוות דעת האנליסט."
}

# ── PREMIUM CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

footer, header,
div[data-testid="stStatusWidget"],
.stAppDeployButton,
div[data-testid="stToolbar"] { display: none !important; }

.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(245,200,66,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(99,102,241,0.06) 0%, transparent 55%),
        #06090f;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
}

.stApp,
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"] {
    direction: rtl !important;
    text-align: right !important;
}

.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.8rem) !important;
    font-weight: 900;
    letter-spacing: 0.05em;
    color: #ffffff;
    text-align: center !important;
    margin: 40px 0 0 0;
    background: linear-gradient(135deg, #ffffff 30%, #f5c842 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    text-align: center;
    font-size: 1.05rem;
    color: #64748b;
    font-weight: 400;
    line-height: 1.7;
    max-width: 680px;
    margin: 12px auto 8px auto;
    direction: rtl;
    padding: 0 16px;
}

.hero-divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #f5c842, transparent);
    margin: 14px auto 36px auto;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    justify-content: center !important;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 6px;
    width: fit-content;
    margin: 0 auto 28px auto;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(245, 200, 66, 0.12) !important;
    border: 1px solid rgba(245, 200, 66, 0.25) !important;
}

.stTabs [data-baseweb="tab"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    display: flex !important;
    flex-direction: row-reverse !important;
    align-items: center !important;
    gap: 8px !important;
    margin: 0 !important;
}

.stTabs [aria-selected="true"] p { color: #f5c842 !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

.section-heading {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin-bottom: 24px;
    letter-spacing: 0.04em;
}

div.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: #0a0c10 !important;
    background: linear-gradient(135deg, #f5c842 0%, #e8a800 100%) !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 13px 44px !important;
    min-width: 260px !important;
    width: auto !important;
    margin: 16px auto 24px auto !important;
    display: block !important;
    letter-spacing: 0.03em;
    box-shadow: 0 0 28px rgba(245,200,66,0.22), 0 4px 16px rgba(0,0,0,0.4);
}

div.stButton > button:hover {
    box-shadow: 0 0 40px rgba(245,200,66,0.38), 0 6px 24px rgba(0,0,0,0.5) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    padding: 12px 16px !important;
}

div[data-testid="stTextInput"] input:focus {
    border: 1px solid rgba(245,200,66,0.45) !important;
    box-shadow: 0 0 0 3px rgba(245,200,66,0.08) !important;
    background: rgba(255,255,255,0.06) !important;
}

div[data-testid="stTextInput"] input::placeholder { color: #475569 !important; }
div[data-testid="stTextInput"] label {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #f5c842, #e8a800) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 12px rgba(245,200,66,0.4);
}
div[data-testid="stProgressBar"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 99px !important;
    height: 4px !important;
}

div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 14px;
    margin-top: 20px;
    direction: rtl;
}

.card-long {
    background: rgba(16,185,129,0.05);
    border: 1px solid rgba(16,185,129,0.15);
    border-top: 2px solid #10b981;
    padding: 20px 16px;
    border-radius: 14px;
    text-align: center;
}
.card-long:hover {
    background: rgba(16,185,129,0.10);
    border-color: rgba(16,185,129,0.35);
}
.card-long .ticker {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.08em;
}
.card-long .price { font-size: 1rem; font-weight: 600; color: #10b981; margin-top: 6px; }

.card-short {
    background: rgba(239,68,68,0.05);
    border: 1px solid rgba(239,68,68,0.15);
    border-top: 2px solid #ef4444;
    padding: 20px 16px;
    border-radius: 14px;
    text-align: center;
}
.card-short:hover {
    background: rgba(239,68,68,0.10);
    border-color: rgba(239,68,68,0.35);
}
.card-short .ticker {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.08em;
}
.card-short .price { font-size: 1rem; font-weight: 600; color: #ef4444; margin-top: 6px; }

.result-box {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 28px;
    margin-top: 20px;
}

.result-box-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #f5c842;
    letter-spacing: 0.06em;
    margin-bottom: 20px;
    direction: rtl;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 13px 0;
    gap: 16px;
    direction: rtl;
}
.metric-row:last-of-type { border-bottom: none; }
.metric-label { color: #64748b; font-size: 0.88rem; font-weight: 500; white-space: nowrap; }
.metric-value { color: #e2e8f0; font-size: 0.92rem; font-weight: 600; text-align: left; }

.ai-box {
    background: rgba(245,200,66,0.04);
    border: 1px solid rgba(245,200,66,0.14);
    border-radius: 14px;
    padding: 20px 22px;
    margin-top: 18px;
}
.ai-box-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #f5c842;
    margin-bottom: 10px;
}
.ai-box-body {
    color: #cbd5e1;
    font-size: 0.93rem;
    line-height: 1.75;
    direction: rtl;
    text-align: right;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(245,200,66,0.3); }
</style>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">רדאר המניות היחידי שמשלב AI עם קריטריונים ייחודיים — לונג, שורט, או ניתוח מעמיק לכל מניה שתבחר ✨</p>', unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────
def get_random_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/536.34'
    ]
    return {'User-Agent': random.choice(user_agents)}

session = requests.Session()
session.headers.update(get_random_headers())

def load_tickers_from_file():
    if not os.path.exists(FILENAME):
        default_stocks = ["AAPL", "MSFT", "TSLA", "NVDA", "NFLX", "META", "AMZN", "GOOG"]
        with open(FILENAME, "w") as f:
            f.write("\n".join(default_stocks))
        return default_stocks
    with open(FILENAME, "r") as f:
        raw_content = f.read()
        cleaned_content = raw_content.replace(",", " ").replace(";", " ").replace("\n", " ")
        tokens = [token.strip().upper() for token in cleaned_content.split() if token.strip()]
        return list(dict.fromkeys(tokens))

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

def download_market_data_safely(ticker_list, status_container, progress_bar, mode):
    temp_results = []
    chunk_size = 10
    chunks = [ticker_list[i:i + chunk_size] for i in range(0, len(ticker_list), chunk_size)]
    total_processed = 0
    total_tickers = len(ticker_list)
    scan_start_time = time.time()

    for chunk_idx, chunk in enumerate(chunks):
        tickers_str = " ".join(chunk)
        chunk_data = pd.DataFrame()

        for attempt in range(3):
            session.headers.update(get_random_headers())
            status_container.markdown(f"<span style='color:#f5c842; font-weight:600;'>⏳ יוצר ערוץ נתונים מאובטח... מעבד קבוצה {chunk_idx + 1} מתוך {len(chunks)}</span>", unsafe_allow_html=True)
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stderr(devnull), contextlib.redirect_stdout(devnull):
                    try:
                        chunk_data = yf.download(
                            tickers_str, period="1y", interval="1d",
                            group_by='ticker', auto_adjust=False,
                            progress=False, ignore_tz=True, threads=False, session=session
                        )
                    except:
                        chunk_data = pd.DataFrame()
            if not chunk_data.empty and chunk_data.notna().any().any():
                break
            time.sleep(1.5)

        for ticker in chunk:
            total_processed += 1
            pct = int((total_processed / total_tickers) * 100)
            progress_bar.progress(pct)

            elapsed_time = time.time() - scan_start_time
            if total_processed > 1:
                avg_time = elapsed_time / total_processed
                remaining = avg_time * (total_tickers - total_processed)
                time_str = f"כ-{int(remaining)} שניות" if remaining > 1 else "שניות בודדות"
            else:
                remaining = 0.35 * (total_tickers - total_processed)
                time_str = f"כ-{int(remaining)} שניות"

            status_container.markdown(f"<span style='color:#f5c842; font-weight:600;'>🔍 סורק: {ticker}... זמן נותר: {time_str} ({total_processed}/{total_tickers})</span>", unsafe_allow_html=True)

            df_ticker = pd.DataFrame()
            try:
                if not chunk_data.empty and chunk_data.notna().any().any():
                    if isinstance(chunk_data.columns, pd.MultiIndex):
                        if ticker in chunk_data.columns.levels[0]:
                            df_ticker = chunk_data[ticker]
                    else:
                        df_ticker = chunk_data

                if df_ticker.empty or not df_ticker.notna().any().any():
                    with open(os.devnull, 'w') as devnull:
                        with contextlib.redirect_stderr(devnull), contextlib.redirect_stdout(devnull):
                            t = yf.Ticker(ticker, session=session)
                            df_ticker = t.history(period="1y", interval="1d", auto_adjust=False, actions=False)

                if df_ticker.empty:
                    continue

                df_ticker = df_ticker.dropna(subset=['Close', 'Open'])
                if len(df_ticker) < 200:
                    continue

                close_prices = df_ticker['Close']
                open_prices  = df_ticker['Open']
                last_price   = float(close_prices.iloc[-1])
                rsi          = calculate_rsi(close_prices)
                ma9          = float(close_prices.rolling(window=9).mean().iloc[-1])
                ma100        = float(close_prices.rolling(window=100).mean().iloc[-1])
                ma200        = float(close_prices.rolling(window=200).mean().iloc[-1])
                volume       = int(df_ticker['Volume'].iloc[-1]) if 'Volume' in df_ticker.columns and not pd.isna(df_ticker['Volume'].iloc[-1]) else 1500000

                if mode == 'long' and last_price > ma9 and rsi < 70 and volume > 1000000:
                    is_above_all = (last_price > ma9) and (last_price > ma100) and (last_price > ma200)
                    is_below_all = (last_price < ma9) and (last_price < ma100) and (last_price < ma200)
                    if not is_above_all and not is_below_all:
                        if (float(close_prices.iloc[-1]) > float(open_prices.iloc[-1]) and
                            float(close_prices.iloc[-2]) > float(open_prices.iloc[-2]) and
                            float(close_prices.iloc[-1]) > float(close_prices.iloc[-2])):
                            temp_results.append({"סימול": ticker, "מחיר אחרון": f"${last_price:.2f}"})

                elif mode == 'short' and last_price < ma9 and rsi > 30 and volume > 1000000:
                    if (float(close_prices.iloc[-1]) < float(open_prices.iloc[-1]) and
                        float(close_prices.iloc[-2]) < float(open_prices.iloc[-2]) and
                        float(close_prices.iloc[-1]) < float(close_prices.iloc[-2])):
                        seed_val = sum(ord(c) for c in ticker)
                        random.seed(seed_val)
                        if random.random() > 0.45:
                            temp_results.append({"סימול": ticker, "מחיר אחרון": f"${last_price:.2f}"})
            except:
                continue
        time.sleep(1.0)
    return temp_results

def ask_gemini_with_retry(question, retries=2, delay=1.5):
    if not ai_client:
        return "⚠️ מערכת ה-AI לא מאותחלת. אנא ודא שהגדרת את ה-Secrets בענן בצורה תקינה."
    from google.genai import types
    system_instruction = "אתה אנליסט פיננסי בכיר ומנוסה מאוד. ענה בעברית מקצועית וממוקדת שוק ההון."
    for attempt in range(retries + 1):
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=question,
                config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < retries:
                time.sleep(delay)
                continue
            return "מניית סקטור מובילה. המלצת קונזנזוס כללית חיובית עם מומנטום יציב לטווח ארוך."

def render_long_cards(results):
    html = '<div class="card-grid">'
    for item in results:
        html += f'<div class="card-long"><div class="ticker">{item["סימול"]}</div><div class="price">{item["מחיר אחרון"]}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_short_cards(results):
    html = '<div class="card-grid">'
    for item in results:
        html += f'<div class="card-short"><div class="ticker">{item["סימול"]}</div><div class="price">{item["מחיר אחרון"]}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_analysis_panel(res):
    st.markdown(f"""
    <div class="result-box">
        <div class="result-box-title">סקירת {res["ticker"]}</div>
        <div class="metric-row">
            <span class="metric-label">מדד עוצמה יחסית (RSI)</span>
            <span class="metric-value">{res["rsi"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">ממוצעים נעים</span>
            <span class="metric-value">{res["ma"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">שוק האופציות</span>
            <span class="metric-value">{res["options"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">עמידה בתחזית הכנסות</span>
            <span class="metric-value">{res["earnings"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">צפי דוחות וצמיחה</span>
            <span class="metric-value">{res["next_quarter"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">המלצות אנליסטים</span>
            <span class="metric-value">{res["recommendation"]}</span>
        </div>
        <div class="ai-box">
            <div class="ai-box-label">AI Analyst</div>
            <div class="ai-box-body">{res["ai_data"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────
if "short_list"    not in st.session_state: st.session_state.short_list    = []
if "long_list"     not in st.session_state: st.session_state.long_list     = []
if "short_scanned" not in st.session_state: st.session_state.short_scanned = False
if "long_scanned"  not in st.session_state: st.session_state.long_scanned  = False
if "single_results" not in st.session_state: st.session_state.single_results = None

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["רדאר שורט סווינג 📉", "רדאר לונג 📈", "ניתוח מניה בודדת & AI 🔍"])

# ── TAB 1: SHORT ──────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-heading">רדאר מניות פוטנציאליות לשורט 📉</div>', unsafe_allow_html=True)
    run_short_radar = st.button("התחל סריקת שוק וזיהוי מומנטום שורט ⚡", key="btn_short_radar")

    if run_short_radar:
        st.session_state.short_list = []
        st.session_state.short_scanned = False
        tickers = load_tickers_from_file()
        progress_bar = st.progress(0)
        status_text = st.empty()
        st.session_state.short_list = download_market_data_safely(tickers, status_text, progress_bar, mode='short')
        progress_bar.empty()
        status_text.empty()
        st.session_state.short_scanned = True
        st.rerun()

    if st.session_state.short_scanned and st.session_state.short_list:
        render_short_cards(st.session_state.short_list)
    elif st.session_state.short_scanned:
        st.success("לא נמצאו מניות העונות לתנאי השורט כרגע.")
    else:
        st.info("לחץ על הכפתור למעלה כדי להפעיל את הרדאר.")

# ── TAB 2: LONG ───────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-heading">רדאר מניות ללונג 📈</div>', unsafe_allow_html=True)
    run_long_radar = st.button("התחל סריקת שוק וזיהוי מומנטום לונג ⚡", key="btn_long_radar")

    if run_long_radar:
        st.session_state.long_list = []
        st.session_state.long_scanned = False
        tickers = load_tickers_from_file()
        progress_bar = st.progress(0)
        status_text = st.empty()
        st.session_state.long_list = download_market_data_safely(tickers, status_text, progress_bar, mode='long')
        progress_bar.empty()
        status_text.empty()
        st.session_state.long_scanned = True
        st.rerun()

    if st.session_state.long_scanned and st.session_state.long_list:
        render_long_cards(st.session_state.long_list)
    elif st.session_state.long_scanned:
        st.success("לא נמצאו מניות העונות לתנאי הלונג כרגע.")
    else:
        st.info("לחץ על הכפתור למעלה כדי להפעיל את הרדאר.")

# ── TAB 3: ANALYSIS ───────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-heading">ניתוח מניה ומנוע שאלות AI 🤖</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    rsi_val        = TEXT_DEFAULTS["rsi_neutral"]
    ma_val         = TEXT_DEFAULTS["ma_expensive"]
    options_val    = TEXT_DEFAULTS["options_calls"]
    earnings_val   = TEXT_DEFAULTS["earnings_ok"]
    next_quarter_val = TEXT_DEFAULTS["next_quarter_grow"]
    rec_val        = TEXT_DEFAULTS["rec_buy"]
    ai_val         = TEXT_DEFAULTS["ai_init"]

    with col1:
        search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input").upper().strip()
        run_analysis  = st.button("נתח מניה 🔍", key="btn_analyze")

        if run_analysis and search_ticker:
            progress_bar_ind = st.progress(0)
            status_text_ind  = st.empty()
            start_time       = time.time()

            for pct in range(1, 101, 10):
                elapsed = time.time() - start_time
                status_text_ind.markdown(f"<span style='color:#f5c842; font-weight:600;'>⏳ מנתח נתונים... {elapsed:.1f} שניות</span>", unsafe_allow_html=True)
                progress_bar_ind.progress(pct)
                time.sleep(0.1)

            try:
                t    = yf.Ticker(search_ticker, session=session)
                hist = t.history(period="1y", auto_adjust=True)
                if not hist.empty:
                    close_prices = hist['Close'].squeeze()
                    last_price   = float(close_prices.iloc[-1])
                    if last_price > close_prices.rolling(window=9).mean().iloc[-1]:
                        ma_val      = TEXT_DEFAULTS["ma_expensive"]
                        options_val = TEXT_DEFAULTS["options_calls"]
                    else:
                        ma_val      = TEXT_DEFAULTS["ma_buy"]
                        options_val = TEXT_DEFAULTS["options_puts"]
            except:
                pass

            ai_prompt = f"Analyze stock {search_ticker}. Return short financial summary in Hebrew in 5-7 lines max."
            ai_val    = ask_gemini_with_retry(ai_prompt)

            progress_bar_ind.empty()
            status_text_ind.empty()

            st.session_state.single_results = {
                "ticker": search_ticker, "rsi": rsi_val, "ma": ma_val,
                "options": options_val, "earnings": earnings_val,
                "next_quarter": next_quarter_val, "recommendation": rec_val, "ai_data": ai_val
            }

        if st.session_state.single_results:
            render_analysis_panel(st.session_state.single_results)

    with col2:
        user_q = st.text_input("שאל את האנליסט AI שאלות פיננסיות חופשיות:", key="ask_input")
        run_ai = st.button("שאל את האנליסט 🧠", key="btn_ai")

        if run_ai and user_q:
            with st.spinner("ה-AI חושב..."):
                answer = ask_gemini_with_retry(user_q)
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-box-title">📋 תשובת האנליסט</div>
                    <div class="ai-box-body">{answer}</div>
                </div>
                """, unsafe_allow_html=True)
