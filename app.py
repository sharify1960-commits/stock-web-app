import streamlit as st
import yfinance as yf
import pandas as pd
import io
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

# הגדרת עיצוב הדף
st.set_page_config(
    page_title="StockScreener Pro - SR", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב CSS מותאם אישית
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 50%, #FED7AA 100%);
        background-attachment: fixed;
    }
    h1, h2, h3 { text-align: center; color: #85330a; }
    p, label, .stMarkdown { text-align: right; color: #431407; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #ff7e1d 0%, #d64d00 50%, #993300 100%);
        color: white;
        border: 1px solid #ffd1a4;
        padding: 0.7rem 1rem;
        box-shadow: 0 4px 15px rgba(214, 77, 0, 0.4);
    }
    .brand-logo-container { text-align: center; margin-top: 25px; margin-bottom: 30px; }
    .diamond-logo {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 160px;
        height: 160px;
        background: linear-gradient(135deg, #ff8c1a 0%, #d64d00 50%, #852e00 100%);
        transform: rotate(45deg);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(184, 69, 0, 0.5);
        border: 4px double #ffdbb5;
        margin: 25px auto;
    }
    .diamond-content { transform: rotate(-45deg); text-align: center; color: #FFF7ED; }
    .diamond-title-en { font-size: 2.4rem; font-weight: 900; }
    .diamond-title-he { font-size: 1.8rem; font-weight: bold; }
    .brand-subtitle { font-size: 1.05rem; color: #993300; font-weight: 800; text-transform: uppercase; margin-top: 15px; }
    .login-card {
        background: linear-gradient(145deg, #ffe5cc 0%, #ffd1a4 50%, #ffbe80 100%);
        border: 2px solid #e67300;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 15px 35px -5px rgba(204, 82, 0, 0.3);
        margin-bottom: 20px;
    }
    .contract-box {
        background: #fff3e6;
        border: 1.5px solid #ff9933;
        padding: 20px;
        border-radius: 12px;
        max-height: 200px;
        overflow-y: scroll;
        margin-bottom: 15px;
    }
    .payment-alert {
        background: #ffe6e6;
        border: 1.5px solid #e60000;
        padding: 20px;
        border-radius: 12px;
        color: #800000;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# חיבור ל-Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(ttl="0m")
    except Exception:
        return pd.DataFrame(columns=['User_ID', 'Join_Date', 'Last_Payment_Date', 'Email', 'Is_Exempt', 'Logins_Count'])

def save_data(df):
    conn.update(data=df)

# טעינת הנתונים מהגיליון
df_db = load_data()

# הגדרת משתני מערכת בבסיס הנתונים אם אינם קיימים
if 'monthly_price' not in st.session_state:
    st.session_state.monthly_price = 75

DEFAULT_PAYMENT_MSG = (
    "💳 איך משלמים?\n"
    "• העברה בנקאית: בנק יהב (04), סניף 120, מספר חשבון 292521.\n"
    "• Bit / PayBox למספר הטלפון 0507634366.\n"
    "• לאחר ביצוע התשלום, שלח את צילום האסמכתא בוואטסאפ למספר 0507634366 יחד עם שם מלא ות.ז לקבלת קבלה ופתיחת הגישה!"
)

if 'payment_message_template' not in st.session_state:
    st.session_state.payment_message_template = DEFAULT_PAYMENT_MSG

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.is_admin = False

ADMIN_SECRET_CODE = "999999"

# פונקציה לעדכון כניסה ב-Google Sheets
def register_login(user_id, email=""):
    global df_db
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # עדכון מונה כולל
    total_idx = df_db[df_db['User_ID'] == 'TOTAL_LOGINS'].index
    if not total_idx.empty:
        curr_count = int(df_db.loc[total_idx[0], 'Logins_Count']) if pd.notnull(df_db.loc[total_idx[0], 'Logins_Count']) else 0
        df_db.loc[total_idx[0], 'Logins_Count'] = curr_count + 1
    else:
        new_row = pd.DataFrame([{'User_ID': 'TOTAL_LOGINS', 'Join_Date': today_str, 'Last_Payment_Date': '', 'Email': '', 'Is_Exempt': False, 'Logins_Count': 1}])
        df_db = pd.concat([df_db, new_row], ignore_index=True)

    # עדכון מונה אישי למשתמש
    user_idx = df_db[df_db['User_ID'] == user_id].index
    if not user_idx.empty:
        u_count = int(df_db.loc[user_idx[0], 'Logins_Count']) if pd.notnull(df_db.loc[user_idx[0], 'Logins_Count']) and str(df_db.loc[user_idx[0], 'Logins_Count']).isdigit() else 0
        df_db.loc[user_idx[0], 'Logins_Count'] = u_count + 1
        if email:
            df_db.loc[user_idx[0], 'Email'] = email
    else:
        new_user = pd.DataFrame([{
            'User_ID': user_id, 
            'Join_Date': today_str, 
            'Last_Payment_Date': '', 
            'Email': email, 
            'Is_Exempt': False, 
            'Logins_Count': 1
        }])
        df_db = pd.concat([df_db, new_user], ignore_index=True)
        
    save_data(df_db)

# --- מסך הזדהות ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        st.markdown("""
            <div class='brand-logo-container'>
                <div class='diamond-logo'>
                    <div class='diamond-content'>
                        <div class='diamond-title-en'>SR</div>
                        <div class='diamond-title-he'>שר</div>
                    </div>
                </div>
                <div class='brand-subtitle'>📈 Your Next Investment | ההשקעה הבאה שלך</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h1>StockScreener Pro</h1>", unsafe_allow_html=True)
        
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.subheader("🔐 התחברות או הרשמה למערכת")
        
        user_id = st.text_input("מספר תעודת זהות (9 ספרות / קוד מנהל):").strip()
        user_password = st.text_input("סיסמה (6 ספרות אחרונות של ת.ז / סיסמת מנהל):", type="password").strip()
        user_email = st.text_input("כתובת אימייל לקבלת דו״ח מניות יומי (אופציונלי):").strip()
        
        if user_id == "ADMIN" and user_password == ADMIN_SECRET_CODE:
            if st.button("התחבר כמנהל מערכת 🛠️"):
                st.session_state.logged_in = True
                st.session_state.current_user = "ADMIN"
                st.session_state.is_admin = True
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        agreed = st.checkbox("אני מאשר/ת שקראתי את תנאי השימוש ומדיניות התשלום.")
        
        if st.button("התחבר / הירשם למערכת 🚀"):
            if not agreed:
                st.error("❌ עליך לאשר את תנאי השימוש לפני ההתחברות.")
            elif user_id != "ADMIN":
                if not user_id.isdigit() or len(user_id) != 9:
                    st.error("❌ תעודת הזהות חייבת להכיל 9 ספרות בדיוק.")
                elif user_password != user_id[-6:]:
                    st.error("❌ הסיסמה שגויה. עליך להזין את 6 הספרות האחרונות של ת.ז.")
                else:
                    today = datetime.now().date()
                    user_rows = df_db[df_db['User_ID'] == user_id]
                    
                    is_exempt = False
                    if not user_rows.empty:
                        is_exempt = str(user_rows.iloc[0]['Is_Exempt']).upper() == 'TRUE'
                    
                    if is_exempt:
                        register_login(user_id, user_email)
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_id
                        st.session_state.is_admin = False
                        st.rerun()
                    
                    if not user_rows.empty:
                        join_date_str = str(user_rows.iloc[0]['Join_Date'])
                        last_pay_str = str(user_rows.iloc[0]['Last_Payment_Date'])
                        
                        join_dt = datetime.strptime(join_date_str, "%Y-%m-%d").date() if join_date_str else today
                        in_trial = (today - join_dt).days <= 30
                        
                        paid = False
                        if last_pay_str and last_pay_str != 'nan' and last_pay_str != 'None':
                            last_p_dt = datetime.strptime(last_pay_str, "%Y-%m-%d").date()
                            paid = (today - last_p_dt).days <= 30
                        
                        if in_trial or paid:
                            register_login(user_id, user_email)
                            st.session_state.logged_in = True
                            st.session_state.current_user = user_id
                            st.session_state.is_admin = False
                            st.rerun()
                        else:
                            st.markdown(f"""
                            <div class="payment-alert">
                                <h3>⏳ תקופת הניסיון או המנוי הסתיימו</h3>
                                <p>להסדרת המנוי בסך <b>{st.session_state.monthly_price} ש"ח</b>:</p>
                                <p style="white-space: pre-line;">{st.session_state.payment_message_template}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        register_login(user_id, user_email)
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_id
                        st.session_state.is_admin = False
                        st.success("🎉 נרשמת בהצלחה! הוענק לך חודש ניסיון חינם.")
                        st.rerun()

# --- פאנל ניהול (מנהל בלבד) ---
elif st.session_state.is_admin:
    st.markdown("<h1>🛠️ פאנל ניהול (קשר ישיר ל-Google Sheets)</h1>", unsafe_allow_html=True)
    
    total_logins_row = df_db[df_db['User_ID'] == 'TOTAL_LOGINS']
    total_count = total_logins_row.iloc[0]['Logins_Count'] if not total_logins_row.empty else 0
    
    st.info(f"📊 סך כניסות כללי שנרשמו ב-Google Sheets: **{total_count}** כניסות.")
    
    if st.button("🚪 התנתק מפאנל מנהל"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.is_admin = False
        st.rerun()
        
    st.markdown("---")
    st.subheader("📋 רשימת משתמשים ומונה כניסות אישי")
    
    users_display = df_db[df_db['User_ID'] != 'TOTAL_LOGINS']
    st.dataframe(users_display, use_container_width=True)
    
    st.markdown("---")
    st.subheader("✍️ עדכון תשלומים ופטורים")
    target_uid = st.text_input("הכנס תעודת זהות (9 ספרות):").strip()
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ אישור תשלום חודשי"):
            idx = df_db[df_db['User_ID'] == target_uid].index
            if not idx.empty:
                df_db.loc[idx[0], 'Last_Payment_Date'] = datetime.now().strftime("%Y-%m-%d")
                save_data(df_db)
                st.success(f"התשלום חודש בהצלחה עבור ת.ז {target_uid}!")
            else:
                st.error("ת.ז לא נמצאה בגיליון.")
    with col_b:
        if st.button("🌟 הגדר / בטל פטור מתשלום"):
            idx = df_db[df_db['User_ID'] == target_uid].index
            if not idx.empty:
                curr_status = str(df_db.loc[idx[0], 'Is_Exempt']).upper() == 'TRUE'
                df_db.loc[idx[0], 'Is_Exempt'] = not curr_status
                save_data(df_db)
                st.success(f"סטטוס פטור עודכן ל-{not curr_status} עבור ת.ז {target_uid}!")
            else:
                st.error("ת.ז לא נמצאה בגיליון.")

# --- אפליקציה ראשית ---
else:
    st.markdown("<h1>📈 StockScreener Pro - SR</h1>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 התנתק"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    tickers_input = st.sidebar.text_input("סימולי מניות", value="AAPL, MSFT, GOOGL, NVDA")
    rsi_buy_threshold = st.sidebar.slider("רף RSI לקנייה", 30, 55, 45)
    rsi_sell_threshold = st.sidebar.slider("רף RSI למכירה", 50, 75, 60)

    if st.sidebar.button("🚀 הפק דו״ח וגרפים"):
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        results = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(period='6mo')
                if not data.empty:
                    c_price = float(data['Close'].iloc[-1])
                    results.append({'מניה': ticker, 'מחיר נוכחי': round(c_price, 2)})
            except Exception:
                pass
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
