# ============================================================
#   THE MIND CHANGER — PREMIUM REDESIGN
#   Drop this st.markdown block AFTER st.set_page_config()
#   and BEFORE any other content in your app.
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── HIDE STREAMLIT CHROME ── */
footer, header,
div[data-testid="stStatusWidget"],
.stAppDeployButton,
div[data-testid="stToolbar"] { display: none !important; }

/* ── APP SHELL ── */
.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(245,200,66,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(99,102,241,0.06) 0%, transparent 55%),
        #06090f;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
}

/* ── GLOBAL RTL ── */
.stApp,
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"] {
    direction: rtl !important;
    text-align: right !important;
}

/* ── HERO TITLE ── */
.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.8rem) !important;
    font-weight: 900;
    letter-spacing: 0.05em;
    color: #ffffff;
    text-align: center !important;
    margin: 40px 0 0 0;
    background: linear-gradient(135deg, #ffffff 30%, #f5c842 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    text-align: center;
    font-size: 1.05rem;
    color: #64748b;
    font-weight: 400;
    line-height: 1.7;
    max-width: 680px;
    margin: 12px auto 40px auto;
    direction: rtl;
    padding: 0 16px;
}

/* ── DIVIDER LINE UNDER TITLE ── */
.hero-divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #f5c842, transparent);
    margin: 0 auto 36px auto;
}

/* ── TAB BAR ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    justify-content: center !important;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 6px;
    width: fit-content;
    margin: 0 auto 28px auto;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    transition: background 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.05) !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(245, 200, 66, 0.12) !important;
    border: 1px solid rgba(245, 200, 66, 0.25) !important;
}

.stTabs [data-baseweb="tab"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    display: flex !important;
    flex-direction: row-reverse !important;
    align-items: center !important;
    gap: 8px !important;
    margin: 0 !important;
}

.stTabs [aria-selected="true"] p {
    color: #f5c842 !important;
}

/* remove underline indicator */
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── SECTION HEADINGS ── */
.section-heading {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin-bottom: 24px;
    letter-spacing: 0.04em;
}

/* ── PRIMARY BUTTON ── */
div.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: #0a0c10 !important;
    background: linear-gradient(135deg, #f5c842 0%, #e8a800 100%) !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 13px 44px !important;
    min-width: 260px !important;
    width: auto !important;
    margin: 16px auto 24px auto !important;
    display: block !important;
    letter-spacing: 0.03em;
    box-shadow: 0 0 28px rgba(245, 200, 66, 0.22), 0 4px 16px rgba(0,0,0,0.4);
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
}

div.stButton > button:hover {
    box-shadow: 0 0 40px rgba(245, 200, 66, 0.38), 0 6px 24px rgba(0,0,0,0.5) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── TEXT INPUT ── */
div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    padding: 12px 16px !important;
    transition: border 0.2s ease;
}

div[data-testid="stTextInput"] input:focus {
    border: 1px solid rgba(245, 200, 66, 0.45) !important;
    box-shadow: 0 0 0 3px rgba(245, 200, 66, 0.08) !important;
    background: rgba(255,255,255,0.06) !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #475569 !important;
}

div[data-testid="stTextInput"] label {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    margin-bottom: 6px !important;
}

/* ── PROGRESS BAR ── */
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #f5c842, #e8a800) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 12px rgba(245, 200, 66, 0.4);
}

div[data-testid="stProgressBar"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 99px !important;
    height: 4px !important;
}

/* ── INFO / SUCCESS ALERTS ── */
div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
}

/* ── STOCK CARDS — LONG (green) ── */
.card-long {
    background: rgba(16, 185, 129, 0.05);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-top: 2px solid #10b981;
    padding: 20px 16px;
    border-radius: 14px;
    text-align: center;
    transition: border-color 0.2s, background 0.2s;
}
.card-long:hover {
    background: rgba(16, 185, 129, 0.10);
    border-color: rgba(16, 185, 129, 0.35);
}
.card-long .ticker {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.08em;
}
.card-long .price {
    font-size: 1rem;
    font-weight: 600;
    color: #10b981;
    margin-top: 6px;
}

