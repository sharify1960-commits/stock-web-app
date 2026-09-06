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

# הגדרות עמוד ראשי
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


# --- פונקציות עזר לשמירה וטעינת נתונים ---
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


def reset_visitor_count():
    with open(VISITORS_FILE, "w", encoding="utf-8") as f:
        json.dump({"count": 0}, f, ensure_ascii=False)
    return 0


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


# --- מנוע איתותים ושליחת מיילים מותאמים אישית ---
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
        <div style="direction: rtl; text-align: right; font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>🚨 איתות חדש זוהה במערכת!</h2>
            <p style="font-size: 1.1rem;">{alert_msg}</p>
            <p><a href="{action_link}" style="background-color: #FF6B00; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">⚡ מעבר מיידי לביצוע העסקה בברוקר שלך</a></p>
            <hr>
            <p style="font-size: 0.8rem; color: #777;">הודעה זו נשלחה באופן אוטומטי מ-StockScreener Pro. המסחר בשוק ההון כרוך בסיכון.</p>
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


def check_and_dispatch_alerts(stocks_list, rsi_buy_threshold, rsi_sell_threshold):
    subs = load_subscribers()
    triggered_alerts = []

    for stock in stocks_list:
        symbol = stock["סימול"]
        price = stock["מחיר ($)"]
        rsi = stock["RSI"]

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
            for email_to, user_info in subs.items():
                if user_info.get("active", True):
                    user_broker = user_info.get("platform", "Interactive Brokers")
                    user_link = generate_broker_link(symbol, user_broker)

                    send_email_notification(email_to, msg_text, user_link)

            default_link = generate_broker_link(symbol, "Interactive Brokers")
            alert_data = {
                "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "type": alert_type,
                "price": price,
                "rsi": rsi,
                "action_link": default_link,
                "message": msg_text,
            }
            triggered_alerts.append(alert_data)
            save_alert_log(alert_data)

    return triggered_alerts


# פונקציית עזר להצגת הלוגו המעוצב
def render_logo():
    logo_html = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
        .custom-logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }
        .custom-logo {
            background: linear-gradient(135deg, #C8692A 0%, #A7521C 100%);
            border: 3px solid #FFFFFF;
            border-radius: 12px;
            padding: 15px 30px;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
            max-width: 90%;
        }
        .custom-logo-text {
            color: #FFFFFF;
            font-family: 'Great Vibes', 'Brush Script MT', cursive;
            font-size: 2.3rem;
            font-weight: bold;
            letter-spacing: 1.5px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin: 0;
            line-height: 1.2;
        }
    </style>
    <div class="custom-logo-container">
        <div class="custom-logo">
            <h1 class="custom-logo-text">SR - מערכת ניהול השקעות מתקדמת</h1>
        </div>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)


