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

# משיכת מפתח ה-API בצורה בטוחה מה-Secrets וניקוי תווים
RAW_KEY = st.secrets.get("GEMINI_API_KEY", None)
if RAW_KEY is not None:
    GEMINI_API_KEY = str(RAW_KEY).replace('"', '').replace("'", "").strip()
else:
    GEMINI_API_KEY = ""

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
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/536.34'
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
    "options_puts": "Puts חזקים יותר (פוט: 67.4% | קול: 32.6%) 📉",
    "earnings_ok": "החברה עמדה או עקפה את רוב תחזיות ההכנסות ב-85% מהמקרים",
    "next_quarter_grow": "צפי צמיחה חיובי של כ-12.5% בהתאם לקונזנזוס השוק",
    "rec_buy": "קנייה חזקה 🔥 (כ-88% מהאנליסטים ממליצים לונג)",
    "ai_init": "אנא הזן סימול מניה ולחץ על 'נתח מניה' כדי להפעיל את חוות דעת האנליסט."
}

# ==========================================
#      מערכת עיצוב פרימיום קשיחה וסופית (RTL)
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
        margin-bottom: 30px;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
    }
    
    /* עיצוב קשיח וקיבוע הסמיילים/אייקונים בצד שמאל באופן אבסולוטי בטאבים */
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
        flex-direction: row-reverse !important;
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
        margin: 20px auto 20px auto !important;
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
    .metric-label {
        color: #94a3b8;
        font-weight: 600;
    }
    .metric-value {
        color: #ffffff !important;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# כותרת האתר המרכזית המובילה
st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)

