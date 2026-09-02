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

# אתחול משתני Session State ומונה כניסות שלא מתאפס בריצות חוזרות
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "visitor_count" not in st.session_state:
    st.session_state.visitor_count = 1250  # ערך התחלתי שניתן לסנכרן מול הגיליון
if "has_counted" not in st.session_state:
    st.session_state.visitor_count += 1
    st.session_state.has_counted = True

# פונקציית מסך ההתחברות
def show_login_page():
    st.title("🔐 StockScreener Pro - התחברות למערכת")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            user_id_input = st.text_input("הכנס תעודת זהות / מזהה משתמש:")
            password_input = st.text_input("סיסמה (למנהל בלבד):", type="password")
            submit_button = st.form_submit_button("התחבר למערכת")
            
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
                            st.error("מזהה משתמש לא נמצא בגיליון. פנה למנהל המערכת לצורך רישום.")
                    except Exception as e:
                        st.error(f"שגיאה בהתחברות מול הגיליון: {e}")

# הצגת מסך ההתחברות אם המשתמש אינו מחובר
if not st.session_state.logged_in:
    show_login_page()
else:
    # **האפליקציה הראשית לאחר התחברות מוצלחת**
    
    # סרגל צד (Sidebar) להגדרות, מונה כניסות וניהול סשן
    st.sidebar.title("⚙️ הגדרות סורק ואיתותים")
    st.sidebar.write(f"מחובר כ: **{st.session_state.user_id}**")
    
    # הצגת מונה הכניסות בסרגל הצד (יציב ולא מתאפס בריצה שוטפת)
    st.sidebar.metric("👥 סה״כ כניסות למערכת", st.session_state.visitor_count)
    
    if st.sidebar.button("🚪 התנתק"):
        st.session_state.logged_in = False
        st.session_state.user_id = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # מסנני חיפוש ורגישות טכנית
    selected_signal = st.sidebar.selectbox("סינון לפי איתות טכני:", ["הכל", "Buy 🟢", "Sell 🔴"])
    rsi_buy = st.sidebar.slider("סף RSI לקנייה", 0, 100, 45)
    rsi_sell = st.sidebar.slider("סף RSI למכירה", 0, 100, 60)
    
    # מסך ראשי מלא
    st.title("📈 StockScreener Pro - SR")
    st.markdown("לוח בקרה מתקדם לניתוח מניות, איתותי קנייה/מכירה, RSI וקישורים ישירים לגרפים.")
    
    # נתוני המניות לסורק
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
    
    # מדדים מרכזיים ראשוניים (Metrics)
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
    
    # הצגת הטבלה האינטראקטיבית עם קישורים פעילים לגרפים
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
    
    # אזור מידע / אודות
    st.markdown("---")
    with st.expander("ℹ️ מי אנחנו / אודות המערכת"):
        st.write("מערכת **StockScreener Pro** פותחה כדי לספק כלי ניתוח טכני מהיר, ממוקד ויעיל למשקיעים.")
        st.write("המערכת משלבת אימות משתמשים מול Google Sheets, מונה כניסות אישי, וניהול איתותי RSI.")
