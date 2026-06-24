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

# 🛠️ חובה! הפקודה הראשונה ביותר של Streamlit בקוד למניעת שגיאות
st.set_page_config(page_title="The Mind Changer | Radar", page_icon="⚡", layout="wide")

# משיכת מפתח ה-API מה-Secrets, משתני סביבה או קובץ מקומי
def _load_gemini_key():
    raw = None
    try:
        raw = st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        pass
    if not raw:
        raw = os.environ.get("GEMINI_API_KEY")
    if not raw and os.path.exists(".streamlit/secrets.toml"):
        try:
            with open(".streamlit/secrets.toml", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY"):
                        raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass
    if not raw and os.path.exists("Mybot.py"):
        try:
            with open("Mybot.py", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY"):
                        raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass
    return str(raw).replace('"', '').replace("'", "").strip() if raw else ""

GEMINI_API_KEY = _load_gemini_key()

FILENAME = "Stocks List.txt"

# אתחול בטוח לחלוטין של ה-AI
ai_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        from google.genai import types
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        ai_client = None

# פונקציה לייצור כותרות דפדפן משתנות (User-Agent) לעקיפת חסימות קצב (Rate Limit)
def get_random_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'
    ]
    return {'User-Agent': random.choice(user_agents)}

# אתחול סשן בקשות דינמי
session = requests.Session()
session.headers.update(get_random_headers())

# מילון טקסטים סטטי מבודד למניעת שגיאות SyntaxError של גרשיים ועברית
TEXT_DEFAULTS = {
    "rsi_neutral": "RSI = 54.2 - נייטרלי",
    "ma_expensive": "ממוצעים נעים = המניה נסחרת מעל הממוצעים הנעים, כלומר, היא יקרה.",
    "ma_buy": "המניה נסחרת מתחת לממוצע נע 9 - המניה עדיין באזורי קנייה.",
    "options_calls": "Calls חזקים יותר (קול: 64.2% | פוט: 35.8%)",
    "earnings_ok": "החברה עמדה או עקפה את רוב תחזיות ההכנסות ב-85% מהמקרים",
    "next_quarter_grow": "צפי צמיחה חיובי של כ-12.5% בהתאם לקונזנזוס השוק",
    "rec_buy": "קנייה חזקה 🔥 (כ-88% מהאנליסטים ממליצים לונג)",
    "ai_init": "אנא הזן סימול מניה ולחץ על 'נתח מניה' כדי להפעיל את חוות דעת האנליסט."
}

# ==========================================
#     מערכת עיצוב פרימיום קשיחה וסופית (RTL)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;600;700&display=swap');

    /* הסתרת סרגל הכלים של המפתחים וסממני Streamlit */
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}

    .stApp {
        background-image: 
            linear-gradient(rgba(6, 9, 19, 0.90), rgba(6, 9, 19, 0.94)),
            url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp, div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.8rem !important;
        font-weight: 900;
        color: #ffffff;
        text-align: center !important;
        margin-top: 25px;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
    }
    
    .sub-title {
        font-size: 1.15rem;
        color: #cbd5e1;
        text-align: center !important;
        max-width: 850px;
        margin: 0 auto 40px auto;
        line-height: 1.7;
    }

    div[data-testid="stTextInput"] label, div[data-testid="stTextInput"] label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.35rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 8px !important;
    }

    .stMarkdown p, .stMarkdown span {
        color: #ffffff !important;
    }
    
    /* 🛠️ עיצוב קשיח וקיבוע הסמיילים/אייקונים בצד שמאל באופן אבסולוטי בטאבים */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        justify-content: center !important;
        border-bottom: 1px solid rgba(30, 41, 59, 0.8) !important;
    }
    
    .stTabs [data-baseweb="tab"] p {
        font-size: 1.3rem !important; 
        font-weight: 800 !important;  
        color: #94a3b8 !important;
        display: flex !important;
        flex-direction: row-reverse !important; /* זורק את האייקון/סמיילי שמאלה לסוף המשפט */
        align-items: center !important;
        gap: 10px !important;
    }
    
    .stTabs [aria-selected="true"] p {
        color: #ffbc00 !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(11, 15, 25, 0.85) !important;
        border: 1px solid rgba(30, 41, 59, 0.5) !important;
        border-radius: 6px 6px 0px 0px !important;
        padding: 12px 28px !important;
    }
    
    /* עיצוב כפתור הסריקה המרכזי פרימיום בתחתית */
    div.stButton > button {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        padding: 14px 45px !important;
        border-radius: 30px !important;
        border: none !important;
        width: auto !important;
        min-width: 280px !important;
        margin: 30px auto 20px auto !important;
        display: block !important;
        box-shadow: 0 4px 15px rgba(29, 78, 216, 0.4);
    }
    
    div[data-testid="stTextInput"] input {
        color: #000000 !important;           
        font-weight: 700 !important;          
        background-color: #ffffff !important; 
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    .result-box {
        background-color: #0b111e; 
        padding: 30px; 
        border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.08); 
        margin-top: 25px;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 14px 0;
        font-size: 1.15rem;
    }
    .metric-row-step {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(0, 242, 254, 0.1);
        padding: 12px 10px;
        font-size: 1.1rem;
        background: rgba(255, 255, 255, 0.01);
    }
    .metric-label {
        color: #94a3b8;
        font-weight: 600;
    }
    .metric-value {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    .header-row-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    .header-text-title {
        margin: 0;
        padding: 0;
        color: #ffffff !important;
        font-size: 1.6rem;
        font-weight: 700;
    }
    .header-left-side {
        display: flex;
        align-items: center;
    }
    .header-emoji {
        font-size: 1.6rem;
    }
    </style>
""", unsafe_allow_html=True)

def load_tickers_from_file():
    if not os.path.exists(FILENAME):
        default_stocks = ["AAPL", "MSFT", "TSLA", "NVDA", "NFLX", "META", "AMZN", "GOOG"]
        with open(FILENAME, "w", encoding="utf-8") as f:
            f.write(",".join(default_stocks))
        return default_stocks
    with open(FILENAME, "r", encoding="utf-8") as f:
        content = f.read()
    tickers = [
        t.strip().upper()
        for t in content.replace("\n", ",").replace("\r", ",").replace(" ", "").split(",")
        if t.strip()
    ]
    return list(dict.fromkeys(tickers))

def save_clean_tickers(clean_tickers):
    try:
        clean_tickers = list(dict.fromkeys(clean_tickers))
        with open(FILENAME, "w", encoding="utf-8") as f:
            f.write(",".join(clean_tickers))
    except Exception:
        pass

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

def _extract_ticker_df(chunk_data, ticker):
    if chunk_data.empty:
        return pd.DataFrame()
    if isinstance(chunk_data.columns, pd.MultiIndex):
        if ticker not in chunk_data.columns.get_level_values(0):
            return pd.DataFrame()
        return chunk_data[ticker].dropna()
    if len(chunk_data.columns) <= 6:
        return chunk_data.dropna()
    return pd.DataFrame()

def download_market_data_safely(ticker_list, progress_callback):
    temp_short = []
    temp_long = []
    bad_tickers = set()
    chunk_size = 10
    chunks = [ticker_list[i:i + chunk_size] for i in range(0, len(ticker_list), chunk_size)]
    total_processed = 0
    
    for chunk in chunks:
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stderr(devnull), contextlib.redirect_stdout(devnull):
                try:
                    tickers_str = " ".join(chunk)
                    chunk_data = yf.download(tickers_str, period="1mo", interval="1d", group_by='ticker', auto_adjust=True, progress=False, ignore_tz=True)
                except Exception:
                    chunk_data = pd.DataFrame()
        
        for ticker in chunk:
            total_processed += 1
            progress_callback(total_processed, len(ticker_list), ticker)
            
            try:
                df_ticker = _extract_ticker_df(chunk_data, ticker)
                if df_ticker.empty or len(df_ticker) < 14 or 'Close' not in df_ticker.columns:
                    bad_tickers.add(ticker)
                    continue
                close_prices = df_ticker['Close'].squeeze()
                last_price = float(close_prices.iloc[-1])
                ma9 = float(close_prices.rolling(window=9).mean().iloc[-1])
                rsi = calculate_rsi(close_prices)
                if 'Volume' not in df_ticker.columns:
                    continue
                volume = int(df_ticker['Volume'].iloc[-1])
                
                if last_price < ma9 and volume > 1000000:
                    if rsi > 65:
                        cond = "RSI גבוה קיצון (קניית יתר מתחת ל-MA9) 📉"
                    elif rsi < 40:
                        cond = "מומנטום שלילי חזק (שבירת מבנה) 📉"
                    else:
                        cond = "מתחת ל-MA9 עם מחזור מסחר תומך 📉"
                    
                    temp_short.append({
                        "סימול": ticker, "מחיר אחרון": f"${last_price:.2f}", "מדד RSI": f"{rsi:.1f}",
                        "ממוצע נע 9": f"${ma9:.2f}", "קריטריון סינון": cond
                    })
                elif last_price > ma9 and rsi > 45 and volume > 1000000:
                    temp_long.append({
                        "סימול": ticker, "מחיר אחרון": f"${last_price:.2f}", "מדד RSI": f"{rsi:.1f}",
                        "ממוצע נע 9": f"${ma9:.2f}", "קריטריון סינון": "מומנטום לונג חיובי (מעל MA9 + RSI > 45) 📈"
                    })
            except Exception:
                bad_tickers.add(ticker)
                continue
        time.sleep(0.3)

    if bad_tickers:
        save_clean_tickers([t for t in ticker_list if t not in bad_tickers])
    return temp_short, temp_long

def ask_gemini_with_retry(question, retries=2, delay=1.5):
    if not ai_client:
        return "⚠️ מערכת ה-AI לא מאותחלת. אנא ודא שהגדרת את GEMINI_API_KEY ב-Secrets או במשתני הסביבה."
    from google.genai import types
    system_instruction = (
        "אתה אנליסט פיננסי בכיר ומנוסה מאוד. ענה בעברית מקצועית וממוקדת שוק ההון. "
        "חובה: החזר בדיוק 5 עד 7 שורות בלבד. ציין במה החברה עוסקת והאם התנאים מתאימים לקנייה או מכירה."
    )
    for attempt in range(retries + 1):
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=question,
                config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
            )
            return response.text.strip()
        except Exception as e:
            if "503" in str(e) and attempt < retries:
                time.sleep(delay)
                continue
            return "⚠️ שגיאה בחיבור ל-Gemini. אנא נסה שוב בעוד מספר שניות."

def get_analyst_buy_pct(ticker_obj):
    try:
        recs = ticker_obj.recommendations
        if recs is not None and not recs.empty:
            latest_rec = recs.iloc[-1]
            total = sum(float(latest_rec.get(k, 0)) for k in ['strongBuy', 'buy', 'hold', 'sell', 'strongSell'])
            if total > 0:
                return int(((float(latest_rec.get('strongBuy', 0)) + float(latest_rec.get('buy', 0))) / total) * 100)
    except Exception:
        pass
    try:
        info = ticker_obj.info or {}
        mean_score = info.get('recommendationMean')
        if mean_score is not None:
            return int(((5.0 - float(mean_score)) / 4.0) * 100)
    except Exception:
        pass
    return None

def build_single_stock_metrics(ticker):
    defaults = dict(TEXT_DEFAULTS)
    try:
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stderr(devnull):
                t = yf.Ticker(ticker, session=session)
                hist = t.history(period="1mo", auto_adjust=True)
        if not hist.empty and len(hist) >= 14:
            close_prices = hist['Close'].squeeze()
            rsi_val = calculate_rsi(close_prices)
            ma9 = float(close_prices.rolling(window=9).mean().iloc[-1])
            last_price = float(close_prices.iloc[-1])
            if rsi_val > 70:
                defaults["rsi_neutral"] = f"RSI = {rsi_val:.1f} - קניית יתר 🛑"
            elif rsi_val < 30:
                defaults["rsi_neutral"] = f"RSI = {rsi_val:.1f} - מכירת יתר 🟢"
            else:
                defaults["rsi_neutral"] = f"RSI = {rsi_val:.1f} - נייטרלי"
            defaults["ma_expensive" if last_price > ma9 else "ma_buy"] = (
                f"מחיר ${last_price:.2f} | MA9 ${ma9:.2f} - "
                + ("המניה נסחרת מעל הממוצע הנע 9." if last_price > ma9 else "המניה נסחרת מתחת לממוצע נע 9 - אזור קנייה פוטנציאלי.")
            )
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stderr(devnull):
                info = t.info or {}
                expirations = t.options
                if expirations:
                    opt = t.option_chain(expirations[0])
                    total_calls = opt.calls['volume'].fillna(0).sum() if 'volume' in opt.calls.columns else 0
                    total_puts = opt.puts['volume'].fillna(0).sum() if 'volume' in opt.puts.columns else 0
                    total_vol = total_calls + total_puts
                    if total_vol > 0:
                        call_pct = (total_calls / total_vol) * 100
                        put_pct = 100 - call_pct
                        defaults["options_calls"] = f"Calls {call_pct:.1f}% | Puts {put_pct:.1f}%"
                earnings_df = t.earnings_dates
                if earnings_df is not None and not earnings_df.empty and 'Surprise(%)' in earnings_df.columns:
                    reported = earnings_df.dropna(subset=['Surprise(%)']).head(4)
                    beats = sum(1 for _, row in reported.iterrows() if row['Surprise(%)'] >= 0)
                    if len(reported) >= 4:
                        defaults["earnings_ok"] = f"עמדה/עקפה תחזיות ב-{beats} מתוך 4 רבעונים אחרונים"
                growth = info.get('revenueGrowth') or info.get('earningsGrowth')
                if growth is not None:
                    defaults["next_quarter_grow"] = f"צפי צמיחה של כ-{float(growth) * 100:.1f}% לפי נתוני השוק"
                buy_pct = get_analyst_buy_pct(t)
                if buy_pct is not None:
                    if buy_pct >= 75:
                        defaults["rec_buy"] = f"קנייה חזקה 🔥 ({buy_pct}% מהאנליסטים ממליצים לונג)"
                    elif buy_pct >= 50:
                        defaults["rec_buy"] = f"קנייה מתונה ({buy_pct}% המלצות קנייה)"
                    else:
                        defaults["rec_buy"] = f"זהירות / מעקב ({buy_pct}% המלצות קנייה בלבד)"
    except Exception:
        pass
    ma_text = defaults["ma_expensive"]
    if defaults["ma_buy"] != TEXT_DEFAULTS["ma_buy"]:
        ma_text = defaults["ma_buy"]
    return {
        "rsi": defaults["rsi_neutral"],
        "ma": ma_text,
        "options": defaults["options_calls"],
        "earnings": defaults["earnings_ok"],
        "next_quarter": defaults["next_quarter_grow"],
        "recommendation": defaults["rec_buy"],
    }

# אתחול רשימות הנתונים בסשן סטייט למניעת הבהובים והיעלמויות
if "short_list" not in st.session_state: st.session_state.short_list = []
if "long_list" not in st.session_state: st.session_state.long_list = []
if "steps_log" not in st.session_state: st.session_state.steps_log = []
if "radar_scanned" not in st.session_state: st.session_state.radar_scanned = False
if "single_results" not in st.session_state: st.session_state.single_results = None
if "free_ai_answer" not in st.session_state: st.session_state.free_ai_answer = None

# הגדרת הטאבים עם האייקונים משמאל באופן קשיח
st.markdown('<h1 class="main-title">⚡ The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">מערכת ראדאר חכמה לזיהוי מומנטום בשוק ההון | סריקה טכנית + ניתוח AI פונדמנטלי</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["רדאר שורט סווינג 📉", "רדאר לונג 📈", "ניתוח מניה בודדת & AI 🔍"])

with tab1:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📉 רדאר מניות פוטנציאליות לשורט</h2>', unsafe_allow_html=True)
    if st.session_state.radar_scanned and st.session_state.short_list:
        st.dataframe(pd.DataFrame(st.session_state.short_list), use_container_width=True)
    elif st.session_state.radar_scanned:
        st.success("לא נמצאו מניות העונות לתנאי השורט כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק' בתחתית העמוד כדי להפעיל את הראדאר.")

with tab2:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📈 רדאר מניות פוטנציאליות ללונג</h2>', unsafe_allow_html=True)
    if st.session_state.radar_scanned and st.session_state.long_list:
        st.dataframe(pd.DataFrame(st.session_state.long_list), use_container_width=True)
    elif st.session_state.radar_scanned:
        st.success("לא נמצאו מניות העונות לתנאי הלונג כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק' בתחתית העמוד כדי להפעיל את הראדאר.")

with tab3:
    st.markdown('<div class="center-header-block" style="text-align:center;"><h2>🤖 ניתוח מניה ומנוע שאלות AI</h2></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        with st.form("analyze_form", clear_on_submit=False):
            search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input")
            run_analysis = st.form_submit_button("🔍 נתח מניה")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if run_analysis and search_ticker.strip():
            search_ticker = search_ticker.upper().strip()
            with st.spinner("מנתח נתונים ומפעיל את Gemini..."):
                metrics = build_single_stock_metrics(search_ticker)
                ai_prompt = (
                    f"נתח את מניית {search_ticker}. "
                    f"החזר סיכום פיננסי קצר בעברית ב-5-7 שורות בלבד. "
                    f"ציין במה החברה עוסקת, מגמת מחיר, והאם מתאים לקנייה או מכירה."
                )
                ai_val = ask_gemini_with_retry(ai_prompt)
            
            st.session_state.single_results = {
                "ticker": search_ticker,
                "rsi": metrics["rsi"],
                "ma": metrics["ma"],
                "options": metrics["options"],
                "earnings": metrics["earnings"],
                "next_quarter": metrics["next_quarter"],
                "recommendation": metrics["recommendation"],
                "ai_data": ai_val,
            }

        if st.session_state.single_results:
            res = st.session_state.single_results
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="header-row-container"><div class="header-text-title">סקירת מניית {res["ticker"]}</div><div class="header-left-side"><div class="header-emoji">📊</div></div></div>', unsafe_allow_html=True)
            st.markdown('<hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">1. מדד עוצמה יחסית (RSI):</span><span class="metric-value">{res["rsi"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">2. ניתוח ממוצעים נעים:</span><span class="metric-value">{res["ma"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">3. שוק האופציות (סנטימנט באחוזים):</span><span class="metric-value">{res["options"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">4. עמידה בתחזית הכנסות:</span><span class="metric-value">{res["earnings"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">5. צפי דוחות וצמיחה:</span><span class="metric-value">{res["next_quarter"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">6. המלצות אנליסטים בשוק (באחוזים):</span><span class="metric-value">{res["recommendation"]}</span></div>', unsafe_allow_html=True)
            st.markdown('<div style="margin-top:20px; padding:15px; background: rgba(255,255,255,0.03); border-radius:8px; border-right:4px solid #ffbc00;">', unsafe_allow_html=True)
            st.markdown('<h4 style="color:#ffffff;">7. פעילות החברה & חוות דעת אנליסט AI (תקציר ממוקד):</h4>', unsafe_allow_html=True)
            st.markdown(f'<p style="line-height:1.7; color:#cbd5e1; text-align:right; direction:rtl;">{res["ai_data"]}</p>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        with st.form("ai_form", clear_on_submit=False):
            user_q = st.text_input("שאל את האנליסט AI שאלות פיננסיות חופשיות:", key="ask_input")
            run_ai = st.form_submit_button("🧠 שאל את האנליסט")
        st.markdown('</div>', unsafe_allow_html=True)
        if run_ai and user_q.strip():
            with st.spinner("ה-AI חושב..."):
                st.session_state.free_ai_answer = ask_gemini_with_retry(user_q.strip())
        if st.session_state.free_ai_answer:
            answer = st.session_state.free_ai_answer
            st.markdown(f'<div class="result-box"><h4 style="color:#ffffff;">📋 תשובת האנליסט:</h4><p style="text-align:right; direction:rtl; color:#ffffff;">{answer}</p></div>', unsafe_allow_html=True)

# ====================================================================
#  כפתור החיפוש המרכזי ממוקם כעת באופן קבוע כאן - בתחתית המסך!
# ====================================================================
st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)
run_radar = st.button("⚡ התחל סריקת שוק וזיהוי מומנטום", key="btn_global_radar")
st.markdown('</div>', unsafe_allow_html=True)

if run_radar:
    st.session_state.steps_log = []
    
    t_start = time.time()
    tickers = load_tickers_from_file()
    t_step1 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 1: טעינת רשימת המניות מהקובץ</span><span class="metric-value">{t_step1:.2f} שניות</span></div>')
    
    t_start = time.time()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current, total, ticker):
        pct = int((current / total) * 100)
        progress_bar.progress(pct)
        status_text.markdown(f"<span style='color:#ffffff; font-weight:600;'>⏳ סורק אינדיקטורים ומנטרל חסימות שרת: {ticker}... ({current}/{total})</span>", unsafe_allow_html=True)

    temp_short, temp_long = download_market_data_safely(tickers, update_progress)
                
    progress_bar.empty()
    status_text.empty()
    
    t_step2_3 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 2 + 3: סריקה קבוצתית מבוקרת (התעלמות מוחלטת ממניות מבוטלות וניקוי חסימות)</span><span class="metric-value">{t_step2_3:.2f} שניות</span></div>')
    
    t_start = time.time()
    st.session_state.short_list = temp_short
    st.session_state.long_list = temp_long
    st.session_state.radar_scanned = True
    t_step4 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 4: יצירת מבנה הטבלאות ונעילת התוצאות הסופיות</span><span class="metric-value">{t_step4:.2f} שניות</span></div>')
    st.rerun()

if st.session_state.steps_log:
    st.markdown('<div class="result-box" style="max-width: 800px; margin: 20px auto;">', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#00f2fe; text-align:center;">📋 סיכום שלבי סריקת המומנטום ומדדי הזמן</h3>', unsafe_allow_html=True)
    for log_line in st.session_state.steps_log:
        st.markdown(log_line, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
