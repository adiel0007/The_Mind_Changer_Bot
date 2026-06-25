<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>The Mind Changer | Stock Radar</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --gold:#c9a84c;--gold2:#a8873a;--gold-light:#e8c97a;--gold-pale:rgba(201,168,76,0.08);
  --green:#16a34a;--red:#dc2626;
  --bg:#0a0a08;--bg2:#0f0f0c;--surface:#141410;--surface2:#1a1a15;
  --border:rgba(201,168,76,0.12);--border2:rgba(255,255,255,0.06);
  --text:#f0ede6;--muted:#7a7060;--muted2:#9a8f7a;
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;overflow-x:hidden;direction:rtl}

/* ── NAV ── */
nav{
  position:fixed;top:0;left:0;right:0;z-index:100;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 56px;height:68px;
  background:rgba(10,10,8,0.92);
  backdrop-filter:blur(24px);
  border-bottom:1px solid var(--border);
}
.nav-logo{
  font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:700;
  color:var(--gold);letter-spacing:0.06em;
}
.nav-links{display:flex;gap:36px;list-style:none}
.nav-links a{color:var(--muted2);font-size:0.82rem;font-weight:500;text-decoration:none;letter-spacing:0.05em;transition:color .2s;cursor:pointer;text-transform:uppercase}
.nav-links a:hover,.nav-links a.active{color:var(--gold)}
.nav-cta{
  background:transparent;border:1px solid var(--gold);
  color:var(--gold);font-weight:600;font-size:0.8rem;letter-spacing:0.08em;
  padding:9px 24px;border-radius:3px;cursor:pointer;text-transform:uppercase;
  transition:background .2s,color .2s;
}
.nav-cta:hover{background:var(--gold);color:#0a0a08}

/* ── TICKER TAPE ── */
.tape-wrap{
  position:fixed;top:68px;left:0;right:0;z-index:99;
  background:var(--surface);border-bottom:1px solid var(--border);
  overflow:hidden;height:34px;display:flex;align-items:center;
}
.tape-inner{display:flex;gap:0;animation:tape 40s linear infinite;white-space:nowrap;width:max-content}
@keyframes tape{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.tape-item{
  font-size:0.72rem;font-weight:600;letter-spacing:0.06em;
  padding:0 28px;border-right:1px solid var(--border);
  display:flex;align-items:center;gap:10px;height:34px;
}
.tape-sym{color:var(--muted2)}
.tape-up{color:var(--green)}.tape-dn{color:var(--red)}
.tape-sep{color:var(--muted);font-size:0.65rem}

/* ── HERO ── */
#hero{
  min-height:100vh;display:grid;grid-template-columns:1fr 1fr;
  align-items:center;padding:140px 56px 80px;gap:80px;
  position:relative;overflow:hidden;
}
.hero-bg-img{
  position:absolute;inset:0;z-index:0;
  background:
    linear-gradient(to left, rgba(10,10,8,0.2) 0%, rgba(10,10,8,0.75) 45%, rgba(10,10,8,1) 75%),
    url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat;
}
.hero-left{position:relative;z-index:1}
.hero-eyebrow{
  display:flex;align-items:center;gap:10px;margin-bottom:24px;
}
.eyebrow-line{width:32px;height:1px;background:var(--gold)}
.eyebrow-text{font-size:0.72rem;font-weight:600;letter-spacing:0.16em;color:var(--gold);text-transform:uppercase}
.hero-title{
  font-family:'Playfair Display',serif;
  font-size:clamp(3rem,5vw,5rem);font-weight:900;
  line-height:1.08;color:var(--text);margin-bottom:8px;
}
.hero-title em{font-style:italic;color:var(--gold)}
.hero-subtitle-line{
  width:48px;height:2px;background:var(--gold);margin:24px 0;
}
.hero-desc{
  font-size:1.05rem;color:var(--muted2);line-height:1.75;
  max-width:440px;margin-bottom:40px;font-weight:400;
}
.hero-btns{display:flex;gap:12px;flex-wrap:wrap}
.btn-gold{
  background:var(--gold);color:#0a0a08;font-weight:700;font-size:0.85rem;
  letter-spacing:0.08em;padding:14px 36px;border:none;border-radius:3px;
  cursor:pointer;text-transform:uppercase;transition:background .2s,transform .15s;
}
.btn-gold:hover{background:var(--gold-light);transform:translateY(-1px)}
.btn-outline{
  background:transparent;color:var(--text);font-weight:600;font-size:0.85rem;
  letter-spacing:0.06em;padding:14px 32px;border:1px solid var(--border2);
  border-radius:3px;cursor:pointer;text-transform:uppercase;transition:border-color .2s;
}
.btn-outline:hover{border-color:rgba(201,168,76,0.35)}

/* HERO RIGHT — LIVE CARD */
.hero-right{position:relative;z-index:1}
.live-card{
  background:var(--surface);border:1px solid var(--border);border-radius:6px;
  padding:28px;
}
.live-card-header{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border2);
}
.live-card-title{font-family:'Playfair Display',serif;font-size:1rem;color:var(--text);font-weight:700}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:blink 1.4s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.live-label{font-size:0.7rem;font-weight:600;color:var(--green);letter-spacing:0.08em;display:flex;align-items:center;gap:6px}
.market-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04)}
.market-row:last-child{border-bottom:none}
.mrow-name{font-size:0.82rem;font-weight:600;color:var(--muted2)}
.mrow-val{font-size:0.88rem;font-weight:700;color:var(--text)}
.mrow-chg-up{font-size:0.78rem;font-weight:600;color:var(--green);background:rgba(22,163,74,0.1);padding:2px 8px;border-radius:2px}
.mrow-chg-dn{font-size:0.78rem;font-weight:600;color:var(--red);background:rgba(220,38,38,0.1);padding:2px 8px;border-radius:2px}

