import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SUBSCRIBERS_FILE = "subscribers.json"

def main():
    if not os.path.exists(SUBSCRIBERS_FILE):
        print("Notice: subscribers.json does not exist yet. Creating empty file.")
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return

    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        subscribers = json.load(f)

    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Error: MAIL_USERNAME or MAIL_PASSWORD secrets are missing.")
        return

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        for email, data in subscribers.items():
            if data.get("active", True):
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = email
                msg["Subject"] = "📈 דוח מניות יומי - StockScreener Pro"
                
                body = "שלום רב,\n\nזהו עדכון מניות יומי אוטומטי ממערכת ניתוח המניות של איציק.\nהנתונים מעודכנים להיום.\n\nבברכה,\nStockScreener Pro"
                msg.attach(MIMEText(body, "plain", "utf-8"))
                
                server.sendmail(sender_email, email, msg.as_string())
                print(f"Email sent successfully to {email}")

        server.quit()
    except Exception as e:
        print(f"SMTP error: {e}")

if __name__ == "__main__":
    main()