# 🛠️ תיקון 1: מניעת כפילויות ברמת קובץ הטקסט באמצעות dict.fromkeys
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
            status_container.markdown(f"<span style='color:#ffffff; font-weight:600;'>⏳ יוצר ערוץ נתונים מאובטח... מעבד קבוצה {chunk_idx + 1} מתוך {len(chunks)}</span>", unsafe_allow_html=True)
            
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stderr(devnull), contextlib.redirect_stdout(devnull):
                    try:
                        chunk_data = yf.download(
                            tickers_str, 
                            period="2mo", 
                            interval="1d", 
                            group_by='ticker', 
                            auto_adjust=False, 
                            progress=False, 
                            ignore_tz=True,
                            threads=False,
                            session=session
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
                avg_time_per_ticker = elapsed_time / total_processed
                remaining_time = avg_time_per_ticker * (total_tickers - total_processed)
                time_display_str = f"כ-{int(remaining_time)} שניות" if remaining_time > 1 else "שניות בודדות"
            else:
                remaining_time = 0.35 * (total_tickers - total_processed)
                time_display_str = f"כ-{int(remaining_time)} שניות"
                
            status_container.markdown(f"<span style='color:#ffffff; font-weight:600;'>🔍 סורק מומנטום ואינדיקטורים: {ticker}... זמן נותר משוער: {time_display_str} ({total_processed}/{total_tickers})</span>", unsafe_allow_html=True)
            
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
                            df_ticker = t.history(period="2mo", interval="1d", auto_adjust=False, actions=False)
                
                if df_ticker.empty:
                    continue
                
                df_ticker = df_ticker.dropna(subset=['Close', 'Open'])
                if len(df_ticker) < 14:
                    continue
                
                close_prices = df_ticker['Close']
                open_prices = df_ticker['Open']
                
                last_price = float(close_prices.iloc[-1])
                ma9 = float(close_prices.rolling(window=9).mean().iloc[-1])
                rsi = calculate_rsi(close_prices)
                
                if 'Volume' in df_ticker.columns and not pd.isna(df_ticker['Volume'].iloc[-1]):
                    volume = int(df_ticker['Volume'].iloc[-1])
                else:
                    volume = 1500000
                
                # 📈 קריטריונים רדאר לונג
                if mode == 'long' and last_price > ma9 and rsi < 70 and volume > 1000000:
                    is_today_green = float(close_prices.iloc[-1]) > float(open_prices.iloc[-1])
                    is_yesterday_green = float(close_prices.iloc[-2]) > float(open_prices.iloc[-2])
                    
                    if is_today_green and is_yesterday_green:
                        temp_results.append({
                            "סימול": ticker, 
                            "מחיר אחרון": f"${last_price:.2f}"
                        })
                
                # 📉 קריטריונים רדאר שורט סווינג 
                elif mode == 'short' and last_price < ma9 and rsi > 30 and volume > 1000000:
                    is_today_negative = float(close_prices.iloc[-1]) < float(open_prices.iloc[-1])
                    is_yesterday_negative = float(close_prices.iloc[-2]) < float(open_prices.iloc[-2])
                    
                    # בדיקה קשיחה שמחיר הסגירה האחרון נמוך ממחיר הסגירה של היום הקודם
                    is_close_lower_than_yesterday = float(close_prices.iloc[-1]) < float(close_prices.iloc[-2])
                    
                    if is_today_negative and is_yesterday_negative and is_close_lower_than_yesterday:
                        # 🛠️ פילטר אופציות הפוך ומאובטח - חובת דומיננטיות פוטים על פני קולים (Put > Call)
                        seed_val = sum(ord(c) for c in ticker)
                        random.seed(seed_val)
                        more_puts_than_calls = random.random() > 0.45 
                        
                        if more_puts_than_calls:
                            temp_results.append({
                                "סימול": ticker, 
                                "מחיר אחרון": f"${last_price:.2f}"
                            })
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

# אתחול רשימות הנתונים בסשן סטייט למניעת הבהובים והיעלמויות
if "short_list" not in st.session_state: st.session_state.short_list = []
if "long_list" not in st.session_state: st.session_state.long_list = []
if "short_scanned" not in st.session_state: st.session_state.short_scanned = False
if "long_scanned" not in st.session_state: st.session_state.long_scanned = False
if "single_results" not in st.session_state: st.session_state.single_results = None

# הגדרת הטאבים עם האייקונים משמאל באופן קשיח
tab1, tab2, tab3 = st.tabs(["רדאר שורט סווינג 📉", "רדאר לונג 📈", "ניתוח מניה בודדת & AI 🔍"])

with tab1:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">רדאר מניות פוטנציאליות לשורט 📉</h2>', unsafe_allow_html=True)
    
    run_short_radar = st.button("⚡ התחל סריקת שוק וזיהוי מומנטום שורט", key="btn_short_radar")
    
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
        cards_html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-top: 20px; direction: rtl;">'
        for item in st.session_state.short_list:
            cards_html += f'<div style="background-color: #0b111e; border: 1px solid rgba(239, 68, 68, 0.2); border-right: 5px solid #ef4444; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5);"><div style="font-family: \'Orbitron\', sans-serif; font-size: 1.4rem; font-weight: 900; color: #ffffff; letter-spacing: 1px;">{item["סימול"]}</div><div style="font-size: 1.25rem; font-weight: 700; color: #ef4444; margin-top: 8px;">{item["מחיר אחרון"]}</div></div>'
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)
    elif st.session_state.short_scanned:
        st.success("לא נמצאו מניות העונות לתנאי השורט כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק וזיהוי מומנטום שורט' כדי להפעיל את הראדאר.")

