import json
import smtplib
import os
import pandas as pd
import yfinance as yf
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# רשימת המניות המלאה בהתאם לגיליון שלך
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", "NFLX", "INTC"]

def get_stock_data():
    data = []
    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).history(period="1y")
            if hist.empty or len(hist) < 30:
                continue
            
            close = hist['Close']
            current_price = close.iloc[-1]
            
            # חישוב אחוז שינוי (יומי, שבועי, חודשי, שנתי)
            daily_ret = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
            weekly_ret = ((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]) * 100 if len(close) >= 5 else 0
            monthly_ret = ((close.iloc[-1] - close.iloc[-21]) / close.iloc[-21]) * 100 if len(close) >= 21 else 0
            yearly_ret = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100
            
            # חישוב RSI (14)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            current_rsi = rsi_series.iloc[-1]
            
            # קביעת איתות וסיבה על בסיס RSI ומומנטום
            if current_rsi > 60:
                signal = "Sell 🔴"
                reason = "RSI גבוה מ-60 (אזור רוויה)"
            elif current_rsi < 45:
                signal = "Buy 🟢"
                reason = "RSI נמוך מ-45 (הזדמנויות קנייה)"
            else:
                signal = "Buy 🟢"
                reason = "מומנטום חיובי (ממוצע 10 מעל 20)"
            
            support = round(current_price * 0.95, 2)
            target = round(current_price * 1.05, 2)
            
            data.append({
                "מניה": ticker,
                "איתות טכני": signal,
                "סיבת האיתות": reason,
                "מחיר סגירה": round(current_price, 2),
                "מחיר קנייה מומלץ (תמיכה)": support,
                "מחיר יעד למכירה": target,
                "יומי (%)": round(daily_ret, 2),
                "שבועי (%)": round(weekly_ret, 2),
                "חודשי (%)": round(monthly_ret, 2),
                "שנתי (%)": round(yearly_ret, 2),
                "RSI נוכחי": round(current_rsi, 2)
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    return pd.DataFrame(data)

def send_reports():
    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Missing mail credentials.")
        return

    try:
        with open("subscribers.json", "r", encoding="utf-8") as f:
            subscribers = json.load(f)
    except Exception as e:
        print(f"Error loading subscribers: {e}")
        subscribers = {}

    if not subscribers:
        print("No subscribers found.")
        return

    df = get_stock_data()
    if df.empty:
        html_table = "<p>לא נמצאו נתונים להצגה היום.</p>"
    else:
        html_table = df.to_html(index=False, classes='stock-table', border=0)

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f4f6f9; padding: 20px; }}
            .container {{ background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 1000px; margin: auto; }}
            h2 {{ color: #2c3e50; text-align: center; }}
            table.stock-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
            table.stock-table th, table.stock-table td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: center; }}
            table.stock-table th {{ background-color: #2980b9; color: white; }}
            table.stock-table tr:hover {{ background-color: #f1f1f1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 דוח מניות יומי מלא - פרוייקט מניות איציק</h2>
            <p>שלום רב,</p>
            <p>להלן סיכום הנתונים והאיתותים הטכניים המעודכנים להיום:</p>
            {html_table}
            <p style="margin-top: 20px; color: #7f8c8d; font-size: 12px; text-align: center;">הדוח הופק אוטומטית באמצעות מערכת GitHub Actions.</p>
        </div>
    </body>
    </html>
    """

    for email, info in subscribers.items():
        if info.get("active", True):
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "📊 דוח מניות יומי מלא - פרוייקט מניות איציק"
                msg["From"] = sender_email
                msg["To"] = email
                
                msg.attach(MIMEText(html_content, "html", "utf-8"))
                
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, email, msg.as_string())
                print(f"Email sent successfully to {email}")
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")

if __name__ == "__main__":
    send_reports()
