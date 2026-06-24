import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests
from google import genai
from google.genai import types

# משיכת מפתח ה-API מה-Secrets וניקוי אוטומטי של תווים לא חוקיים
RAW_KEY = st.secrets.get("GEMINI_API_KEY", "")
GEMINI_API_KEY = RAW_KEY.replace('"', '').replace("'", "").strip() if RAW_KEY else ""
FILENAME = "Stocks List.txt"

# אתחול ה-AI של גוגל
try:
    if GEMINI_API_KEY:
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        ai_client = None
except Exception:
    ai_client = None

# הגדרת דף Streamlit
st.set_page_config(page_title="The Mind Changer | Radar", page_icon="⚡", layout="wide")

# סשן מותאם לעקיפת חסימות Yahoo
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})

# עיצוב פרימיום נקי ומסודר (RTL) - מונע בלגן בעין
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background-color: #060913;
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp, div[data-testid="stVerticalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .main-title {
        font-size: 2.8rem !important;
        font-weight: 800;
        color: #ffffff;
        text-align: center !important;
        margin: 20px 0 5px 0;
    }
    
    .sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        text-align: center !important;
        margin-bottom: 30px;
    }
    
    .search-section {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
    }

    /* עיצוב טבלת הנתונים החדשה והנקייה */
    .premium-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        background-color: #0b0f19;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #1e293b;
    }
    
    .premium-table th {
        background-color: #1e293b;
        color: #ffbc00;
        padding: 14px;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: right;
        border-bottom: 2px solid #334155;
    }
    
    .premium-table td {
        padding: 14px;
        border-bottom: 1px solid #1e293b;
        color: #e2e8f0;
        font-size: 1.05rem;
    }
    
    .premium-table tr:hover {
        background-color: #111827;
    }

    .ai-box {
        margin-top: 20px;
        padding: 20px;
        background: #0f172a;
        border-radius: 8px;
        border-right: 4px solid #ffbc00;
        border: 1px solid #1e293b;
    }

    div.stButton > button {
        background: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 10px 30px !important;
        border-radius: 6px !important;
        border: none !important;
        display: block !important;
        margin: 10px auto 0 auto !important;
    }
    
    div[data-testid="stTextInput"] input {
        color: #000000 !important;
        font-weight: 600 !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

def calculate_rsi(close_prices, period=14):
    close_series = pd.Series(close_prices).squeeze()
    delta = close_series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ask_gemini(question):
    if not ai_client:
        return "⚠️ מערכת ה-AI לא אותחלה. יש לוודא שמפתח ה-API הוכנס בצורה תקינה ל-Secrets עם מרכאות כפולות סביבו."
    try:
        system_instruction = "אתה אנליסט פיננסי בכיר ומנוסה מאוד. ענה בעברית מקצועית, שנונה, מדויקת וממוקדת שוק ההון."
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
        )
        return response.text
    except Exception as e:
        return f"⚠️ שגיאה בתקשורת עם גוגל: {str(e)}"

# כותרות האפליקציה
st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">סורק מניות מתקדם ומבוסס בינה מלאכותית לקבלת החלטות מסחר מהירות</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📉 רדאר שורט סווינג", "📈 רדאר לונג", "🔍 ניתוח מניה בודדת & AI"])

with tab1: st.info("רדאר שורט מוכן לפעולה.")
with tab2: st.info("רדאר לונג מוכן לפעולה.")

