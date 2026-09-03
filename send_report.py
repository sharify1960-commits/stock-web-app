import json
import smtplib
import os
import pandas as pd
import yfinance as yf
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# רשימת המניות למעקב בדוח
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]

def get_stock_data():
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change = ((current_price - prev_price) / prev_price) * 100
                data.append({
                    "מניה": ticker,
                    "מחיר נוכחי ($)": round(current_price, 2),
                    "שינוי יומי (%)": round(change, 2)
                })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return pd.DataFrame(data)

def send_reports():
    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Missing mail credentials in environment variables.")
        return

    # טעינת מנויים מקובץ subscribers.json
    try:
        with open("subscribers.json", "r", encoding="utf-8") as f:
            subscribers = json.load(f)
    except Exception as e:
        print(f"Error loading subscribers: {e}")
        subscribers = {}

    if not subscribers:
        print("No subscribers found.")
        return

    # יצירת נתוני הטבלה
    df = get_stock_data()
    if df.empty:
        html_table = "<p>לא נמצאו נתונים להצגה היום.</p>"
    else:
        html_table = df.to_html(index=False, classes='stock-table', border=0)

    # בניית גוף המייל בעיצוב HTML נקי
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; background-color: #f9f9f9; padding: 20px; }}
            .container {{ background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h2 {{ color: #2c3e50; }}
            table.stock-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            table.stock-table th, table.stock-table td {{ padding: 12px; border-bottom: 1px solid #ddd; text-align: center; }}
            table.stock-table th {{ background-color: #3498db; color: white; }}
            table.stock-table tr:hover {{ background-color: #f1f1f1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>דוח מניות יומי - פרוייקט מניות איציק</h2>
            <p>שלום רב,</p>
            <p>להלן סיכום נתוני המניות היומי:</p>
            {html_table}
            <p style="margin-top: 20px; color: #7f8c8d; font-size: 12px;">הדוח הופק אוטומטית באמצעות מערכת GitHub Actions.</p>
        </div>
    </body>
    </html>
    """

    # שליחת המייל לכל מנוי פעיל
    for email, info in subscribers.items():
        if info.get("active", True):
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "דוח מניות יומי - פרוייקט מניות איציק"
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
