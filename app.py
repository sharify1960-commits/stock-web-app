import json
import os
import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="StockScreener Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

SUBSCRIBERS_FILE = "subscribers.json"
VISITORS_FILE = "visitors.json"
COUNTER_FILE = "counter.json"
ALERTS_LOG_FILE = "alerts_log.json"


# Helper Data Functions
def load_subscribers():
  if os.path.exists(SUBSCRIBERS_FILE):
    try:
      with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return {}
  return {}


def save_subscribers(subs):
  with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
    json.dump(subs, f, ensure_ascii=False, indent=4)


def get_visitor_count():
  if os.path.exists(VISITORS_FILE):
    try:
      with open(VISITORS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("count", 1245)
    except:
      return 1245
  return 1245


def increment_visitor_count():
  count = get_visitor_count() + 1
  with open(VISITORS_FILE, "w", encoding="utf-8") as f:
    json.dump({"count": count}, f, ensure_ascii=False)
  return count


def load_counter():
  if os.path.exists(COUNTER_FILE):
    try:
      with open(COUNTER_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("count", 0)
    except:
      return 0
  return 0


def save_counter(count):
  with open(COUNTER_FILE, "w", encoding="utf-8") as f:
    json.dump({"count": count}, f, ensure_ascii=False, indent=4)


def increment_counter():
  count = load_counter() + 1
  save_counter(count)
  return count


def generate_broker_link(symbol, platform):
  symbol_clean = symbol.strip().upper()
  if platform == "TradingView":
    return f"https://www.tradingview.com/chart/?symbol={symbol_clean}"
  elif platform == "Interactive Brokers":
    return f"https://www.interactivebrokers.com/mkt/?ticker={symbol_clean}"
  elif platform == "Investing.com":
    return f"https://www.investing.com/search/?q={symbol_clean}"
  elif platform == "Webull":
    return f"https://www.webull.com/quote/{symbol_clean.lower()}"
  else:
    return f"https://finance.yahoo.com/quote/{symbol_clean}"


# Real-time Alert Engine Functions
def load_alerts_log():
  if os.path.exists(ALERTS_LOG_FILE):
    try:
      with open(ALERTS_LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return []
  return []


def save_alert_log(alert_item):
  logs = load_alerts_log()
  logs.insert(0, alert_item)
  with open(ALERTS_LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(logs[:50], f, ensure_ascii=False, indent=4)


def send_email_notification(recipient, alert_msg, action_link):
  """שולחת מייל התראה בפועל בעזרת הפרטים שמוגדרים ב-Streamlit Secrets"""
  try:
    if "email" not in st.secrets:
      return False, "הגדרות email חסרות ב-Secrets"

    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = st.secrets["email"]["smtp_port"]
    sender_email = st.secrets["email"]["sender_email"]
    sender_password = st.secrets["email"]["sender_password"]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = "🚨 איתות בזמן אמת - StockScreener Pro"

    body = f"""
        <div style="direction: rtl; text-align: right; font-family: Arial, sans-serif;">
            <h2>🚨 איתות חדש זוהה במערכת!</h2>
            <p style="font-size: 1.1rem;">{alert_msg}</p>
            <p><a href="{action_link}" style="background-color: #FF6B00; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; font-weight: bold;">⚡ מעבר מיידי לביצוע העסקה</a></p>
        </div>
        """
    msg.attach(MIMEText(body, "html"))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    return True, "נשלח בהצלחה"
  except Exception as e:
    return False, str(e)


def check_and_dispatch_alerts(
    stocks_list, rsi_buy_threshold, rsi_sell_threshold, current_platform
):
  subs = load_subscribers()
  active_emails = [
      email for email, info in subs.items() if info.get("active", True)
  ]
  triggered_alerts = []

  for stock in stocks_list:
    symbol = stock["סימול"]
    price = stock["מחיר ($)"]
    rsi = stock["RSI"]
    broker_link = generate_broker_link(symbol, current_platform)

    alert_type = None
    if rsi <= rsi_buy_threshold:
      alert_type = "BUY"
      msg_text = (
          f"🚨 איתות קנייה בזמן אמת! המניה {symbol} הגיעה ל-RSI של {rsi} (מחיר:"
          f" ${price})"
      )
    elif rsi >= rsi_sell_threshold:
      alert_type = "SELL"
      msg_text = (
          f"⚠️ איתות מכירה/מימוש! המניה {symbol} הגיעה ל-RSI של {rsi} (מחיר:"
          f" ${price})"
      )

    if alert_type:
      alert_data = {
          "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
          "symbol": symbol,
          "type": alert_type,
          "price": price,
          "rsi": rsi,
          "action_link": broker_link,
          "message": msg_text,
      }
      triggered_alerts.append(alert_data)
      save_alert_log(alert_data)

      # שליחת מייל לכל המשתמשים הפעילים
      for email_to in active_emails:
        success, err = send_email_notification(
            email_to, msg_text, broker_link
        )
        if not success:
          st.error(f"שגיאה בשליחת מייל ל-{email_to}: {err}")

  return triggered_alerts, active_emails


# Custom CSS styling
st.markdown(
    """
<style>
    .stApp { 
        background: linear-gradient(0deg, #A7521C 0%, #C8692A 10%, #DF8542 30%, #EFA466 80%);
        background-attachment: fixed;
    }
    .main-header { 
        font-size: 2.2rem; color: #ffffff; text-align: center; font-weight: 800; margin-bottom: 1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4); 
    }
    .stButton>button, [data-testid="stFormSubmitButton"]>button {
        width: 100% !important; border-radius: 14px !important; font-weight: 950 !important; font-size: 1.3rem !important;
        background: linear-gradient(135deg, #FF6B00 0%, #D85A00 100%) !important; color: white !important; border: 2px solid #FFFFFF !important; padding: 0.8rem 1rem !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5) !important; text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
    }
    .stTextInput input, .stSelectbox select {
        font-weight: 800 !important; font-size: 1rem !important; color: #000000 !important; background-color: #ffffff !important; border: 2px solid #333333 !important; direction: rtl !important; text-align: right !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "role" not in st.session_state:
  st.session_state["role"] = ""
if "user_email" not in st.session_state:
  st.session_state["user_email"] = ""
if "trading_platform" not in st.session_state:
  st.session_state["trading_platform"] = "TradingView"
if "pilot_counted" not in st.session_state:
  st.session_state["pilot_counted"] = False

if "visited" not in st.session_state:
  st.session_state["visited"] = True
  current_visitors = increment_visitor_count()
else:
  current_visitors = get_visitor_count()

if "stocks_list" not in st.session_state:
  st.session_state["stocks_list"] = [
      {
          "סימול": "AAPL",
          "שם חברה": "Apple Inc.",
          "מחיר ($)": 189.50,
          "RSI": 28.5,
          "מגמת SMA": "חיובית",
          "שינוי יומי (%)": "+1.2%",
          "המלצה": "קנייה",
      },
      {
          "סימול": "MSFT",
          "שם חברה": "Microsoft Corp.",
          "מחיר ($)": 415.20,
          "RSI": 58.1,
          "מגמת SMA": "חיובית",
          "שינוי יומי (%)": "-0.5%",
          "המלצה": "החזק",
      },
      {
          "סימול": "GOOGL",
          "שם חברה": "Alphabet Inc.",
          "מחיר ($)": 142.80,
          "RSI": 32.4,
          "מגמת SMA": "תיקון",
          "שינוי יומי (%)": "+2.1%",
          "המלצה": "קנייה לבחינה",
      },
      {
          "סימול": "AMZN",
          "שם חברה": "Amazon.com",
          "מחיר ($)": 178.25,
          "RSI": 68.9,
          "מגמת SMA": "חזקה",
          "שינוי יומי (%)": "+0.8%",
          "המלצה": "קנייה",
      },
      {
          "סימול": "NVDA",
          "שם חברה": "NVIDIA Corp.",
          "מחיר ($)": 875.40,
          "RSI": 74.2,
          "מגמת SMA": "חזקה מאוד",
          "שינוי יומי (%)": "+3.4%",
          "המלצה": "חזק מאוד",
      },
  ]

# Login Screen
if not st.session_state["logged_in"]:
  col_l1, col_l2, col_l3 = st.columns([0.1, 0.8, 0.1])
  with col_l2:
    st.markdown(
        "<h2 style='text-align: center; color: #ffffff;'>כניסת לקוחות למערכת"
        " 🔐</h2>",
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
      username = st.text_input("מספר תעודת זהות / מנהל:")
      user_email_input = st.text_input("כתובת מייל (חובה):")
      password = st.text_input("סיסמה:", type="password")
      platform_pref = st.selectbox(
          "פלטפורמת מסחר:",
          [
              "TradingView",
              "Interactive Brokers",
              "Yahoo Finance",
              "Investing.com",
              "Webull",
          ],
      )
      annual_price_pref = st.selectbox(
          "מחיר שנתי מוערך:",
          [
              "טרם נבחר",
              'עד 150 ש"ח לשנה',
              '150 - 300 ש"ח לשנה',
              '300 - 500 ש"ח לשנה',
              'מעל 500 ש"ח לשנה',
          ],
      )
      agree = st.checkbox(
          "אני מאשר/ת שקראתי והבנתי את תנאי השימוש, שהמסחר על אחריותי בלבד, ושכל"
          " הזכויות שמורות."
      )
      submit_button = st.form_submit_button("התחבר למערכת")

      if submit_button:
        if username.strip().lower() == "admin" and password == "999999":
          st.session_state["logged_in"] = True
          st.session_state["role"] = "admin"
          st.session_state["user_email"] = (
              user_email_input if user_email_input else "admin@admin.com"
          )
          st.session_state["trading_platform"] = platform_pref
          st.rerun()
        elif not agree:
          st.error("יש לאשר את תנאי השימוש לפני ההתחברות.")
        elif not user_email_input or "@" not in user_email_input:
          st.error("נא להזין כתובת מייל תקינה.")
        elif len(password) >= 4:
          st.session_state["logged_in"] = True
          st.session_state["role"] = "user"
          st.session_state["user_email"] = user_email_input
          st.session_state["trading_platform"] = platform_pref

          subs = load_subscribers()
          subs[user_email_input] = {
              "active": True,
              "id": username,
              "platform": platform_pref,
              "expected_annual_price": annual_price_pref,
          }
          save_subscribers(subs)
          st.rerun()

else:
  # Main Dashboard View
  st.sidebar.markdown(
      '<h2 style="color: #FF6B00; font-weight: 900;">🧭 ניווט וניהול</h2>',
      unsafe_allow_html=True,
  )
  st.sidebar.write(f"מחובר כ: **{st.session_state['user_email']}**")

  st.sidebar.markdown("---")
  rsi_buy = st.sidebar.slider("סף קנייה יתר (Oversold RSI):", 10, 40, 35)
  rsi_sell = st.sidebar.slider("סף מכירת יתר (Overbought RSI):", 60, 90, 70)

  if st.sidebar.button("התנתק"):
    st.session_state["logged_in"] = False
    st.rerun()

  st.markdown(
      "<h1 class='main-header'>📈 StockScreener Pro - לוח בקרה וניתוח"
      " טכני</h1>",
      unsafe_allow_html=True,
  )

  count = st_autorefresh(interval=60000, limit=1000, key="stock_autorefresh")

  # הרצת מנוע האיתותים ושליחת המיילים בפועל
  alerts, subscribers_list = check_and_dispatch_alerts(
      st.session_state["stocks_list"],
      rsi_buy,
      rsi_sell,
      st.session_state["trading_platform"],
  )

  if alerts:
    st.toast(f"🚨 נלכדו {len(alerts)} איתותים בזמן אמת!", icon="🔔")
    for alt in alerts:
      action_btn_html = f"<a href='{alt['action_link']}' target='_blank' style='background-color: #FF6B00; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-weight: bold;'>⚡ עשה דיל ב-{st.session_state['trading_platform']}</a>"
      st.markdown(
          f"🔔 **{alt['type']}:** {alt['message']} {action_btn_html}",
          unsafe_allow_html=True,
      )

  df = pd.DataFrame(st.session_state["stocks_list"])
  st.dataframe(df, use_container_width=True)
