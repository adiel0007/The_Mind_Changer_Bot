import streamlit as st
import streamlit.components.v1 as components

# הגדרת תצורת הדף לרוחב מלא (Wide Mode)
st.set_page_config(page_title="The Mind Changer", layout="wide", initial_sidebar_state="collapsed")

# קוד ה-HTML המלא שלך (מאוחסן במשתנה טקסט)
html_code = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>The Mind Changer | Stock Radar</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght=400;700;900&family=Inter:wght=300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
/* כאן נמצא כל ה-CSS שסיפקת... */
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
/* המשך ה-CSS וה-HTML שסיפקת... */
""" + """
<body>
<div class="modal-overlay open" id="modal">
  <div class="modal">
    <div class="modal-logo">The Mind Changer</div>
    <p>המידע המוצג באתר זה מיועד למטרות לימוד...</p>
    <button class="modal-btn" onclick="document.getElementById('modal').classList.remove('open')">הבנתי — כניסה לאתר</button>
  </div>
</div>
</body>
</html>
"""

# הזרקת CSS מיוחד כדי להעלים את הריפוד (Padding) המובנה של Streamlit
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
        iframe {
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

# הצגת קוד ה-HTML ברוחב מלא וגובה רספונסיבי (למשל 2200 פיקסלים כדי להכיל את כל הגלילה)
components.html(html_code, height=2200, scrolling=True)
