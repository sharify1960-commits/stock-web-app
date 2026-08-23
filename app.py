import streamlit as st
import yfinance as yf
import pandas as pd
import io
from datetime import datetime, timedelta

# הגדרת עיצוב הדף ופריסה רחבה
st.set_page_config(
    page_title="StockScreener Pro", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב CSS מותאם אישית (כיוון מימין לשמאל)
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #F8FAFC;
    }
    h1, h2, h3 {
        text-align: center;
        color: #1E3A8A;
    }
    p, label, .stMarkdown {
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white;
        border: none;
        padding: 0.7rem 1rem;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
        color: white;
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
    }
    </style>
""", unsafe_allow_html=True)

# ניהול בסיס נתונים פנימי (לדוגמה: שמירת תאריך הרשמה וסטטוס תשלום)
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        # דוגמה ללקוח ששילם כבר: "123456789": {"join_date": "2026-01-01", "paid": True}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- מסך הזדהות וכניסת משתמשים ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1>🔐 כניסת לקוחות למערכת</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>הזן את מספר תעודת הזהות שלך ו-6 הספרות האחרונות כסיסמה</p>", unsafe_allow_html=True)
        
        user_id = st.text_input("מספר תעודת זהות:")
        user_password = st.text_input("סיסמה (6 ספרות אחרונות של הת.ז):", type="password")
        
        # חוזה התקשרות והסרת אחריות משפטית
        st.markdown("### 📄 תנאי שימוש והסרת אחריות משפטית")
        st.markdown("""
        <div class="contract-box">
            <b>1. היעדר ייעוץ השקעות:</b> המערכת מספקת נתונים טכניים, חישובים וכלים סטטיסטיים בלבד ואינה מהווה בשום אופן ייעוץ השקעות, שיווק השקעות או הצעה לקנייה/מכירה של ניירות ערך.<br><br>
            <b>2. אחריות המשתמש:</b> השימוש במידע שמופק במערכת נעשה על אחריותו הבלעדית והמלאה של המשתמש. מפתח המערכת ו/או מפעיליה לא יישאו באחריות כלשהי לכל הפסד, נזק פיננסי או תוצאה ישירה/עקיפה שנגרמו כתוצאה מהסתמכות על הנתונים.<br><br>
            <b>3. תשלום ומנוי:</b> הלקוח זכאי לחודש ניסיון ראשון חינם. לאחר מכן, יש להסדיר את התשלום החודשי מול מנהל המערכת. אי-הסדרת תשלום תגרור חסימת גישה למערכת עד לחידושה.
        </div>
        """, unsafe_allow_html=True)
        
        agreed = st.checkbox("אני מאשר/ת שקראתי את תנאי השימוש, הסרת האחריות ומדיניות התשלום ואני מסכים/ה להם.")
        
        if st.button("התחבר למערכת"):
            if not agreed:
                st.error("❌ עליך לאשר את תנאי השימוש וכתב הסרת האחריות לפני ההתחברות.")
            elif len(user_id) >= 6 and user_password == user_id[-6:]:
                today = datetime.now().date()
                
                # בדיקה האם המשתמש קיים במערכת
                if user_id in st.session_state.users_db:
                    user_data = st.session_state.users_db[user_id]
                    join_date = datetime.strptime(user_data["join_date"], "%Y-%m-%d").date()
                    days_passed = (today - join_date).days
                    
                    # בדיקה האם בתקופת ניסיון (30 יום) או ששילם
                    if days_passed <= 30 or user_data.get("paid", False):
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_id
                        st.rerun()
                    else:
                        st.warning("⏳ תקופת הניסיון החינמית שלך (30 יום) הסתיימה.")
                        st.info("💳 **להסדרת תשלום:** אנא העבר את דמי המנוי ב-Bit / העברה בנקאית ושלח אסמכתא לוואטסאפ או למייל של המערכת כדי שנפתח לך את החשבון מיד.")
                else:
                    # משתמש חדש לגמרי - פותחים לו חודש ניסיון חינם אוטומטית
                    st.session_state.users_db[user_id] = {
                        "join_date": today.strftime("%Y-%m-%d"),
                        "paid": False
                    }
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_id
                    st.success("🎉 נרשמת בהצלחה! הוענק לך חודש ניסיון חינם למערכת.")
                    st.rerun()
            else:
                st.error("❌ מספר תעודת זהות או סיסמה שגויים (יש לוודא שהוזנו 6 הספרות האחרונות הנכונות).")

# --- האפליקציה הראשית (מוצגת רק לאחר התחנות ומעבר בדיקה) ---
else:
    # כותרת ראשית מעוצבת
    st.markdown("<h1>⚡ StockScreener Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #64748B; font-size: 1.1rem; font-weight: normal; text-align: center;'>מערכת מתקדמת לניתוח מניות, איתותי מומנטום, דוחות אקסל וגרפים ויזואליים</h3>", unsafe_allow_html=True)
    
    # כפתור התנתקות קטן בצד
    if st.sidebar.button("🚪 התנתק מהמערכת"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.markdown("---")

    # --- סרגל צד (Sidebar) ---
    st.sidebar.header("⚙️ הגדרות ניתוח וסיכון")
    tickers_input = st.sidebar.text_input(
        "הזן סימולי מניות (מופרדים בפסיקים)", 
        value="AAPL, MSFT, GOOGL, AMZN, NVDA, META"
    )

    rsi_buy_threshold = st.sidebar.slider("רף RSI לקנייה", min_value=30, max_value=55, value=45)
    rsi_sell_threshold = st.sidebar.slider("רף RSI למכירה", min_value=50, max_value=75, value=60)

    st.sidebar.markdown("---")
    run_scan = st.sidebar.button("🚀 הפק דו״ח וגרפים עכשיו")

    # --- אזור הצגת הנתונים ---
    if run_scan:
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        
        if not tickers:
            st.warning("⚠️ אנא הזן לפחות סימול מניה אחד תקין.")
        else:
            with st.spinner(f"🔍 מבצע סריקה ויזואלית עבור {len(tickers)} מניות... אנא המתן"):
                results = []
                chart_data_dict = {}
                progress_bar = st.progress(0)
                total = len(tickers)

                for i, ticker in enumerate(tickers):
                    try:
                        stock = yf.Ticker(ticker)
                        data = stock.history(period='6mo')
                        
                        if data.empty or len(data) < 20:
                            continue

                        close_prices = data['Close']
                        chart_data_dict[ticker] = close_prices
                        
                        current_price = float(close_prices.iloc[-1])
                        daily_return = ((current_price - float(close_prices.iloc[-2])) / float(close_prices.iloc[-2])) * 100 if len(close_prices) >= 2 else 0
                        weekly_return = ((current_price - float(close_prices.iloc[-5])) / float(close_prices.iloc[-5])) * 100 if len(close_prices) >= 5 else 0
                        monthly_return = ((current_price - float(close_prices.iloc[-21])) / float(close_prices.iloc[-21])) * 100 if len(close_prices) >= 21 else 0

                        # מתנדים
                        delta = close_prices.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        data['RSI'] = 100 - (100 / (1 + rs))

                        latest_rsi = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50
                        sma10 = float(close_prices.rolling(window=10).mean().iloc[-1])
                        sma20 = float(close_prices.rolling(window=20).mean().iloc[-1])

                        # איתותים
                        signal = 'Hold 🟡'
                        if sma10 > sma20 and latest_rsi < (rsi_buy_threshold + 20):
                            signal = 'Buy 🟢'
                        elif latest_rsi < rsi_buy_threshold: 
                            signal = 'Buy 🟢'
                        elif sma10 < sma20 and latest_rsi > (rsi_sell_threshold - 20):
                            signal = 'Sell 🔴'
                        elif latest_rsi > rsi_sell_threshold:
                            signal = 'Sell 🔴'

                        results.append({
                            'מניה': ticker,
                            'איתות טכני': signal,
                            'מחיר נוכחי': round(current_price, 2),
                            'יומי (%)': round(daily_return, 2),
                            'שבועי (%)': round(weekly_return, 2),
                            'חודשי (%)': round(monthly_return, 2),
                            'RSI נוכחי': round(latest_rsi, 2)
                        })
                    except Exception as e:
                        pass
                    
                    progress_bar.progress((i + 1) / total)

            if len(results) > 0:
                df = pd.DataFrame(results)
                
                st.success("✨ הסריקה הושלמה בהצלחה! הנה נתוני המניות והגרפים הויזואליים:")
                
                # הצגת טבלה חיה מעוצבת
                st.dataframe(df, use_container_width=True)

                # הצגת גרף ויזואלי חי לכל המניות שנבחרו
                st.markdown("---")
                st.markdown("<h2>📈 השוואת גרפי מחירים (6 חודשים אחרונים)</h2>", unsafe_allow_html=True)
                if chart_data_dict:
                    df_charts = pd.DataFrame(chart_data_dict)
                    st.line_chart(df_charts)

                # הכנת קובץ אקסל להורדה
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Stock Report')
                
                excel_data = output.getvalue()

                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 הורד דו״ח אקסל מלא ומעוצב",
                    data=excel_data,
                    file_name="stocks_professional_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("❌ לא נמצאו נתונים עבור המניות שהוזנו.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👈 בחר את המניות ורמות הסיכון בסרגל הצד משמאל, ולחץ על **'הפק דו״ח וגרפים עכשיו'** כדי לצפות בנתונים וגרפים חזותיים.")