/* HERO STATS */
.hero-stats{display:flex;gap:0;margin-top:40px;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
.hstat{flex:1;padding:20px 0;text-align:center;border-right:1px solid var(--border)}
.hstat:last-child{border-right:none}
.hstat-num{font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:var(--gold);display:block}
.hstat-label{font-size:0.7rem;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase;margin-top:4px}

/* ── SECTION COMMONS ── */
section{position:relative;z-index:1}
.section-wrap{padding:100px 56px;max-width:1200px;margin:0 auto}
.section-eyebrow{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.section-title{font-family:'Playfair Display',serif;font-size:clamp(1.8rem,3vw,2.8rem);font-weight:900;color:var(--text);margin-bottom:12px;line-height:1.15}
.section-desc{color:var(--muted2);font-size:0.95rem;max-width:500px;line-height:1.7;margin-bottom:56px}

/* ── TAB BAR ── */
.tab-bar{
  display:flex;gap:0;border-bottom:1px solid var(--border);margin-bottom:48px;
}
.tab-btn{
  background:transparent;border:none;border-bottom:2px solid transparent;
  padding:14px 32px;font-size:0.82rem;font-weight:600;letter-spacing:0.08em;
  color:var(--muted);cursor:pointer;text-transform:uppercase;
  transition:color .2s,border-color .2s;margin-bottom:-1px;
  font-family:'Inter',sans-serif;
}
.tab-btn:hover{color:var(--muted2)}
.tab-btn.active{color:var(--gold);border-bottom-color:var(--gold)}

.tab-panel{display:none;animation:fadeIn .3s ease}
.tab-panel.active{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ── RADAR PANEL ── */
.radar-layout{display:grid;grid-template-columns:320px 1fr;gap:32px}
@media(max-width:800px){.radar-layout{grid-template-columns:1fr}}

.panel-card{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:28px}
.panel-title{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--text);margin-bottom:6px}
.panel-sub{font-size:0.8rem;color:var(--muted);line-height:1.6;margin-bottom:24px}

.criteria-list{list-style:none;margin-bottom:24px}
.criteria-list li{
  font-size:0.8rem;color:var(--muted2);padding:8px 0;
  border-bottom:1px solid rgba(255,255,255,0.04);
  display:flex;align-items:center;gap:8px;
}
.criteria-list li:last-child{border-bottom:none}
.crit-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.dot-green{background:var(--green)}.dot-red{background:var(--red)}.dot-gold{background:var(--gold)}

.scan-btn{
  width:100%;padding:13px;border-radius:3px;
  font-family:'Inter',sans-serif;font-size:0.82rem;font-weight:700;
  letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;border:none;
  transition:opacity .2s,transform .15s;
}
.scan-btn:hover{opacity:.88;transform:translateY(-1px)}
.scan-btn:active{transform:translateY(0)}
.scan-green{background:var(--green);color:#fff}
.scan-red{background:var(--red);color:#fff}
.scan-gold{background:var(--gold);color:#0a0a08}

.progress-wrap{margin-top:16px;display:none}
.progress-status{font-size:0.75rem;color:var(--muted);margin-bottom:6px}
.progress-bg{background:rgba(255,255,255,0.06);border-radius:1px;height:2px}
.progress-fill{height:100%;border-radius:1px;width:0%;transition:width .25s ease}
.fill-g{background:var(--green)}.fill-r{background:var(--red)}.fill-gold{background:var(--gold)}

/* RESULTS PANEL */
.results-panel{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:28px}
.results-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border2)}
.results-title{font-size:0.72rem;font-weight:600;letter-spacing:0.12em;color:var(--muted);text-transform:uppercase}
.results-count{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--gold)}

.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px}
.stock-card{
  border-radius:3px;padding:16px 12px;text-align:center;cursor:pointer;
  transition:all .18s;border:1px solid;
}
.card-long{background:rgba(22,163,74,0.06);border-color:rgba(22,163,74,0.18)}
.card-long:hover{background:rgba(22,163,74,0.12);border-color:rgba(22,163,74,0.35);transform:translateY(-2px)}
.card-short{background:rgba(220,38,38,0.06);border-color:rgba(220,38,38,0.18)}
.card-short:hover{background:rgba(220,38,38,0.12);border-color:rgba(220,38,38,0.35);transform:translateY(-2px)}
.card-sym{font-size:0.88rem;font-weight:700;color:var(--text);letter-spacing:0.06em}
.card-price-g{font-size:0.8rem;font-weight:600;color:var(--green);margin-top:5px}
.card-price-r{font-size:0.8rem;font-weight:600;color:var(--red);margin-top:5px}
.card-chg{font-size:0.7rem;color:var(--muted);margin-top:2px}

.empty-msg{color:var(--muted);font-size:0.85rem;text-align:center;padding:48px 0}

/* ── AI SECTION ── */
.ai-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}
@media(max-width:700px){.ai-grid{grid-template-columns:1fr}}

