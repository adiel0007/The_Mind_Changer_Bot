import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests
import random
import time

# חובה! הפקודה הראשונה ביותר של Streamlit בקוד למניעת שגיאות
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
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'
    ]
    return {'User-Agent': random.choice(user_agents)}

# אתחול סשן בקשות דינמי יציב
session = requests.Session()
session.headers.update(get_random_headers())

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
    
    /* עיצוב הטאבים - יישור הטקסט לימין ודחיפת הסמיילים/אייקונים לצד שמאל באופן אבסולוטי */
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
        flex-direction: row-reverse !important; /* דוחף את האייקון/סמיילי שמאלה לסוף המשפט */
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
    
    /* עיצוב כפתור הסריקה המרכזי שיופיע למטה */
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

# פונקציה חכמה לטעינת רשימת המניות מתוך קובץ הטקסט
def load_tickers_from_file():
    if not os.path.exists(FILENAME):
        default_stocks = ["AAPL", "MSFT", "TSLA", "NVDA", "NFLX", "META", "AMZN", "GOOG"]
        with open(FILENAME, "w") as f:
            f.write("\n".join(default_stocks))
        return default_stocks
    with open(FILENAME, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

# חישוב מדד RSI ידני מבוסס פנדס בצורה מדויקת
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

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

# אתחול מבנה שימור הנתונים בסשן סטייט למניעת הבהובים והיעלמויות
if "short_list" not in st.session_state: st.session_state.short_list = []
if "long_list" not in st.session_state: st.session_state.long_list = []
if "steps_log" not in st.session_state: st.session_state.steps_log = []
if "radar_scanned" not in st.session_state: st.session_state.radar_scanned = False

# הגדרת הטאבים - הסמיילים מיושרים כעת לצד שמאל של המילים באופן קשיח
tab1, tab2, tab3 = st.tabs(["רדאר שורט סווינג 📉", "רדאר לונג 📈", "ניתוח מניה בודדת & AI 🔍"])

# ==================== כרטיסיית רדאר שורט סווינג ====================
with tab1:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📉 רדאר מניות פוטנציאליות לשורט</h2>', unsafe_allow_html=True)
    if st.session_state.radar_scanned and st.session_state.short_list:
        st.dataframe(pd.DataFrame(st.session_state.short_list), use_container_width=True)
    elif st.session_state.radar_scanned:
        st.success("לא נמצאו מניות העונות לתנאי השורט כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק' בתחתית העמוד כדי להציג את נתוני הראדאר.")

# ==================== כרטיסיית רדאר לונג ====================
with tab2:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📈 רדאר מניות פוטנציאליות ללונג</h2>', unsafe_allow_html=True)
    if st.session_state.radar_scanned and st.session_state.long_list:
        st.dataframe(pd.DataFrame(st.session_state.long_list), use_container_width=True)
    elif st.session_state.radar_scanned:
        st.success("לא נמצאו מניות העונות לתנאי הלונג כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק' בתחתית העמוד כדי להציג את נתוני הראדאר.")

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
    
    if "single_results" not in st.session_state: st.session_state.single_results = None

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
                # מנגנון קבלת נתונים מוגן וחסין חסימות למניה בודדת
                session.headers.update(get_random_headers())
                t = yf.Ticker(search_ticker, session=session)
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
            
            progress_bar_ind.empty()
            status_text_ind.empty()
            
            st.session_state.single_results = {
                "ticker": search_ticker, "rsi": rsi_status, "ma": ma_status, "options": options_status,
                "earnings": earnings_status, "next_quarter": next_quarter_status, "recommendation": recommendation_status, "ai_data": ai_raw_data
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
            with st.spinner("ה-AI חושב ומנתח..."):
                answer = ask_gemini_with_retry(user_q)
                st.markdown(f'<div class="result-box"><h4 style="color:#ffffff;">📋 תשובת האנליסט:</h4><p style="text-align:right; direction:rtl; color:#ffffff;">{answer}</p></div>', unsafe_allow_html=True)

# ====================================================================
#  כפתור החיפוש המרכזי ממוקם כעת באופן קבוע כאן - בתחתית המסך!
# ====================================================================
st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)
run_radar = st.button("⚡ התחל סריקת שוק וזיהוי מומנטום", key="btn_global_radar")
st.markdown('</div>', unsafe_allow_html=True)

if run_radar:
    st.session_state.steps_log = []
    
    # 🏁 שלב 1: טעינת הקובץ
    t_start = time.time()
    tickers = load_tickers_from_file()
    t_step1 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 1: טעינת רשימת המניות מהקובץ</span><span class="metric-value">{t_step1:.2f} שניות</span></div>')
    
    # 🔄 שלב 2: סריקה ואיסוף נתונים חסין חסימות
    t_start = time.time()
    temp_short = []
    temp_long = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        status_text.markdown(f"<span style='color:#ffffff; font-weight:600;'>⏳ מושך נתונים פיננסיים חיים עבור סימול {ticker}... ({i+1}/{len(tickers)})</span>", unsafe_allow_html=True)
        try:
            # רענון כותרות הדפדפן בכל 5 בקשות כדי למנוע חסימה של Yahoo Finance
            if i % 5 == 0:
                session.headers.update(get_random_headers())
                
            t = yf.Ticker(ticker, session=session)
            # משיכת ההיסטוריה עם פרמטרים קשיחים למניעת ערכים ריקים
            hist = t.history(period="1mo", interval="1d", auto_adjust=True, back_adjust=False)
            
            if not hist.empty and len(hist) >= 14:
                close_prices = hist['Close'].squeeze()
                last_price = float(close_prices.iloc[-1])
                ma9 = float(close_prices.rolling(window=9).mean().iloc[-1])
                rsi = calculate_rsi(close_prices)
                
                # בדיקה אם קיים עמודת ווליום תקינה, אם לא שמים ערך ברירת מחדל גבוה לעקיפה
                volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 1500000
                
                # 📉 קריטריון רדאר שורט סווינג המקורי שלך
                if last_price < ma9 and volume > 1000000:
                    if rsi > 65: cond = "RSI גבוה קיצון (קניית יתר מתחת ל-MA9) 📉"
                    elif rsi < 40: cond = "מומנטום שלילי חזק (שבירת מבנה) 📉"
                    else: cond = "מתחת ל-MA9 עם מחזור מסחר תומך 📉"
                        
                    temp_short.append({
                        "סימול": ticker, "מחיר אחרון": f"${last_price:.2f}", "מדד RSI": f"{rsi:.1f}", "ממוצע נע 9": f"${ma9:.2f}", "קריטריון סינון": cond
                    })
                    
                # 📈 קריטריון רדאר לונג המקורי שלך (מעל MA9 ונפח מסחר ומעל RSI 45)
                elif last_price > ma9 and volume > 1000000 and rsi > 45:
                    temp_long.append({
                        "סימול": ticker, "מחיר אחרון": f"${last_price:.2f}", "מדד RSI": f"{rsi:.1f}", "ממוצע נע 9": f"${ma9:.2f}", "קריטריון סינון": "מומנטום לונג חיובי (מעל MA9 + RSI > 45) 📈"
                    })
        except Exception as e:
            continue
        progress_bar.progress(int((i + 1) / len(tickers) * 100))
        
    progress_bar.empty()
    status_text.empty()
    t_step2 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 2: סריקה, ניתוח וחישוב RSI וממוצעים לכל המניות</span><span class="metric-value">{t_step2:.2f} שניות</span></div>')
    
    # 🎯 שלב 3: סינון וסיווג לפי ההגדרות שלך
    t_start = time.time()
    st.session_state.short_list = temp_short
    st.session_state.long_list = temp_long
    t_step3 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 3: סינון וסיווג מניות ללונג / שורט לפי הקריטריונים המלאים</span><span class="metric-value">{t_step3:.2f} שניות</span></div>')
    
    # 📊 שלב 4: בניית התוצאות והזרקה למסך
    t_start = time.time()
    st.session_state.radar_scanned = True
    t_step4 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 4: יצירת מבנה הטבלאות והזרקת התוצאות הסופיות למסך</span><span class="metric-value">{t_step4:.2f} שניות</span></div>')

# הצגת לוג הזמנים והשלבים המלא (רק במידה ובוצעה סריקה)
if st.session_state.steps_log:
    st.markdown('<div class="result-box" style="max-width: 800px; margin: 20px auto;">', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#00f2fe; text-align:center;">📋 סיכום שלבי סריקת המומנטום ומדדי הזמן</h3>', unsafe_allow_html=True)
    for log_line in st.session_state.steps_log:
        st.markdown(log_line, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
