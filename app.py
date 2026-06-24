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
FILENAME = "FILENAME = "Stocks List.txt""

# אתחול ה-AI של גוגל
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# הגדרת עיצוב הדף של Streamlit לחוויה מעולה בנייד ובמחשב
st.set_page_config(page_title="Radar System", page_icon="📊", layout="wide")

# --- פונקציות מתמטיות וטעינה (ללא שינוי מהבוט שלך) ---
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

def get_analyst_data(ticker_obj):
    try:
        info = ticker_obj.info
        total = int(info.get('numberOfAnalystOpinions', 0))
        mean_score = info.get('recommendationMean', None)
        if total > 0 and mean_score is not None:
            buy_pct = ((5.0 - float(mean_score)) / 4.0) * 100
            return int(buy_pct), total
    except: pass
    return 0, 0

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

# --- עיצוב ממשק המשתמש של האפליקציה (UI) ---
st.title("📊 מערכת רדאר מניות מתקדמת")
st.write("ברוך הבא אדיאל. כאן תוכל להריץ את סורקי הלונג והשורט או לנתח מניה בודדת 24/7.")

# חלוקה לכרטיסיות (Tabs) בתוך האתר
tab1, tab2, tab3 = st.tabs(["📉 רדאר שורט סווינג", "📈 רדאר לונג", "🔍 ניתוח מניה בודדת & AI"])

# ==================== כרטיסיית רדאר שורט ====================
with tab1:
    st.header("🐻 סורק מניות לשורט (Short Swing)")
    st.write("טווח: 15$-450$ | 3 ימים אדומים | RSI > 30 | מתחת ל-MA9 או MA100 | ווליום מתגבר | אופציות Put > 50%")
    
    if st.button("🚀 הפעל סריקת שורט"):
        tickers = get_all_tickers()
        st.info(f"מתחיל לסרוק {len(tickers)} מניות מתוך הקובץ...")
        
        # הרצת הלוגיקה שלך
        progress_bar = st.progress(0)
        stage1_passed = []
        
        # הורדת הנתונים במכה אחת (מתואם ספליטים)
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
                        
                        # 3 ימים אדומים
                        day1 = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                        day2 = df['Close'].iloc[-2] - df['Close'].iloc[-3]
                        day3 = df['Close'].iloc[-3] - df['Close'].iloc[-4]
                        
                        if day1 < 0 and day2 < 0 and day3 < 0:
                            # ממוצעים ונפח
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
            
            # שלב אופציות Put > Call
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
                
                # תצוגה בטבלה מעוצבת באתר
                df_display = pd.DataFrame(final_short)
                df_display.columns = ["סימול", "מחיר נוכחי", "RSI נוכחי", "אחוז אופציות PUT"]
                st.dataframe(df_display.style.format({"מחיר נוכחי": "${:.2f}", "RSI נוכחי": "{:.1f}", "אחוז אופציות PUT": "{:.1f}%"}), use_container_width=True)
            else:
                st.warning("אף מניה לא עברה את סינון האופציות (Put > Call).")

# ==================== כרטיסיית רדאר לונג ====================
with tab2:
    st.header("🐂 סורק מניות ללונג (Long)")
    st.write("לחץ על הכפתור כדי לסרוק הזדמנויות קנייה מתוך רשימת המניות שלך.")
    if st.button("🚀 הפעל סריקת לונג"):
        st.info("רדאר הלונג בבנייה קלה, בקרוב יוצגו כאן נתוני הקניות והדוחות המושלמים!")

# ==================== כרטיסיית מניה בודדת ו-AI ====================
with tab3:
    st.header("🤖 ניתוח מניה ומנוע שאלות AI")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        search_ticker = st.text_input("הזן שם מניה לניתוח טכני מהיר (למשל NFLX, AAPL):").upper().strip()
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
        user_q = st.text_input("שאל את האנליסט AI שאלות פיננסיות וכלכליות חופשיות:")
        if st.button("🧠 שאל את האנליסט"):
            if user_q:
                with st.spinner("ה-AI חושב ומנתח..."):
                    answer = ask_gemini(user_q)
                    st.markdown(f"### 📋 תשובת האנליסט:\n{answer}")
            else:
                st.warning("אנא הקלד שאלה תחילה.")
