import streamlit as st
import yfinance as yf
import pandas as pd
import io
from datetime import datetime, timedelta

# הגדרת עיצוב הדף ופריסה רחבה
st.set_page_config(
    page_title="StockScreener Pro - SR", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב CSS מותאם אישית (כיוון מימין לשמאל + רקע מדורג כתום ולוגו SR-שר)
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 50%, #FED7AA 100%);
        background-attachment: fixed;
    }
    h1, h2, h3 {
        text-align: center;
        color: #9A3412;
    }
    p, label, .stMarkdown {
        text-align: right;
        color: #431407;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #F97316 0%, #C2410C 100%);
        color: white;
        border: none;
        padding: 0.7rem 1rem;
        box-shadow: 0 4px 6px rgba(249, 115, 22, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #EA580C 0%, #9A3412 100%);
        color: white;
    }
    .brand-logo-container {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .brand-logo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%);
        color: white;
        font-size: 2.2rem;
        font-weight: 900;
        width: 85px;
        height: 85px;
        border-radius: 22px;
        box-shadow: 0 10px 20px rgba(194, 65, 12, 0.4);
        letter-spacing: 2px;
        border: 2px solid #FFEDD5;
    }
    .brand-subtitle {
        font-size: 0.95rem;
        color: #7C2D12;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 8px;
    }
    .login-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid #FDBA74;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 15px 25px -5px rgba(234, 88, 12, 0.15);
        margin-bottom: 20px;
    }
    .market-badge {
        display: inline-block;
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        border: 1px solid #FDBA74;
        margin-bottom: 10px;
    }
    .contract-box {
        background-color: rgba(255, 255, 255, 0.95);
        border: 1px solid #FDBA74;
        padding: 20px;
        border-radius: 12px;
        max-height: 200px;
        overflow-y: scroll;
        margin-bottom: 15px;
        font-size: 0.9rem;
        color: #431407;
    }
    .payment-alert {
        background-color: #FEF2F2;
        border: 1px solid #F87171;
        padding: 20px;
        border-radius: 12px;
        color: #991B1B;
        text-align: center;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ניהול בסיס נתונים פנימי לזיכרון המערכת
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}

# מחיר מנוי חודשי דינמי
if 'monthly_price' not in st.session_state:
    st.session_state.monthly_price = 75  # מחיר התחלתי 75 ש"ח כולל מע"מ

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.is_admin = False

# סיסמת מנהל סודית
ADMIN_SECRET_CODE = "999999" 

