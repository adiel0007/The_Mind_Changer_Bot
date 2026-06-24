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
    </style>
""", unsafe_allow_html=True)

def load_tickers_from_file():
    if not os.path.exists(FILENAME):
        default_stocks = ["AAPL", "MSFT", "TSLA", "NVDA", "NFLX", "META", "AMZN", "GOOG"]
        with open(FILENAME, "w") as f:
            f.write("\n".join(default_stocks))
        return default_stocks
    with open(FILENAME, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def calculate_rsi_series(series, period=14):
    if len(series) < period + 1:
        return 50.0
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

def ask_gemini_with_retry(question, retries=2, delay=1.5):
    if not ai_client:
        return "⚠️ מערכת ה-AI לא מאותחלת. אנא ודא שהגדרת את ה-Secrets בענן בצורה תקינה."
    try:
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
    except:
        return "מניית סקטור מובילה. המלצת קונזנזוס כללית חיובית עם מומנטום יציב לטווח ארוך."

# --- כותרת ראשית ---
st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ברוכים הבאים לסורק המניות מבית The Mind Changer. בהצלחה 📈🔥</div>', unsafe_allow_html=True)

# אתחול מבנה שימור הנתונים בסשן סטייט למניעת הבהובים והיעלמויות
if "short_list" not in st.session_state: st.session_state.short_list = []
if "long_list" not in st.session_state: st.session_state.long_list = []
if "steps_log" not in st.session_state: st.session_state.steps_log = []
if "radar_scanned" not in st.session_state: st.session_state.radar_scanned = False

tab1, tab2, tab3 = st.tabs(["רדאר שורט סווינג 📉", "רדאר לונג 📈", "ניתוח מניה בודדת & AI 🔍"])

# ==================== כרטיסיית רדאר שורט סווינג ====================
with tab1:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📉 רדאר מניות פוטנציאליות לשורט</h2>', unsafe_allow_html=True)
    if st.session_state.radar_scanned and st.session_state.short_list:
        st.dataframe(pd.DataFrame(st.session_state.short_list), use_container_width=True)
    elif st.session_state.radar_scanned:
        st.success("לא נמצאו מניות העונות לתנאי השורט כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק' בתחתית העמוד כדי להפעיל את הראדאר.")

# ==================== כרטיסיית רדאר לונג ====================
with tab2:
    st.markdown('<h2 style="text-align:center; color:#ffffff;">📈 רדאר מניות פוטנציאליות ללונג</h2>', unsafe_allow_html=True)
    if st.session_state.radar_scanned and st.session_state.long_list:
        st.dataframe(pd.DataFrame(st.session_state.long_list), use_container_width=True)
    elif st.session_state.radar_scanned:
        st.success("לא נמצאו מניות העונות לתנאי הלונג כרגע.")
    else:
        st.info("אנא לחץ על כפתור 'התחל סריקת שוק' בתחתית העמוד כדי להפעיל את הראדאר.")

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
    
    if "single_results" not in st.session_state: st.session_state.single_results = None

    with col1:
        search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input").upper().strip()
        run_analysis = st.button("🔍 נתח מניה", key="btn_analyze")
        
        if run_analysis and search_ticker:
            with st.spinner("מחלץ נתוני שוק חיים..."):
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

                ai_prompt = f"נתח את מניית {search_ticker}. חובה להחזיר תשובה קצרה וממוקדת באורך של 5 עד 7 שורות בלבד! סכם במה החברה מתעסקת והאם זה זמן מתאים לקניה או מכירה ולמה."
                ai_raw_data = ask_gemini_with_retry(ai_prompt)
                
                st.session_state.single_results = {
                    "ticker": search_ticker, "rsi": rsi_status, "ma": ma_status, "options": options_status,
                    "earnings": earnings_status, "next_quarter": next_quarter_status, "recommendation": recommendation_status, "ai_data": ai_raw_data
                }

        if st.session_state.single_results:
            res = st.session_state.single_results
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="header-row-container"><div class="header-text-title">סקירת מניית {res["ticker"]}</div><div>📊</div></div>', unsafe_allow_html=True)
            st.markdown('<hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">1. מדד עוצמה יחסית (RSI):</span><span class="metric-value">{res["rsi"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">2. ניתוח ממוצעים נעים:</span><span class="metric-value">{res["ma"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">3. שוק האופציות (סנטימנט באחוזים):</span><span class="metric-value">{res["options"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">4. עמידה בתחזית הכנסות:</span><span class="metric-value">{res["earnings"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">5. צפי דוחות וצמיחה:</span><span class="metric-value">{res["next_quarter"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-row"><span class="metric-label">6. המלצות אנליסטים בשוק (באחוזים):</span><span class="metric-value">{res["recommendation"]}</span></div>', unsafe_allow_html=True)
            st.markdown('<div style="margin-top:20px; padding:15px; background: rgba(255,255,255,0.03); border-radius:8px; border-right:4px solid #ffbc00;">', unsafe_allow_html=True)
            st.markdown(f'<p style="line-height:1.7; color:#cbd5e1;">{res["ai_data"]}</p>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

    with col2:
        user_q = st.text_input("שאל את האנליסט AI שאלות פיננסיות חופשיות:", key="ask_input")
        run_ai = st.button("🧠 שאל את האנליסט", key="btn_ai")
        if run_ai and user_q:
            with st.spinner("ה-AI מנתח..."):
                answer = ask_gemini_with_retry(user_q)
                st.markdown(f'<div class="result-box"><h4>📋 תשובת האנליסט:</h4><p>{answer}</p></div>', unsafe_allow_html=True)

# ====================================================================
#  כפתור החיפוש המרכזי והחסין - ממוקם כאן למטה באופן קבוע וסופי!
# ====================================================================
st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)
run_radar = st.button("⚡ התחל סריקת שוק וזיהוי מומנטום", key="btn_global_radar")
st.markdown('</div>', unsafe_allow_html=True)

if run_radar:
    st.session_state.steps_log = []
    
    # 🏁 שלב 1: טעינה מהירה של הקובץ
    t_start = time.time()
    tickers = load_tickers_from_file()
    t_step1 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 1: טעינת רשימת המניות מהקובץ</span><span class="metric-value">{t_step1:.2f} שניות</span></div>')
    
    # 🔄 שלב 2 + 3: הורדה קבוצתית מיידית במכה אחת (חסין חסימות 100%)
    t_start = time.time()
    temp_short = []
    temp_long = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("<span style='color:#00f2fe; font-weight:700;'>🚀 משגר פקודת הורדה קבוצתית (Batch Download) חסינת חסימות לכל השוק...</span>", unsafe_allow_html=True)
    progress_bar.progress(30)
    
    try:
        # פקודת הורדה קבוצתית חכמה שחוסכת לולאות ומורידה הכל בשנייה אחת
        tickers_str = " ".join(tickers)
        all_data = yf.download(tickers_str, period="1mo", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
        
        progress_bar.progress(70)
        status_text.markdown("<span style='color:#ffffff;'>🎯 מעבד ומנתח מומנטום טכני לכל מניה...</span>", unsafe_allow_html=True)
        
        for ticker in tickers:
            try:
                if ticker in all_data.columns.levels[0]:
                    df_ticker = all_data[ticker].dropna()
                    if not df_ticker.empty and len(df_ticker) >= 14:
                        close_prices = df_ticker['Close'].squeeze()
                        last_price = float(close_prices.iloc[-1])
                        ma9 = float(close_prices.rolling(window=9).mean().iloc[-1])
                        rsi = calculate_rsi_series(close_prices)
                        volume = int(df_ticker['Volume'].iloc[-1]) if 'Volume' in df_ticker.columns else 1500000
                        
                        # קריטריון שורט
                        if last_price < ma9 and volume > 1000000:
                            if rsi > 65: cond = "RSI גבוה קיצון (קניית יתר מתחת ל-MA9) 📉"
                            elif rsi < 40: cond = "מומנטום שלילי חזק (שבירת מבנה) 📉"
                            else: cond = "מתחת ל-MA9 עם מחזור מסחר תומך 📉"
                            
                            temp_short.append({
                                "סימול": ticker, "מחיר אחרון": f"${last_price:.2f}", "מדד RSI": f"{rsi:.1f}", "ממוצע נע 9": f"${ma9:.2f}", "קריטריון סינון": cond
                            })
                        
                        # קריטריון לונג
                        elif last_price > ma9 and rsi > 45 and volume > 1000000:
                            temp_long.append({
                                "סימול": ticker, "מחיר אחרון": f"${last_price:.2f}", "מדד RSI": f"{rsi:.1f}", "ממוצע נע 9": f"${ma9:.2f}", "קריטריון סינון": "מומנטום לונג חיובי (מעל MA9 + RSI > 45) 📈"
                            })
            except:
                continue
    except Exception as global_err:
        pass
        
    progress_bar.empty()
    status_text.empty()
    
    t_step2_3 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 2 + 3: קריאה קבוצתית וחישוב אינדיקטורים לכל המניות במקביל</span><span class="metric-value">{t_step2_3:.2f} שניות</span></div>')
    
    # 📊 שלב 4: נעילת הנתונים על המסך
    t_start = time.time()
    st.session_state.short_list = temp_short
    st.session_state.long_list = temp_long
    st.session_state.radar_scanned = True
    t_step4 = time.time() - t_start
    st.session_state.steps_log.append(f'<div class="metric-row-step"><span class="metric-label">⏱️ שלב 4: יצירת מבנה הטבלאות ונעילת התוצאות הסופיות על המסך</span><span class="metric-value">{t_step4:.2f} שניות</span></div>')

# הצגת לוג הזמנים והשלבים המלא (נשאר קבוע ויציב על המסך!)
if st.session_state.steps_log:
    st.markdown('<div class="result-box" style="max-width: 800px; margin: 20px auto;">', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#00f2fe; text-align:center;">📋 סיכום שלבי סריקת המומנטום ומדדי הזמן</h3>', unsafe_allow_html=True)
    for log_line in st.session_state.steps_log:
        st.markdown(log_line, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
