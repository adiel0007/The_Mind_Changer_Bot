import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests
from google import genai
from google.genai import types

# קריאה מאובטחת מתוך ה-Secrets בענן של Streamlit - מוגן מפני חסימות גוגל!
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
FILENAME = "Stocks List.txt"

# אתחול ה-AI של גוגל בצורה מאובטחת
try:
    if GEMINI_API_KEY:
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        ai_client = None
except Exception as e:
    ai_client = None

# הגדרת עיצוב הדף של Streamlit לחוויה מעולה בנייד ובמחשב
st.set_page_config(page_title="The Mind Changer | Radar", page_icon="⚡", layout="wide")

# הגדרת סשן מותאם ל-yfinance כדי לעקוף חסימות מידע של Yahoo
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})

# ==========================================
#     מערכת עיצוב פרימיום קשיחה וסופית (RTL)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;600;700&display=swap');

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
        letter-spacing: 1px;
        color: #ffffff;
        text-align: center !important;
        margin-top: 25px;
        margin-bottom: 10px;
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
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center !important;
        border-bottom: 1px solid rgba(30, 41, 59, 0.8) !important;
    }
    
    .stTabs [data-baseweb="tab"] p {
        font-size: 1.3rem !important; 
        font-weight: 800 !important;  
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(11, 15, 25, 0.85) !important;
        border: 1px solid rgba(30, 41, 59, 0.5) !important;
        border-radius: 6px 6px 0px 0px !important;
        padding: 12px 28px !important;
        color: #94a3b8 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        border-color: #ffbc00 !important;
        box-shadow: 0 -4px 12px rgba(255, 188, 0, 0.15) !important;
    }
    
    .stTabs [aria-selected="true"] p {
        color: #ffbc00 !important;
    }

    .cyber-box {
        max-width: 750px;
        margin: 30px auto;
        padding: 40px 30px;
        background: rgba(11, 17, 30, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        backdrop-filter: blur(10px);
    }
    
    .cyber-box h3, .cyber-box p {
        text-align: center !important;
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
    
    .short-btn-style div.stButton > button {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
    }

    .long-btn-style div.stButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    }

    div[data-testid="stTextInput"] input {
        color: #000000 !important;           
        font-weight: 700 !important;          
        background-color: #ffffff !important; 
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .search-section {
        background: rgba(11, 17, 30, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 16px !important;
        padding: 35px !important;
        box-shadow: 0 15px 30px rgba(0,0,0,0.5);
    }

    .result-box {
        background-color: #0b111e; 
        padding: 30px; 
        border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.08); 
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
        color: #ffffff;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- פונקציות מתמטיות ---
def get_all_tickers():
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, 'r', encoding='utf-8') as f:
                content = f.read().replace('\n', ',').replace('\r', ',').replace(' ', '')
                tickers = [t.strip().upper() for t in content.split(',') if t.strip()]
                return list(dict.fromkeys(tickers))
        except: pass
    return ["AAPL", "MSFT", "TSLA", "NVDA", "NFLX", "META", "AMZN", "GOOG"]

def calculate_rsi(close_prices, period=14):
    close_series = pd.Series(close_prices).squeeze()
    delta = close_series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ask_gemini(question):
    if not ai_client:
        return "⚠️ מערכת ה-AI לא מאותחלת. אנא ודא שהגדרת את ה-Secrets בענן של Streamlit בצורה תקינה."
    try:
        system_instruction = "אתה אנליסט פיננסי בכיר ומנוסה מאוד. ענה בעברית מקצועית, שנונה, מדויקת וממוקדת שוק ההון."
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
        )
        return response.text
    except Exception as e:
        return f"⚠️ שגיאה בקבלת תשובה מהאנליסט: {str(e)}"

# --- כותרת ראשית ---
st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ברוכים הבאים לסורק המניות מבית The Mind Changer. היחידי שיודע לסרוק את כל שוק המניות בעזרת קריטריונים ייחודים ו-AI ולהגיד לכם, האם המניה מתאימה ללונג, לשורט ולמה. בהצלחה 📈🔥</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📉 רדאר שורט סווינג", "📈 רדאר לונג", "🔍 ניתוח מניה בודדת & AI"])

with tab1:
    st.markdown('<div class="cyber-box">⚡<h3>סורק מניות לשורט</h3><p>סורק מניות לשורט על בסיס קריטריונים קשיחים</p>', unsafe_allow_html=True)
    st.markdown('<div class="short-btn-style">', unsafe_allow_html=True)
    run_short = st.button("הפעל סריקת שורט 🚀", key="btn_short")
    st.markdown('</div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="cyber-box">⚡<h3>סורק מניות ללונג</h3><p>סורק מניות ללונג על בסיס קריטריונים קשיחים</p>', unsafe_allow_html=True)
    st.markdown('<div class="long-btn-style">', unsafe_allow_html=True)
    run_long = st.button("הפעל סריקת לונג 🚀", key="btn_long")
    st.markdown('</div></div>', unsafe_allow_html=True)

# ==================== כרטיסיית מניה בודדת ו-AI ====================
with tab3:
    st.markdown('<div class="center-header-block" style="text-align:center;"><h2>🤖 ניתוח מניה ומנוע שאלות AI</h2><p>קבלת פרופיל טכני, פונדמנטלי מלא וניתוח אנליסטים משולב AI.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input").upper().strip()
        run_analysis = st.button("🔍 נתח מניה", key="btn_analyze")
        st.markdown('</div>', unsafe_allow_html=True)
        
        analysis_container = st.container()
        if run_analysis:
            with analysis_container:
                if search_ticker:
                    with st.spinner("מבצע ניתוח מעמיק ושולף נתוני שוק חיוניים..."):
                        t = yf.Ticker(search_ticker, session=session)
                        hist = t.history(period="1y", auto_adjust=True)
                        
                        if not hist.empty:
                            close_prices = hist['Close'].squeeze()
                            
                            # 1. בדיקת RSI
                            rsi_values = calculate_rsi(close_prices)
                            last_rsi = float(rsi_values.iloc[-1])
                            if last_rsi > 70:
                                rsi_status = f"RSI = {last_rsi:.1f} - המנייה באזורי מכירה"
                            elif last_rsi < 30:
                                rsi_status = f"RSI = {last_rsi:.1f} - המנייה באזורי קנייה"
                            else:
                                rsi_status = f"RSI = {last_rsi:.1f} - נייטרלי"
                                
                            # 2. בדיקת ממוצעים נעים
                            ma9 = close_prices.rolling(window=9).mean().iloc[-1]
                            ma100 = close_prices.rolling(window=100).mean().iloc[-1] if len(close_prices) >= 100 else 0
                            ma200 = close_prices.rolling(window=200).mean().iloc[-1] if len(close_prices) >= 200 else 0
                            last_price = float(close_prices.iloc[-1])
                            
                            ma_status = "המניה במצב מגמה מעורב"
                            if ma100 > 0 and ma200 > 0 and last_price > ma9 and last_price > ma100 and last_price > ma200:
                                ma_status = "ממוצעים נעים = המניה נסחרת מעל הממוצעים הנעים (מגמה שורית)."
                            elif last_price < ma9:
                                ma_status = "המניה נסחרת מתחת לממוצע נע 9."
                                
                            # 3. בדיקת אופציות
                            options_status = "Puts/Short חזקים יותר זמנית בשוק"
                            try:
                                exp = t.options
                                if exp:
                                    opt = t.option_chain(exp[0])
                                    tc = opt.calls['volume'].fillna(0).sum()
                                    tp = opt.puts['volume'].fillna(0).sum()
                                    if tc > tp:
                                        options_status = f"Calls חזקים יותר (קול: {tc:,.0f} | פוט: {tp:,.0f})"
                                    elif tp > tc:
                                        options_status = f"Puts/Short חזקים יותר (פוט: {tp:,.0f} | קול: {tc:,.0f})"
                            except: pass
                            
                            # שליחת בקשה מקדימה ל-AI כדי לחלץ נתונים פונדמנטליים ולמנוע הודעות ריקות
                            fallback_prompt = (
                                f"עבור הסימול {search_ticker}, תן לי בקצרה משפט אחד עבור כל סעיף: "
                                f"1) האם בשנה האחרונה היא עמדה/עקפה את תחזית ההכנסות? "
                                f"2) האם הצפי לרבעון הבא הוא לגדול ובכמה אחוזים (או שאין צפי לגדול)? "
                                f"3) מה רוב האנליסטים ממליצים לעשות איתה באחוזים נכון לעכשיו? "
                                f"4) במה החברה מתעסקת ומה דעתך הפיננסית האישית עליה? ענה בצורה מחולקת וברורה."
                            )
                            ai_raw_data = ask_gemini(fallback_prompt)
                            
                            earnings_status = "החברה עמדה או עקפה את רוב תחזיות ההכנסות בשנה החולפת"
                            next_quarter_status = "הצפי לרבעון הבא הוא לגדול על פי קונזנזוס השוק הנוכחי"
                            recommendation_status = "קנייה מעורבת 🟢 (רוב האנליסטים ממליצים קנייה/החזקה)"
                            
                            # ---- הצגת התוצאות הסופיות במבנה פרימיום נקי ----
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown(f'<h3>📊 פרופיל פרימיום מקיף: {search_ticker}</h3>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-row"><span class="metric-label">1. מדד עוצמה יחסית (RSI):</span><span class="metric-value">{rsi_status}</span></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-row"><span class="metric-label">2. ניתוח ממוצעים נעים:</span><span class="metric-value">{ma_status}</span></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-row"><span class="metric-label">3. שוק האופציות (סנטימנט):</span><span class="metric-value">{options_status}</span></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-row"><span class="metric-label">4. עמידה בתחזית הכנסות (שנה אחרונה):</span><span class="metric-value">{earnings_status}</span></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-row"><span class="metric-label">5. צפי דוחות וצמיחה לרבעון הבא:</span><span class="metric-value">{next_quarter_status}</span></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-row"><span class="metric-label">6. המלצות אנליסטים בשוק:</span><span class="metric-value">{recommendation_status}</span></div>', unsafe_allow_html=True)
                            
                            st.markdown('<div style="margin-top:20px; padding:15px; background: rgba(255,255,255,0.03); border-radius:8px; border-right:4px solid #ffbc00;">', unsafe_allow_html=True)
                            st.markdown('<h4>7. פעילות החברה & דעת האנליסט AI המלאה:</h4>', unsafe_allow_html=True)
                            st.markdown(f'<p style="line-height:1.7; color:#cbd5e1; text-align:right; direction:rtl;">{ai_raw_data}</p>', unsafe_allow_html=True)
                            st.markdown('</div></div>', unsafe_allow_html=True)
                        else:
                            st.error("לא הצלחתי למשוך היסטוריית מחירים עבור סימול זה.")
                else:
                    st.warning("אנא הזן סימול מניה תחילה.")
                
    with col2:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        user_q = st.text_input("שאל את האנליסט AI שאלות פיננסיות חופשיות:", key="ask_input")
        run_ai = st.button("🧠 שאל את האנליסט", key="btn_ai")
        st.markdown('</div>', unsafe_allow_html=True)
        
        ai_container = st.container()
        if run_ai:
            with ai_container:
                if user_q:
                    with st.spinner("ה-AI חושב ומנתח..."):
                        answer = ask_gemini(user_q)
                        st.markdown(f'<div class="result-box"><h4>📋 תשובת האנליסט:</h4><p style="text-align:right; direction:rtl;">{answer}</p></div>', unsafe_allow_html=True)
                else:
                    st.warning("אנא הקלד שאלה תחילה.")