# --- מסך הזדהות וכניסת משתמשים / מנהל מעוצב ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        # לוגו SR / שר מעוצב
        st.markdown("""
            <div class='brand-logo-container'>
                <div class='brand-logo'>SR</div>
                <div class='brand-subtitle'>שר | Your Next Investment</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center;'><span class='market-badge'>📈 פלטפורמת מסחר וניתוחים טכניים מתקדמים</span></div>", unsafe_allow_html=True)
        st.markdown("<h1>StockScreener Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #7C2D12; font-size: 1.05rem;'>מערכת חכמה לאיתור מניות מובילות, ניתוח RSI וייצור דוחות אקסל וגרפים ויזואליים בקליק אחד.</p>", unsafe_allow_html=True)
        
        # קופסת כניסה מעוצבת
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.subheader("🔐 התחברות לחשבון שלך")
        st.markdown("<p style='color: #7C2D12; font-size: 0.9rem;'>הקליד תעודת זהות (<b>9 ספרות בדיוק</b>) וסיסמה (<b>6 הספרות האחרונות</b> של התעודת זהות)</p>", unsafe_allow_html=True)
        
        user_id = st.text_input("מספר תעודת זהות (9 ספרות / קוד מנהל):").strip()
        user_password = st.text_input("סיסמה (6 ספרות אחרונות / סיסמת מנהל):", type="password").strip()
        
        is_admin_attempt = (user_id == "ADMIN" and user_password == ADMIN_SECRET_CODE)
        
        if is_admin_attempt:
            if st.button("התחבר כמנהל מערכת 🛠️"):
                st.session_state.logged_in = True
                st.session_state.current_user = "ADMIN"
                st.session_state.is_admin = True
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # חוזה התקשרות והסרת אחריות משפטית
        st.markdown("### 📄 תנאי שימוש והסרת אחריות משפטית")
        st.markdown(f"""
        <div class="contract-box">
            <b>1. היעדר ייעוץ השקעות:</b> המערכת מספקת נתונים טכניים, חישובים וכלים סטטיסטיים בלבד ואינה מהווה בשום אופן ייעוץ השקעות, שיווק השקעות או הצעה לקנייה/מכירה של ניירות ערך.<br><br>
            <b>2. אחריות המשתמש:</b> השימוש במידע שמופק במערכת נעשה על אחריותו הבלעדית והמלאה של המשתמש. מפתח המערכת ו/או מפעיליה לא יישאו באחריות כלשהי לכל הפסד, נזק פיננסי או תוצאה ישירה/עקיפה שנגרמו כתוצאה מהסתמכות על הנתונים.<br><br>
            <b>3. תשלום ומנוי חודשי:</b> הלקוח זכאי לחודש ניסיון ראשון חינם. לאחר מכן, דמי השימוש החודשיים במערכת הינם <b>{st.session_state.monthly_price} ש"ח כולל מע"מ</b> לחודש. התשלום מתחדש מדי חודש, ואי-הסדרת תשלום במועד תגרור חסימת גישה זמנית עד לחידושו.
        </div>
        """, unsafe_allow_html=True)
        
        agreed = st.checkbox("אני מאשר/ת שקראתי את תנאי השימוש, הסרת האחריות ומדיניות התשלום ואני מסכים/ה להם.")
        
        if st.button("התחבר למערכת 🚀"):
            if not agreed:
                st.error("❌ עליך לאשר את תנאי השימוש וכתב הסרת האחריות לפני ההתחברות.")
            elif user_id != "ADMIN":
                if not user_id.isdigit() or len(user_id) != 9:
                    st.error("❌ מספר תעודת הזהות חייב להכיל בדיוק 9 ספרות.")
                elif user_password != user_id[-6:]:
                    st.error("❌ הסיסמה שגויה. עליך להזין בדיוק את 6 הספרות האחרונות של מספר תעודת הזהות.")
                else:
                    today = datetime.now().date()
                    
                    if user_id in st.session_state.users_db:
                        user_data = st.session_state.users_db[user_id]
                        join_date = datetime.strptime(user_data["join_date"], "%Y-%m-%d").date()
                        
                        in_first_trial = (today - join_date).days <= 30
                        
                        is_cycle_paid = False
                        if user_data.get("last_payment_date"):
                            last_pay = datetime.strptime(user_data["last_payment_date"], "%Y-%m-%d").date()
                            if (today - last_pay).days <= 30:
                                is_cycle_paid = True
                        
                        if in_first_trial or is_cycle_paid:
                            st.session_state.logged_in = True
                            st.session_state.current_user = user_id
                            st.session_state.is_admin = False
                            st.rerun()
                        else:
                            st.markdown(f"""
                            <div class="payment-alert">
                                <h3>⏳ תקופת הניסיון או מחזור החודש הנוכחי הסתיימו!</h3>
                                <p>כדי להמשיך להשתמש במערכת ללא הפרעה, עליך להסדיר את התשלום החודשי בסך <b>{st.session_state.monthly_price} ש"ח כולל מע"מ</b>.</p>
                                <hr style="border-color: #FCA5A5;">
                                <p style="text-align: right; margin: 0;">💳 <b>איך משלמים?</b><br>
                                • העברה בנקאית / Bit / PayBox למספר הטלפון או החשבון של המערכת.<br>
                                • לאחר ביצוע התשלום, שלח את צילום האסמכתא בוואטסאפ, והמנהל יפתח לך מיד את הגישה לחודש נוסף!</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.session_state.users_db[user_id] = {
                            "join_date": today.strftime("%Y-%m-%d"),
                            "last_payment_date": None
                        }
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_id
                        st.session_state.is_admin = False
                        st.success("🎉 נרשמת בהצלחה! הוענק לך חודש ניסיון חינם למערכת.")
                        st.rerun()

# --- אזור ניהול (מנהל בלבד) ---
elif st.session_state.is_admin:
    st.markdown("<h1>🛠️ פאנל ניהול מנויים ועדכון מחירים</h1>", unsafe_allow_html=True)
    st.write("כאן תוכל לעדכן את מחיר המנוי, לצפות בכל הלקוחות, ולאשר להם חידוש חודשי לאחר ששילמו.")
    
    if st.button("🚪 התנתק מפאנל מנהל"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.is_admin = False
        st.rerun()
        
    st.markdown("---")
    
    st.subheader("⚙️ הגדרת מחיר מנוי חודשי")
    new_price = st.number_input("עדכן מחיר מנוי חודשי (ש״ח כולל מע״מ):", min_value=0, value=st.session_state.monthly_price, step=5)
    if st.button("💾 שמור מחיר חדש"):
        st.session_state.monthly_price = new_price
        st.success(f"✅ המחיר החודשי עודכן בהצלחה ל-{new_price} ש״ח! מעתה הוא יופיע אוטומטית בחוזה ובהודעות התשלום.")

    st.markdown("---")
    
    if len(st.session_state.users_db) == 0:
        st.info("ℹ️ עדיין אין משתמשים רשומים במערכת.")
    else:
        admin_data = []
        today_date = datetime.now().date()
        for uid, uinfo in st.session_state.users_db.items():
            join_d = uinfo["join_date"]
            last_p = uinfo.get("last_payment_date")
            
            join_dt = datetime.strptime(join_d, "%Y-%m-%d").date()
            is_active = (today_date - join_dt).days <= 30
            if last_p:
                last_dt = datetime.strptime(last_p, "%Y-%m-%d").date()
                if (today_date - last_dt).days <= 30:
                    is_active = True
            
            status_str = "פעיל 🟢 (בניסיון או שילם)" if is_active else "דרוש תשלום חודשי 🔴 (פג תוקף)"
            admin_data.append({
                "תעודת זהות": uid, 
                "תאריך הרשמה": join_d, 
                "תשלום אחרון": last_p if last_p else "טרם שילם (תקופת ניסיון)",
                "סטטוס נוכחי": status_str
            })
        
        st.table(pd.DataFrame(admin_data))
        
        st.markdown("### ✍️ אישור תשלום חודשי חדש ללקוח (חידוש מחזור)")
        target_uid = st.text_input("הכנס תעודת זהות של הלקוח ששילם עבור החודש הנוכחי (9 ספרות):").strip()
        if st.button("✅ אישור תשלום ופתיחת גישה לחודש נוסף"):
            if target_uid in st.session_state.users_db:
                st.session_state.users_db[target_uid]["last_payment_date"] = datetime.now().date().strftime("%Y-%m-%d")
                st.success(f"המנוי עבור ת.ז {target_uid} עודכן! הגישה נפתחה לחודש נוסף מעכשיו.")
            else:
                st.error("❌ תעודת זהות זו לא נמצאה במערכת.")

# --- האפליקציה הראשית (מוצגת ללקוחות מורשים) ---
else:
    st.markdown("<h1>📈 StockScreener Pro - SR</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #7C2D12; font-size: 1.1rem; font-weight: normal; text-align: center;'>מערכת מתקדמת לניתוח מניות, איתותי מומנטום, דוחות אקסל וגרפים ויזואליים</h3>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 התנתק מהמערכת"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.markdown("---")

    st.sidebar.header("⚙️ הגדרות ניתוח וסיכון")
    tickers_input = st.sidebar.text_input(
        "הזן סימולי מניות (מופרדים בפסיקים)", 
        value="AAPL, MSFT, GOOGL, AMZN, NVDA, META"
    )

    rsi_buy_threshold = st.sidebar.slider("רף RSI לקנייה", min_value=30, max_value=55, value=45)
    rsi_sell_threshold = st.sidebar.slider("רף RSI למכירה", min_value=50, max_value=75, value=60)

    st.sidebar.markdown("---")
    run_scan = st.sidebar.button("🚀 הפק דו״ח וגרפים עכשיו")

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

                        delta = close_prices.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        data['RSI'] = 100 - (100 / (1 + rs))

                        latest_rsi = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50
                        sma10 = float(close_prices.rolling(window=10).mean().iloc[-1])
                        sma20 = float(close_prices.rolling(window=20).mean().iloc[-1])

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
                st.dataframe(df, use_container_width=True)

                st.markdown("---")
                st.markdown("<h2>📈 השוואת גרפי מחירים (6 חודשים אחרונים)</h2>", unsafe_allow_html=True)
                if chart_data_dict:
                    df_charts = pd.DataFrame(chart_data_dict)
                    st.line_chart(df_charts)

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
