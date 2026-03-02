import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import sqlite3
import calendar
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="369 SHADOW V43", layout="wide")

# --- CSS: التصميم المودرن والنيون ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
.stApp { background: #05070a; color: #e6edf3; font-family: 'Inter', sans-serif; }

/* Sidebar Styling */
div[data-testid="stSidebar"] { background-color: #080b10; border-right: 2px solid #00d4ff33; }
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2);
    padding: 15px; border-radius: 10px; margin-bottom: 10px; color: #8b949e; font-family: 'Orbitron';
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb='radio']:has(input:checked) {
    background: rgba(0, 212, 255, 0.2) !important; border: 1px solid #00d4ff !important;
    box-shadow: 0 0 15px #00d4ff66; color: #00ffcc !important;
}

/* Journal Status Cards */
.win-card { border-left: 5px solid #00ffcc; background: rgba(0, 255, 204, 0.05); padding: 15px; margin-bottom: 10px; border-radius: 8px; }
.loss-card { border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); padding: 15px; margin-bottom: 10px; border-radius: 8px; }
.be-card { border-left: 5px solid #ffcc00; background: rgba(255, 204, 0, 0.05); padding: 15px; margin-bottom: 10px; border-radius: 8px; }

/* Calendar Style */
.cal-day-box { height: 100px; border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 5px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
conn = sqlite3.connect('shadow_pro_v43.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, outcome TEXT, 
              pnl REAL, rr REAL, setup_name TEXT, setup_desc TEXT, mindset_type TEXT, 
              mindset_desc TEXT, image TEXT, month_archive TEXT)''')
conn.commit()

# --- DATA LOADING ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00ffcc; font-family:Orbitron;'>SHADOW V43</h2>", unsafe_allow_html=True)
    
    # إدخال مبلغ الحساب الأساسي
    initial_deposit = st.number_input("INITIAL DEPOSIT ($)", value=1000.0, step=100.0)
    
    # حساب الرصيد الحالي تلقائياً
    total_pnl_all_time = df['pnl'].sum() if not df.empty else 0.0
    current_live_balance = initial_deposit + total_pnl_all_time
    
    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.1); border:1px solid #00d4ff; padding:15px; border-radius:12px; text-align:center; margin: 10px 0;">
        <small style="color:#00d4ff; letter-spacing:2px;">LIVE BALANCE</small><br>
        <span style="font-size:1.6rem; font-family:Orbitron; color:#fff;">${current_live_balance:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    choice = st.radio("SELECT MODULE", ["TERMINAL", "PERFORMANCE", "JOURNAL", "CALENDAR"])
    
    st.divider()
    # نظام الأرشفة
    if not df.empty:
        df['month_year'] = df['date'].dt.strftime('%B %Y')
        available_months = sorted(df['month_year'].unique().tolist(), reverse=True)
        selected_month = st.selectbox("ARCHIVE VIEWER", available_months)
        active_df = df[df['month_year'] == selected_month].copy()
    else:
        selected_month = datetime.now().strftime('%B %Y')
        active_df = pd.DataFrame()

# --- MAIN INTERFACE ---
st.markdown(f"<h3 style='font-family:Orbitron; color:#00d4ff; text-align:center;'>{selected_month} DATA</h3>", unsafe_allow_html=True)

# ------------------- 1. TERMINAL -------------------
if choice == "TERMINAL":
    col_input, col_chart = st.columns([1, 2])
    
    with col_input:
        with st.form("trade_entry_form", clear_on_submit=True):
            st.markdown("### 📥 LOG ENTRY")
            t_date = st.date_input("Trade Date", date.today())
            t_pair = st.text_input("Pair", "NAS100").upper()
            t_out = st.selectbox("Outcome", ["WIN", "LOSS", "BE"])
            t_pnl = st.number_input("Net P&L ($)", step=1.0)
            t_rr = st.number_input("Risk:Reward", step=0.1)
            
            st.markdown("---")
            t_setup_name = st.text_input("Setup Name")
            t_setup_desc = st.text_area("Setup Description")
            t_mindset_type = st.selectbox("Mindset", ["Focused", "Impulsive", "Revenge", "Bored"])
            t_mindset_desc = st.text_area("Psychology Description")
            
            img_file = st.file_uploader("Upload Chart Screenshot", type=['png','jpg'])
            
            if st.form_submit_button("LOCK TRADE"):
                img_str = base64.b64encode(img_file.read()).decode() if img_file else None
                m_archive = t_date.strftime('%B %Y')
                c.execute("""INSERT INTO trades (date, pair, outcome, pnl, rr, setup_name, setup_desc, 
                             mindset_type, mindset_desc, image, month_archive) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                          (str(t_date), t_pair, t_out, t_pnl, t_rr, t_setup_name, t_setup_desc, 
                           t_mindset_type, t_mindset_desc, img_str, m_archive))
                conn.commit()
                st.success("Trade Encrypted & Saved.")
                st.rerun()

    with col_chart:
        if not df.empty:
            df_equity = df.sort_values('date').copy()
            df_equity['cumulative_pnl'] = df_equity['pnl'].cumsum()
            df_equity['equity_curve'] = initial_deposit + df_equity['cumulative_pnl']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_equity['date'], y=df_equity['equity_curve'], mode='lines+markers',
                                     line=dict(color='#00ffcc', width=3), fill='tozeroy', fillcolor='rgba(0,255,204,0.1)'))
            fig.update_layout(template="plotly_dark", title="ALL-TIME EQUITY GROWTH", height=500)
            st.plotly_chart(fig, use_container_width=True)

# ------------------- 2. PERFORMANCE -------------------
elif choice == "PERFORMANCE":
    if not active_df.empty:
        p1, p2, p3, p4 = st.columns(4)
        m_pnl = active_df['pnl'].sum()
        m_wr = (len(active_df[active_df['outcome'] == 'WIN']) / len(active_df)) * 100
        
        p1.markdown(f'<div class="win-card" style="text-align:center;"><small>MONTH P&L</small><br><b style="font-size:1.5rem;">${m_pnl:,.2f}</b></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="win-card" style="text-align:center;"><small>WIN RATE</small><br><b style="font-size:1.5rem;">{m_wr:.1f}%</b></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="win-card" style="text-align:center;"><small>AVG RR</small><br><b style="font-size:1.5rem;">{active_df["rr"].mean():.2f}</b></div>', unsafe_allow_html=True)
        p4.markdown(f'<div class="win-card" style="text-align:center;"><small>TRADES</small><br><b style="font-size:1.5rem;">{len(active_df)}</b></div>', unsafe_allow_html=True)
        
        st.divider()
        st.plotly_chart(px.bar(active_df, x='date', y='pnl', color='outcome', title="Daily Performance Break-down", template="plotly_dark"), use_container_width=True)
        st.plotly_chart(px.pie(active_df, names='mindset_type', values='pnl', title="Psychology Impact on Profit", template="plotly_dark", hole=0.5), use_container_width=True)

# ------------------- 3. JOURNAL -------------------
elif choice == "JOURNAL":
    if not active_df.empty:
        for _, row in active_df.sort_values('date', ascending=False).iterrows():
            card_class = "win-card" if row['outcome'] == "WIN" else "loss-card" if row['outcome'] == "LOSS" else "be-card"
            with st.container():
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                st.markdown(f"**{row['date'].strftime('%Y-%m-%d')} | {row['pair']} | P&L: ${row['pnl']} | Setup: {row['setup_name']}**")
                with st.expander("VIEW FULL DETAILS"):
                    jx1, jx2 = st.columns(2)
                    with jx1:
                        st.info(f"**Setup Strategy:**\n\n{row['setup_desc']}")
                        st.warning(f"**Mindset ({row['mindset_type']}):**\n\n{row['mindset_desc']}")
                    with jx2:
                        if row['image']:
                            st.image(base64.b64decode(row['image']), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ------------------- 4. CALENDAR -------------------
elif choice == "CALENDAR":
    if not active_df.empty:
        first_day = active_df['date'].min().replace(day=1)
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        
        # عرض أيام الشهر بالكامل
        cols = st.columns(7)
        weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for i, wd in enumerate(weekdays):
            cols[i].markdown(f"<center style='color:#00d4ff;'>{wd}</center>", unsafe_allow_html=True)
        
        month_days = pd.date_range(start=first_day, periods=last_day_num)
        
        for i, day in enumerate(month_days):
            with cols[day.weekday()]:
                day_str = day.strftime('%Y-%m-%d')
                trades_today = active_df[active_df['date'].dt.strftime('%Y-%m-%d') == day_str]
                daily_pnl = trades_today['pnl'].sum()
                num_trades = len(trades_today)
                
                bg = "rgba(255,255,255,0.02)"
                border_color = "rgba(255,255,255,0.1)"
                if num_trades > 0:
                    bg = "rgba(0,255,204,0.1)" if daily_pnl > 0 else "rgba(255,75,75,0.1)" if daily_pnl < 0 else "rgba(255,204,0,0.1)"
                    border_color = "#00ffcc" if daily_pnl > 0 else "#ff4b4b" if daily_pnl < 0 else "#ffcc00"
                
                st.markdown(f"""
                <div style="background:{bg}; border:1px solid {border_color}; border-radius:8px; padding:10px; height:110px; text-align:center; margin-bottom:10px;">
                    <div style="font-size:0.8rem; opacity:0.5;">{day.day}</div>
                    <div style="color:{border_color}; font-weight:bold; font-size:1rem;">{f'${daily_pnl}' if num_trades > 0 else ''}</div>
                    <div style="font-size:0.7rem; color:#8b949e;">{f'{num_trades} Trades' if num_trades > 0 else ''}</div>
                </div>
                """, unsafe_allow_html=True)
