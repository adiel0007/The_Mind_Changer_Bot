import streamlit as st
import yfinance as yf
import pandas as pd
import json
import random
import os
import contextlib

st.set_page_config(page_title="The Mind Changer", page_icon="📈", layout="wide")

# --- CSS בסיסי לעיצוב ---
st.markdown("""
<style>
    .gauge-container { position: relative; width: 200px; height: 100px; margin: 20px auto; overflow: hidden; }
    .gauge-body { position: absolute; top: 0; left: 0; width: 200px; height: 200px; border-radius: 50%; 
                  background: conic-gradient(from 270deg, #dc2626 0deg 60deg, #eab308 60deg 120deg, #16a34a 120deg 180deg, #141410 180deg 360deg); }
    .gauge-cover { position: absolute; top: 20px; left: 20px; width: 160px; height: 160px; border-radius: 50%; background: #0a0a08; display: flex; align-items: center; justify-content: center; }
    .gauge-needle { position: absolute; bottom: 100px; left: 100px; width: 3px; height: 80px; background: #fff; transform-origin: bottom center; transition: transform 0.5s; }
</style>
""", unsafe_allow_html=True)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return float(100 - (100 / (1 + rs.iloc[-1])))

def get_market_data(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        if hist.empty: return None
        
        info = t.info
        return {
            "price": f"{hist['Close'].iloc[-1]:.2f}",
            "rsi": f"{calculate_rsi(hist['Close']):.1f}",
            "target": info.get('targetMeanPrice', 'אין נתון'),
            "rec": info.get('recommendationKey', 'אין נתון'),
            "up": hist['Close'].iloc[-1] > hist['Close'].iloc[-2]
        }
    except:
        return None

# --- ממשק משתמש ---
tab1, tab2, tab3 = st.tabs(["📊 ניתוח מניה", "🧭 מדד הפחד", "🤖 שאלות AI"])

with tab1:
    sym = st.text_input("הכנס סימול מניה (למשל TSLA):")
    if st.button("נתח מניה"):
        data = get_market_data(sym.upper())
        if data:
            st.metric("מחיר אחרון", data['price'])
            st.write(f"RSI: {data['rsi']}")
            st.write(f"המלצת אנליסטים: {data['rec']}")
            st.write(f"מחיר יעד ממוצע: {data['target']}")
        else:
            st.error("לא נמצאו נתונים עבור המניה.")

with tab2:
    # שעון פחד וגרידיות רנדומלי (ה-API של CNN לרוב חסום בבקשות שרתים)
    val = random.randint(30, 80)
    angle = (val / 100) * 180 - 90
    st.markdown(f"""
    <div class="gauge-container">
        <div class="gauge-body"></div>
        <div class="gauge-cover"><span style="font-size:2rem;">{val}</span></div>
        <div class="gauge-needle" style="transform: rotate({angle}deg);"></div>
    </div>
    """, unsafe_allow_html=True)
    st.write(f"ציון סנטימנט שוק: {val}")

with tab3:
    q = st.text_input("שאל שאלה טכנית:")
    if st.button("שאל"):
        if "rsi" in q.lower():
            st.write("RSI הוא מתנד מומנטום המודד מהירות ושינוי מחירים. מעל 70 = קניית יתר, מתחת ל-30 = מכירת יתר.")
        elif "ממוצע" in q.lower():
            st.write("ממוצע נע מחליק תנודות מחיר לאורך זמן כדי לזהות מגמה.")
        else:
            st.write("אנא שאל על RSI, ממוצעים נעים או טכניקות מסחר.")
