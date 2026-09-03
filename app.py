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
VISITORS_FILE = "visitors.json"
COUNTER_FILE = "counter.json"

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

# Custom CSS styling with proper RTL alignment and bold text for all fields and labels
st.markdown("""
<style>
    .stApp { 
        background: linear-gradient(0deg, #A7521C 0%, #C8692A 10%, #DF8542 30%, #EFA466 80%);
        background-attachment: fixed;
    }
    .main-header { font-size: 2.6rem; color: #ffffff; text-align: center; font-weight: 800; margin-bottom: 1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4); }
    
    /* Enhanced button styling for maximum boldness and size */
    .stButton>button, [data-testid="stFormSubmitButton"]>button {
        width: 100% !important; 
        border-radius: 14px !important; 
        font-weight: 950 !important; 
        font-size: 1.5rem !important;
        background: linear-gradient(135deg, #FF6B00 0%, #D85A00 100%) !important;
        color: white !important; 
        border: 3px solid #FFFFFF !important; 
        padding: 1rem 1rem !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5) !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
    }
    .stButton>button:hover, [data-testid="stFormSubmitButton"]>button:hover { 
        background: linear-gradient(135deg, #D85A00 0%, #B54900 100%) !important; 
        color: white !important; 
    }
    
    .stTextInput input {
        font-weight: 800 !important;
        font-size: 1.1rem !important;
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
        font-size: 1.18rem !important;
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
            <div style="display: inline-block; background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%); padding: 50px; border-radius: 35px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); color: white; width: 260px; height: 260px;">
                <div style="font-size: 75px; font-weight: 900; letter-spacing: 3px; line-height: 160px; color: #FFFFFF;">SR</div>
            </div>
            <h3 style="margin-top: 25px; color: #ffffff; font-size: 2.1rem; font-weight: 900; line-height: 1.4; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">
                YOUR NEXT SMART INVESTMENT<br>ההשקעה החכמה הבאה שלך 📊
            </h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; color: #ffffff; font-size: 2rem; font-weight: 900; margin-top: 20px; text-shadow: 0 2px 4px rgba(0,0,0,0.4);'>כניסת לקוחות למערכת 🔐</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #ffffff; font-size: 1.15rem; font-weight: 700; text-shadow: 0 1px 3px rgba(0,0,0,0.4);'>הזן מספר תעודת זהות, כתובת מייל וסיסמה</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.3rem; direction: rtl; text-align: right;">מספר תעודת זהות / מנהל:</p>', unsafe_allow_html=True)
            username = st.text_input("מספר תעודת זהות / מנהל:", label_visibility="collapsed")
            
            st.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.3rem; direction: rtl; text-align: right;">כתובת מייל (חובה):</p>', unsafe_allow_html=True)
            user_email_input = st.text_input("כתובת מייל (חובה):", label_visibility="collapsed")
            
            st.markdown('<p style="color: #FF6B00; font-weight: 950; font-size: 1.3rem; direction: rtl; text-align: right;">סיסמה:</p>', unsafe_allow_html=True)
            password = st.text_input("סיסמה:", type="password", label_visibility="collapsed")
            
            st.markdown("<h4 style='direction: rtl; text-align: right; color: #FF6B00; font-size: 1.4rem; font-weight: 900; text-shadow: 0 1px 3px rgba(0,0,0,0.6);'>📋 תנאי שימוש, הצהרת מומחיות והגנה משפטית</h4>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color: #ffffff; border: 2px solid #000000; padding: 18px; border-radius: 10px; margin-bottom: 15px; direction: rtl; text-align: right; color: #000000;">
                <table style="width: 100%; border-collapse: collapse; font-size: 1rem; color: #000000;">
                    <tr style="line-height: 1.6;">
                        <td style="vertical-align: top; width: 25px; font-weight: 900;">1.</td>
                        <td style="vertical-align: top; font-weight: 950; padding-left: 10px; white-space: nowrap;">ייעוד המערכת (למבינים בלבד):</td>
                        <td style="vertical-align: top; font-weight: 700;">אפליקציה זו מיועדת אך ורק למשתמשים בעלי ידע והבנה עמוקה בניתוח טכני בשווקים הפיננסיים.</td>
                    </tr>
                    <tr style="line-height: 1.6;">
                        <td style="vertical-align: top; width: 25px; font-weight: 900;">2.</td>
                        <td style="vertical-align: top; font-weight: 950; padding-left: 10px; white-space: nowrap;">אחריות מסחר מלאה:</td>
                        <td style="vertical-align: top; font-weight: 700;">כל פעולות המסחר וההשקעה נעשות על אחריות המשתמש הבלעדית. המערכת אינה נושאת באחריות לכל הפסד פיננסי.</td>
                    </tr>
                    <tr style="line-height: 1.6;">
                        <td style="vertical-align: top; width: 25px; font-weight: 900;">3.</td>
                        <td style="vertical-align: top; font-weight: 950; padding-left: 10px; white-space: nowrap;">קניין רוחני והגנה משפטית:</td>
                        <td style="vertical-align: top; font-weight: 700;">כל הזכויות שמורות מפני העתקה, שכפול או הפצה בלתי מורשית. המערכת מוגנת מפני כל תביעה משפטית.</td>
                    </tr>
                    <tr style="line-height: 1.6;">
                        <td style="vertical-align: top; width: 25px; font-weight: 900;">4.</td>
                        <td style="vertical-align: top; font-weight: 950; padding-left: 10px; white-space: nowrap;">שליחה אוטומטית:</td>
                        <td style="vertical-align: top; font-weight: 700;">עם ההתחברות, המייל יצורף לקבלת הדוח היומי האוטומטי בשעה 17:30. ניתן לבטל זאת בכל עת מהתפריט.</td>
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
                    subs[user_email_input] = {"active": True, "id": username}
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
        
        if st.sidebar.button("🔄 איפוס מונה פיילוט"):
            save_counter(0)
            st.sidebar.success("המונה אופס בהצלחה ל-0!")
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown('<h3 style="color: #FF6B00; font-weight: 900; direction: rtl; text-align: right;">⚙️ ניהול שליחה אוטומטית</h3>', unsafe_allow_html=True)
    
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
    st.success("ברוך הבא למערכת ניתוח המניות! הדוח היומי יישלח אליך אוטומטית בסיום המסחר (17:30) כל עוד השליחה מופעלת.")
    
    df = pd.DataFrame(st.session_state["stocks_list"])
    df["קישור לגרף"] = df["סימול"].apply(lambda s: f"https://finance.yahoo.com/quote/{s}")
    
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "קישור לגרף": st.column_config.LinkColumn("צפה בגרף חיצוני (Yahoo Finance)", display_text="פתח גרף 📈")
        }
    )
