import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import calendar
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="369 SHADOW V43", layout="wide")

# --- CSS لتصميم Modern Neon ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

.stApp { background: #05070a; color: #e6edf3; font-family: 'Inter', sans-serif; }

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #080b10;
    border-right: 2px solid #00d4ff33;
}

/* Neon Cards */
.metric-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(0, 212, 255, 0.2);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
}

/* Journal Status Colors */
.win-card { border-left: 5px solid #00ffcc !important; background: rgba(0, 255, 204, 0.05) !important; margin-bottom: 10px; border-radius: 8px; }
.loss-card { border-left: 5px solid #ff4b4b !important; background: rgba(255, 75, 75, 0.05) !important; margin-bottom: 10px; border-radius: 8px; }
.be-card { border-left: 5px solid #ffcc00 !important; background: rgba(255, 204, 0, 0.05) !important; margin-bottom: 10px; border-radius: 8px; }

/* Welcome Text */
.welcome-header {
    font-family: 'Orbitron';
    color: #00d4ff;
    text-align: center;
    text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
    letter-spacing: 2px;
}
</style>
""", unsafe_allow_html=True)

# --- قاعدة البيانات ---
conn = sqlite3.connect('shadow_v43.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, outcome TEXT, 
              pnl REAL, rr REAL, setup_name TEXT, setup_desc TEXT, mindset_type TEXT, 
              mindset_desc TEXT, image TEXT, month_year TEXT)''')
conn.commit()

# --- التحميل والمعالجة ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.strftime('%B %Y')

# --- SIDEBAR MODERN ---
with st.sidebar:
    st.markdown("<h1 style='color:#00ffcc; font-family:Orbitron; font-size:1.2rem;'>SHADOW TERMINAL</h1>", unsafe_allow_html=True)
    
    # إدخال مبلغ الحساب
    account_balance = st.number_input("ACCOUNT BALANCE ($)", value=1000.0, step=100.0)
    
    st.divider()
    menu = st.radio("NAVIGATION", ["TERMINAL", "DASHBOARD", "JOURNAL", "CALENDAR"])
    
    # اختيار الشهر للأرشفة
    st.divider()
    if not df.empty:
        available_months = df['month_year'].unique().tolist()
        selected_month = st.selectbox("ARCHIVE (SELECT MONTH)", available_months)
        filtered_df = df[df['month_year'] == selected_month]
    else:
        st.info("No data yet.")
        filtered_df = pd.DataFrame()

st.markdown(f'<h2 class="welcome-header">SYSTEM STATUS: {menu}</h2>', unsafe_allow_html=True)

# ------------------- 1. TERMINAL (Entry) -------------------
if menu == "TERMINAL":
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("trade_form", clear_on_submit=True):
            st.markdown("### 📥 LOG NEW TRADE")
            t_date = st.date_input("Date", datetime.now())
            t_pair = st.text_input("Pair", "NAS100")
            t_out = st.selectbox("Outcome", ["WIN", "LOSS", "BE"])
            t_pnl = st.number_input("P&L ($)", step=1.0)
            t_rr = st.number_input("RR Ratio", step=0.1)
            
            st.divider()
            t_setup = st.text_input("Setup Name (Short)")
            t_setup_desc = st.text_area("Setup Description (Why you took it?)")
            
            t_mind = st.selectbox("Mindset Status", ["Focused", "Impulsive", "Revenge", "Bored"])
            t_mind_desc = st.text_area("Psychology Notes")
            
            if st.form_submit_button("LOCK TRADE"):
                m_y = t_date.strftime('%B %Y')
                c.execute("""INSERT INTO trades (date, pair, outcome, pnl, rr, setup_name, setup_desc, 
                             mindset_type, mindset_desc, month_year) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                          (str(t_date), t_pair.upper(), t_out, t_pnl, t_rr, t_setup, t_setup_desc, t_mind, t_mind_desc, m_y))
                conn.commit()
                st.success("Trade Recorded Successfully!")
                st.rerun()
    
    with col2:
        st.markdown("### 📈 QUICK VIEW")
        if not filtered_df.empty:
            fig = px.line(filtered_df.sort_values('date'), x='date', y='pnl', title="Monthly P&L Curve")
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# ------------------- 2. DASHBOARD (Performance) -------------------
elif menu == "DASHBOARD":
    if not filtered_df.empty:
        m1, m2, m3, m4 = st.columns(4)
        net_pnl = filtered_df['pnl'].sum()
        win_rate = (len(filtered_df[filtered_df['outcome'] == 'WIN']) / len(filtered_df)) * 100
        
        m1.markdown(f'<div class="metric-card"><small>NET P&L</small><br><b style="color:#00ffcc; font-size:1.5rem;">${net_pnl:,.2f}</b></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><small>WIN RATE</small><br><b style="color:#00ffcc; font-size:1.5rem;">{win_rate:.1f}%</b></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><small>AVG RR</small><br><b style="color:#00ffcc; font-size:1.5rem;">{filtered_df["rr"].mean():.2f}</b></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><small>NEW BALANCE</small><br><b style="color:#00ffcc; font-size:1.5rem;">${(account_balance + net_pnl):,.2f}</b></div>', unsafe_allow_html=True)
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(filtered_df, names='mindset_type', values='pnl', title="P&L by Mindset", hole=0.4, template="plotly_dark"), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(filtered_df, x='setup_name', y='pnl', color='outcome', title="Setup Performance", template="plotly_dark"), use_container_width=True)

# ------------------- 3. JOURNAL (Detailed) -------------------
elif menu == "JOURNAL":
    if not filtered_df.empty:
        for idx, row in filtered_df.sort_values('date', ascending=False).iterrows():
            # تحديد الكلاس بناء على النتيجة
            card_style = "win-card" if row['outcome'] == "WIN" else "loss-card" if row['outcome'] == "LOSS" else "be-card"
            
            with st.container():
                st.markdown(f'<div class="{card_style}">', unsafe_allow_html=True)
                with st.expander(f"➔ {row['date'].strftime('%Y-%m-%d')} | {row['pair']} | P&L: ${row['pnl']} | {row['outcome']}"):
                    a, b = st.columns(2)
                    with a:
                        st.markdown(f"**Setup:** {row['setup_name']}")
                        st.info(f"**Description:** {row['setup_desc']}")
                    with b:
                        st.markdown(f"**Mindset:** {row['mindset_type']}")
                        st.warning(f"**Notes:** {row['mindset_desc']}")
                st.markdown('</div>', unsafe_allow_html=True)

# ------------------- 4. CALENDAR -------------------
elif menu == "CALENDAR":
    if not filtered_df.empty:
        # عرض ملخص بسيط لكل يوم في الشهر المختار
        cal_df = filtered_df.groupby(filtered_df['date'].dt.day)['pnl'].sum().reset_index()
        st.markdown(f"### 📅 {selected_month} Calendar View")
        
        # عرض مربعات الأيام (تجريبي)
        cols = st.columns(7)
        for i, row in cal_df.iterrows():
            with cols[int(i%7)]:
                color = "#00ffcc" if row['pnl'] > 0 else "#ff4b4b" if row['pnl'] < 0 else "#ffcc00"
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid {color}; border-radius:10px; padding:10px; text-align:center; margin-bottom:10px;">
                    <small>Day {int(row['date'])}</small><br>
                    <b style="color:{color}">${row['pnl']}</b>
                </div>
                """, unsafe_allow_html=True)
