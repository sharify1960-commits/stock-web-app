import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="StockScreener Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        font-size: 2.3rem;
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
    .info-box {
        background-color: #e2e8f0;
        border-right: 4px solid #FF6B00;
        padding: 10px 15px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #1e293b;
        margin-bottom: 10px;
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for login and stocks data
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = ""

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
        st.markdown("<p style='text-align: center; color: #64748b;'>הזן את מספר תעודת הזהות שלך ו-6 הספרות האחרונות כסיסמה</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("מספר תעודת זהות:")
            password = st.text_input("סיסמה (6 ספרות אחרונות של הת.ז.):", type="password")
            
            st.markdown("<h4 style='direction: rtl; text-align: right; color: #1e293b; font-size: 1rem;'>📋 תנאי שימוש והסרת אחריות משפטית</h4>", unsafe_allow_html=True)
            
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
    st.sidebar.title("🧭 ניווט וניהול פרמטרים")
    st.sidebar.write(f"מחובר כ: **{st.session_state['role']}**")
    
    if st.sidebar.button("התנתק"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = ""
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

    # Main Page Content
    st.markdown("<h1 class='main-header'>📈 StockScreener Pro - לוח בקרה וניתוח טכני</h1>", unsafe_allow_html=True)
    st.success("ברוך הבא למערכת ניתוח המניות המתקדמת! לחץ על הקישור בטבלה כדי לפתוח את הגרף החיצוני של המניה.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="מניות פעילות במסנן", value=str(len(st.session_state["stocks_list"])), delta="+1")
    with col2:
        st.metric(label="מניות במומנטום RSI", value="18", delta="4.2%")
    with col3:
        st.metric(label="ממוצע שוק כללי", value="+1.8%", delta="חיובי 🟢")
    with col4:
        st.metric(label="סטטוס חיבור", value="פעיל 🟢", delta="Google Sheets")
        
    st.markdown("---")
    st.subheader("📊 תוצאות סריקת מניות וקישורים לגרפים")
    
    df = pd.DataFrame(st.session_state["stocks_list"])
    df["קישור לגרף"] = df["סימול"].apply(lambda s: f"https://finance.yahoo.com/quote/{s}")
    
    st.dataframe(
        df,
        width='stretch',
        column_config={
            "קישור לגרף": st.column_config.LinkColumn("צפה בגרף חיצוני (Yahoo Finance)", display_text="פתח גרף 📈")
        }
    )
    
    st.markdown("---")
    st.subheader("📉 ניתוח גרפי מורחב למניה נבחרת")
    selected_stock = st.selectbox("בחר מניה להצגת גרף מפורט:", [item["סימול"] for item in st.session_state["stocks_list"]])
    
    if selected_stock:
        st.write(f"הצגת מגמת מחירים היסטורית עבור: **{selected_stock}**")
        chart_data = pd.DataFrame(
            np.random.randn(20, 3) * 5 + 100,
            columns=['מחיר פתיחה', 'גבוה', 'נמוך']
        )
        st.line_chart(chart_data)
