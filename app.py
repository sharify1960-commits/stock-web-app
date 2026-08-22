import streamlit as st
import yfinance as yf
import pandas as pd
import io

# הגדרת עיצוב הדף
st.set_page_config(page_title="מערכת סריקת מניות חכמה", page_icon="📈", layout="wide")

st.title("📈 מערכת ניתוח מניות ואיתותים מתקדמת")
st.write("הזן את סימול המניות שתרצה לסרוק, הגדר את רמת הרגישות (הסיכון), וקבל דו״ח אקסל מקצועי להורדה מיידית.")

# --- סרגל צד (Sidebar) להגדרות משתמש ---
st.sidebar.header("⚙️ הגדרות ניתוח וסיכון")

# 1. בחירת מניות
tickers_input = st.sidebar.text_input(
    "הזן סימולי מניות (מופרדים בפסיקים)", 
    value="AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, AMD, NFLX, INTC"
)

# 2. הגדרת רמות רגישות / סיכון
st.sidebar.subheader("רמות רגישות לאיתותים")
rsi_buy_threshold = st.sidebar.slider("רף RSI לקנייה (ככל שגבוה יותר, רגיש יותר)", min_value=30, max_value=55, value=45)
rsi_sell_threshold = st.sidebar.slider("רף RSI למכירה (אזור רוויה)", min_value=50, max_value=75, value=60)

# כפתור הפעלה ראשי
run_scan = st.sidebar.button("🚀 הפק דו״ח מניות", type="primary")

# --- אזור הצגת הנתונים ---
if run_scan:
    # עיבוד רשימת המניות שהמשתמש הקליד
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if not tickers:
        st.warning("אנא הזן לפחות סימול מניה אחד תקין.")
    else:
        st.info(f"מבצע סריקה עבור {len(tickers)} מניות בהתאם להגדרות שבחרת...")
        
        results = []
        progress_bar = st.progress(0)
        total = len(tickers)

        for i, ticker in enumerate(tickers):
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(period='1y')
                
                if data.empty or len(data) < 21:
                    continue

                close_prices = data['Close']
                current_price = float(close_prices.iloc[-1])

                # חישוב תשואות
                daily_return = ((current_price - float(close_prices.iloc[-2])) / float(close_prices.iloc[-2])) * 100 if len(close_prices) >= 2 else 0
                weekly_return = ((current_price - float(close_prices.iloc[-5])) / float(close_prices.iloc[-5])) * 100 if len(close_prices) >= 5 else 0
                monthly_return = ((current_price - float(close_prices.iloc[-21])) / float(close_prices.iloc[-21])) * 100 if len(close_prices) >= 21 else 0
                yearly_return = ((current_price - float(close_prices.iloc[0])) / float(close_prices.iloc[0])) * 100 if len(close_prices) >= 200 else 0

                # יעדי קנייה ומכירה (תמיכה והתנגדות חודשית)
                recent_month_data = close_prices.tail(21)
                support_price = float(recent_month_data.min()) * 0.99
                resistance_price = float(recent_month_data.max()) * 1.01

                # חישוב מתנדים
                data['SMA_10'] = close_prices.rolling(window=10).mean()
                data['SMA_20'] = close_prices.rolling(window=20).mean()
                
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                data['RSI'] = 100 - (100 / (1 + rs))

                latest_rsi = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50
                latest_sma10 = float(data['SMA_10'].iloc[-1]) if not pd.isna(data['SMA_10'].iloc[-1]) else current_price
                latest_sma20 = float(data['SMA_20'].iloc[-1]) if not pd.isna(data['SMA_20'].iloc[-1]) else current_price

                # קביעת איתות לפי הרגישות שהמשתמש בחר בסרגל הצד
                signal = 'Hold 🟡'
                reason = 'מגמה צדדית / המתנה'

                if latest_sma10 > latest_sma20 and latest_rsi < (rsi_buy_threshold + 20):
                    signal = 'Buy 🟢'
                    reason = 'מומנטום חיובי (ממוצע 10 מעל 20)'
                elif latest_rsi < rsi_buy_threshold: 
                    signal = 'Buy 🟢'
                    reason = f'RSI נמוך מ-{rsi_buy_threshold} (הזדמנות קנייה)'
                elif latest_sma10 < latest_sma20 and latest_rsi > (rsi_sell_threshold - 20):
                    signal = 'Sell 🔴'
                    reason = 'מומנטום שלילי (ממוצע 10 שבר למטה)'
                elif latest_rsi > rsi_sell_threshold:
                    signal = 'Sell 🔴'
                    reason = f'RSI גבוה מ-{rsi_sell_threshold} (אזור רוויה)'

                chart_url = f"https://finance.yahoo.com/quote/{ticker}"
                ticker_link_formula = f'=HYPERLINK("{chart_url}", "{ticker}")'

                results.append({
                    'מניה': ticker_link_formula,
                    'איתות טכני': signal,
                    'סיבת האיתות': reason,
                    'מחיר סגירה': round(current_price, 2),
                    'מחיר קנייה מומלץ (תמיכה)': round(support_price, 2),
                    'מחיר יעד למכירה': round(resistance_price, 2),
                    'יומי (%)': round(daily_return, 2),
                    'שבועי (%)': round(weekly_return, 2),
                    'חודשי (%)': round(monthly_return, 2),
                    'שנתי (%)': round(yearly_return, 2),
                    'RSI נוכחי': round(latest_rsi, 2)
                })
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
            
            progress_bar.progress((i + 1) / total)

        if len(results) > 0:
            df = pd.DataFrame(results)
            
            st.success("הסריקה הסתיימה בהצלחה! הנה תוצאות הדו״ח:")
            
            # הצגת טבלה חיה למשתמש במסך
            st.dataframe(df, use_container_width=True)

            # הכנת קובץ האקסל להורדה ישירה
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Stock Report')
            
            excel_data = output.getvalue()

            # כפתור הורדה לאקסל
            st.download_button(
                label="📥 הורד דו״ח מלא כקובץ Excel",
                data=excel_data,
                file_name="custom_stock_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("לא נמצאו נתונים עבור המניות שהוזנו. נסה סימולים אחרים.")
else:
    st.info("👈 הגדר את המניות ורמות הסיכון בסרגל הצד משמאל, ולחץ על **'הפק דו״ח מניות'** כדי להתחיל.")
