import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

# הגדרת מאפייני עמוד
st.set_page_config(page_title="StockScreener Pro - SR", page_icon="📈", layout="wide")

# חיבור ל-Google Sheets באמצעות GSheetsConnection
@st.cache_resource
def get_gsheets_connection():
    return st.connection("gsheets", type=GSheetsConnection)

try:
    conn = get_gsheets_connection()
except Exception as e:
    st.error(f"שגיאה בחיבור ל-Google Sheets: {e}")
    st.stop()

# אתחול משתני Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

# פונקציית מסך ההתחברות
def show_login_page():
    st.title("🔐 StockScreener Pro - התחברות למערכת")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            user_id_input = st.text_input("הכנס תעודת זהות / מזהה משתמש:")
            password_input = st.text_input("סיסמה (למנהל בלבד):", type="password")
            submit_button = st.form_submit_button("התחבר / הירשם למערכת")
            
            if submit_button:
                # בדיקת כניסת מנהל (Admin)
                if user_id_input.strip() == "admin" and password_input.strip() == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user_id = "admin"
                    st.success("התחברת בהצלחה כמנהל מערכת!")
                    st.rerun()
                else:
                    try:
                        # קריאת הנתונים מגיליון גוגל
                        df_db = conn.read(ttl=0)
                        df_db.columns = df_db.columns.str.strip()
                        
                        # מציאת עמודת מזהה המשתמש בצורה חסינה לרווחים ואותיות
                        id_cols = [col for col in df_db.columns if col.lower() == 'user_id']
                        if not id_cols:
                            st.error("שגיאה במבנה הגיליון: לא נמצאה עמודת User_ID.")
                            return
                        
                        id_col = id_cols[0]
                        df_db[id_col] = df_db[id_col].astype(str).str.strip()
                        user_id_clean = str(user_id_input).strip()
                        
                        user_row = df_db[df_db[id_col] == user_id_clean]
                        
                        if not user_row.empty:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id_clean
                            st.success("התחברת בהצלחה!")
                            st.rerun()
                        else:
                            st.error("מזהה משתמש לא נמצא בגיליון. פנה למנהל המערכת.")
                    except Exception as e:
                        st.error(f"שגיאה בהתחברות מול הגיליון: {e}")

# הצגת מסך ההתחברות אם המשתמש אינו מחובר
if not st.session_state.logged_in:
    show_login_page()
else:
    # **האפליקציה הראשית לאחר התחברות מוצלחת**
    
    # סרגל צד (Sidebar) להגדרות ולניהול סשן
    st.sidebar.title("⚙️ הגדרות סורק")
    st.sidebar.write(f"מחובר כ: **{st.session_state.user_id}**")
    
    if st.sidebar.button("🚪 התנתק"):
        st.session_state.logged_in = False
        st.session_state.user_id = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # קלטים לבחירת מניות ורגישות טכנית
    tickers_input = st.sidebar.text_input("סימולי מניות (מופרדים בפסיקים)", "AAPL, MSFT, GOOGL, NVDA")
    rsi_buy = st.sidebar.slider("סף RSI לקנייה", 0, 100, 45)
    rsi_sell = st.sidebar.slider("סף RSI למכירה", 0, 100, 60)
    
    # מסך ראשי מלא
    st.title("StockScreener Pro - SR 📈")
    st.markdown("ברוך הבא למערכת ניתוח המניות והסריקה הטכנית המתקדמת שלך.")
    
    # אזור הצגת הסורק והתוצאות
    st.subheader("תוצאות ניתוח מניות")
    
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    sample_data = []
    for ticker in tickers:
        sample_data.append({
            "סימול": ticker,
            "סף קנייה מוגדר": rsi_buy,
            "סף מכירה מוגדר": rsi_sell,
            "סטטוס": "פעיל לסריקה"
        })
    
    df_results = pd.DataFrame(sample_data)
    st.dataframe(df_results, use_container_width=True)
    
    # אזור מידע / אודות
    st.markdown("---")
    with st.expander("ℹ️ מי אנחנו / אודות המערכת"):
        st.write("מערכת **StockScreener Pro** פותחה כדי לספק כלי ניתוח טכני מהיר, ממוקד ויעיל למשקיעים.")
        st.write("המערכת מאפשרת מעקב אישי, הגדרת ספי רגישות (RSI) וניהול נתונים שוטף.")