/* ── STOCK CARDS — SHORT (red) ── */
.card-short {
    background: rgba(239, 68, 68, 0.05);
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-top: 2px solid #ef4444;
    padding: 20px 16px;
    border-radius: 14px;
    text-align: center;
    transition: border-color 0.2s, background 0.2s;
}
.card-short:hover {
    background: rgba(239, 68, 68, 0.10);
    border-color: rgba(239, 68, 68, 0.35);
}
.card-short .ticker {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.08em;
}
.card-short .price {
    font-size: 1rem;
    font-weight: 600;
    color: #ef4444;
    margin-top: 6px;
}

/* ── CARD GRID ── */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 14px;
    margin-top: 20px;
    direction: rtl;
}

/* ── RESULT BOX (analysis panel) ── */
.result-box {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 28px;
    margin-top: 20px;
}

.result-box-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #f5c842;
    letter-spacing: 0.06em;
    margin-bottom: 20px;
    direction: rtl;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 13px 0;
    gap: 16px;
    direction: rtl;
}

.metric-row:last-of-type { border-bottom: none; }

.metric-label {
    color: #64748b;
    font-size: 0.88rem;
    font-weight: 500;
    white-space: nowrap;
}

.metric-value {
    color: #e2e8f0;
    font-size: 0.92rem;
    font-weight: 600;
    text-align: left;
}

/* ── AI ANSWER BOX ── */
.ai-box {
    background: rgba(245, 200, 66, 0.04);
    border: 1px solid rgba(245, 200, 66, 0.14);
    border-radius: 14px;
    padding: 20px 22px;
    margin-top: 18px;
}

.ai-box-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #f5c842;
    margin-bottom: 10px;
}

.ai-box-body {
    color: #cbd5e1;
    font-size: 0.93rem;
    line-height: 1.75;
    direction: rtl;
    text-align: right;
}

/* ── SPINNER ── */
div[data-testid="stSpinner"] {
    color: #f5c842 !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(245, 200, 66, 0.3); }
</style>
""", unsafe_allow_html=True)


# ============================================================
#   UPDATED HERO — replace your existing title/subtitle block
# ============================================================

st.markdown('<h1 class="main-title">The Mind Changer</h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">רדאר המניות היחידי שמשלב AI עם קריטריונים ייחודיים — לונג, שורט, או ניתוח מעמיק לכל מניה שתבחר ✨</p>', unsafe_allow_html=True)


# ============================================================
#   UPDATED CARD HTML GENERATORS
#   Replace the cards_html blocks in tab1 and tab2
# ============================================================

# --- TAB 1: Short cards ---
# Replace your existing cards_html in tab1 with:
def render_short_cards(results):
    html = '<div class="card-grid">'
    for item in results:
        html += f"""
        <div class="card-short">
            <div class="ticker">{item["סימול"]}</div>
            <div class="price">{item["מחיר אחרון"]}</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# --- TAB 2: Long cards ---
# Replace your existing cards_html in tab2 with:
def render_long_cards(results):
    html = '<div class="card-grid">'
    for item in results:
        html += f"""
        <div class="card-long">
            <div class="ticker">{item["סימול"]}</div>
            <div class="price">{item["מחיר אחרון"]}</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
#   UPDATED ANALYSIS PANEL (Tab 3, col1)
#   Replace the result-box block inside the `if st.session_state.single_results:` block
# ============================================================

def render_analysis_panel(res):
    st.markdown(f"""
    <div class="result-box">
        <div class="result-box-title">סקירת {res["ticker"]}</div>
        <div class="metric-row">
            <span class="metric-label">מדד עוצמה יחסית (RSI)</span>
            <span class="metric-value">{res["rsi"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">ממוצעים נעים</span>
            <span class="metric-value">{res["ma"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">שוק האופציות</span>
            <span class="metric-value">{res["options"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">עמידה בתחזית הכנסות</span>
            <span class="metric-value">{res["earnings"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">צפי דוחות וצמיחה</span>
            <span class="metric-value">{res["next_quarter"]}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">המלצות אנליסטים</span>
            <span class="metric-value">{res["recommendation"]}</span>
        </div>
        <div class="ai-box">
            <div class="ai-box-label">AI Analyst</div>
            <div class="ai-box-body">{res["ai_data"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