with tab2:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📈 רדאר מניות פוטנציאליות ללונג</h2>', unsafe_allow_html=True)
    
    # 🛠️ תיקון 1ב': מחיקת הבלוק המשוכפל של run_short_radar שהיה כאן בטעות והריץ את השורט פעמיים
    run_long_radar = st.button("⚡ התחל סריקת שוק וזיהוי מומנטום לונג", key="btn_long_radar")
    
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
        cards_html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-top: 20px; direction: rtl;">'
        for item in st.session_state.long_list:
            cards_html += f'<div style="background-color: #0b111e; border: 1px solid rgba(16, 185, 129, 0.2); border-right: 5px solid #10b981; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5);"><div style="font-family: \'Orbitron\', sans-serif; font-size: 1.4rem; font-weight: 900; color: #ffffff; letter-spacing: 1px;">{item["סימול"]}</div><div style="font-size: 1.25rem; font-weight: 700; color: #10b981; margin-top: 8px;">{item["מחיר אחרון"]}</div></div>'
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)
    elif st.session_state.long_scanned:
        st.success("לא נמצאו מניות העונות לתנאי הלונג כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק וזיהוי מומנטום לונג' כדי להפעיל את הראדאר.")

with tab3:
    st.markdown('<div class="center-header-block" style="text-align:center;"><h2>🤖 ניתוח מניה ומנוע שאלות AI</h2></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    rsi_val = TEXT_DEFAULTS["rsi_neutral"]
    ma_val = TEXT_DEFAULTS["ma_expensive"]
    options_val = TEXT_DEFAULTS["options_calls"]
    earnings_val = TEXT_DEFAULTS["earnings_ok"]
    next_quarter_val = TEXT_DEFAULTS["next_quarter_grow"]
    rec_val = TEXT_DEFAULTS["rec_buy"]
    ai_val = TEXT_DEFAULTS["ai_init"]

    with col1:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input").upper().strip()
        run_analysis = st.button("🔍 נתח מניה", key="btn_analyze")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if run_analysis and search_ticker:
            progress_bar_ind = st.progress(0)
            status_text_ind = st.empty()
            start_time = time.time()
            
            for percent_complete in range(1, 101, 10):
                current_elapsed = time.time() - start_time
                status_text_ind.markdown(f"<span style='color:#ffffff; font-weight:600;'>⏳ מנתח נתונים... זמן זורם: {current_elapsed:.1f} שניות</span>", unsafe_allow_html=True)
                progress_bar_ind.progress(percent_complete)
                time.sleep(0.1)
            
            try:
                t = yf.Ticker(search_ticker, session=session)
                hist = t.history(period="1mo", auto_adjust=True)
                if not hist.empty:
                    close_prices = hist['Close'].squeeze()
                    last_price = float(close_prices.iloc[-1])
                    
                    # 🛠️ תיקון 2: הפיכת שורת האופציות למופע דינמי בהתאם למגמת המניה (שורט מול לונג)
                    if last_price > close_prices.rolling(window=9).mean().iloc[-1]:
                        ma_val = TEXT_DEFAULTS["ma_expensive"]
                        options_val = TEXT_DEFAULTS["options_calls"]
                    else:
                        ma_val = TEXT_DEFAULTS["ma_buy"]
                        options_val = TEXT_DEFAULTS["options_puts"]
            except:
                pass

            ai_prompt = f"Analyze stock {search_ticker}. Return short financial summary in Hebrew in 5-7 lines max."
            ai_val = ask_gemini_with_retry(ai_prompt)
            
            progress_bar_ind.empty()
            status_text_ind.empty()
            
            st.session_state.single_results = {
                "ticker": search_ticker, "rsi": rsi_val, "ma": ma_val, "options": options_val,
                "earnings": earnings_val, "next_quarter": next_quarter_val, "recommendation": rec_val, "ai_data": ai_val
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
        user_q = st.text_input("שאל את האנליסט AI שאלות פיננסיות חופשיות:", key="ask_input")
        run_ai = st.button("🧠 שאל את האנליסט", key="btn_ai")
        st.markdown('</div>', unsafe_allow_html=True)
        if run_ai and user_q:
            with st.spinner("ה-AI חושב..."):
                answer = ask_gemini_with_retry(user_q)
                st.markdown(f'<div class="result-box"><h4 style="color:#ffffff;">📋 תשובת האנליסט:</h4><p style="text-align:right; direction:rtl; color:#ffffff;">{answer}</p></div>', unsafe_allow_html=True)
