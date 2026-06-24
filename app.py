import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
import time
from google import genai
from google.genai import types

# הגדרות בסיסיות
GEMINI_API_KEY = "AQ.Ab8RN6JI56jLqTcysBdf4I4sWDgn89UCTGLzoT0y2ZVVL0giuw" 
FILENAME = "Stocks List.txt"

# אתחול ה-AI של גוגל
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# הגדרת עיצוב הדף של Streamlit לחוויה מעולה בנייד ובמחשב
st.set_page_config(page_title="The Mind Changer | Radar", page_icon="⚡", layout="wide")

# ==========================================
#          עיצוב מותאם אישית (CSS)
# ==========================================
st.markdown("""
    <style>
    /* רקע כללי וצבעי בסיס */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* עיצוב כותרת ראשית ענקית - THE MIND CHANGER */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem !important;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ffbc00 0%, #ff8800 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #8b949e;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 300;
    }
    
    /* עיצוב כרטיסיות (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #8b949e;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background-color: #21262d;
        border-color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #ffbc00 !important;
        border-color: #ffbc00 !important;
    }

    /* עיצוב תיבות תוכן וכפתורים */
    div.stButton > button {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: #ffffff;
        border: 1px solid #4b5563;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div.stButton > button:hover {
        border-color: #ffbc00;
        color: #ffbc00;
        box-shadow: 0 10px 15px -3px rgba(255, 188, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* כפתור שורט ייעודי - אדום */
    .short-btn div.stButton > button {
        background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%);
        border: 1px solid #ef4444;
    }
    .short-btn div.stButton > button:hover {
        border-color: #ffffff;
        color: #ffffff;
        box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.3);
    }

    /* כפתור לונג ייעודי - ירוק */
    .long-btn div.stButton > button {
        background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
        border: 1px solid #10b981;
    }
    .long-btn div.stButton > button:hover {
        border-color: #ffffff;
        color: #ffffff;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
    }

    /* עיצוב טבלאות נתונים */
    .stDataFrame {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    
    /* התאמות טקסט מימין לשמאל עבור עברית */
    .rtl-text {
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# --- פונקציות מתמטיות וטעינה ---
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
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ask_gemini(question):
    try:
        system_instruction = "אתה אנליסט פיננסי בכיר. ענה בעברית מקצועית, מדויקת וממוקדת שוק ההון."
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        )
        return response.text
    except Exception as e:
        return f"⚠️ שגיאה בחיבור ל-AI: {str(e)}"

# --- כותרת ראשית מעוצבת של האתר ---
st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">מערכת רדאר מתקדמת לסריקת מניות וניתוח AI בזמן אמת</div>', unsafe_allow_html=True)

# חלוקה לכרטיסיות (Tabs)
tab1, tab2, tab3 = st.tabs(["📉 רדאר שורט סווינג", "📈 רדאר לונג", "🔍 ניתוח מניה בודדת & AI"])

# ==================== כרטיסיית רדאר שורט ====================
with tab1:
    st.markdown('<div class="rtl-text"><h3>🐻 סורק מניות לשורט (Short Swing)</h3>'
                '<p style="color:#8b949e;">טווח: 15$-450$ | 3 ימים אדומים | RSI > 30 | מתחת ל-MA9 או MA100 | ווליום מתגבר | אופציות Put > 50%</p></div>', unsafe_allow_html=True)
    
    # שימוש ב-container ייעודי לצבע כפתור אדום לשורט
    st.markdown('<div class="short-btn">', unsafe_allow_html=True)
    run_short = st.button("🚀 הפעל סריקת שורט")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if run_short:
        tickers = get_all_tickers()
        st.info(f"מתחיל לסרוק {len(tickers)} מניות מתוך הקובץ...")
        
        progress_bar = st.progress(0)
        stage1_passed = []
        
        with st.spinner("מוריד נתוני שוק ומחשב שלבים טכניים..."):
            try:
                data = yf.download(tickers, period="6mo", group_by='ticker', progress=False, auto_adjust=True)
                
                for idx, ticker in enumerate(tickers):
                    try:
                        if ticker not in data.columns.levels[0]: continue
                        df = data[ticker].dropna()
                        if len(df) < 110: continue
                        
                        current_price = float(df['Close'].iloc[-1])
                        if not (15 <= current_price <= 450): continue
                        
                        df['RSI'] = calculate_rsi(df['Close'])
                        last_rsi = float(df['RSI'].iloc[-1])
                        if np.isnan(last_rsi) or last_rsi < 30: continue
                        
                        day1 = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                        day2 = df['Close'].iloc[-2] - df['Close'].iloc[-3]
                        day3 = df['Close'].iloc[-3] - df['Close'].iloc[-4]
                        
                        if day1 < 0 and day2 < 0 and day3 < 0:
                            df['MA9'] = df['Close'].rolling(window=9).mean()
                            df['MA100'] = df['Close'].rolling(window=100).mean()
                            df['Avg_Vol'] = df['Volume'].rolling(window=15).mean()
                            
                            ma9 = df['MA9'].iloc[-1]
                            ma100 = df['MA100'].iloc[-1]
                            vol = df['Volume'].iloc[-1]
                            avg_vol = df['Avg_Vol'].iloc[-1]
                            
                            if (current_price < ma9 or current_price < ma100) and (vol > avg_vol):
                                stage1_passed.append({"ticker": ticker, "price": current_price, "rsi": last_rsi})
                    except: continue
                    progress_bar.progress((idx + 1) / len(tickers))
            except Exception as e:
                st.error(f"שגיאה בהורדת הנתונים: {e}")
                
        if not stage1_passed:
            st.warning("0 מניות עברו את הסינון הטכני הראשוני.")
        else:
            st.success(f"מצאתי {len(stage1_passed)} מניות שעברו סינון טכני. בודק שוק אופציות...")
            final_short = []
            
            for s in stage1_passed:
                try:
                    t = yf.Ticker(s['ticker'])
                    exp = t.options
                    if exp:
                        opt = t.option_chain(exp[0])
                        tc = opt.calls['volume'].fillna(0).sum()
                        tp = opt.puts['volume'].fillna(0).sum()
                        total = tc + tp
                        if total > 100:
                            put_pct = (tp / total) * 100
                            if put_pct > 50:
                                s['put_pct'] = put_pct
                                final_short.append(s)
                except: pass
                
            if final_short:
                final_short = sorted(final_short, key=lambda x: x['put_pct'], reverse=True)[:10]
                st.balloons()
                
                df_display = pd.DataFrame(final_short)
                df_display.columns = ["סימול", "מחיר נוכחי", "RSI נוכחי", "אחוז אופציות PUT"]
                st.dataframe(df_display.style.format({"מחיר נוכחי": "${:.2f}", "RSI נוכחי": "{:.1f}", "אחוז אופציות PUT": "{:.1f}%"}), use_container_width=True)
            else:
                st.warning("אף מניה לא עברה את סינון האופציות (Put > Call).")

# ==================== כרטיסיית רדאר לונג ====================
with tab2:
    st.markdown('<div class="rtl-text"><h3>🐂 סורק מניות ללונג (Long Swing)</h3>'
                '<p style="color:#8b949e;">סריקת הזדמנויות קנייה ודוחות מושלמים מתוך רשימת המניות שלך.</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="long-btn">', unsafe_allow_html=True)
    run_long = st.button("🚀 הפעל סריקת לונג")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if run_long:
        st.info("רדאר הלונג בבנייה קלה, בקרוב יוצגו כאן נתוני הקניות והדוחות המושלמים!")

# ==================== כרטיסיית מניה בודדת ו-AI ====================
with tab3:
    st.markdown('<div class="rtl-text"><h3>🤖 ניתוח מניה ומנוע שאלות AI</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="rtl-text" style="font-weight:bold;">ניתוח טכני מהיר:</div>', unsafe_allow_html=True)
        search_ticker = st.text_input("הזן סימול מניה (למשל NFLX, AAPL):", key="search_input").upper().strip()
        if st.button("🔍 נתח מניה"):
            if search_ticker:
                with st.spinner("מושך נתונים..."):
                    t = yf.download(search_ticker, period="6mo", auto_adjust=True)
                    if not t.empty:
                        t['RSI'] = calculate_rsi(t['Close'])
                        last_row = t.iloc[-1]
                        st.metric("מחיר נוכחי", f"${float(last_row['Close']):.2f}")
                        st.metric("מדד RSI", f"{float(last_row['RSI']):.1f}")
                    else:
                        st.error("המניה לא נמצאה.")
            else:
                st.warning("אנא הזן סימול.")
                
    with col2:
        st.markdown('<div class="rtl-text" style="font-weight:bold;">שאל את האנליסט AI:</div>', unsafe_allow_html=True)
        user_q = st.text_input("שאל שאלות פיננסיות וכלכליות חופשיות:", key="ask_input")
        if st.button("🧠 שאל את האנליסט"):
            if user_q:
                with st.spinner("ה-AI חושב ומנתח..."):
                    answer = ask_gemini(user_q)
                    st.markdown(f'<div class="rtl-text" style="background-color:#161b22; padding:20px; border-radius:8px; border:1px solid #30363d;">'
                                f'<h4>📋 תשובת האנליסט:</h4><p>{answer}</p></div>', unsafe_allow_html=True)
            else:
                st.warning("אנא הקלד שאלה תחילה.")
