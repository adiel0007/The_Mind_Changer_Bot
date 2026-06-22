import yfinance as yf
import pandas as pd
import numpy as np
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# טוקן הבוט הרשמי שלך
TELEGRAM_TOKEN = "8987317993:AAH3tjfShAtX0ejdfOh2Mi_IlZXWUXD45b8"

def get_all_us_tickers():
    """קריאת רשימת המניות ישירות מקובץ הטקסט המעודכן שלך"""
    filename = "Stocks List.txt"
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                tickers = [t.strip().upper() for t in content.split(',') if t.strip()]
                print(f"נטענו {len(tickers)} מניות בהצלחה מתוך הקובץ {filename}")
                return tickers
        else:
            print(f"אזהרה: קובץ {filename} לא נמצא בתיקיית הבוט! משתמש ברשימת גיבוי.")
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "AMD", "NFLX", "PLTR"]
    except Exception as e:
        print(f"שגיאה בקריאת קובץ המניות: {e}")
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "AMD", "NFLX", "PLTR"]

def calculate_rsi_panel(close_prices, period=14):
    """חישוב RSI יעיל"""
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def verify_earnings_history(ticker_obj):
    """בדיקת היסטוריית דוחות (Revenue Beat) ב-4 הרבעונים האחרונים"""
    try:
        earnings_df = ticker_obj.earnings_dates
        if earnings_df is None or earnings_df.empty: return False
        if 'Surprise(%)' in earnings_df.columns:
            reported = earnings_df.dropna(subset=['Surprise(%)']).head(4)
            if len(reported) < 4: return False
            for idx, row in reported.iterrows():
                if row['Surprise(%)'] < 0: return False
            return True
        return False
    except:
        return False

async def radar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # שליחת הודעה ראשונית כדי שהמשתמש ידע שהבוט קיבל את הפקודה ועובד
    progress_message = await update.message.reply_text("🌐 מתחיל בסריקת השוק מהרשימה שלך... ⚡\nמוריד ומנתח נתונים, אנא המתן כ-30 שניות.")
    
    tickers = get_all_us_tickers()
    
    # פיצול לקבוצות קטנות של 100 מניות כדי למנוע קפיאה של השרת
    chunk_size = 100
    ticker_chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    
    first_stage_passed = []
    
    # שלב 1 ו-2: הורדה וחישוב אינדיקטורים מקומיים
    for chunk in ticker_chunks:
        try:
            # הרצה בצורה שלא תוקעת את הבוט באוויר
            data = await asyncio.to_thread(yf.download, chunk, period="6mo", group_by='ticker', progress=False, timeout=10)
            
            for ticker in chunk:
                try:
                    if ticker not in data.columns.levels[0]: continue
                    df = data[ticker].dropna(subset=['Close'])
                    if len(df) < 20: continue
                    
                    df['RSI'] = calculate_rsi_panel(df['Close'], period=14)
                    df['MA9'] = df['Close'].rolling(window=9).mean()
                    
                    last_row = df.iloc[-1]
                    current_price = float(last_row['Close'])
                    rsi_val = float(last_row['RSI'])
                    ma9_val = float(last_row['MA9'])
                    avg_volume = df['Volume'].tail(10).mean()
                    
                    # סינון מחיר 15-250, RSI מתחת ל-30, נמוך מ-MA9 ונפח בריא
                    if (15 <= current_price <= 250) and (rsi_val < 30) and (current_price < ma9_val) and (avg_volume >= 500000):
                        first_stage_passed.append({
                            "ticker": ticker,
                            "price": current_price,
                            "rsi": rsi_val
                        })
                except:
                    continue
            # הפסקה קטנה בין קבוצה לקבוצה כדי לתת לבוט "לנשום" ולמנוע חסימות
            await asyncio.sleep(0.5)
        except:
            continue

    if not first_stage_passed:
        await progress_message.edit_text("🔍 הסריקה הסתיימה! מתוך מאות המניות, לא נמצאו כרגע חברות בטווח של 15$-250$ שעונות על תנאי ה-RSI והממוצע הנע הנדרשים.")
        return

    await progress_message.edit_text(f"📊 שלב א' הושלם! נמצאו {len(first_stage_passed)} מניות פוטנציאליות טכנית.\nמבצע כעת בדיקת דוחות פיננסיים ואופציות... ⏳")
    
    final_stocks = []
    
    # שלב 3: בדיקת דוחות ואופציות
    for stock in first_stage_passed:
        try:
            t = yf.Ticker(stock['ticker'])
            
            # בדיקת דוחות (Revenue Beat)
            has_good_earnings = await asyncio.to_thread(verify_earnings_history, t)
            if not has_good_earnings: continue
            
            # בדיקת אופציות קול/פוט
            expirations = t.options
            if not expirations: continue
            
            opt = await asyncio.to_thread(t.option_chain, expirations[0])
            total_calls = opt.calls['volume'].fillna(0).sum() if 'volume' in opt.calls.columns else 0
            total_puts = opt.puts['volume'].fillna(0).sum() if 'volume' in opt.puts.columns else 0
            total_volume = total_calls + total_puts
            
            if total_volume < 1000: continue
            
            call_percentage = (total_calls / total_volume) * 100
            put_percentage = (total_puts / total_volume) * 100
            
            if call_percentage >= 50:
                final_stocks.append({
                    "ticker": stock['ticker'],
                    "price": stock['price'],
                    "rsi": stock['rsi'],
                    "call_pct": call_percentage,
                    "put_pct": put_percentage
                })
        except:
            continue

    if not final_stocks:
        await progress_message.edit_text("הסריקה הסתיימה! המניות שעברו טכנית נפסלו בשלב הדוחות או בשל יחס אופציות קול נמוך.")
        return

    # מיון לפי ה-RSI הנמוך ביותר והצגת טופ 10
    final_stocks = sorted(final_stocks, key=lambda x: x['rsi'])[:10]
    
    response_text = f"📊 **תוצאות רדאר סריקת המניות המורחבת ($15-$250):**\n\n"
    for stock in final_stocks:
        response_text += f"🔹 **{stock['ticker']}**\n" \
                         f" 💵 מחיר: ${stock['price']:.2f}\n" \
                         f" 📉 RSI: {stock['rsi']:.1f}\n" \
                         f" 📈 אופציות: {stock['call_pct']:.1f}% Calls | {stock['put_pct']:.1f}% Puts\n" \
                         f" 📜 דוחות: פגיעה מלאה ב-4 רבעונים! ✅\n\n"
                         
    await update.message.reply_text(response_text, parse_mode="Markdown")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "👋 ברוכים הבאים לבוט הרדאר הפיננסי!\n\n" \
                   "שלח את הפקודה /radar כדי להתחיל בסריקה המורחבת של השוק ($15-$250). 📊"
    await update.message.reply_text(welcome_text)

def main():
    # בניית האפליקציה עם הגדרות טיימאאוט מורחבות כדי למנוע ניתוקים מהשרת
    application = Application.builder().token(TELEGRAM_TOKEN).read_timeout(30).write_timeout(30).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("radar", radar_command))
    
    print("הבוט האסינכרוני החסין פעיל! קורא מתוך 'Stocks List.txt'.")
    application.run_polling()

if __name__ == '__main__':
    main()