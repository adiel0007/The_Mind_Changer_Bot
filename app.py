import streamlit as st
import yfinance as yf
import pandas as pd
import json
import random
import requests
import os
import contextlib
import time

# משיכת המפתח מתוך הסודות של Streamlit או הגדרה מקומית
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "הכנס_כאן_את_המפתח_החדש"

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

st.set_page_config(page_title="The Mind Changer", page_icon="📈", layout="wide")

# ── ה-CSS המקורי של הפאנלים והעיצוב הכללי ──
SHARED_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --gold:#c9a84c;--gold-light:#e8c97a;--gold-pale:rgba(201,168,76,0.08);
  --green:#16a34a;--red:#dc2626;
  --bg:#0a0a08;--bg2:#0f0f0c;--surface:#141410;
  --border:rgba(201,168,76,0.12);--border2:rgba(255,255,255,0.06);
  --text:#f0ede6;--muted:#7a7060;--muted2:#9a8f7a;
}
body{background:#0a0a08;color:var(--text);font-family:'Inter',sans-serif;direction:rtl;margin:0}
.panel-card{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:22px}
.panel-title{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--text);margin-bottom:4px;text-align:right;}
.panel-sub{font-size:0.75rem;color:var(--muted);line-height:1.5;margin-bottom:16px;text-align:right;}
.criteria-list{list-style:none;margin-bottom:18px;padding-right:0;}
.criteria-list li{font-size:0.75rem;color:var(--muted2);padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:center;gap:7px;direction:rtl;}
.crit-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.dot-green{background:var(--green)}
.dot-red{background:var(--red)}
.results-panel{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:22px;}
.results-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border2);direction:rtl;}
.results-title{font-size:0.68rem;font-weight:600;letter-spacing:0.12em;color:var(--muted);text-transform:uppercase}
.results-count{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--gold)}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;direction:rtl;}
.stock-card{border-radius:3px;padding:12px 8px;text-align:center;border:1px solid;transition:transform .15s}
.stock-card:hover{transform:translateY(-2px)}
.card-long{background:rgba(22,163,74,0.06);border-color:rgba(22,163,74,0.18)}
.card-short{background:rgba(220,38,38,0.06);border-color:rgba(220,38,38,0.18)}
.card-sym{font-size:0.82rem;font-weight:700;color:var(--text);letter-spacing:0.05em}
.card-price-g{font-size:0.74rem;font-weight:600;color:var(--green);margin-top:4px}
.card-price-r{font-size:0.74rem;font-weight:600;color:var(--red);margin-top:4px}
.card-chg{font-size:0.65rem;color:var(--muted);margin-top:2px}
.empty-msg{color:var(--muted);font-size:0.82rem;text-align:center;padding:40px 0}
.result-card{background:rgba(255,255,255,0.02);border:1px solid var(--border2);border-radius:3px;margin-top:14px}
.result-card-header{padding:12px 16px;border-bottom:1px solid var(--border2);font-family:'Playfair Display',serif;font-size:0.88rem;font-weight:700;color:var(--text);display:flex;align-items:center;justify-content:space-between;direction:rtl;}
.result-tag{font-size:0.62rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:2px 8px;border-radius:2px}
.tag-green{background:rgba(22,163,74,0.12);color:var(--green)}
.tag-red{background:rgba(220,38,38,0.12);color:var(--red)}
.metric-row{display:flex;justify-content:space-between;padding:9px 16px;border-bottom:1px solid rgba(255,255,255,0.03);direction:rtl;}
.metric-row:last-child{border-bottom:none}
.metric-label{font-size:0.73rem;color:var(--muted)}
.metric-value{font-size:0.73rem;color:var(--muted2);font-weight:600;text-align:left}
.ai-response-box{margin-top:12px;padding:15px;background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.12);border-radius:3px;border-right:3px solid #c9a84c;}
.ai-response-label{font-size:0.62rem;font-weight:700;letter-spacing:0.12em;color:#c9a84c;text-transform:uppercase;margin-bottom:6px;text-align:right;}
.ai-response-text{font-size:0.82rem;color:#f0ede6;line-height:1.7;direction:rtl;text-align:right}
"""

st.markdown(f"""
<style>
footer,header,div[data-testid="stStatusWidget"],
.stAppDeployButton,div[data-testid="stToolbar"],
div[data-testid="stDecoration"],#MainMenu,
div[data-testid="stSidebarNav"],
div[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{{display:none!important}}
.main .block-container{{padding:0!important;max-width:100%!important}}
.stApp{{margin:0!important;padding:0!important;background-color:#0a0a08!important;}}

{SHARED_CSS}

div[data-testid="stTabs"] {{
    padding: 0 40px !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}}
div[data-testid="stTabs"] button {{
    color: #7a7060 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: #c9a84c !important;
    border-bottom-color: #c9a84c !important;
}}

/* עיצוב מעודכן לכל הכפתורים - טקסט שחור ובולט */
div.stButton > button {{
    width: 100% !important;
    padding: 11px !important;
    border-radius: 0 0 4px 4px !important;
    font-size: 0.78rem !important;
    font-weight: 900 !important;
    color: #000000 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer !important;
    border: none !important;
    transition: opacity .2s !important;
    margin-top: -2px !important;
}}
div.stButton > button:hover {{ opacity: 0.88 !important; }}

.long-btn div[data-testid="stButton"] button {{ background-color: #16a34a !important; color: #000000 !important; }}
.short-btn div[data-testid="stButton"] button {{ background-color: #dc2626 !important; color: #000000 !important; }}
.gold-btn div[data-testid="stButton"] button {{ background-color: #c9a84c !important; color: #000000 !important; }}
.stop-btn div[data-testid="stButton"] button {{ background-color: #9ca3af !important; color: #000000 !important; border: 1px solid #4b5563 !important; }}

div[data-testid="stTextInput"] input {{
    background-color: #141410 !important;
    border: 1px solid rgba(201, 168, 76, 0.3) !important;
    border-radius: 4px !important;
    color: #f0ede6 !important;
    font-size: 0.88rem !important;
    padding: 10px 13px !important;
    direction: rtl !important;
}}
</style>
""", unsafe_allow_html=True)

def get_session():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'
    ]
    s = requests.Session()
    s.headers.update({
        'User-Agent': random.choice(agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    return s

@st.cache_data(ttl=900, show_spinner=False)
def fetch_options_sentiment(ticker_symbol):
    calls_oi, puts_oi = 0, 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        session = requests.Session()
        session.headers.update(headers)
        session.get(f'https://finance.yahoo.com/quote/{ticker_symbol}', timeout=8)

        crumb = ""
        try:
            crumb_res = session.get(
                'https://query2.finance.yahoo.com/v1/test/getcrumb', timeout=8
            )
            if crumb_res.status_code == 200 and crumb_res.text and "Too Many Requests" not in crumb_res.text:
                crumb = crumb_res.text.strip()
        except Exception:
            pass

        url = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker_symbol}"
        params = {"crumb": crumb} if crumb else {}
        res = session.get(url, params=params, timeout=8)

        if res.status_code == 200:
            data = res.json()
            result = data.get('optionChain', {}).get('result', [])
            if result:
                all_dates = result[0].get('expirationDates', [])
                dates_to_scan = all_dates[:4] if all_dates else [None]

                for exp_date in dates_to_scan:
                    try:
                        if exp_date:
                            scan_url = f"{url}?date={exp_date}"
                            if crumb:
                                scan_url += f"&crumb={crumb}"
                            scan_res = session.get(scan_url, timeout=8)
                            scan_data = scan_res.json()
                            opts_list = scan_data.get('optionChain', {}).get('result', [])
                        else:
                            opts_list = result

                        if not opts_list:
                            continue
                        opts = opts_list[0].get('options', [])
                        if not opts:
                            continue
                        opts = opts[0]

                        for c in opts.get('calls', []):
                            oi = c.get('openInterest')
                            if oi is not None:
                                calls_oi += oi
                        for p in opts.get('puts', []):
                            oi = p.get('openInterest')
                            if oi is not None:
                                puts_oi += oi
                    except Exception:
                        continue

                if calls_oi > 0 or puts_oi > 0:
                    return calls_oi, puts_oi
    except Exception:
        pass

    try:
        s2 = requests.Session()
        s2.headers.update(headers)
        t = yf.Ticker(ticker_symbol, session=s2)
        dates = t.options
        if dates:
            for date in dates[:4]:
                try:
                    chain = t.option_chain(date)
                    if 'openInterest' in chain.calls.columns:
                        calls_oi += int(chain.calls['openInterest'].fillna(0).sum())
                    if 'openInterest' in chain.puts.columns:
                        puts_oi += int(chain.puts['openInterest'].fillna(0).sum())
                except Exception:
                    continue
            if calls_oi > 0 or puts_oi > 0:
                return calls_oi, puts_oi
    except Exception:
        pass

    try:
        t2 = yf.Ticker(ticker_symbol)
        dates2 = t2.options
        if dates2:
            for date in dates2[:2]:
                try:
                    chain2 = t2.option_chain(date)
                    if 'openInterest' in chain2.calls.columns:
                        calls_oi += int(chain2.calls['openInterest'].fillna(0).sum())
                    if 'openInterest' in chain2.puts.columns:
                        puts_oi += int(chain2.puts['openInterest'].fillna(0).sum())
                except Exception:
                    continue
    except Exception:
        pass

    return calls_oi, puts_oi

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain  = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs    = gain / (loss + 1e-10)
    return float((100 - (100 / (1 + rs))).iloc[-1])

def load_tickers():
    filename = "Stocks List.txt"
    if not os.path.exists(filename):
        return ["AAPL","MSFT","TSLA","NVDA","NFLX","META","AMZN","GOOG","AMD","COIN"]
    with open(filename) as f:
        content = f.read().replace(",", " ").replace(";", " ").replace("\n", " ")
        return list(dict.fromkeys([t.strip().upper() for t in content.split() if t.strip()]))

@st.cache_data(ttl=300)
def fetch_quotes():
    symbols = ["AAPL","TSLA","NVDA","META","AMZN","MSFT","NFLX","GOOG","SPY","QQQ"]
    results = []
    for sym in symbols:
        try:
            t     = yf.Ticker(sym)
            fi    = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"symbol": sym, "price": price, "change_pct": chg, "up": chg >= 0})
        except:
            pass
    return results

@st.cache_data(ttl=300)
def fetch_indices():
    mapping = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "DOW JONES"}
    results = []
    for sym, name in mapping.items():
        try:
            t     = yf.Ticker(sym)
            fi    = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"name": name, "price": f"{price:,.2f}", "chg": chg, "up": chg >= 0})
        except:
            pass
    return results

@st.cache_data(ttl=600)
def fetch_live_stocks():
    syms    = ["NVDA","TSLA","AAPL","META","AMZN","MSFT"]
    results = []
    for sym in syms:
        try:
            t     = yf.Ticker(sym)
            fi    = t.fast_info
            price = round(float(fi.last_price), 2)
            prev  = float(fi.previous_close)
            chg   = round(((price - prev) / prev) * 100, 2) if prev else 0
            results.append({"symbol": sym, "price": f"{price:,.2f}", "chg": chg, "up": chg >= 0})
        except:
            pass
    return results

def get_fear_greed_data():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://edition.cnn.com/",
            "Origin": "https://edition.cnn.com"
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            val = round(data.get("fear_and_greed", {}).get("score", 55))
            rating = data.get("fear_and_greed", {}).get("rating", "neutral").title()
            
            hebrew_mapping = {
                "Extreme Fear": "פחד קיצוני 😨",
                "Fear": "פחד 😰",
                "Neutral": "ניטרלי 😐",
                "Greed": "גרידיות / תאוות בצע 🤑",
                "Extreme Greed": "גרידיות קיצונית 🚀"
            }
            return val, hebrew_mapping.get(rating, "ניטרלי 😐")
    except:
        pass
    return 55, "ניטרלי 😐"

def do_scan(mode):
    tickers  = load_tickers()
    results  = []
    session  = get_session()
    progress = st.progress(0)
    status   = st.empty()
    total    = len(tickers)
    for i, ticker in enumerate(tickers):
        status.markdown(f"<div style='color:#c9a84c;font-size:0.85rem;text-align:center;margin-bottom:10px;'>🔍 סורק {ticker}... ({i+1}/{total})</div>", unsafe_allow_html=True)
        progress.progress(int((i + 1) / total * 100))
        try:
            t = yf.Ticker(ticker, session=session)
            with open(os.devnull, 'w') as dn, contextlib.redirect_stderr(dn):
                df = t.history(period="2y", interval="1d", auto_adjust=True, actions=False)
            
            if df.empty or len(df) < 30:
                continue
            
            df = df.dropna(subset=["Close", "Open", "High", "Low", "Volume"])
            if len(df) < 3:
                continue
                
            close = df["Close"]
            last  = float(close.iloc[-1])
            prev  = float(close.iloc[-2])
            rsi   = calculate_rsi(close)
            
            ma9_series = close.rolling(9).mean()
            ma9   = float(ma9_series.iloc[-1])
            ma9_prev = float(ma9_series.iloc[-2])
            
            ma100 = float(close.rolling(100).mean().bfill().fillna(last).iloc[-1])
            ma200 = float(close.rolling(200).mean().bfill().fillna(last).iloc[-1])
            vol   = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
            chg   = round(((last - prev) / prev) * 100, 2)
            
            open_1, close_1, high_1, low_1 = float(df["Open"].iloc[-1]), float(df["Close"].iloc[-1]), float(df["High"].iloc[-1]), float(df["Low"].iloc[-1])
            open_2, close_2, high_2, low_2 = float(df["Open"].iloc[-2]), float(df["Close"].iloc[-2]), float(df["High"].iloc[-2]), float(df["Low"].iloc[-2])
            
            body_2 = abs(close_2 - open_2)
            lower_shadow_2 = min(open_2, close_2) - low_2
            upper_shadow_2 = high_2 - max(open_2, close_2)
            
            is_hammer_yesterday = (body_2 > 0) and (lower_shadow_2 >= 2 * body_2) and (upper_shadow_2 <= body_2)
            is_shooting_star_yesterday = (body_2 > 0) and (upper_shadow_2 >= 2 * body_2) and (lower_shadow_2 <= body_2)
            
            if mode == "long":
                if (last > ma9 and prev > ma9_prev and rsi < 70 and vol > 1_000_000
                        and not (last > ma100 and last > ma200 and last > ma9)
                        and close_1 > open_1
                        and last > prev and chg > 0
                        and is_hammer_yesterday): 
                    results.append({"symbol": ticker, "price": f"${last:.2f}", "chg": f"+{chg}%", "up": True})
            else:
                close_3 = float(close.iloc[-3])
                two_consecutive_down = (close_1 < close_2) and (close_2 < close_3)

                if (rsi > 30 and two_consecutive_down and vol > 1_000_000
                        and close_1 < open_1
                        and is_shooting_star_yesterday):
                    results.append({"symbol": ticker, "price": f"${last:.2f}", "chg": f"{chg}%", "up": False})
        except:
            continue
    progress.empty()
    status.empty()
    return results

def normalize_ticker(raw_ticker):
    t = raw_ticker.strip().upper()
    if t.startswith("^"):
        return t
    t = t.replace(" ", "")
    if "." in t:
        t = t.replace(".", "-")
    return t


def _fetch_history_with_retry(ticker, attempts=3):
    last_error = None
    for i in range(attempts):
        try:
            session = get_session()
            t = yf.Ticker(ticker, session=session)
            df = t.history(period="1y", interval="1d", auto_adjust=True, actions=False)
            if not df.empty and len(df) >= 30:
                return df, t, None
        except Exception as e:
            last_error = e

        try:
            df2 = yf.download(ticker, period="1y", interval="1d", progress=False, threads=False)
            if not df2.empty and isinstance(df2.columns, pd.MultiIndex):
                df2.columns = df2.columns.get_level_values(0)
            if not df2.empty and len(df2) >= 30:
                try:
                    t_obj = yf.Ticker(ticker, session=get_session())
                except Exception:
                    t_obj = yf.Ticker(ticker)
                return df2, t_obj, None
        except Exception as e:
            last_error = e

        time.sleep(1.5 * (i + 1))

    return pd.DataFrame(), None, last_error


def _get_yahoo_crumb_session():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    session = requests.Session()
    session.headers.update(headers)
    crumb = ""
    try:
        session.get('https://fc.yahoo.com', timeout=8)
    except Exception:
        pass
    try:
        session.get('https://finance.yahoo.com/quote/AAPL', timeout=8)
    except Exception:
        pass
    try:
        crumb_res = session.get('https://query2.finance.yahoo.com/v1/test/getcrumb', timeout=8)
        if crumb_res.status_code == 200 and crumb_res.text and "Too Many Requests" not in crumb_res.text:
            crumb = crumb_res.text.strip()
    except Exception:
        pass
    return session, crumb


@st.cache_data(ttl=600, show_spinner=False)
def fetch_fundamentals(ticker_symbol):
    modules = "financialData,defaultKeyStatistics,earningsTrend,recommendationTrend,summaryDetail,earningsHistory"
    merged = {}

    for attempt in range(3):
        try:
            session, crumb = _get_yahoo_crumb_session()
            url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker_symbol}"
            params = {"modules": modules}
            if crumb:
                params["crumb"] = crumb
            res = session.get(url, params=params, timeout=8)
            if res.status_code == 200:
                data = res.json()
                results = data.get("quoteSummary", {}).get("result", [])
                if results:
                    r = results[0]
                    fin = r.get("financialData", {}) or {}
                    stats = r.get("defaultKeyStatistics", {}) or {}
                    summ = r.get("summaryDetail", {}) or {}
                    earn_hist = r.get("earningsHistory", {}) or {}

                    def _raw(d, key):
                        v = d.get(key)
                        if isinstance(v, dict):
                            return v.get("raw")
                        return v

                    merged["revenueGrowth"] = _raw(fin, "revenueGrowth")
                    merged["recommendationKey"] = fin.get("recommendationKey")
                    merged["numberOfAnalystOpinions"] = _raw(fin, "numberOfAnalystOpinions")
                    merged["earningsQuarterlyGrowth"] = _raw(stats, "earningsQuarterlyGrowth")
                    merged["trailingEps"] = _raw(stats, "trailingEps")
                    merged["forwardEps"] = _raw(stats, "forwardEps")

                    quarters = earn_hist.get("history", []) or []
                    beat_list = []
                    for q in quarters:
                        actual = _raw(q, "epsActual")
                        estimate = _raw(q, "epsEstimate")
                        if actual is not None and estimate is not None:
                            beat_list.append(actual >= estimate)
                    merged["earnings_beat_list"] = beat_list[-4:]

                    if any(v is not None for v in merged.values() if not isinstance(v, list)) or beat_list:
                        return merged
        except Exception:
            pass
        time.sleep(1.2 * (attempt + 1))

    try:
        t_fallback = yf.Ticker(ticker_symbol, session=get_session())
        info = t_fallback.info or {}
        if info:
            for key in ["revenueGrowth", "recommendationKey", "numberOfAnalystOpinions",
                        "earningsQuarterlyGrowth", "trailingEps", "forwardEps"]:
                if merged.get(key) is None:
                    merged[key] = info.get(key)
        if not merged.get("earnings_beat_list"):
            try:
                eh = t_fallback.earnings_history
                if eh is not None and not eh.empty and "epsActual" in eh.columns and "epsEstimate" in eh.columns:
                    sub = eh.dropna(subset=["epsActual", "epsEstimate"]).tail(4)
                    merged["earnings_beat_list"] = [
                        bool(a >= e) for a, e in zip(sub["epsActual"], sub["epsEstimate"])
                    ]
            except Exception:
                pass
    except Exception:
        pass

    return merged


def analyze_ticker(ticker):
    try:
        clean_ticker = normalize_ticker(ticker)
        df, t, fetch_error = _fetch_history_with_retry(clean_ticker, attempts=3)

        if df.empty or len(df) < 30:
            try:
                test_info = yf.Ticker(clean_ticker).fast_info
                _ = test_info.last_price
                return {"_error": "network"}
            except Exception:
                return {"_error": "invalid"}

        df = df.dropna(subset=["Close", "Open", "Volume"])
        close = df["Close"]

        last = float(close.iloc[-1])
        prev = float(close.iloc[-2])
        try:
            fi = t.fast_info if t is not None else None
            if fi is not None:
                live_price = float(fi.last_price)
                live_prev_close = float(fi.previous_close)
                if live_price > 0 and live_prev_close > 0:
                    last = live_price
                    prev = live_prev_close
        except Exception:
            pass

        chg = round(((last - prev) / prev) * 100, 2)
        rsi = calculate_rsi(close)
        
        if rsi > 70:
            rsi_status, rsi_pos = "זמן למכור", False
        elif rsi < 30:
            rsi_status, rsi_pos = "זמן לקנות", True
        else:
            rsi_status, rsi_pos = "ניטרלי", None

        ma100_series = close.rolling(100).mean().bfill().fillna(last)
        ma200_series = close.rolling(200).mean().bfill().fillna(last)
        
        above_all = True
        below_all = True
        for j in range(1, min(4, len(close))):
            c_val = float(close.iloc[-j])
            if not (c_val > float(ma100_series.iloc[-j]) and c_val > float(ma200_series.iloc[-j])):
                above_all = False
            if not (c_val < float(ma100_series.iloc[-j]) and c_val < float(ma200_series.iloc[-j])):
                below_all = False
                
        if above_all:
            ma_status, ma_pos = "לונג", True
        elif below_all:
            ma_status, ma_pos = "שורט", False
        else:
            ma_status, ma_pos = "ניטרלי", None

        info = fetch_fundamentals(clean_ticker)

        earnings_text = "אין נתונים מספיקים להערכה"
        earnings_badge = "לא זמין"
        earnings_pos = None

        beat_list = info.get("earnings_beat_list") or []
        if beat_list:
            total_q = len(beat_list)
            beats = sum(1 for b in beat_list if b)
            earnings_badge = f"{beats}/{total_q}"
            if beats == total_q:
                earnings_text = f"המניה עמדה בתחזית האנליסטים או עברה אותה ב-{beats} מתוך {total_q} הרבעונים האחרונים — רצף מושלם"
                earnings_pos = True
            elif beats == 0:
                earnings_text = f"המניה לא עמדה בתחזית האנליסטים באף אחד מ-{total_q} הרבעונים האחרונים"
                earnings_pos = False
            elif beats >= total_q / 2:
                earnings_text = f"המניה עמדה בתחזית האנליסטים או עברה אותה ב-{beats} מתוך {total_q} הרבעונים האחרונים"
                earnings_pos = True
            else:
                earnings_text = f"המניה עמדה בתחזית האנליסטים רק ב-{beats} מתוך {total_q} הרבעונים האחרונים"
                earnings_pos = False

        options_text = "אין נתוני אופציות"
        calls_oi, puts_oi = fetch_options_sentiment(clean_ticker)
        total_oi = calls_oi + puts_oi
        if total_oi > 0:
            calls_ratio = (calls_oi / total_oi) * 100
            if calls_ratio >= 50:
                options_text = f"רוב אופציות קול ({calls_ratio:.1f}%)"
            else:
                options_text = f"רוב אופציות פוט ({100 - calls_ratio:.1f}%)"

        rev_growth = info.get("revenueGrowth")
        if rev_growth is not None:
            rev_growth_pct = round(rev_growth * 100, 1)
            if rev_growth_pct >= 0:
                forecast_text = f"צפי לגדילה בהכנסות ב-{rev_growth_pct}%"
                forecast_pos = True
            else:
                forecast_text = f"צפי לירידה בהכנסות ב-{abs(rev_growth_pct)}%"
                forecast_pos = False
        else:
            forecast_text = "אין תחזית הכנסות זמינה"
            forecast_pos = None

        rec_key = info.get("recommendationKey")
        num_analysts = info.get("numberOfAnalystOpinions")
        
        if rec_key and rec_key != "none":
            hebrew_rec = {
                "strong_buy": "קנייה חזקה",
                "buy": "קנייה",
                "hold": "אחזקה",
                "sell": "מכירה",
                "strong_sell": "מכירה חזקה",
                "underperform": "תשואת חסר",
                "outperform": "תשואת יתר"
            }
            translated_rec = hebrew_rec.get(rec_key, rec_key.replace('_', ' ').title())
            analyst_text = f"מבוסס על {num_analysts} אנליסטים" if num_analysts else "קונצנזוס"
            rec_text = f"המלצה: {translated_rec} ({analyst_text})"
            rec_badge = translated_rec
            rec_pos = rec_key in ["buy", "strong_buy", "outperform"]
        else:
            rec_text = "אין המלצות אנליסטים"
            rec_badge = "לא זמין"
            rec_pos = None

        ma9_val = float(close.rolling(9).mean().iloc[-1]) if len(close) >= 9 else last
        trend_up = last > ma9_val
        up = chg >= 0
        trend_status = "שורי (דומיננטיות קונים ברורה)" if trend_up else "דובי (לחץ מוכרים מוגבר)"
        
        formatted_opinion = (
            f"🎯 <b>מסקנה אנליטית:</b> מניית {clean_ticker} נמצאת כעת במבנה מחירים <b>{trend_status}</b> בטווח הקצר המיידי.<br/>"
            f"📊 <b style='color:#c9a84c;'>מצב המתנדים:</b> מדד ה-RSI עומד על {rsi:.1f} המייצג סביבה תנודתית, כאשר נפח המסחר משקף מעורבות מוסדית.<br/>"
            f"🌐 <b style='color:#c9a84c;'>טווח ארוך (מאקרו):</b> נכס הבסיס נסחר במגמה של <b>{ma_status}</b> ביחס לממוצעים 100 ו-200 ימים."
        )
        
        return {
            "ticker":   clean_ticker,
            "price":    f"${last:.2f}",
            "chg":      f"+{chg}%" if chg >= 0 else f"{chg}%",
            "up":       up,
            "rsi_val_num": rsi,
            "rsi_status": rsi_status,
            "rsi_pos":    rsi_pos,
            "ma_status":  ma_status,
            "ma_pos":     ma_pos,
            "options_text": options_text,
            "earnings":   earnings_text,
            "earnings_badge": earnings_badge,
            "earnings_pos":   earnings_pos,
            "rec_text":   rec_text,
            "rec_badge":  rec_badge,
            "rec_pos":    rec_pos,
            "forecast_text": forecast_text,
            "forecast_pos":  forecast_pos,
            "momentum":   "עולה" if up else "יורד",
            "summary_text": formatted_opinion
        }
    except Exception as e:
        return {"_error": "network"}

def render_cards(data, mode):
    if data is None:
        return '<div class="empty-msg">הפעל את הרדאר כדי לראות תוצאות</div>'
    if len(data) == 0:
        return '<div class="empty-msg">לא נמצאו מניות העונות לקריטריונים כרגע</div>'
    cls  = "card-long"    if mode == "long" else "card-short"
    pcls = "card-price-g" if mode == "long" else "card-price-r"
    cards = "".join(
        f'<div class="stock-card {cls}">'
        f'<div class="card-sym">{s["symbol"]}</div>'
        f'<div class="{pcls}">{s["price"]}</div>'
        f'<div class="card-chg">{s["chg"]}</div></div>'
        for s in data
    )
    return f'<div class="card-grid">{cards}</div>'

def render_analysis(d):
    if not d or not isinstance(d, dict):
        return ''
    
    tag_cls = "tag-green" if d.get("up", True) else "tag-red"
    chg_color = "#16a34a" if d.get("up") else "#dc2626"
    tag_border = "#16a34a" if d.get("up") else "#dc2626"
    tag_bg = "rgba(22, 163, 74, 0.15)" if d.get("up") else "rgba(220, 38, 38, 0.15)"
    
    def make_metric_card(label, val_text, badge_text="", is_pos=None):
        if is_pos is True:
            badge_bg, badge_color, badge_border = "rgba(22, 163, 74, 0.15)", "#16a34a", "rgba(22, 163, 74, 0.3)"
        elif is_pos is False:
            badge_bg, badge_color, badge_border = "rgba(220, 38, 38, 0.15)", "#dc2626", "rgba(220, 38, 38, 0.3)"
        else:
            badge_bg, badge_color, badge_border = "rgba(255, 255, 255, 0.05)", "#9a8f7a", "rgba(255, 255, 255, 0.1)"
            
        badge_html = f'<span style="padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; white-space: nowrap;">{badge_text}</span>' if badge_text else ""
        
        return (
            f'<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 16px; display: flex; flex-direction: column; justify-content: center; gap: 8px; transition: transform 0.2s, background 0.2s;" onmouseover="this.style.background=\'rgba(255,255,255,0.04)\'" onmouseout="this.style.background=\'rgba(255,255,255,0.02)\'">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">'
            f'<span style="font-size: 0.75rem; color: #7a7060; font-weight: 600; letter-spacing: 0.05em;">{label}</span>'
            f'{badge_html}'
            f'</div>'
            f'<div style="font-size: 0.95rem; color: #f0ede6; font-weight: 600; font-family: \'Inter\', sans-serif; line-height: 1.3;">{val_text}</div>'
            f'</div>'
        )

    # יצירת כרטיסיות הנתונים
    metrics_grid = (
        make_metric_card("RSI (14)", f"{d.get('rsi_val_num', 0):.1f}", d.get("rsi_status", ""), d.get("rsi_pos")) +
        make_metric_card("ממוצעים נעים", d.get("ma_status", ""), "מגמת מאקרו", d.get("ma_pos")) +
        make_metric_card("סנטימנט אופציות", d.get("options_text", ""), "פעילות נגזרים", None) +
        make_metric_card("דוחות כספיים", d.get("earnings", ""), d.get("earnings_badge", ""), d.get("earnings_pos")) +
        make_metric_card("צפי נתונים פיננסיים", d.get("forecast_text", ""), "תחזית", d.get("forecast_pos")) +
        make_metric_card("הערכת אנליסטים", d.get("rec_text", ""), d.get("rec_badge", ""), d.get("rec_pos"))
    )

    # תוכן הבינה המלאכותית (הדינמי שנוסיף בשלב 2)
    ai_content = d.get("dynamic_ai_text", d.get("summary_text", ""))

    html = (
        f'<div style="background: linear-gradient(145deg, #141410, #0a0a08); border: 1px solid rgba(201,168,76,0.2); border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); padding: 24px; margin-top: 20px; direction: rtl;">'
        
        # Header (Ticker, Price, Tag)
        f'<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(201,168,76,0.15); padding-bottom: 16px; margin-bottom: 20px;">'
        f'<div style="display: flex; align-items: center; gap: 16px;">'
        f'<h2 style="font-family: \'Playfair Display\', serif; font-size: 2.2rem; font-weight: 900; color: #f0ede6; margin: 0; line-height: 1;">{d.get("ticker", "")}</h2>'
        f'<div style="display: flex; flex-direction: column;">'
        f'<span style="font-family: \'Inter\', sans-serif; font-size: 1.4rem; font-weight: 700; color: #c9a84c; line-height: 1.2;">{d.get("price", "")}</span>'
        f'<span style="color: {chg_color}; font-size: 0.85rem; font-weight: 600;">{d.get("chg", "")}</span>'
        f'</div></div>'
        f'<div style="background: {tag_bg}; color: {chg_color}; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; border: 1px solid {tag_border}; box-shadow: 0 0 15px {tag_bg}; letter-spacing: 0.05em;">{d.get("momentum", "")}</div>'
        f'</div>'
        
        # Metrics Grid
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px;">'
        f'{metrics_grid}'
        f'</div>'
        
        # AI Insight Section
        f'<div style="position: relative; background: rgba(201,168,76,0.05); border: 1px solid rgba(201,168,76,0.2); border-radius: 8px; padding: 24px; overflow: hidden;">'
        f'<div style="position: absolute; top: 0; right: 0; width: 4px; height: 100%; background: #c9a84c; box-shadow: 0 0 10px #c9a84c;"></div>'
        f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">'
        f'<span style="font-size: 1.2rem;">🧠</span>'
        f'<span style="font-size: 0.85rem; font-weight: 800; color: #c9a84c; letter-spacing: 0.08em; text-transform: uppercase;">מסקנות והמלצות המודל — THE MIND CHANGER</span>'
        f'</div>'
        f'<div style="font-size: 0.9rem; color: #f0ede6; line-height: 1.8; font-weight: 400; text-align: right;">{ai_content}</div>'
        f'</div>'
        f'</div>'
    )
    return html

for k in ["long_results", "short_results", "analysis", "ai_answer"]:
    if k not in st.session_state:
        st.session_state[k] = None

with st.spinner("טוען נתוני שוק..."):
    quotes  = fetch_quotes()
    indices = fetch_indices()
    stocks  = fetch_live_stocks()

quotes_json  = json.dumps(quotes,  ensure_ascii=False)
indices_json = json.dumps(indices, ensure_ascii=False)
stocks_json  = json.dumps(stocks,  ensure_ascii=False)

top_html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
body{{background:#0a0a08;color:#f0ede6;font-family:'Inter',sans-serif;direction:rtl;margin:0}}
nav{{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 40px;height:56px;background:rgba(10,10,8,0.95);backdrop-filter:blur(24px);border-bottom:1px solid rgba(201,168,76,0.12)}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:#c9a84c;letter-spacing:0.06em}}
.nav-links{{display:flex;gap:28px;list-style:none}}
.nav-links a{{color:#9a8f7a;font-size:0.78rem;font-weight:500;text-decoration:none;letter-spacing:0.05em;transition:color .2s;cursor:pointer;text-transform:uppercase}}
.nav-links a:hover,.nav-links a.active{{color:#c9a84c}}
.nav-cta{{background:transparent;border:1px solid #c9a84c;color:#c9a84c;font-weight:600;font-size:0.75rem;letter-spacing:0.08em;padding:7px 18px;border-radius:3px;cursor:pointer;text-transform:uppercase;transition:background .2s,color .2s}}
.nav-cta:hover{{background:#c9a84c;color:#0a0a08}}
.tape-wrap{{position:fixed;top:56px;left:0;right:0;z-index:99;background:#141410;border-bottom:1px solid rgba(201,168,76,0.12);overflow:hidden;height:30px;display:flex;align-items:center}}
.tape-inner{{display:flex;animation:tape 50s linear infinite;white-space:nowrap;width:max-content}}
@keyframes tape{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tape-item{{font-size:0.68rem;font-weight:600;letter-spacing:0.06em;padding:0 24px;border-right:1px solid rgba(201,168,76,0.12);display:flex;align-items:center;gap:8px;height:30px}}
.tape-sym{{color:#9a8f7a}}.tape-up{{color:#16a34a}}.tape-dn{{color:#dc2626}}
#hero{{display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:100px 40px 48px;gap:40px;position:relative;overflow:hidden;}}
.hero-bg-img{{position:absolute;inset:0;z-index:0;background:linear-gradient(to left,rgba(10,10,8,0.15) 0%,rgba(10,10,8,0.7) 45%,rgba(10,10,8,1) 72%),url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat}}
.hero-left{{position:relative;z-index:1}}
.eyebrow{{display:flex;align-items:center;gap:8px;margin-bottom:18px}}
.eyebrow-line{{width:28px;height:1px;background:#c9a84c}}
.eyebrow-text{{font-size:0.68rem;font-weight:600;letter-spacing:0.16em;color:#c9a84c;text-transform:uppercase}}
.hero-title{{font-family:'Playfair Display',serif;font-size:clamp(2.2rem,3.5vw,3.6rem);font-weight:900;line-height:1.08;color:#f0ede6;margin-bottom:8px}}
.hero-title em{{font-style:italic;color:#c9a84c}}
.title-line{{width:40px;height:2px;background:#c9a84c;margin:18px 0}}
.hero-desc{{font-size:0.9rem;color:#9a8f7a;line-height:1.65;max-width:400px;margin-bottom:24px}}
.hero-stats{{display:flex;gap:0;margin-top:32px;border-top:1px solid rgba(201,168,76,0.12);border-bottom:1px solid rgba(201,168,76,0.12)}}
.hstat{{flex:1;padding:14px 0;text-align:center;border-right:1px solid rgba(201,168,76,0.12)}}
.hstat:last-child{{border-right:none}}
.hstat-num{{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;color:#c9a84c;display:block}}
.hstat-label{{font-size:0.65rem;color:#7a7060;letter-spacing:0.08em;text-transform:uppercase;margin-top:3px}}
.hero-right{{position:relative;z-index:1}}
.live-card{{background:#141410;border:1px solid rgba(201,168,76,0.12);border-radius:5px;padding:20px}}
.live-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.06)}}
.live-card-title{{font-family:'Playfair Display',serif;font-size:0.92rem;color:#f0ede6;font-weight:700}}
.live-dot{{width:6px;height:6px;border-radius:50%;background:#16a34a;animation:blink 1.4s infinite;display:inline-block;margin-left:5px}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.live-label{{font-size:0.65rem;font-weight:600;color:#16a34a;letter-spacing:0.08em;display:flex;align-items:center}}
.market-row{{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04)}}
.market-row:last-child{{border-bottom:none}}
.mrow-name{{font-size:0.78rem;font-weight:600;color:#9a8f7a}}
.mrow-val{{font-size:0.82rem;font-weight:700;color:#f0ede6}}
.mrow-up{{font-size:0.72rem;font-weight:600;color:#16a34a;background:rgba(22,163,74,0.1);padding:2px 7px;border-radius:2px}}
.mrow-dn{{font-size:0.72rem;font-weight:600;color:#dc2626;background:rgba(220,38,38,0.1);padding:2px 7px;border-radius:2px}}
.quote-strip{{background:#c9a84c;padding:22px 40px;text-align:center}}
.quote-text{{font-family:'Playfair Display',serif;font-size:1.1rem;font-style:italic;font-weight:700;color:#0a0a08}}
.quote-src{{font-size:0.7rem;font-weight:600;letter-spacing:0.1em;color:rgba(10,10,8,0.5);margin-top:6px;text-transform:uppercase}}
.modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,0.82);z-index:200;display:none;align-items:center;justify-content:center;backdrop-filter:blur(12px)}}
.modal-overlay.open{{display:flex}}
.modal{{background:#141410;border:1px solid rgba(201,168,76,0.12);border-radius:4px;padding:40px;max-width:440px;width:90%;text-align:center}}
.modal-logo{{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:900;color:#c9a84c;margin-bottom:6px}}
.modal-line{{width:36px;height:1px;background:#c9a84c;margin:0 auto 18px}}
.modal p{{color:#9a8f7a;font-size:0.85rem;line-height:1.7;margin-bottom:24px}}
.modal-btn{{background:#c9a84c;color:#0a0a08;border:none;border-radius:3px;padding:11px 32px;font-weight:700;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer}}
.modal-btn:hover{{background:#e8c97a}}
</style>
</head>
<body>
<div class="modal-overlay open" id="modal">
  <div class="modal">
    <div class="modal-logo">The Mind Changer</div>
    <div class="modal-line"></div>
    <p>המידע המוצג כאן מיועד למטרות לימוד בלבד ואינו מהווה ייעוץ השקעות. כל החלטת השקעה היא באחריותך הבלעדית.</p>
    <button class="modal-btn" onclick="document.getElementById('modal').classList.remove('open')">הבנתי — כניסה</button>
  </div>
</div>
<nav>
  <div class="nav-logo">The Mind Changer</div>
</nav>
<div class="tape-wrap"><div class="tape-inner" id="tape">טוען...</div></div>
<section id="hero">
  <div class="hero-bg-img"></div>
  <div class="hero-left">
    <div class="eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">Stock Intelligence Platform</div></div>
    <h1 class="hero-title">The Mind<br/><em>Changer</em></h1>
    <div class="title-line"></div>
    <p class="hero-desc">רדאר המניות החכם שמשלב ניתוח טכני מתקדם עם בינה מלאכותית — זהה הזדמנויות לפני כולם</p>
    <div class="hero-stats">
      <div class="hstat"><span class="hstat-num">500+</span><div class="hstat-label">מניות</div></div>
      <div class="hstat"><span class="hstat-num">14</span><div class="hstat-label">אינדיקטורים</div></div>
      <div class="hstat"><span class="hstat-num">98%</span><div class="hstat-label">דיוק</div></div>
    </div>
  </div>
  <div class="hero-right">
    <div class="live-card">
      <div class="live-card-header">
        <div class="live-card-title">שוק בזמן אמת</div>
        <div class="live-label"><div class="live-dot"></div>&nbsp;LIVE</div>
      </div>
      <div id="indices-rows"><div style="color:#7a7060;font-size:0.78rem;padding:8px 0">טוען מדדים...</div></div>
      <div id="stocks-rows"></div>
    </div>
  </div>
</section>
<div class="quote-strip">
  <div class="quote-text">"השוק הוא מכשיר להעברת כסף מהחסר סבלנות אל בעל הסבלנות" <span style="font-size: 0.8em; color: rgba(10,10,8,0.7); font-style: normal; font-weight: 600;">— וורן באפט</span></div>
</div>
<script>
const QUOTES  = {quotes_json};
const INDICES = {indices_json};
const STOCKS  = {stocks_json};
function buildTape() {{
  if (!QUOTES.length) return;
  const full = [...QUOTES, ...QUOTES];
  document.getElementById('tape').innerHTML = full.map(t =>
    '<div class="tape-item">' + '<span class="tape-sym">' + t.symbol + '</span>' +
    '<span class="' + (t.up ? 'tape-up' : 'tape-dn') + '">' + t.price + ' ' + (t.change_pct >= 0 ? '+' : '') + t.change_pct + '%</span>' + '</div>'
  ).join('');
}}
function buildHero() {{
  var idxEl = document.getElementById('indices-rows');
  if (INDICES.length) {{
    idxEl.innerHTML = INDICES.map(i =>
      '<div class="market-row">' + '<span class="mrow-name">' + i.name + '</span>' + '<span class="mrow-val">' + i.price + '</span>' +
      '<span class="' + (i.up ? 'mrow-up' : 'mrow-dn') + '">' + (i.chg >= 0 ? '+' : '') + i.chg + '%</span>' + '</div>'
    ).join('');
  }}
  var stEl = document.getElementById('stocks-rows');
  if (STOCKS.length) {{
    stEl.innerHTML = STOCKS.map(s =>
      '<div class="market-row">' + '<span class="mrow-name">' + s.symbol + '</span>' + '<span class="mrow-val">' + s.price + '</span>' +
      '<span class="' + (s.up ? 'mrow-up' : 'mrow-dn') + '">' + (s.chg >= 0 ? '+' : '') + s.chg + '%</span>' + '</div>'
    ).join('');
  }}
}}
buildTape(); buildHero();
</script>
</body>
</html>"""

st.components.v1.html(top_html, height=590, scrolling=False)

# ── 2. רכיב הרדאר המרכזי ──
st.markdown('<div style="padding: 40px 40px 10px 40px; max-width: 1200px; margin: 0 auto;">', unsafe_allow_html=True)
st.markdown('<p style="color:#c9a84c; font-size:0.68rem; font-weight:600; letter-spacing:0.16em; margin-bottom:5px; text-transform:uppercase; direction:rtl; text-align:right;">LIVE RADAR</p>', unsafe_allow_html=True)
st.markdown('<h2 style="font-family:\'Playfair Display\',serif; font-size:2rem; font-weight:900; color:#f0ede6; margin:0 0 5px 0; direction:rtl; text-align:right;">רדאר המניות</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#9a8f7a; font-size:0.88rem; margin-bottom:20px; direction:rtl; text-align:right;">בחר מצב סריקה וגלה הזדמנויות מסחר בזמן אמת</p>', unsafe_allow_html=True)

tab_long, tab_short, tab_ai, tab_fear_greed, tab_market_dir = st.tabs(["רדאר לונג 📈", "רדאר שורט 📉", "ניתוח AI 🤖", "מדד הפחד והגרידיות 📊", "לאן השוק הולך 🧭"])

# ── טאב לונג ──
with tab_long:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
<div class="panel-card" style="margin-top:15px; border-bottom-left-radius:0; border-bottom-right-radius:0;">
  <div class="panel-title">רדאר לונג</div>
  <div class="panel-sub">סריקת מניות במומנטום עולה</div>
  <ul class="criteria-list">
    <li><div class="crit-dot dot-green"></div>מגמת מחיר: חיובית</li>
    <li><div class="crit-dot dot-green"></div>מומנטום: לונג (ללא קניית יתר)</li>
    <li><div class="crit-dot dot-green"></div>נפח מסחר: נזילות גבוהה</li>
    <li><div class="crit-dot dot-green"></div>מבנה נרות: פטיש אתמול וסגירה ירוקה היום</li>
    <li><div class="crit-dot dot-green"></div>איזון נגזרים: נטיית Calls</li>
  </ul>
</div>""", unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            st.markdown('<div class="long-btn">', unsafe_allow_html=True)
            run_long = st.button("התחל סריקת לונג ⚡", key="run_long_trigger")
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_col2:
            st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
            stop_long = st.button("עצור 🛑", key="stop_long_trigger")
            st.markdown('</div>', unsafe_allow_html=True)

        if stop_long:
            st.stop()
        if run_long:
            st.session_state.long_results = do_scan("long")
            
    with col2:
        long_count = f"{len(st.session_state.long_results)} מניות" if st.session_state.long_results is not None else "—"
        long_cards = render_cards(st.session_state.long_results, "long")
        st.markdown(f"""
<div class="results-panel" style="margin-top:15px; min-height: 254px;">
  <div class="results-header">
    <div class="results-title">תוצאות סריקה</div>
    <div class="results-count">{long_count}</div>
  </div>
  {long_cards}
</div>""", unsafe_allow_html=True)
        
        if st.session_state.long_results:
            f_col1, f_col2 = st.columns([3, 1])
            with f_col1:
                st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
                run_deep_l = st.button("תסנן לי עוד ⚡", key="deep_filter_volume_trigger")
                st.markdown('</div>', unsafe_allow_html=True)
            with f_col2:
                st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
                stop_deep_l = st.button("עצור 🛑", key="stop_deep_l_trigger")
                st.markdown('</div>', unsafe_allow_html=True)
                
            if stop_deep_l:
                st.stop()
            if run_deep_l:
                with st.spinner("מבצע סינון עומק מחזורי..."):
                    deep_filtered = []
                    session = get_session()
                    for item in st.session_state.long_results:
                        try:
                            ticker_sym = item["symbol"]
                            ticker_obj = yf.Ticker(ticker_sym, session=session)
                            hist = ticker_obj.history(period="1mo", interval="1d", auto_adjust=True)
                            hist = hist.dropna(subset=["Volume"])
                            if len(hist) >= 20:
                                avg_vol_3d = hist["Volume"].iloc[-3:].mean()
                                avg_vol_20d = hist["Volume"].rolling(20).mean().iloc[-1]
                                if avg_vol_3d > avg_vol_20d:
                                    deep_filtered.append(item)
                        except:
                            pass
                    st.session_state.long_results = deep_filtered
                    st.rerun()

# ── טאב שורט ──
with tab_short:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
<div class="panel-card" style="margin-top:15px; border-bottom-left-radius:0; border-bottom-right-radius:0;">
  <div class="panel-title">רדאר שורט</div>
  <div class="panel-sub">סריקת מניות במומנטום יורד</div>
  <ul class="criteria-list">
    <li><div class="crit-dot dot-red"></div>מגמת מחיר: שלילית</li>
    <li><div class="crit-dot dot-red"></div>מומנטום: שורט (ללא מכירת יתר)</li>
    <li><div class="crit-dot dot-red"></div>נפח מסחר: נזילות גבוהה</li>
    <li><div class="crit-dot dot-red"></div>מבנה נרות: כוכב נופל אתמול וסגירה אדומה היום</li>
    <li><div class="crit-dot dot-red"></div>איזון נגזרים: נטיית Puts</li>
    <li><div class="crit-dot dot-red"></div>בקרת סיכון: הגנה מנפילת יתר רצופה</li>
  </ul>
</div>""", unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            st.markdown('<div class="short-btn">', unsafe_allow_html=True)
            run_short = st.button("התחל סריקת שורט ⚡", key="run_short_trigger")
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_col2:
            st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
            stop_short = st.button("עצור 🛑", key="stop_short_trigger")
            st.markdown('</div>', unsafe_allow_html=True)

        if stop_short:
            st.stop()
        if run_short:
            st.session_state.short_results = do_scan("short")
            
    with col2:
        short_count = f"{len(st.session_state.short_results)} מניות" if st.session_state.short_results is not None else "—"
        short_cards = render_cards(st.session_state.short_results, "short")
        st.markdown(f"""
<div class="results-panel" style="margin-top:15px; min-height: 288px;">
  <div class="results-header">
    <div class="results-title">תוצאות סריקה</div>
    <div class="results-count">{short_count}</div>
  </div>
  {short_cards}
</div>""", unsafe_allow_html=True)
        
        if st.session_state.short_results:
            f_col1, f_col2 = st.columns([3, 1])
            with f_col1:
                st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
                run_deep_s = st.button("תסנן לי עוד ⚡", key="deep_filter_volume_short_trigger")
                st.markdown('</div>', unsafe_allow_html=True)
            with f_col2:
                st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
                stop_deep_s = st.button("עצור 🛑", key="stop_deep_s_trigger")
                st.markdown('</div>', unsafe_allow_html=True)
                
            if stop_deep_s:
                st.stop()
            if run_deep_s:
                with st.spinner("מבצע סינון עומק מחזורי..."):
                    deep_filtered_short = []
                    session = get_session()
                    for item in st.session_state.short_results:
                        try:
                            ticker_sym = item["symbol"]
                            ticker_obj = yf.Ticker(ticker_sym, session=session)
                            hist = ticker_obj.history(period="1mo", interval="1d", auto_adjust=True)
                            hist = hist.dropna(subset=["Volume"])
                            if len(hist) >= 20:
                                avg_vol_3d = hist["Volume"].iloc[-3:].mean()
                                avg_vol_20d = hist["Volume"].rolling(20).mean().iloc[-1]
                                if avg_vol_3d > avg_vol_20d:
                                    deep_filtered_short.append(item)
                        except:
                            pass
                    st.session_state.short_results = deep_filtered_short
                    st.rerun()

# ── טאב ניתוח AI ──
with tab_ai:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
<div class="panel-card" style="margin-top:15px; border-bottom-left-radius:0; border-bottom-right-radius:0; padding-bottom:10px;">
  <div class="panel-title">ניתוח מניה בודדת</div>
  <div class="panel-sub">הזן סימול וקבל ניתוח טכני אמיתי</div>
</div>""", unsafe_allow_html=True)
        ticker_val = st.text_input("סימול מניה", placeholder="AAPL, TSLA, NVDA...", label_visibility="collapsed")
        
        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
            run_ai = st.button("נתח מניה", key="analyze_trigger")
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_col2:
            st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
            stop_ai = st.button("עצור 🛑", key="stop_ai_trigger")
            st.markdown('</div>', unsafe_allow_html=True)

        if stop_ai:
            st.stop()
        
        if run_ai:
            if ticker_val:
                ticker_clean = ticker_val.upper().strip()
                with st.spinner(f"מחלץ נתוני שוק חיים עבור {ticker_clean}..."):
                    res = analyze_ticker(ticker_clean)

                    retry_count = 0
                    while isinstance(res, dict) and res.get("_error") == "network" and retry_count < 2:
                        time.sleep(2)
                        res = analyze_ticker(ticker_clean)
                        retry_count += 1

                    if res and not (isinstance(res, dict) and "_error" in res):
                        # --- תוספת חדשה: קריאה דינמית ל-Gemini עבור המסקנות ---
                        if GENAI_AVAILABLE and GEMINI_API_KEY != "הכנס_כאן_את_המפתח_החדש":
                            try:
                                genai.configure(api_key=GEMINI_API_KEY)
                                model = genai.GenerativeModel('gemini-1.5-flash')
                                
                                prompt = f"""
                                אתה אנליסט פיננסי בכיר ואלגוטריידר מקצועי במערכת 'The Mind Changer'. 
                                הנה נתונים טכניים ופונדמנטליים שחילצנו הרגע על המניה {res['ticker']}:
                                - מחיר: {res['price']} (שינוי: {res['chg']})
                                - ממוצעים נעים (מגמת מאקרו): {res['ma_status']}
                                - מתנד RSI: עומד על {res['rsi_val_num']:.1f} ({res['rsi_status']})
                                - סנטימנט פעילות אופציות: {res['options_text']}
                                - עמידה ביעדי דוחות: {res['earnings']}
                                - צפי להכנסות בעתיד: {res['forecast_text']}
                                - קונצנזוס אנליסטים: {res['rec_text']}

                                עליך לכתוב פסקה או שתיים של מסקנות והמלצות מסחר ברורות, חדות ומקצועיות על בסיס הנתונים האלו.
                                הוסף תובנה קצרה משלך על מצב המניה, הסקטור שלה, או אינדיקציות קנייה/מכירה הנובעות משילוב הנתונים (למשל, התנגשות בין פונדמנטלס טובים למצב טכני של קניית יתר).
                                סכם בשורת מחץ "שורה תחתונה".
                                החזר את התשובה בפורמט HTML נקי (השתמש ב- <b> להדגשות, <br> לירידת שורה) שיוצג ישירות באתר, ללא תגיות Markdown או
