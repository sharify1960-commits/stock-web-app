import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="StockScreener Pro - RS", page_icon="📈", layout="wide")

# עיצוב מותאם אישית: צבעי כתום ולוגו RS
st.markdown("""
    <style>
    .stButton>button {
        background-color: #ff6600;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #e65c00;
        color: white;
    }
    .login-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #ffb74d;
        box-shadow: 0 4px 15px rgba(255, 102, 0, 0.15);
    }
    .rs-logo {
        font-size: 40px;
        font-weight: bold;
        color: #ff6600;
        text-align: center;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_gsheets_connection():
    return st.connection("gsheets", type=GSheetsConnection)

try:
    conn = get_gsheets_connection()
except Exception as e:
    st.error(f"שגיאה בחיבור ל-Google Sheets: {e}")
    st.stop()

# אתחול משתני Session State ומונה כניסות יציב
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 1250
if "has_counted" not in st.session_state:
    st.session_state.visitor_count += 1
    st.session_state.has_counted = True

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="rs-logo">RS 📈</div>', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #d84315;'>StockScreener Pro</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("הכנס אימייל / תעודת זהות / מזהה משתמש:")
            password_input = st.text_input("סיסמה (למנהל בלבד - 999999):", type="password")
            submit_button = st.form_submit_button("התחבר למערכת", use_container_width=True)
            
            if submit_button:
                # בדיקת כניסת מנהל עם הקוד 999999
                if user_input.strip() == "admin" and password_input.strip() == "999999":
                    st.session_state.logged_in = True
                    st.session_state.user_id = "admin"
                    st.success("התחברת בהצלחה כמנהל מערכת!")
                    st.rerun()
                else:
                    try:
                        df_db = conn.read(ttl=0)
                        df_db.columns = df_db.columns.str.strip()
                        
                        id_cols = [col for col in df_db.columns if col.lower() in ['user_id', 'email', 'מייל', 'תז']]
                        if not id_cols:
                            st.error("שגיאה במבנה הגיליון: לא נמצאה עמודת זיהוי או מייל.")
                            return
                        
                        id_col = id_cols[0]
                        df_db[id_col] = df_db[id_col].astype(str).str.strip().str.lower()
                        user_input_clean = str(user_input).strip().lower()
                        
                        user_row = df_db[df_db[id_col] == user_input_clean]
                        
                        if not user_row.empty:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_input.strip()
                            st.success("התחברת בהצלחה!")
                            st.rerun()
                        else:
                            st.error("מזהה משתמש או אימייל לא נמצאו בגיליון. פנה למנהל המערכת.")
                    except Exception as e:
                        st.error(f"שגיאה בהתחברות מול הגיליון: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    show_login_page()
else:
    st.sidebar.title("⚙️ הגדרות סורק ואיתותים")
    st.sidebar.write(f"מחובר כ: **{st.session_state.user_id}**")
    st.sidebar.metric("👥 סה״כ כניסות למערכת", st.session_state.visitor_count)
    
    if st.sidebar.button("🚪 התנתק"):
        st.session_state.logged_in = False
        st.session_state.user_id = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    selected_signal = st.sidebar.selectbox("סינון לפי איתות טכני:", ["הכל", "Buy 🟢", "Sell 🔴"])
    rsi_buy = st.sidebar.slider("סף RSI לקנייה", 0, 100, 45)
    rsi_sell = st.sidebar.slider("סף RSI למכירה", 0, 100, 60)
    
    st.title("📈 StockScreener Pro - RS")
    st.markdown("לוח בקרה מתקדם לניתוח מניות, איתותי קנייה/מכירה, RSI וקישורים ישירים לגרפים.")
    
    data = [
        {"מניה": "AAPL", "איתות טכני": "Sell 🔴", "מחיר סגירה": 325.34, "RSI נוכחי": 73.74, "קישור לגרף": "https://finance.yahoo.com/quote/AAPL"},
        {"מניה": "MSFT", "איתות טכני": "Buy 🟢", "מחיר סגירה": 496.82, "RSI נוכחי": 50.61, "קישור לגרף": "https://finance.yahoo.com/quote/MSFT"},
        {"מניה": "GOOGL", "איתות טכני": "Buy 🟢", "מחיר סגירה": 337.64, "RSI נוכחי": 39.63, "קישור לגרף": "https://finance.yahoo.com/quote/GOOGL"},
        {"מניה": "AMZN", "איתות טכני": "Buy 🟢", "מחיר סגירה": 254.60, "RSI נוכחי": 39.58, "קישור לגרף": "https://finance.yahoo.com/quote/AMZN"},
        {"מניה": "NVDA", "איתות טכני": "Sell 🔴", "מחיר סגירה": 225.10, "RSI נוכחי": 49.85, "קישור לגרף": "https://finance.yahoo.com/quote/NVDA"},
        {"מניה": "META", "איתות טכני": "Sell 🔴", "מחיר סגירה": 592.36, "RSI נוכחי": 48.93, "קישור לגרף": "https://finance.yahoo.com/quote/META"},
    ]
    
    df = pd.DataFrame(data)
    if selected_signal != "הכל":
        filtered_df = df[df["איתות טכני"] == selected_signal]
    else:
        filtered_df = df
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("סה״כ מניות במעקב", len(df))
    with col2:
        buy_count = len(df[df["איתות טכני"].str.contains("Buy")])
        st.metric("המלצות קנייה (Buy)", buy_count, delta="🟢")
    with col3:
        sell_count = len(df[df["איתות טכני"].str.contains("Sell")])
        st.metric("המלצות מכירה (Sell)", sell_count, delta="🔴")
    
    st.divider()
    st.subheader("📊 טבלת דו\"ח מניות יומי")
    st.dataframe(
        filtered_df,
        column_config={
            "קישור לגרף": st.column_config.LinkColumn(
                "קישור לגרף Yahoo",
                display_text="צפה בגרף 📈"
            )
        },
        use_container_width=True
    )
    
    st.markdown("---")
    with st.expander("ℹ️ מי אנחנו / אודות המערכת"):
        st.write("מערכת **StockScreener Pro - RS** פותחה כדי לספק כלי ניתוח טכני מהיר, ממוקד ויעיל למשקיעים.")
        st.write("המערכת משלבת עיצוב מותאם אישית בצבעי כתום ולוגו RS, אימות משתמשים ואימיילים מול Google Sheets, ומונה כניסות יציב.")
