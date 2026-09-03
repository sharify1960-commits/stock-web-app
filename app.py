import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import requests

# Page configuration
st.set_page_config(
    page_title="StockScreener Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
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
    logs.insert(0, alert_item)  # Keep latest first
    with open(ALERTS_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs[:50], f, ensure_ascii=False, indent=4)  # Keep last 50 alerts

def check_and_dispatch_alerts(stocks_list, rsi_buy_threshold, rsi_sell_threshold):
    """
    סורקת את רשימת המניות ומזהה איתותים בזמן אמת לפי הפרמטרים שנקבעו
    """
    subs = load_subscribers()
    active_emails = [email for email, info in subs.items() if info.get("active", True)]
    triggered_alerts = []

    for stock in stocks_list:
        symbol = stock["סימול"]
        price = stock["מחיר ($)"]
        rsi = stock["RSI"]

        # איתות קנייה
        if rsi <= rsi_buy_threshold:
            alert_data = {
                "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "type": "BUY",
                "price": price,
                "rsi": rsi,
                "message": f"🚨 איתות קנייה בזמן אמת! המניה {symbol} הגיעה ל-RSI של {rsi} (מחיר: ${price})"
            }
            triggered_alerts.append(alert_data)
            save_alert_log(alert_data)

        # איתות מכירה
        elif rsi >= rsi_sell_threshold:
            alert_data = {
                "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "type": "SELL",
                "price": price,
                "rsi": rsi,
                "message": f"⚠️ איתות מכירה/מימוש! המניה {symbol} הגיעה ל-RSI של {rsi} (מחיר: ${price})"
            }
            triggered_alerts.append(alert_data)
            save_alert_log(alert_data)

    return triggered_alerts, active_emails

# Custom CSS styling with Mobile Responsiveness
st.markdown("""
<style>
    .stApp { 
        background: linear-gradient(0deg, #A7521C 0%, #C8692A 10%, #DF8542 30%, #EFA466 80%);
        background-attachment: fixed;
    }
    .main-header { 
        font-size: 2.2rem; 
        color: #ffffff; 
        text-align: center; 
        font-weight: 800; 
        margin-bottom: 1rem; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.4); 
    }
    
    /* Enhanced button styling */
    .stButton>button, [data-testid="stFormSubmitButton"]>button {
        width: 100% !important; 
        border-radius: 14px !important; 
        font-weight: 950 !important; 
        font-size: 1.3rem !important;
        background: linear-gradient(135deg, #FF6B00 0%, #D85A00 100%) !important;
        color: white !important; 
        border: 2px solid #FFFFFF !important; 
        padding: 0.8rem 1rem !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5) !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
    }
    .stButton>button:hover, [data-testid="stFormSubmitButton"]>button:hover { 
        background: linear-gradient(135deg, #D85A00 0%, #B54900 100%) !important; 
        color: white !important; 
    }
    
    .stTextInput input {
        font-weight: 800 !important;
        font-size: 1rem !important;
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #333333 !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stCheckbox {
        direction: rtl !important;
        text-align: right !important;
    }
    .stCheckbox label {
        direction: rtl !important;
        text-align: right !important;
        display: flex !important;
        align-items: flex-start !important;
        width: 100% !important;
    }
    .stCheckbox label span, .stCheckbox div[data-testid="stMarkdownContainer"] p {
        font-weight: 900 !important;
        font-size: 1.05rem !important;
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.7);
        direction: rtl !important;
        text-align: right !important;
        width: 100% !important;
    }
    
    .info-box {
        background-color: #ffffff; border-right: 4px solid #FF6B00; border: 1px solid #CBD5E1;
        padding: 10px 15px; border-radius: 4px; font-size: 0.95rem; font-weight: 700;
        color: #000000; margin-bottom: 10px; direction: rtl; text-align: right;
    }

    /* Mobile Responsive Rules */
    @media (max-width: 768px) {
        .main-header { font-size: 1.6rem !important; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .logo-box { width: 160px !important; height: 160px !important; padding: 20px !important; }
        .logo-text { font-size: 50px !important; line-height: 120px !important; }
        .terms-table td { display: block !important; width: 100% !important; padding: 2px 0 !important; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = ""
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "pilot_counted" not in st.session_state:
    st.session_state["pilot_counted"] = False

if "visited" not in st.session_state:
    st.session_state["visited"] = True
    current_visitors = increment_visitor_count()
else:
    current_visitors = get_visitor_count()

if "stocks_list" not in st.session_state:
    st.session_state["stocks_list"] = [
        {"סימול": "AAPL", "שם חברה": "Apple Inc.", "מחיר ($)": 189.50, "RSI": 28.5, "מגמת SMA": "חיובית", "שינוי יומי (%)": "+1.2%", "המלצה": "קנייה"},
        {"סימול": "MSFT", "שם חברה": "Microsoft Corp.", "מחיר ($)": 415.20, "RSI": 58.1, "מגמת SMA": "חיובית", "שינוי יומי (%)": "-0.5%", "המלצה": "החזק"},
        {"סימול": "GOOGL", "שם חברה": "Alphabet Inc.", "מחיר ($)": 142.80, "RSI": 32.4, "מגמת SMA": "תיקון", "שינוי יומי (%)": "+2.1%", "המלצה": "קנייה לבחינה"},
        {"סימול": "AMZN", "שם חברה": "Amazon.com", "מחיר ($)": 178.25, "RSI": 68.9, "מגמת SMA": "חזקה", "שינוי יומי (%)": "+0.8%", "המלצה": "קנייה"},
        {"סימול": "NVDA", "שם חברה": "NVIDIA Corp.", "מחיר ($)": 875.40, "RSI": 74.2, "מגמת SMA": "חזקה מאוד", "שינוי יומי (%)": "+3.4%", "המלצה": "חזק מאוד"}
    ]

# Login Screen
if not st.session_state["logged_in"]:
    col_l1, col_l2, col_l3 = st.columns([0.1, 0.8, 0.1])
    with col_l2:
        st.markdown("""
        <div style="text-align: center; margin-top: 10px;">
            <div class="logo-box" style="display: inline-block; background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%); padding: 30px; border-radius: 30px; box-shadow: 0 8px 20px rgba(0,0,0,0.4); color: white; width: 180px; height: 180px;">
                <div class="logo-text" style="font-size: 60px; font-weight: 900; letter-spacing: 2px; line-height: 120px; color: #FFFFFF;">SR</div>
            </div>
            <h3 style="margin-top: 15px; color: #ffffff; font-size: 1.6rem; font-weight: 900; line-height: 1.3; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">
                YOUR NEXT SMART INVESTMENT<br>ההשקעה החכמה הבאה שלך 📊
            </h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; color: #ffffff; font-size: 1.6rem; font-weight: 900; margin-top: 15px; text-shadow: 0 2px 4px rgba(0,0,0,0.4);'>כניסת לקוחות למערכת 🔐</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #ffffff; font-size: 1rem; font-weight: 700; text-shadow: 0 1px 3px rgba(0,0,0,0.4);'>הזן מספר תעודת זהות, כתובת מייל וסיסמה</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<p style="color: #ffffff; font-weight: 950; font-size: 1.1rem; direction: rtl; text-align: right; margin-bottom: 2px;">מספר תעודת זהות / מנהל:</p>', unsafe_allow_html=True)
            username = st.text_input("מספר תעודת זהות / מנהל:", label_visibility="collapsed")
            
            st.markdown('<p style="color: #ffffff; font-weight: 950; font-size: 1.1rem; direction: rtl; text-align: right; margin-bottom: 2px;">כתובת מייל (חובה):</p>', unsafe_allow_html=True)
            user_email_input = st.text_input("כתובת מייל (חובה):", label_visibility="collapsed")
            
            st.markdown('<p style="color: #ffffff; font-weight: 950; font-size: 1.1rem; direction: rtl; text-align: right; margin-bottom: 2px;">סיסמה:</p>', unsafe_allow_html=True)
            password = st.text_input("סיסמה:", type="password", label_visibility="collapsed")
            
            st.markdown('<p style="color: #ffffff; font-weight: 950; font-size: 1.05rem; direction: rtl; text-align: right; margin-top: 10px; margin-bottom: 2px;">💡 מה המחיר השנתי המרבי שהיית מוכן לשלם על המערכת? (סקר ללא התחייבות):</p>', unsafe_allow_html=True)
            annual_price_pref = st.selectbox(
                "מחיר שנתי:",
                ["טרם נבחר", "עד 150 ש\"ח לשנה", "150 - 300 ש\"ח לשנה", "300 - 500 ש\"ח לשנה", "מעל 500 ש\"ח לשנה"],
                label_visibility="collapsed"
            )
            
            st.markdown("<h4 style='direction: rtl; text-align: right; color: #ffffff; font-size: 1.2rem; font-weight: 900; margin-top: 15px;'>📋 תנאי שימוש, הצהרת מומחיות והגנה משפטית</h4>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color: #ffffff; border: 2px solid #000000; padding: 12px; border-radius: 10px; margin-bottom: 15px; direction: rtl; text-align: right; color: #000000;">
                <table class="terms-table" style="width: 100%; border-collapse: collapse; font-size: 0.95rem; color: #000000;">
                    <tr style="line-height: 1.5; border-bottom: 1px solid #ddd;">
                        <td style="vertical-align: top; font-weight: 950; padding: 4px 0;">1. ייעוד המערכת (למבינים בלבד):</td>
                        <td style="vertical-align: top; font-weight: 700; padding: 4px 0;">אפליקציה זו מיועדת אך ורק למשתמשים בעלי ידע והבנה עמוקה בניתוח טכני בשווקים הפיננסיים.</td>
                    </tr>
                    <tr style="line-height: 1.5; border-bottom: 1px solid #ddd;">
                        <td style="vertical-align: top; font-weight: 950; padding: 4px 0;">2. אחריות מסחר מלאה:</td>
                        <td style="vertical-align: top; font-weight: 700; padding: 4px 0;">כל פעולות המסחר וההשקעה נעשות על אחריות המשתמש הבלעדית. המערכת אינה נושאת באחריות לכל הפסד פיננסי.</td>
                    </tr>
                    <tr style="line-height: 1.5; border-bottom: 1px solid #ddd;">
                        <td style="vertical-align: top; font-weight: 950; padding: 4px 0;">3. קניין רוחני והגנה משפטית:</td>
                        <td style="vertical-align: top; font-weight: 700; padding: 4px 0;">כל הזכויות שמורות מפני העתקה, שכפול או הפצה בלתי מורשית. המערכת מוגנת מפני כל תביעה משפטית.</td>
                    </tr>
                    <tr style="line-height: 1.5;">
                        <td style="vertical-align: top; font-weight: 950; padding: 4px 0;">4. שליחה אוטומטית והתראות בזמן אמת:</td>
                        <td style="vertical-align: top; font-weight: 700; padding: 4px 0;">המייל יצורף לקבלת הדוח היומי (17:30) והתראות בזמן אמת בעת זיהוי איתותי קנייה/מכירה. ניתן לבטל בכל עת.</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            agree = st.checkbox("אני מאשר/ת שקראתי והבנתי את תנאי השימוש, שאני מבין/ה בניתוח טכני, שהמסחר על אחריותי בלבד, ושכל הזכויות שמורות.")
            submit_button = st.form_submit_button("התחבר למערכת")
            
            if submit_button:
                if username.strip().lower() == "admin" and password == "999999":
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "admin"
                    st.session_state["user_email"] = user_email_input if user_email_input else "admin@admin.com"
                    st.rerun()
                elif not agree:
                    st.error("יש לאשר את תנאי השימוש, ההצהרה והגנת הזכויות לפני ההתחברות.")
                elif not user_email_input or "@" not in user_email_input:
                    st.error("נא להזין כתובת מייל תקינה לקבלת הדוח.")
                elif len(password) >= 4:
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "user"
                    st.session_state["user_email"] = user_email_input
                    
                    subs = load_subscribers()
                    subs[user_email_input] = {
                        "active": True, 
                        "id": username,
                        "expected_annual_price": annual_price_pref
                    }
                    save_subscribers(subs)
                    
                    st.rerun()
                else:
                    st.error("מספר תעודת זהות או סיסמה שגוים.")

else:
    if st.session_state["role"] == "user" and not st.session_state["pilot_counted"]:
        increment_counter()
        st.session_state["pilot_counted"] = True

    # Sidebar & Dashboard
    st.sidebar.markdown('<h2 style="color: #FF6B00; font-weight: 900; direction: rtl; text-align: right;">🧭 ניווט וניהול פרמטרים</h2>', unsafe_allow_html=True)
    st.sidebar.write(f"מחובר כ: **{st.session_state['role']}**")
    st.sidebar.write(f"מייל: **{st.session_state['user_email']}**")
    
    subs = load_subscribers()
    current_email = st.session_state["user_email"]
    is_active_sub = subs.get(current_email, {}).get("active", True)
    
    if st.session_state["role"] == "admin":
        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3 style="color: #FF6B00; font-weight: 900; direction: rtl; text-align: right;">🔐 אזור ניהול פיילוט ומנויים</h3>', unsafe_allow_html=True)
        
        current_counter = load_counter()
        total_subs = len(subs)
        
        st.sidebar.metric(label="📊 מונה פיילוט (Counter)", value=current_counter)
        st.sidebar.metric(label="👥 סך מנויים פעילים", value=total_subs)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3 style="color: #FF6B00; font-weight: 900; direction: rtl; text-align: right;">📊 סיכום סקר תמחור</h3>', unsafe_allow_html=True)
        
        prices_list = [data.get("expected_annual_price", "טרם נבחר") for data in subs.values()]
        
        if prices_list:
            price_summary = pd.Series(prices_list).value_counts().reset_index()
            price_summary.columns = ["טווח מחיר מוצע", "כמות בוחרים"]
            st.sidebar.dataframe(price_summary, use_container_width=True, hide_index=True)
        else:
            st.sidebar.info("טרם התקבלו תשובות לסקר.")
        
        if st.sidebar.button("🔄 איפוס מונה פיילוט"):
            save_counter(0)
            st.sidebar.success("המונה אופס בהצלחה ל-0!")
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown('<h3 style="color: #FF6B00; font-weight: 900; direction: rtl; text-align: right;">⚙️ ניהול שליחה אוטומטית</h3>', unsafe_allow_html=True)
    
    if is_active_sub:
        st.sidebar.info("הדוח היומי והתראות איתות בזמן אמת מוגדרים להישלח אליך למייל.")
        if st.sidebar.button("🛑 ביטול שליחה אוטומטית לדוח"):
            subs[current_email]["active"] = False
            save_subscribers(subs)
            st.sidebar.success("השליחה האוטומטית בוטלה בהצלחה.")
            st.rerun()
    else:
        st.sidebar.warning("השליחה האוטומטית לדוח והתראות מושבתת עבורך.")
        if st.sidebar.button("✅ הפעל מחדש שליחה אוטומטית"):
            subs[current_email]["active"] = True
            save_subscribers(subs)
            st.sidebar.success("השליחה האוטומטית הופעלה מחדש.")
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown('<h3 style="color: #FF6B00; font-weight: 900; direction: rtl; text-align: right;">⚙️ סרגלי ניתוח טכני ופרמטרים</h3>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">סף קנייה יתר (Oversold RSI):</p>', unsafe_allow_html=True)
    rsi_buy = st.sidebar.slider("סף קנייה יתר (Oversold RSI):", min_value=10, max_value=40, value=30, step=1, label_visibility="collapsed")
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> מדד RSI נמוך מסף זה מסמן שנכס נסחר ביתר מכירה ויכול להוות הזדמנות כניסה.</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">סף מכירת יתר (Overbought RSI):</p>', unsafe_allow_html=True)
    rsi_sell = st.sidebar.slider("סף מכירת יתר (Overbought RSI):", min_value=60, max_value=90, value=70, step=1, label_visibility="collapsed")
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> מדד RSI גבוה מסף זה מצביע על נכס במצב קניית יתר וסיכון לתיקון חד.</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.2rem; direction: rtl; text-align: right;">ממוצעים נעים (Moving Averages)</p>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">תקופת ממוצע קצר (SMA Short):</p>', unsafe_allow_html=True)
    ma_short = st.sidebar.selectbox("תקופת ממוצע קצר (SMA Short):", [10, 20, 50], index=1, label_visibility="collapsed")
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> משקף את מומנטום המחירים בטווח הקצר.</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">תקופת ממוצע ארוך (SMA Long):</p>', unsafe_allow_html=True)
    ma_long = st.sidebar.selectbox("תקופת ממוצע ארוך (SMA Long):", [100, 150, 200], index=2, label_visibility="collapsed")
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> מגדיר את המגמה הראשית של השוק לטווח הארוך.</div>', unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown('<h3 style="color: #FF6B00; font-weight: 900; direction: rtl; text-align: right;">➕ הוספת מניה חדשה למערכת</h3>', unsafe_allow_html=True)
    with st.sidebar.form("add_stock_form"):
        st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">סימול מניה (למשל TSLA):</p>', unsafe_allow_html=True)
        new_symbol = st.text_input("סימול מניה (למשל TSLA):", label_visibility="collapsed")
        
        st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">שם חברה מלא:</p>', unsafe_allow_html=True)
        new_name = st.text_input("שם חברה מלא:", label_visibility="collapsed")
        
        st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">מחיר ($):</p>', unsafe_allow_html=True)
        new_price = st.number_input("מחיר ($):", min_value=0.1, value=100.0, label_visibility="collapsed")
        
        st.sidebar.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.15rem; direction: rtl; text-align: right; margin-bottom: 0px;">ערך RSI:</p>', unsafe_allow_html=True)
        new_rsi = st.number_input("ערך RSI:", min_value=0.0, max_value=100.0, value=50.0, label_visibility="collapsed")
        
        add_btn = st.form_submit_button("הוסף מניה למעקב")
        
        if add_btn and new_symbol and new_name:
            st.session_state["stocks_list"].append({
                "סימול": new_symbol.upper(),
                "שם חברה": new_name,
                "מחיר ($)": new_price,
                "RSI": new_rsi,
                "מגמת SMA": "ניטרלי",
                "שינוי יומי (%)": "+0.0%",
                "המלצה": "בדיקה"
            })
            st.sidebar.success(f"המניה {new_symbol.upper()} נוספה בהצלחה!")

    st.sidebar.markdown("---")
    st.sidebar.metric(label="סך כניסות למערכת (קבוע)", value=f"{current_visitors:,}")

    st.sidebar.markdown("---")
    if st.sidebar.button("התנתק"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = ""
        st.session_state["user_email"] = ""
        st.session_state["visited"] = False
        st.session_state["pilot_counted"] = False
        st.rerun()

    # Main Dashboard View
    st.markdown("<h1 class='main-header'>📈 StockScreener Pro - לוח בקרה וניתוח טכני</h1>", unsafe_allow_html=True)
    st.success("ברוך הבא למערכת ניתוח המניות! הדוח היומי והתראות בזמן אמת פעילים עבורך.")

    # Real-Time Alert Scanner Bar
    st.markdown("### 🔔 מנוע סריקת איתותים בזמן אמת")
    col_a1, col_a2 = st.columns([0.7, 0.3])
    with col_a1:
        st.markdown(f"**סף קנייה נוכחי (RSI):** `{rsi_buy}` | **סף מכירה נוכחי (RSI):** `{rsi_sell}`")
    with col_a2:
        if st.button("⚡ הרץ סריקת איתותים עכשיו"):
            alerts, subscribers_list = check_and_dispatch_alerts(st.session_state["stocks_list"], rsi_buy, rsi_sell)
            if alerts:
                st.toast(f"🚨 נשלחו {len(alerts)} התראות בזמן אמת ל-{len(subscribers_list)} מנויים!", icon="🔔")
                for alt in alerts:
                    if alt["type"] == "BUY":
                        st.success(f"**איתות קנייה שנשלח:** {alt['message']}")
                    else:
                        st.warning(f"**איתות מכירה שנשלח:** {alt['message']}")
            else:
                st.info("לא זוהו איתותים חדשים החורגים מספי ה-RSI שהוגדרו.")

    # Table View
    df = pd.DataFrame(st.session_state["stocks_list"])
    df["קישור לגרף"] = df["סימול"].apply(lambda s: f"https://finance.yahoo.com/quote/{s}")
    
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "קישור לגרף": st.column_config.LinkColumn("צפה בגרף חיצוני (Yahoo Finance)", display_text="פתח גרף 📈")
        }
    )

    # Historical Alerts Log View
    st.markdown("---")
    st.markdown("### 📜 יומן התראות בזמן אמת שנשלחו לאחרונה")
    logs = load_alerts_log()
    if logs:
        log_df = pd.DataFrame(logs)
        log_df.columns = ["זמן שליחה", "סימול", "סוג איתות", "מחיר ($)", "RSI", "הודעה שנשלחה"]
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("טרם נרשמו התראות בזמן אמת ביומן.")
