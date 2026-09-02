import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# Page configuration
st.set_page_config(
    page_title="StockScreener Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUBSCRIBERS_FILE = "subscribers.json"

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

# Custom CSS styling
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-header { font-size: 2.3rem; color: #1f2937; text-align: center; font-weight: 700; margin-bottom: 1rem; }
    .contract-box {
        background-color: #ffffff; border: 1px solid #CBD5E1; padding: 20px;
        border-radius: 10px; max-height: 250px; overflow-y: scroll;
        margin-bottom: 15px; font-size: 0.9rem; color: #334155; direction: rtl; text-align: right;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold;
        background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%);
        color: white; border: none; padding: 0.7rem 1rem;
        box-shadow: 0 4px 6px rgba(230, 81, 0, 0.3);
    }
    .stButton>button:hover { background: linear-gradient(135deg, #E65100 0%, #C43E00 100%); color: white; }
    .info-box {
        background-color: #e2e8f0; border-right: 4px solid #FF6B00;
        padding: 10px 15px; border-radius: 4px; font-size: 0.85rem;
        color: #1e293b; margin-bottom: 10px; direction: rtl; text-align: right;
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

if "stocks_list" not in st.session_state:
    st.session_state["stocks_list"] = [
        {"סימול": "AAPL", "שם חברה": "Apple Inc.", "מחיר ($)": 189.50, "RSI": 45.2, "מגמת SMA": "חיובית", "שינוי יומי (%)": "+1.2%", "המלצה": "קנייה"},
        {"סימול": "MSFT", "שם חברה": "Microsoft Corp.", "מחיר ($)": 415.20, "RSI": 58.1, "מגמת SMA": "חיובית", "שינוי יומי (%)": "-0.5%", "המלצה": "החזק"},
        {"סימול": "GOOGL", "שם חברה": "Alphabet Inc.", "מחיר ($)": 142.80, "RSI": 32.4, "מגמת SMA": "תיקון", "שינוי יומי (%)": "+2.1%", "המלצה": "קנייה לבחינה"},
        {"סימול": "AMZN", "שם חברה": "Amazon.com", "מחיר ($)": 178.25, "RSI": 68.9, "מגמת SMA": "חזקה", "שינוי יומי (%)": "+0.8%", "המלצה": "קנייה"},
        {"סימול": "NVDA", "שם חברה": "NVIDIA Corp.", "מחיר ($)": 875.40, "RSI": 74.2, "מגמת SMA": "חזקה מאוד", "שינוי יומי (%)": "+3.4%", "המלצה": "חזק מאוד"}
    ]

# Login Screen
if not st.session_state["logged_in"]:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <div style="display: inline-block; background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%); padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(230,81,0,0.3); color: white; width: 140px; height: 140px;">
                <div style="font-size: 38px; font-weight: bold; letter-spacing: 2px;">SR</div>
                <div style="font-size: 20px; margin-top: 5px; font-weight: 600;">שר</div>
            </div>
            <h3 style="margin-top: 15px; color: #334155; font-size: 1.1rem;">השקעה הבאה שלך | YOUR NEXT INVESTMENT 📊</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; color: #1e293b;'>כניסת לקוחות למערכת 🔐</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>הזן תעודת זהות, כתובת מייל (חובה לקבלת דוחות אוטומטיים) וסיסמה</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("מספר תעודת זהות:")
            user_email_input = st.text_input("כתובת מייל (חובה):")
            password = st.text_input("סיסמה (6 ספרות אחרונות של הת.ז.):", type="password")
            
            st.markdown("<h4 style='direction: rtl; text-align: right; color: #1e293b; font-size: 1rem;'>📋 תנאי שימוש והסרת אחריות משפטית</h4>", unsafe_allow_html=True)
            st.markdown("""
            <div class="contract-box">
                <b>1. היעדר ייעוץ השקעות:</b> המערכת מספקת נתונים טכניים בלבד ואינה מהווה ייעוץ השקעות.<br><br>
                <b>2. אחריות המשתמש:</b> השימוש במידע נעשה על אחריות המשתמש בלבד.<br><br>
                <b>3. שליחה אוטומטית:</b> עם ההתחברות, המייל יצורף לקבלת הדוח היומי האוטומטי בשעה 17:30. ניתן לבטל זאת בכל עת מהתפריט.
            </div>
            """, unsafe_allow_html=True)
            
            agree = st.checkbox("אני מאשר/ת שקראתי את תנאי השימוש ומסכים/ה לקבלת דוחות אוטומטיים.")
            submit_button = st.form_submit_button("התחבר למערכת")
            
            if submit_button:
                if username == "admin" and password == "999999":
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "admin"
                    st.session_state["user_email"] = user_email_input if user_email_input else "admin@admin.com"
                    st.rerun()
                elif not agree:
                    st.error("יש לאשר את תנאי השימוש לפני ההתחברות.")
                elif not user_email_input or "@" not in user_email_input:
                    st.error("נא להזין כתובת מייל תקינה לקבלת הדוח.")
                elif len(password) >= 4:
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "user"
                    st.session_state["user_email"] = user_email_input
                    
                    subs = load_subscribers()
                    subs[user_email_input] = {"active": True, "id": username}
                    save_subscribers(subs)
                    
                    st.rerun()
                else:
                    st.error("מספר תעודת זהות או סיסמה שגוים.")

else:
    # Sidebar & Dashboard
    st.sidebar.title("🧭 ניווט וניהול פרמטרים")
    st.sidebar.write(f"מחובר כ: **{st.session_state['role']}**")
    st.sidebar.write(f"מייל: **{st.session_state['user_email']}**")
    
    subs = load_subscribers()
    current_email = st.session_state["user_email"]
    is_active_sub = subs.get(current_email, {}).get("active", True)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ ניהול שליחה אוטומטית")
    
    if is_active_sub:
        st.sidebar.info("הדוח היומי מוגדר להישלח אליך אוטומטית בכל יום ב-17:30.")
        if st.sidebar.button("🛑 ביטול שליחה אוטומטית לדוח"):
            subs[current_email]["active"] = False
            save_subscribers(subs)
            st.sidebar.success("השליחה האוטומטית בוטלה בהצלחה.")
            st.rerun()
    else:
        st.sidebar.warning("השליחה האוטומטית לדוח זה מושבתת עבורך.")
        if st.sidebar.button("✅ הפעל מחדש שליחה אוטומטית"):
            subs[current_email]["active"] = True
            save_subscribers(subs)
            st.sidebar.success("השליחה האוטומטית הופעלה מחדש.")
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ סרגלי ניתוח טכני ופרמטרים")
    
    rsi_buy = st.sidebar.slider("סף קנייה יתר (Oversold RSI):", min_value=10, max_value=40, value=30, step=1)
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> מדד RSI נמוך מסף זה מסמן שנכס נסחר ביתר מכירה ויכול להוות הזדמנות כניסה.</div>', unsafe_allow_html=True)
    
    rsi_sell = st.sidebar.slider("סף מכירת יתר (Overbought RSI):", min_value=60, max_value=90, value=70, step=1)
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> מדד RSI גבוה מסף זה מצביע על נכס במצב קניית יתר וסיכון לתיקון חד.</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### ממוצעים נעים (Moving Averages)")
    ma_short = st.sidebar.selectbox("תקופת ממוצע קצר (SMA Short):", [10, 20, 50], index=1)
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> משקף את מומנטום המחירים בטווח הקצר.</div>', unsafe_allow_html=True)
    
    ma_long = st.sidebar.selectbox("תקופת ממוצע ארוך (SMA Long):", [100, 150, 200], index=2)
    st.sidebar.markdown('<div class="info-box"><b>הסבר שדה:</b> מגדיר את המגמה הראשית של השוק לטווח הארוך.</div>', unsafe_allow_html=True)

    # Add new stock section in sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("➕ הוספת מניה חדשה למערכת")
    with st.sidebar.form("add_stock_form"):
        new_symbol = st.text_input("סימול מניה (למשל TSLA):")
        new_name = st.text_input("שם חברה מלא:")
        new_price = st.number_input("מחיר ($):", min_value=0.1, value=100.0)
        new_rsi = st.number_input("ערך RSI:", min_value=0.0, max_value=100.0, value=50.0)
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
    if st.sidebar.button("התנתק"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = ""
        st.session_state["user_email"] = ""
        st.rerun()

    # Main Dashboard View
    st.markdown("<h1 class='main-header'>📈 StockScreener Pro - לוח בקרה וניתוח טכני</h1>", unsafe_allow_html=True)
    st.success("ברוך הבא למערכת ניתוח המניות! הדוח היומי יישלח אליך אוטומטית בסיום המסחר (17:30) כל עוד השליחה מופעלת.")
    
    df = pd.DataFrame(st.session_state["stocks_list"])
    df["קישור לגרף"] = df["סימול"].apply(lambda s: f"https://finance.yahoo.com/quote/{s}")
    
    st.dataframe(
        df,
        width='stretch',
        column_config={
            "קישור לגרף": st.column_config.LinkColumn("צפה בגרף חיצוני (Yahoo Finance)", display_text="פתח גרף 📈")
        }
    )