.ai-input-group{margin-bottom:14px}
.input-label{font-size:0.7rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.ai-input{
  width:100%;background:rgba(255,255,255,0.03);
  border:1px solid var(--border2);border-radius:3px;
  color:var(--text);font-family:'Inter',sans-serif;
  font-size:0.9rem;font-weight:400;padding:11px 14px;
  outline:none;direction:rtl;transition:border .2s;
}
.ai-input:focus{border-color:rgba(201,168,76,0.4)}
.ai-input::placeholder{color:var(--muted)}

/* ANALYSIS RESULT */
.analysis-result{margin-top:18px}
.result-card{background:rgba(255,255,255,0.02);border:1px solid var(--border2);border-radius:3px}
.result-card-header{
  padding:14px 18px;border-bottom:1px solid var(--border2);
  font-family:'Playfair Display',serif;font-size:0.92rem;font-weight:700;color:var(--text);
  display:flex;align-items:center;justify-content:space-between;
}
.result-tag{font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:3px 10px;border-radius:2px}
.tag-green{background:rgba(22,163,74,0.12);color:var(--green)}
.tag-red{background:rgba(220,38,38,0.12);color:var(--red)}
.metric-row{display:flex;justify-content:space-between;align-items:center;padding:10px 18px;border-bottom:1px solid rgba(255,255,255,0.03)}
.metric-row:last-child{border-bottom:none}
.metric-label{font-size:0.76rem;color:var(--muted);font-weight:500}
.metric-value{font-size:0.78rem;color:var(--muted2);font-weight:600;text-align:left}

.ai-response-box{
  margin-top:14px;padding:18px;
  background:var(--gold-pale);border:1px solid var(--border);border-radius:3px;
  border-right:3px solid var(--gold);
}
.ai-response-label{font-size:0.65rem;font-weight:700;letter-spacing:0.12em;color:var(--gold);text-transform:uppercase;margin-bottom:8px}
.ai-response-text{font-size:0.85rem;color:var(--muted2);line-height:1.75;direction:rtl;text-align:right}

/* SPINNER */
.spinner{display:none;width:16px;height:16px;border:1.5px solid rgba(201,168,76,0.2);border-top-color:var(--gold);border-radius:50%;animation:spin .6s linear infinite;margin:16px auto 0}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── FEATURES ── */
#features{background:var(--bg2);border-top:1px solid var(--border)}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1px;background:var(--border);border:1px solid var(--border)}
.feat-card{background:var(--bg2);padding:36px 32px;transition:background .2s}
.feat-card:hover{background:var(--surface)}
.feat-icon{font-size:1.5rem;margin-bottom:18px;display:block}
.feat-title{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px}
.feat-desc{font-size:0.82rem;color:var(--muted);line-height:1.65}

/* ── HOW IT WORKS ── */
#how{border-top:1px solid var(--border)}
.steps-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:1px solid var(--border);background:var(--border)}
@media(max-width:700px){.steps-grid{grid-template-columns:1fr}}
.step-card{background:var(--surface);padding:40px 32px}
.step-num{font-family:'Playfair Display',serif;font-size:3rem;font-weight:900;color:var(--border);line-height:1;margin-bottom:20px}
.step-title{font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:var(--text);margin-bottom:10px}
.step-desc{font-size:0.82rem;color:var(--muted);line-height:1.65}

