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
#     מערכת עיצוב פרימיום קשיחה וסופית (RTL)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;600;700&display=swap');

    /* תמונת רקע של בורסה וגרפים */
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
    
    /* כפיית כיוון RTL על כל האפליקציה בצורה גורפת */
    .stApp, div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* כותרת ראשית ממורכזת */
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
    
    /* תת כותרת ממורכזת */
    .sub-title {
        font-size: 1.15rem;
        color: #cbd5e1;
        text-align: center !important;
        max-width: 850px;
        margin: 0 auto 40px auto;
        line-height: 1.7;
        direction: rtl !important;
    }
    
    /* עיצוב והגדלת כרטיסיות (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center !important;
        border-bottom: 1px solid rgba(30, 41, 59, 0.8) !important;
        direction: rtl !important;
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

    /* קונטיינר מרכזי לרדארים */
    .cyber-box {
        direction: rtl !important;
        text-align: center !important;
        max-width: 750px;
        margin: 30px auto;
        padding: 40px 30px;
        background: rgba(11, 17, 30, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        backdrop-filter: blur(10px);
    }
    
    .cyber-box h3 {
        color: #ffffff !important;
        font-size: 1.7rem;
        text-align: center !important;
    }
    
    .cyber-box p {
        color: #cbd5e1 !important;
        font-size: 1.1rem;
        margin-bottom: 30px;
        text-align: center !important;
    }

    /* עיצוב גורף ויציב לכפתורים */
    div.stButton > button, div.stButton > button:focus, div.stButton > button:active {
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
        box-shadow: 0 4px 15px rgba(29, 78, 216, 0.4) !important;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border-color: #60a5fa !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    
    .short-btn-style div.stButton > button {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        border: 1px solid #ef4444 !important;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4) !important;
    }
    .short-btn-style div.stButton > button:hover {
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
    }

    .long-btn-style div.stButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        border: 1px solid #10b981 !important;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.4) !important;
    }
    .long-btn-style div.stButton > button:hover {
        background: linear-gradient(135deg, #10b981 0%, #065f46 100%) !important;
    }

    /* שינוי צבע הטקסט בתוך הודעות המידע ללבן קריא */
    div[data-testid="stNotification"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-align: right !important;
    }

    /* עיצוב הטבלאות, מרכוז אבסולוטי לצמצום חורים מרווחים */
    div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        max-width: 450px !important; 
        margin: 25px auto !important; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
    }
    
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        text-align: center !important; 
        font-weight: 600 !important;
        padding: 10px 15px !important;
    }

    /* עיצוב תיבות ההקלדה הלבנות (Inputs) */
    div[data-testid="stTextInput"] input {
        color: #000000 !important;           
        -webkit-text-fill-color: #000000 !important; 
        font-weight: 700 !important;          
        font-size: 1.15rem !important;        
        background-color: #ffffff !important; 
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    div[data-testid="stTextInput"] label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important; 
    }
    
    /* מרכוז כותרות פנימיות וטקסטים בכרטיסייה 3 */
    .center-header-block {
        text-align: center !important;
        margin: 20px auto 10px auto;
        width: 100%;
        direction: rtl !important;
    }
    .center-header-block h2, .center-header-block h3 {
        color: #ffffff !important;
        text-align: center !important;
        font-weight: 800 !important;
    }
    .center-header-block p {
        color: #94a3b8 !important;
        text-align: center !important;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    
    /* עיצוב המכולות של אזורי החיפוש */
    .search-section {
        background: rgba(11, 17, 30, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 16px !important;
        padding: 35px !important;
        margin-top: 15px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.5);
    }

    /* תיבת תוצאות יפה לניתוח טכני ו-AI */
    .result-box {
        background-color: #0b111e; 
        padding: 30px; 
        border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.08); 
        margin-top: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 14px 0;
        font-size: 1.15rem;
        direction: rtl !important;
    }
    .metric-label {
        color: #94a3b8;
        font-weight: 600;
        text-align: right;
    }
    .metric-value {
        color: #ffffff;
        font-weight: 700;
        text-align: left;
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
    return