# עיצוב ויזואלי (CSS)
st.markdown(
    """
<style>
    .stApp { 
        background: linear-gradient(0deg, #A7521C 0%, #C8692A 10%, #DF8542 30%, #EFA466 80%);
        background-attachment: fixed;
    }
    /* כותרת ראשית לבנה מבריקה ובולטת */
    .main-header { 
        font-size: 2.6rem !important; 
        color: #FFFFFF !important; 
        text-align: center; 
        font-weight: 900 !important; 
        margin-bottom: 1rem; 
        text-shadow: 
            0 0 10px rgba(255, 255, 255, 0.8),
            0 0 20px rgba(255, 255, 255, 0.5),
            2px 2px 4px rgba(0, 0, 0, 0.8);
        letter-spacing: 1px;
    }
    .stButton>button, [data-testid="stFormSubmitButton"]>button {
        width: 100% !important; border-radius: 14px !important; font-weight: 950 !important; font-size: 1.3rem !important;
        background: linear-gradient(135deg, #FF6B00 0%, #D85A00 100%) !important; color: white !important; border: 2px solid #FFFFFF !important; padding: 0.8rem 1rem !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5) !important; text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
    }
    /* הגדלת גופן, הדגשה ויישור לימין עבור כותרות שדות הקלט */
    [data-testid="stWidgetLabel"] label, label {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        direction: rtl !important;
        text-align: right !important;
        display: block !important;
    }
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        font-weight: 800 !important; font-size: 1rem !important; color: #000000 !important; background-color: #ffffff !important; border: 2px solid #333333 !important; direction: rtl !important; text-align: right !important;
    }
    .legal-box {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        color: #222222;
        direction: rtl;
        text-align: right;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ניהול Session State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = ""
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "trading_platform" not in st.session_state:
    st.session_state["trading_platform"] = "Interactive Brokers"

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

# --- סרגל צדדי (Sidebar) ראשי - זמין תמיד ---
st.sidebar.markdown(
    '<h2 style="color: #FF6B00; font-weight: 900;">🧭 ניווט וניהול</h2>',
    unsafe_allow_html=True,
)

if st.session_state["logged_in"]:
    st.sidebar.write(f"מחובר כ: **{st.session_state['user_email']}**")
    if st.session_state["role"] == "admin":
        st.sidebar.info("👑 מצב מנהל מערכת (Admin)")
else:
    st.sidebar.write("מצב: **אורח / טרם התחבר/ה**")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ סרגלי ניתוח טכני ופרמטרים")

# סליידר והסבר: סף קניית יתר
rsi_buy = st.sidebar.slider("סף קנייה יתר (Oversold RSI):", 10, 40, 35)
st.sidebar.info(
    "**הסבר שדה:** מדד RSI נמוך מסף זה מסמן שנכס נסחר במכירת יתר ויכול"
    " להוות הזדמנות כניסה."
)

# סליידר והסבר: סף מכירת יתר
rsi_sell = st.sidebar.slider("סף מכירת יתר (Overbought RSI):", 60, 90, 70)
st.sidebar.info(
    "**הסבר שדה:** מדד RSI גבוה מסף זה מצביע על נכס במצב קניית יתר וסיכון"
    " לתיקון חד."
)

st.sidebar.markdown("---")
st.sidebar.subheader("ממוצעים נעים (Moving Averages)")

# ממוצע נע קצר
sma_short = st.sidebar.selectbox(
    "תקופת ממוצע קצר (SMA Short):", [5, 10, 20, 50], index=2
)
st.sidebar.info("**הסבר שדה:** משקף את מומנטום המחירים בטווח הקצר.")

# ממוצע נע ארוך
sma_long = st.sidebar.selectbox(
    "תקופת ממוצע ארוך (SMA Long):", [50, 100, 200], index=2
)
st.sidebar.info(
    "**הסבר שדה:** מגדיר את המגמה הראשית של השוק לטווח הארוך."
)

st.sidebar.markdown("---")
st.sidebar.subheader("➕ הוספת מניה חדשה למערכת")
with st.sidebar.form("add_stock_form"):
    new_symbol = st.text_input("סימול מניה (למשל TSLA):")
    new_name = st.text_input("שם חברה מלא:")
    new_price = st.number_input("מחיר ($):", value=100.0)
    new_rsi = st.number_input("ערך RSI:", value=50.0)
    add_submitted = st.form_submit_button("הוסף מניה למעקב")

    if add_submitted:
        if new_symbol and new_name:
            st.session_state["stocks_list"].append({
                "סימול": new_symbol.upper(),
                "שם חברה": new_name,
                "מחיר ($)": new_price,
                "RSI": new_rsi,
                "מגמת SMA": "ניטרלי",
                "שינוי יומי (%)": "+0.0%",
                "המלצה": "בדיקה",
            })
            st.sidebar.success(f"המניה {new_symbol} הוספה בהצלחה!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.metric("סך כניסות למערכת", current_visitors)

if st.session_state["logged_in"]:
    if st.sidebar.button("התנתק"):
        st.session_state["logged_in"] = False
        st.rerun()


# --- מסך התחברות והסברים ---
if not st.session_state["logged_in"]:
    col_l1, col_l2, col_l3 = st.columns([0.1, 0.8, 0.1])
    with col_l2:
        render_logo()

        st.markdown(
            "<h1 style='text-align: center; color: #ffffff; font-weight: 900;'>🚀"
            " StockScreener Pro - מערכת איתותים בזמן אמת</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="legal-box">
                <h3>ℹ️ על המערכת</h3>
                <p>מערכת <b>StockScreener Pro</b> הינה סורק מניות מתקדם המבוסס על אלגוריתמים לניתוח טכני (RSI, ממוצעים נעים SMA). המערכת מזהה הזדמנויות מסחר בזמן אמת ושולחת התראות מיידיות לתיבת הדואר האלקטרוני שלך, כולל קישור ישיר לביצוע הפעולה בברוקר המועדף עליך.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<h3 style='text-align: center; color: #ffffff;'>כניסת לקוחות והרשמה"
            " לפיילוט 🔐</h3>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("מספר תעודת זהות / מנהל:")
            user_email_input = st.text_input("כתובת מייל (חובה לקבלת איתותים):")
            password = st.text_input("סיסמה:", type="password")
            platform_pref = st.selectbox(
                "פלטפורמת מסחר מועדפת (עבור קישורים ישירים):",
                [
                    "Interactive Brokers",
                    "TradingView",
                    "Yahoo Finance",
                    "Investing.com",
                    "Webull",
                ],
            )
            annual_price_pref = st.selectbox(
                "מחיר שנתי מוערך לפיילוט:",
                [
                    "טרם נבחר",
                    'עד 150 ש"ח לשנה',
                    '150 - 300 ש"ח לשנה',
                    '300 - 500 ש"ח לשנה',
                    'מעל 500 ש"ח לשנה',
                ],
            )

            st.markdown("---")

            st.markdown(
                """
                <div style="font-size: 0.85rem; color: #333333; background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px; direction: rtl; text-align: right;">
                    <b>⚖️ הגנה משפטית ותנאי שימוש:</b><br>
                    המערכת מספקת נתונים ואיתותים טכניים בלבד-לפי קביעת ספים של פרמטרים בניתוח טכני שאותם קבע הלקוח והם באחריותו. אין לראות באמור ייעוץ השקעות, המלצה או שידול לקנייה/מכירה של ניירות ערך. המסחר בשוק ההון טומן בחובו סיכון כספי. המשתמש נושא באחריות המלאה בלבד לכל פעולה כספית שיבצע.<br><br>
                    <b>© זכויות יוצרים:</b><br>
                    כל הזכויות שמורות למפתח המערכת. אין להעתיק, לשכפל או להפיץ חלקים מקוד המערכת או התכנים ללא אישור בכתב.
                </div>
                """,
                unsafe_allow_html=True,
            )

            agree = st.checkbox(
                "אני מאשר/ת שקראתי והבנתי את תנאי השימוש וההגנה המשפטית, שהמסחר על"
                " אחריותי בלבד, ושכל הזכויות שמורות."
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
                    st.error("יש לאשר את תנאי השימוש וההגנה המשפטית לפני ההתחברות.")
                elif not user_email_input or "@" not in user_email_input:
                    st.error("נא להזין כתובת מייל תקינה לקבלת התראות.")
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
    # --- לוח בקרה ראשי (מחובר) ---

    render_logo()

    st.markdown(
        "<h1 class='main-header'>📈 StockScreener Pro - לוח בקרה וניתוח"
        " טכני</h1>",
        unsafe_allow_html=True,
    )
    st.info(
        f"ברוך הבא! המערכת מחוברת לפלטפורמת **{st.session_state['trading_platform']}**, והתראות איתות יכללו קישור ישיר אליה."
    )

    count = st_autorefresh(interval=60000, limit=1000, key="stock_autorefresh")

    alerts = check_and_dispatch_alerts(
        st.session_state["stocks_list"], rsi_buy, rsi_sell
    )

    if alerts:
        st.toast(f"🚨 נלכדו {len(alerts)} איתותים בזמן אמת!", icon="🔔")
        for alt in alerts:
            action_btn_html = f"<a href='{alt['action_link']}' target='_blank' style='background-color: #FF6B00; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-weight: bold;'>⚡ עשה דיל ב-{st.session_state['trading_platform']}</a>"
            st.markdown(
                f"🔔 **{alt['type']}:** {alt['message']} {action_btn_html}",
                unsafe_allow_html=True,
            )

    st.subheader("📊 רשימת מניות במעקב בזמן אמת")
    df = pd.DataFrame(st.session_state["stocks_list"])

    df[f"פתח ב-{st.session_state['trading_platform']}"] = df["סימול"].apply(
        lambda s: generate_broker_link(s, st.session_state["trading_platform"])
    )

    st.dataframe(
        df,
        column_config={
            f"פתח ב-{st.session_state['trading_platform']}": st.column_config.LinkColumn(
                "קישור ישיר", display_text="פתח מניה ↗️"
            )
        },
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("📜 יומן התראות בזמן אמת שנשלחו לאחרונה")
    logs = load_alerts_log()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.write("טרם נרשמו התראות במערכת.")

    if st.session_state["role"] == "admin":
        st.markdown("---")
        st.markdown(
            "<h2 style='color: #FF6B00;'>🛠️ פאנל ניהול מתקדם (Admin)</h2>",
            unsafe_allow_html=True,
        )

        col_adm1, col_adm2 = st.columns(2)

        with col_adm1:
            st.subheader("👥 ניהול מנויים ומשתמשים")
            subs = load_subscribers()
            if subs:
                st.dataframe(pd.DataFrame.from_dict(subs, orient="index"))
            else:
                st.write("אין מנויים רשומים כרגע.")

        with col_adm2:
            st.subheader("📊 סטטיסטיקות ותפעול")
            st.write(f"**סך הכל כניסות ייחודיות:** {current_visitors}")

            if st.button("🔄 איפוס מונה כניסות למערכת"):
                reset_visitor_count()
                st.success("מונה הכניסות אופס בהצלחה!")
                st.rerun()