/* ── QUOTE STRIP ── */
.quote-strip{
  background:var(--gold);padding:32px 56px;text-align:center;
  direction:rtl;
}
.quote-text{
  font-family:'Playfair Display',serif;font-size:1.3rem;font-style:italic;
  font-weight:700;color:#0a0a08;line-height:1.5;
}
.quote-src{font-size:0.75rem;font-weight:600;letter-spacing:0.1em;color:rgba(10,10,8,0.55);margin-top:10px;text-transform:uppercase}

/* ── FOOTER ── */
footer{
  background:var(--bg2);border-top:1px solid var(--border);
  padding:48px 56px;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:24px;
}
.footer-logo{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--gold);margin-bottom:8px}
.footer-copy{font-size:0.75rem;color:var(--muted)}
.footer-links{display:flex;gap:28px}
.footer-links a{font-size:0.75rem;color:var(--muted);text-decoration:none;letter-spacing:0.06em;text-transform:uppercase;transition:color .2s;cursor:pointer}
.footer-links a:hover{color:var(--gold)}

/* ── MODAL ── */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:200;display:none;align-items:center;justify-content:center;backdrop-filter:blur(12px)}
.modal-overlay.open{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:48px;max-width:460px;width:90%;text-align:center;animation:fadeIn .3s ease}
.modal-logo{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:900;color:var(--gold);margin-bottom:6px}
.modal-line{width:40px;height:1px;background:var(--gold);margin:0 auto 20px}
.modal p{color:var(--muted2);font-size:0.88rem;line-height:1.7;margin-bottom:28px}
.modal-btn{background:var(--gold);color:#0a0a08;border:none;border-radius:3px;padding:12px 36px;font-weight:700;font-size:0.82rem;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;transition:background .2s}
.modal-btn:hover{background:var(--gold-light)}
</style>
</head>
<body>

<!-- MODAL -->
<div class="modal-overlay open" id="modal">
  <div class="modal">
    <div class="modal-logo">The Mind Changer</div>
    <div class="modal-line"></div>
    <p>המידע המוצג באתר זה מיועד למטרות לימוד ומידע בלבד ואינו מהווה ייעוץ השקעות, המלצה לקנייה או מכירה של ניירות ערך. כל החלטת השקעה היא באחריותך הבלעדית.</p>
    <button class="modal-btn" onclick="document.getElementById('modal').classList.remove('open')">הבנתי — כניסה לאתר</button>
  </div>
</div>

<!-- NAV -->
<nav>
  <div class="nav-logo">The Mind Changer</div>
  <ul class="nav-links">
    <li><a onclick="gotoSection('hero')" class="active">בית</a></li>
    <li><a onclick="gotoSection('radar')">רדאר</a></li>
    <li><a onclick="gotoSection('features')">יתרונות</a></li>
    <li><a onclick="gotoSection('how')">תהליך</a></li>
  </ul>
  <button class="nav-cta" onclick="gotoSection('radar')">התחל לסרוק</button>
</nav>

<!-- TICKER TAPE -->
<div class="tape-wrap">
  <div class="tape-inner" id="tape"></div>
</div>

<!-- HERO -->
<section id="hero">
  <div class="hero-bg-img"></div>
  <div class="hero-left">
    <div class="hero-eyebrow">
      <div class="eyebrow-line"></div>
      <div class="eyebrow-text">Stock Intelligence Platform</div>
    </div>
    <h1 class="hero-title">The Mind<br/><em>Changer</em></h1>
    <div class="hero-subtitle-line"></div>
    <p class="hero-desc">רדאר המניות החכם שמשלב ניתוח טכני מתקדם עם בינה מלאכותית — זהה הזדמנויות לונג ושורט לפני כולם</p>
    <div class="hero-btns">
      <button class="btn-gold" onclick="gotoSection('radar')">התחל לסרוק עכשיו</button>
      <button class="btn-outline" onclick="gotoSection('how')">איך זה עובד</button>
    </div>
    <div class="hero-stats">
      <div class="hstat"><span class="hstat-num" data-target="500">0</span><div class="hstat-label">מניות</div></div>
      <div class="hstat"><span class="hstat-num" data-target="14">0</span><div class="hstat-label">אינדיקטורים</div></div>
      <div class="hstat"><span class="hstat-num" data-target="98">0</span><div class="hstat-label">% דיוק</div></div>
    </div>
  </div>
  <div class="hero-right">
    <div class="live-card">
      <div class="live-card-header">
        <div class="live-card-title">שוק בזמן אמת</div>
        <div class="live-label"><div class="live-dot"></div>LIVE</div>
      </div>
      <div class="market-row"><span class="mrow-name">S&P 500</span><span class="mrow-val">5,428.14</span><span class="mrow-chg-up">+0.84%</span></div>
      <div class="market-row"><span class="mrow-name">NASDAQ</span><span class="mrow-val">17,301.71</span><span class="mrow-chg-up">+1.12%</span></div>
      <div class="market-row"><span class="mrow-name">DOW JONES</span><span class="mrow-val">38,852.27</span><span class="mrow-chg-dn">-0.23%</span></div>
      <div class="market-row"><span class="mrow-name">NVDA</span><span class="mrow-val">875.30</span><span class="mrow-chg-up">+3.1%</span></div>
      <div class="market-row"><span class="mrow-name">TSLA</span><span class="mrow-val">248.17</span><span class="mrow-chg-dn">-0.8%</span></div>
      <div class="market-row"><span class="mrow-name">AAPL</span><span class="mrow-val">189.42</span><span class="mrow-chg-up">+1.2%</span></div>
    </div>
  </div>
</section>

<!-- QUOTE -->
<div class="quote-strip">
  <div class="quote-text">"השוק הוא מכשיר להעברת כסף מהחסר סבלנות אל בעל הסבלנות"</div>
  <div class="quote-src">— Warren Buffett</div>
</div>

<!-- RADAR -->
<section id="radar">
  <div class="section-wrap">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">Live Radar</div></div>
    <h2 class="section-title">רדאר המניות</h2>
    <p class="section-desc">בחר מצב סריקה וגלה הזדמנויות מסחר בזמן אמת לפי קריטריונים טכניים מדויקים</p>

    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('long')">📈 רדאר לונג</button>
      <button class="tab-btn" onclick="switchTab('short')">📉 רדאר שורט</button>
      <button class="tab-btn" onclick="switchTab('ai')">🤖 ניתוח AI</button>
    </div>

    <!-- LONG -->
    <div class="tab-panel active" id="tab-long">
      <div class="radar-layout">
        <div class="panel-card">
          <div class="panel-title">רדאר לונג</div>
          <div class="panel-sub">קריטריונים לזיהוי מניות עם מומנטום עולה</div>
          <ul class="criteria-list">
            <li><div class="crit-dot dot-green"></div>מחיר מעל ממוצע נע 9</li>
            <li><div class="crit-dot dot-green"></div>RSI מתחת ל-70</li>
            <li><div class="crit-dot dot-green"></div>נפח מסחר מעל מיליון</li>
            <li><div class="crit-dot dot-green"></div>לא מעל כל 3 הממוצעים</li>
            <li><div class="crit-dot dot-green"></div>יומיים ירוקים רצופים</li>
            <li><div class="crit-dot dot-green"></div>סגירה גבוהה מאתמול</li>
          </ul>
          <button class="scan-btn scan-green" onclick="simulateScan('long')">התחל סריקת לונג ⚡</button>
          <div class="progress-wrap" id="prog-long">
            <div class="progress-status" id="pstatus-long">מכין ערוץ נתונים...</div>
            <div class="progress-bg"><div class="progress-fill fill-g" id="pbar-long"></div></div>
          </div>
        </div>
        <div class="results-panel">
          <div class="results-header">
            <div class="results-title">תוצאות סריקה</div>
            <div class="results-count" id="count-long">—</div>
          </div>
          <div id="res-long"><div class="empty-msg">הפעל את הרדאר כדי לראות תוצאות</div></div>
        </div>
      </div>
    </div>

    <!-- SHORT -->
    <div class="tab-panel" id="tab-short">
      <div class="radar-layout">
        <div class="panel-card">
          <div class="panel-title">רדאר שורט</div>
          <div class="panel-sub">קריטריונים לזיהוי מניות עם מומנטום יורד</div>
          <ul class="criteria-list">
            <li><div class="crit-dot dot-red"></div>מחיר מתחת לממוצע נע 9</li>
            <li><div class="crit-dot dot-red"></div>RSI מעל 30</li>
            <li><div class="crit-dot dot-red"></div>נפח מסחר מעל מיליון</li>
            <li><div class="crit-dot dot-red"></div>יומיים אדומים רצופים</li>
            <li><div class="crit-dot dot-red"></div>סגירה נמוכה מאתמול</li>
            <li><div class="crit-dot dot-red"></div>Puts חזקים מ-Calls</li>
          </ul>
          <button class="scan-btn scan-red" onclick="simulateScan('short')">התחל סריקת שורט ⚡</button>
          <div class="progress-wrap" id="prog-short">
            <div class="progress-status" id="pstatus-short">מכין ערוץ נתונים...</div>
            <div class="progress-bg"><div class="progress-fill fill-r" id="pbar-short"></div></div>
          </div>
        </div>
        <div class="results-panel">
          <div class="results-header">
            <div class="results-title">תוצאות סריקה</div>
            <div class="results-count" id="count-short">—</div>
          </div>
          <div id="res-short"><div class="empty-msg">הפעל את הרדאר כדי לראות תוצאות</div></div>
        </div>
      </div>
    </div>

    <!-- AI -->
    <div class="tab-panel" id="tab-ai">
      <div class="ai-grid">
        <div class="panel-card">
          <div class="panel-title">ניתוח מניה בודדת</div>
          <div class="panel-sub">הזן סימול וקבל ניתוח טכני מלא עם חוות דעת AI</div>
          <div class="ai-input-group">
            <div class="input-label">סימול מניה</div>
            <input class="ai-input" id="ticker-input" placeholder="AAPL, TSLA, NVDA..."/>
          </div>
          <button class="scan-btn scan-gold" onclick="analyzeStock()">נתח מניה</button>
          <div class="spinner" id="sp-analyze"></div>
          <div id="res-analyze"></div>
        </div>
        <div class="panel-card">
          <div class="panel-title">אנליסט AI</div>
          <div class="panel-sub">שאל כל שאלה פיננסית וקבל תשובה מקצועית בעברית</div>
          <div class="ai-input-group">
            <div class="input-label">שאלה פיננסית</div>
            <input class="ai-input" id="ai-q" placeholder="מה זה RSI? איך לזהות פריצה?"/>
          </div>
          <button class="scan-btn scan-gold" onclick="askAI()">שאל את האנליסט</button>
          <div class="spinner" id="sp-ai"></div>
          <div id="res-ai"></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- FEATURES -->
<section id="features">
  <div class="section-wrap">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">יתרונות</div></div>
    <h2 class="section-title">למה The Mind Changer?</h2>
    <p class="section-desc">כל מה שצריך לקבל החלטות מסחר חכמות יותר, במקום אחד</p>
    <div class="features-grid">
      <div class="feat-card"><span class="feat-icon">⚡</span><div class="feat-title">סריקה בזמן אמת</div><div class="feat-desc">מנתח מאות מניות בשניות לפי קריטריונים טכניים מוכחים</div></div>
      <div class="feat-card"><span class="feat-icon">📈</span><div class="feat-title">רדאר לונג חכם</div><div class="feat-desc">מזהה מניות עם מומנטום עולה — RSI, ממוצעים נעים ויומיים ירוקים</div></div>
      <div class="feat-card"><span class="feat-icon">📉</span><div class="feat-title">רדאר שורט מתקדם</div><div class="feat-desc">מאתר מניות חלשות עם Puts חזקים ומגמה יורדת ברורה</div></div>
      <div class="feat-card"><span class="feat-icon">🤖</span><div class="feat-title">אנליסט AI — Gemini</div><div class="feat-desc">ניתוח עמוק לכל מניה ומענה לשאלות פיננסיות בעברית</div></div>
      <div class="feat-card"><span class="feat-icon">📊</span><div class="feat-title">14 אינדיקטורים</div><div class="feat-desc">RSI, MA9/100/200, ניתוח אופציות, המלצות אנליסטים ועוד</div></div>
      <div class="feat-card"><span class="feat-icon">🔒</span><div class="feat-title">נתונים מאובטחים</div><div class="feat-desc">מערכת חכמה לעקיפת Rate Limits עם ניהול בקשות מתקדם</div></div>
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section id="how">
  <div class="section-wrap">
    <div class="section-eyebrow"><div class="eyebrow-line"></div><div class="eyebrow-text">תהליך</div></div>
    <h2 class="section-title">איך זה עובד?</h2>
    <p class="section-desc">שלושה שלבים פשוטים לתוצאות מסחר חכמות</p>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-num">01</div>
        <div class="step-title">בחר מצב סריקה</div>
        <div class="step-desc">בחר בין רדאר לונג, שורט, או ניתוח מניה בודדת. המערכת מתחילה לאסוף נתוני שוק בזמן אמת.</div>
      </div>
      <div class="step-card">
        <div class="step-num">02</div>
        <div class="step-title">סריקה אלגוריתמית</div>
        <div class="step-desc">האלגוריתם בודק RSI, ממוצעים נעים, נפח מסחר, נרות אחרונים ושוק האופציות עבור כל מניה.</div>
      </div>
      <div class="step-card">
        <div class="step-num">03</div>
        <div class="step-title">קבל תוצאות + AI</div>
        <div class="step-desc">המניות שעוברות את הקריטריונים מוצגות. תנתח לעומק עם אנליסט ה-AI המובנה.</div>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div>
    <div class="footer-logo">The Mind Changer</div>
    <div class="footer-copy">© 2025 — למטרות מידע בלבד. אינו ייעוץ השקעות.</div>
  </div>
  <div class="footer-links">
    <a onclick="gotoSection('radar')">רדאר</a>
    <a onclick="gotoSection('features')">יתרונות</a>
    <a onclick="gotoSection('how')">תהליך</a>
  </div>
</footer>

<script>
// TICKER TAPE
const tickers=[
  {s:'AAPL',p:'189.42',c:'+1.24%',u:true},{s:'TSLA',p:'248.17',c:'-0.83%',u:false},
  {s:'NVDA',p:'875.30',c:'+3.14%',u:true},{s:'META',p:'512.44',c:'+0.61%',u:true},
  {s:'AMZN',p:'192.80',c:'-1.31%',u:false},{s:'MSFT',p:'430.15',c:'+0.94%',u:true},
  {s:'NFLX',p:'685.22',c:'+2.40%',u:true},{s:'GOOG',p:'178.55',c:'-0.44%',u:false},
  {s:'AMD',p:'164.30',c:'+1.71%',u:true},{s:'COIN',p:'234.88',c:'-2.10%',u:false},
  {s:'SPY',p:'542.81',c:'+0.84%',u:true},{s:'QQQ',p:'461.20',c:'+1.12%',u:true},
];
const tape=document.getElementById('tape');
const full=[...tickers,...tickers];
tape.innerHTML=full.map(t=>`<div class="tape-item"><span class="tape-sym">${t.s}</span><span class="${t.u?'tape-up':'tape-dn'}">${t.p} &nbsp;${t.c}</span><span class="tape-sep">|</span></div>`).join('');

// SCROLL
function gotoSection(id){document.getElementById(id).scrollIntoView({behavior:'smooth'})}

// COUNTERS
function animateCounters(){
  document.querySelectorAll('[data-target]').forEach(el=>{
    const target=+el.dataset.target;let cur=0,step=target/55;
    const iv=setInterval(()=>{cur+=step;if(cur>=target){cur=target;clearInterval(iv)}el.textContent=Math.floor(cur);},16);
  });
}
setTimeout(animateCounters,600);

// NAV ACTIVE
window.addEventListener('scroll',()=>{
  const ids=['hero','radar','features','how'];
  const links=document.querySelectorAll('.nav-links a');
  let cur='hero';
  ids.forEach(id=>{const el=document.getElementById(id);if(el&&scrollY>=el.offsetTop-120)cur=id;});
  links.forEach((l,i)=>l.classList.toggle('active',ids[i]===cur));
});

// TABS
function switchTab(name){
  document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active',['long','short','ai'][i]===name));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
}

// SCAN
const longData=[
  {s:'NVDA',p:'$875.30',c:'+3.1%'},{s:'MSFT',p:'$430.15',c:'+0.9%'},
  {s:'META',p:'$512.44',c:'+0.6%'},{s:'AAPL',p:'$189.42',c:'+1.2%'},
  {s:'AMD',p:'$164.30',c:'+1.7%'},{s:'CRM',p:'$298.50',c:'+2.1%'},
  {s:'AMZN',p:'$192.80',c:'+0.5%'},{s:'UBER',p:'$78.40',c:'+1.9%'},
];
const shortData=[
  {s:'TSLA',p:'$248.17',c:'-0.8%'},{s:'COIN',p:'$234.88',c:'-2.1%'},
  {s:'GOOG',p:'$178.55',c:'-0.4%'},{s:'NFLX',p:'$685.22',c:'-1.3%'},
];

function simulateScan(mode){
  const prog=document.getElementById('prog-'+mode);
  const bar=document.getElementById('pbar-'+mode);
  const status=document.getElementById('pstatus-'+mode);
  const res=document.getElementById('res-'+mode);
  const count=document.getElementById('count-'+mode);
  prog.style.display='block';res.innerHTML='';bar.style.width='0%';count.textContent='—';
  const msgs=['מכין ערוץ נתונים...','מוריד נתוני שוק...','מחשב RSI...','בודק ממוצעים נעים...','מנתח נפח מסחר...','מסנן קריטריונים...','מסיים סריקה...'];
  let pct=0,si=0;
  const iv=setInterval(()=>{
    pct+=Math.random()*7+4;if(pct>100)pct=100;
    bar.style.width=pct+'%';
    if(si<msgs.length)status.textContent=msgs[si++];
    if(pct>=100){
      clearInterval(iv);prog.style.display='none';
      const stocks=mode==='long'?longData:shortData;
      const cc=mode==='long'?'card-long':'card-short';
      const pc=mode==='long'?'card-price-g':'card-price-r';
      count.textContent=stocks.length+' מניות';
      res.innerHTML='<div class="card-grid">'+stocks.map(s=>`
        <div class="stock-card ${cc}">
          <div class="card-sym">${s.s}</div>
          <div class="${pc}">${s.p}</div>
          <div class="card-chg">${s.c}</div>
        </div>`).join('')+'</div>';
    }
  },220);
}

// ANALYZE
function analyzeStock(){
  const t=document.getElementById('ticker-input').value.trim().toUpperCase();
  if(!t)return;
  const sp=document.getElementById('sp-analyze');
  const res=document.getElementById('res-analyze');
  sp.style.display='block';res.innerHTML='';
  setTimeout(()=>{
    sp.style.display='none';
    const up=Math.random()>.4;
    res.innerHTML=`
    <div class="analysis-result">
      <div class="result-card">
        <div class="result-card-header">
          <span>סקירת ${t}</span>
          <span class="result-tag ${up?'tag-green':'tag-red'}">${up?'מומנטום עולה':'מומנטום יורד'}</span>
        </div>
        <div class="metric-row"><span class="metric-label">RSI (14)</span><span class="metric-value">${(45+Math.random()*20).toFixed(1)} — נייטרלי</span></div>
        <div class="metric-row"><span class="metric-label">ממוצעים נעים</span><span class="metric-value">${up?'מעל MA9 — אזור חיובי':'מתחת MA9 — אזור שלילי'}</span></div>
        <div class="metric-row"><span class="metric-label">שוק האופציות</span><span class="metric-value">${up?'Calls 63.4%':'Puts 58.7%'}</span></div>
        <div class="metric-row"><span class="metric-label">עמידה בתחזיות</span><span class="metric-value">85% מהמקרים</span></div>
        <div class="metric-row"><span class="metric-label">המלצות אנליסטים</span><span class="metric-value">${up?'קנייה חזקה (88%)':'אחזקה (52%)'}</span></div>
      </div>
      <div class="ai-response-box">
        <div class="ai-response-label">AI Analyst — Gemini</div>
        <div class="ai-response-text">מניית ${t} מציגה ${up?'מומנטום חיובי עם תמיכה ברורה מעל הממוצעים הנעים. הסנטימנט בשוק האופציות תומך בהמשך עלייה':'לחץ מוכרים ניכר עם חולשה טכנית מתחת לממוצעים הנעים. מומלץ להמתין לאישור היפוך מגמה לפני כניסה'}. עקוב אחר רמות התמיכה הקריטיות בסשן הבא.</div>
      </div>
    </div>`;
  },2000);
}

// ASK AI
const answers=[
  'RSI (Relative Strength Index) הוא אינדיקטור מומנטום שמודד את מהירות ועוצמת שינויי המחיר בסולם 0-100. RSI מעל 70 מצביע על קנייה יתר — סיגנל זהירות, RSI מתחת ל-30 מצביע על מכירת יתר — הזדמנות כניסה אפשרית.',
  'ממוצע נע הוא הממוצע של מחירי הסגירה על פני תקופה נבחרת. MA9 רגיש לשינויים קצרי טווח, MA200 מייצג את המגמה הארוכה. כשמחיר חוצה מעל MA מסוים — זה סיגנל כניסה. כשחוצה מתחת — סיגנל יציאה.',
  'פריצה (Breakout) היא כאשר מחיר מניה חוצה רמת התנגדות משמעותית בנפח גבוה. לזיהוי פריצה אמתית: ודא נפח גבוה פי 1.5 מהממוצע, שני סגירות מעל ההתנגדות, ו-RSI מעל 50 אך מתחת ל-70.',
  'שוק האופציות מספק מדד לסנטימנט המשקיעים. Put/Call Ratio מעל 1 מצביע על פסימיות — יותר הגנות. מתחת ל-0.7 מצביע על אופטימיות. כ-64% קולים לעומת 36% פוטים מעיד על ציפייה לעלייה בטווח הקצר.',
];
function askAI(){
  const q=document.getElementById('ai-q').value.trim();
  if(!q)return;
  const sp=document.getElementById('sp-ai');
  const res=document.getElementById('res-ai');
  sp.style.display='block';res.innerHTML='';
  setTimeout(()=>{
    sp.style.display='none';
    const ans=answers[Math.floor(Math.random()*answers.length)];
    res.innerHTML=`<div class="ai-response-box" style="margin-top:16px"><div class="ai-response-label">תשובת האנליסט</div><div class="ai-response-text">${ans}</div></div>`;
  },1600);
}

document.getElementById('ticker-input').addEventListener('keydown',e=>{if(e.key==='Enter')analyzeStock()});
document.getElementById('ai-q').addEventListener('keydown',e=>{if(e.key==='Enter')askAI()});
</script>
</body>
</html>
