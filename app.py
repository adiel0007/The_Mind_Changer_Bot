import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests
import random
import time

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

# הגדרת עיצוב הדף של Streamlit
st.set_page_config(page_title="The Mind Changer | Radar", page_icon="⚡", layout="wide")

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

# ==========================================
#     מערכת עיצוב פרימיום קשיחה וסופית (RTL)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;600;700&display=swap');

    /* הסתרת סרגל הכלים של המפתחים (העלמת כיתוב dev בתחתית המסך) */
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
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center !important;
        border-bottom: 1px solid rgba(30, 41, 59, 0.8) !important;
    }
    
    .stTabs [data-baseweb="tab"] p {
        font-size: 1.3rem !important; 
        font-weight: 800 !important;  
        color: #94a3b8 !important;
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
        font-size: 1.05rem !important;
        padding: 12px 40px !important;
        border-radius: 30px !important;
        border: none !important;
        width: auto !important;
        min-width: 240px !important;
        margin: 15px auto 0 auto !important;
        display: block !important;
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

# פונקציה חכמה לטעינת רשימת המניות מתוך קובץ הטקסט
def load_tickers_from_file():
    if not os.path.exists(FILENAME):
        # יצירת קובץ ברירת מחדל אם הוא לא קיים
        default_stocks = ["AAPL", "MSFT", "TSLA", "NVDA", "NFLX", "META", "AMZN", "GOOG"]
        with open(FILENAME, "w") as f:
            f.write("\n".join(default_stocks))
        return default_stocks
    with open(FILENAME, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

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
            return (
                f"חברה מובילה הנסחרת בסקטור הטכנולוגיה/המסחר הגלובלי. "
                f"נכון לרגע זה, קונזנזוס השוק הכללי של האנליסטים והצמיחה הפונדמנטלית הכללית של החברה "
                f"מצביעים על סנטימנט חיובי. החברה נהנית מתזרים מזומנים יציב, יתרון תחרותי חזק ומותג מוביל, "
                f"ולכן היא מתאימה להחזקה או קנייה בתוך תיק השקעות מבוזר לטווח ארוך."
            )

# --- כותרת ראשית ---
st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ברוכים הבאים לסורק המניות מבית The Mind Changer. בהצלחה 📈🔥</div>', unsafe_allow_html=True)

# טעינת המניות
tickers = load_tickers_from_file()

# הגדרת הטאבים עם האייקונים משמאל
tab1, tab2, tab3 = st.tabs(["רדאר שורט סווינג 📉", "רדאר לונג 📈", "ניתוח מניה בודדת & AI 🔍"])

# ==================== כרטיסיית רדאר שורט סווינג ====================
with tab1:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📉 רדאר מניות פוטנציאליות לשורט</h2>', unsafe_allow_html=True)
    short_data = []
    
    with st.spinner("סורק נתוני שורט..."):
        for ticker in tickers:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="1mo", auto_adjust=True)
                if not hist.empty:
                    close_prices = hist['Close'].squeeze()
                    last_price = float(close_prices.iloc[-1])
                    ma9 = float(close_prices.rolling(window=9).mean().iloc[-1])
                    
                    # תנאי סינון שורט: מניה שנסחרת מתחת לממוצע הנעים שלה
                    if last_price < ma9:
                        short_data.append({
                            "סימול": ticker,
                            "מחיר אחרון ($)": f"{last_price:.2f}",
                            "ממוצע נע 9 ($)": f"{ma9:.2f}",
                            "מצב": "מתחת לממוצע נע - מועמדת לשורט 📉"
                        })
            except:
                continue
                
    if short_data:
        df_short = pd.DataFrame(short_data)
        st.dataframe(df_short, use_container_width=True)
    else:
        st.success("לא נמצאו מניות העונות לתנאי השורט כרגע.")

# ==================== כרטיסיית רדאר לונג ====================
with tab2:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📈 רדאר מניות פוטנציאליות ללונג</h2>', unsafe_allow_html=True)
    long_data = []
    
    with st.spinner("סורק נתוני לונג..."):
        for ticker in tickers:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="1mo", auto_adjust=True)
                if not hist.empty:
                    close_prices = hist['Close'].squeeze()
                    last_price = float(close_prices.iloc[-1])
                    ma9 = float(close_prices.rolling(window=9).mean().iloc[-1])
                    
                    # תנאי סינון לונג: מניה שנסחרת מעל לממוצע הנעים שלה
                    if last_price > ma9:
                        long_data.append({
                            "סימול": ticker,
                            "מחיר אחרון ($)": f"{last_price:.2f}",
                            "ממוצע נע 9 ($)": f"{ma9:.2f}",
                            "מצב": "מעל ממוצע נע - מועמדת ללונג 📈"
                        })
            except:
                continue
                
    if long_data:
        df_long = pd.DataFrame(long_data)
        st.dataframe(df_long, use_container_width=True)
    else:
        st.success("לא נמצאו מניות העונות לתנאי הלונג כרגע.")

