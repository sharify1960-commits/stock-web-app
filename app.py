import streamlit as st
import pandas as pd
import datetime

# Page configuration
st.set_page_config(
    page_title="StockScreener Pro",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS styling (orange branding, containers, inputs)
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1f2937;
        text-align: center;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .contract-box {
        background-color: #ffffff;
        border: 1px solid #CBD5E1;
        padding: 20px;
        border-radius: 10px;
        max-height: 250px;
        overflow-y: scroll;
        margin-bottom: 15px;
        font-size: 0.9rem;
        color: #334155;
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%);
        color: white;
        border: none;
        padding: 0.7rem 1rem;
        box-shadow: 0 4px 6px rgba(230, 81, 0, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #E65100 0%, #C43E00 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = ""

# Login Screen
if not st.session_state["logged_in"]:
    # Logo / Branding HTML
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
    st.markdown("<p style='text-align: center; color: #64748b;'>הזן את מספר תעודת הזהות שלך ו-6 הספרות האחרונות כסיסמה</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("מספר תעודת זהות:")
        password = st.text_input("סיסמה (6 ספרות אחרונות של הת.ז.):", type="password")
        
        st.markdown("<h4 style='text-direction: rtl; text-align: right; color: #1e293b; font-size: 1rem;'>📋 תנאי שימוש והסרת אחריות משפטית</h4>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="contract-box">
            <b>1. היעדר ייעוץ השקעות:</b> המערכת מספקת נתונים טכניים, חישובים וכלים סטטיסטיים בלבד ואינה מהווה בשום אופן ייעוץ השקעות, שיווק השקעות או הצעה לקנייה/מכירה של ניירות ערך.<br><br>
            <b>2. אחריות המשתמש:</b> השימוש במידע שמופק במערכת נעשה על אחריותו בלבד והמלאה של המשתמש. מפתח המערכת ו/או מפעיליה לא יישאו באחריות כלשהי לכל הפסד, נזק פיננסי או תוצאה ישירה/עקיפה שנגרמו כתוצאה מהסתמכות על הנתונים.<br><br>
            <b>3. תשלום ומנוי:</b> הלקוח זכאי לחודש ניסיון ראשון חינם. לאחר מכן, יש להסדיר את התשלום החודשי מול מנהל המערכת. אי-הסדרת תשלום תגרור חסימת גישה למערכת עד לחדישה.
        </div>
        """, unsafe_allow_html=True)
        
        agree = st.checkbox("אני מאשר/ת שקראתי את תנאי השימוש, הסרת האחריות ומדיניות התשלום ואני מסכים/ה להם.")
        
        submit_button = st.form_submit_button("התחבר למערכת")
        
        if submit_button:
            # Admin bypass check
            if username == "admin" and password == "999999":
                st.session_state["logged_in"] = True
                st.session_state["role"] = "admin"
                st.rerun()
            elif not agree:
                st.error("יש לאשר את תנאי השימוש והסרת האחריות לפני ההתחברות.")
            elif username and password:
                if len(password) >= 4:
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "user"
                    st.rerun()
                else:
                    st.error("מספר תעודת זהות או סיסמה שגוים (יש לוודא שהוזנו 6 הספרות האחרונות).")
            else:
                st.error("נא למלא מספר תעודת זהות וסיסמה.")

else:
    # Main Dashboard after login
    st.sidebar.title("🧭 ניווט במערכת")
    st.sidebar.write(f"מחובר כ: **{st.session_state['role']}**")
    
    if st.sidebar.button("התנתק"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = ""
        st.rerun()
        
    st.markdown("<h1 class='main-header'>📈 StockScreener Pro - לוח בקרה</h1>", unsafe_allow_html=True)
    st.success("ברוך הבא למערכת ניתוח המניות המתקדמת!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="מניות במעקב", value="42", delta="+3")
    with col2:
        st.metric(label="מניות במומנטום חיובי", value="18", delta="4.2%")
    with col3:
        st.metric(label="סטטוס חיבור", value="פעיל 🟢", delta="Google Sheets")
        
    st.markdown("---")
    st.subheader("נתוני שוק לדוגמה")
    
    data = {
        "סימול": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
        "שם חברה": ["Apple Inc.", "Microsoft Corp.", "Alphabet Inc.", "Amazon.com", "NVIDIA Corp."],
        "מחיר ($)": [189.50, 415.20, 142.80, 178.25, 875.40],
        "שינוי יומי (%)": ["+1.2%", "-0.5%", "+2.1%", "+0.8%", "+3.4%"],
        "המלצה": ["קנייה", "החזק", "קנייה", "קנייה", "חזק מאוד"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)