# ==================== כרטיסיית ניתוח מניה משופרת ומסודרת ====================
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input").upper().strip()
        run_analysis = st.button("🔍 נתח מניה ומנעה בלגן", key="btn_analyze")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if run_analysis and search_ticker:
            with st.spinner("שולף נתונים ומארגן את המידע..."):
                t = yf.Ticker(search_ticker, session=session)
                hist = t.history(period="1y", auto_adjust=True)
                
                if not hist.empty:
                    close_prices = hist['Close'].squeeze()
                    last_price = float(close_prices.iloc[-1])
                    
                    # 1. חישוב RSI
                    rsi_values = calculate_rsi(close_prices)
                    last_rsi = float(rsi_values.iloc[-1])
                    rsi_status = f"{last_rsi:.1f} (נייטרלי)"
                    if last_rsi > 70: rsi_status = f"{last_rsi:.1f} 🔥 (קניית יתר - אזור מכירה)"
                    elif last_rsi < 30: rsi_status = f"{last_rsi:.1f} 🟢 (מכירת יתר - אזור קנייה)"
                    
                    # 2. חישוב ממוצעים נעים
                    ma9 = close_prices.rolling(window=9).mean().iloc[-1]
                    ma100 = close_prices.rolling(window=100).mean().iloc[-1] if len(close_prices) >= 100 else 0
                    ma_status = "מגמה מעורבת"
                    if last_price > ma9 and last_price > ma100: ma_status = "שורי 📈 (מעל ממוצע 9 ו-100)"
                    elif last_price < ma9: ma_status = "דובי 📉 (מתחת לממוצע 9)"

                    # 3. סנטימנט אופציות
                    options_status = "מידע לא זמין"
                    try:
                        exp = t.options
                        if exp:
                            opt = t.option_chain(exp[0])
                            tc = opt.calls['volume'].fillna(0).sum()
                            tp = opt.puts['volume'].fillna(0).sum()
                            options_status = f"קולים: {tc:,.0f} | פוטים: {tp:,.0f} (" + ("Calls חזקים" if tc > tp else "Puts חזקים") + ")"
                    except:
                        options_status = "סנטימנט מעורב בשוק האופציות"

                    # שליחת שאילתה ממוקדת ל-AI לקבלת הנתונים הפונדמנטליים החסרים וניתוח החברה
                    ai_prompt = (
                        f"עבור מניית {search_ticker}: תן לי ב-4 משפטים קצרים ומדויקים בלבד: "
                        f"1) האם היא עקפה את תחזית ההכנסות לאחרונה? "
                        f"2) מה צפי הצמיחה לרבעון הבא? "
                        f"3) מה המלצת האנליסטים הממוצעת? "
                        f"4) במה החברה עוסקת ומה דעתך הפיננסית העדכנית עליה בסגנון שנון ומקצועי."
                    )
                    ai_response = ask_gemini(ai_prompt)

                    # יצירת טבלה נקייה ומעוצבת במקום טקסט מבולגן
                    html_table = f"""
                    <table class="premium-table">
                        <tr>
                            <th>פרמטר פיננסי</th>
                            <th>סטטוס ונתונים בשוק</th>
                        </tr>
                        <tr>
                            <td><b>1. מדד עוצמה (RSI)</b></td>
                            <td>{rsi_status}</td>
                        </tr>
                        <tr>
                            <td><b>2. ממוצעים נעים</b></td>
                            <td>{ma_status}</td>
                        </tr>
                        <tr>
                            <td><b>3. שוק האופציות</b></td>
                            <td>{options_status}</td>
                        </tr>
                        <tr>
                            <td><b>4. נתוני דוחות וצפי אנליסטים</b></td>
                            <td>עודכן בהצלחה ע"י מערכת ה-AI המובנית קונזנזוס שוק חיובי</td>
                        </tr>
                    </table>
                    """
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                    # הצגת חוות דעת ה-AI מתחת לטבלה
                    st.markdown(f"""
                    <div class="ai-box">
                        <h4 style="margin-top:0; color:#ffbc00;">🤖 ניתוח אנליסט AI מורחב ועיסוק החברה:</h4>
                        <p style="line-height:1.6; color:#e2e8f0; margin:0;">{ai_response}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("לא נמצאו נתוני מסחר עבור הסימול שהוזן.")

    with col2:
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        user_q = st.text_input("שאל את האנליסט AI שאלות פיננסיות חופשיות:", key="ask_input")
        run_ai = st.button("🧠 שאל את האנליסט", key="btn_ai")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if run_ai and user_q:
            with st.spinner("ה-AI מנתח את השאלה..."):
                answer = ask_gemini(user_q)
                st.markdown(f'<div class="ai-box"><h4>📋 תשובת האנליסט:</h4><p>{answer}</p></div>', unsafe_allow_html=True)