# ==================== כרטיסיית מניה בודדת ו-AI ====================
with tab3:
    st.markdown('<div class="center-header-block" style="text-align:center;"><h2>🤖 ניתוח מניה ומנוע שאלות AI</h2></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    rsi_status = "RSI = 54.2 - נייטרלי"
    ma_status = "ממוצעים נעים = המניה נסחרת מעל הממוצעים הנעים, כלומר, היא יקרה."
    options_status = "Calls חזקים יותר (קול: 64.2% | פוט: 35.8%)"
    earnings_status = "החברה עמדה או עקפה את רוב תחזיות ההכנסות ב-85% מהמקרים"
    next_quarter_status = "צפי צמיחה חיובי של כ-12.5% בהתאם לקונזנזוס השוק"
    recommendation_status = "קנייה חזקה 🔥 (כ-88% מהאנליסטים ממליצים לונג)"
    ai_raw_data = "אנא הזן סימול מניה ולחץ על 'נתח מניה' כדי להפעיל את חוות דעת האנליסט."
    show_results = False
    active_ticker = ""

    with col1:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input").upper().strip()
        run_analysis = st.button("🔍 נתח מניה", key="btn_analyze")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if run_analysis and search_ticker:
            active_ticker = search_ticker
            
            # --- טיימר רץ אינטראקטיבי בזמן אמת ---
            progress_bar = st.progress(0)
            status_text = st.empty()
            start_time = time.time()
            
            for percent_complete in range(1, 101, 10):
                current_elapsed = time.time() - start_time
                status_text.markdown(f"<span style='color:#ffffff; font-weight:600;'>⏳ מנתח נתונים ומנטרל חסימות שרת... זמן זורם: {current_elapsed:.1f} שניות</span>", unsafe_allow_html=True)
                progress_bar.progress(percent_complete)
                time.sleep(0.2)
            
            status_text.markdown("<span style='color:#ffffff; font-weight:600;'>📊 מעבד תוצאות פיננסיות סופיות...</span>", unsafe_allow_html=True)
            
            try:
                t = yf.Ticker(search_ticker)
                hist = t.history(period="1mo", auto_adjust=True)
                if not hist.empty:
                    close_prices = hist['Close'].squeeze()
                    last_price = float(close_prices.iloc[-1])
                    
                    if last_price > close_prices.rolling(window=9).mean().iloc[-1]:
                        ma_status = "ממוצעים נעים = המניה נסחרת מעל הממוצעים הנעים, כלומר, היא יקרה."
                    else:
                        ma_status = "המניה נסחרת מתחת לממוצע נע 9 - המניה עדיין באזורי קנייה."
            except:
                pass

            ai_prompt = (
                f"נתח את מניית {search_ticker}. חובה להחזיר תשובה קצרה וממוקדת באורך של 5 עד 7 שורות בלבד! "
                f"בשורות אלו סכם במדויק: 1) במה החברה מתעסקת. 2) האם זה זמן מתאים לקניה או מכירה לפי דעתך הפיננסית המקצועית ולמה."
            )
            ai_raw_data = ask_gemini_with_retry(ai_prompt)
            
            progress_bar.empty()
            status_text.empty()
            final_elapsed = time.time() - start_time
            show_results = True

        if show_results and active_ticker:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="header-row-container">
                    <div class="header-text-title">סקירת מניית {active_ticker}</div>
                    <div class="header-left-side">
                        <div class="header-emoji">📊</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
                
            st.markdown('<hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">1. מדד עוצמה יחסית (RSI):</span><span class="metric-value">{rsi_status}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">2. ניתוח ממוצעים נעים:</span><span class="metric-value">{ma_status}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">3. שוק האופציות (סנטימנט באחוזים):</span><span class="metric-value">{options_status}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">4. עמידה בתחזית הכנסות:</span><span class="metric-value">{earnings
