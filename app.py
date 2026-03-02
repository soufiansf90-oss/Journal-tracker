import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import calendar
import base64

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="369 SHADOW V43", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    
    .stApp { background: #050508; color: #e6edf3; font-family: 'Inter', sans-serif; }
    
    /* Welcome Message - نيون أزرق كيف طلبتي */
    .welcome-text { 
        font-family: 'Orbitron'; 
        color: #00d4ff; 
        font-size: 1.4rem; 
        text-align: center; 
        margin-bottom: 25px; 
        text-shadow: 0 0 15px rgba(0,212,255,0.7); 
        letter-spacing: 2px; 
    }
    
    .equity-box { 
        background: rgba(188, 19, 254, 0.05); border: 1px solid #bc13fe; 
        border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px; 
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #080810; border-right: 2px solid #bc13fe33; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(188, 19, 254, 0.02) !important;
        border: 1px solid rgba(188, 19, 254, 0.3) !important;
        padding: 12px 20px !important;
        border-radius: 15px !important;
        color: #8b949e; font-family: 'Orbitron'; font-size: 0.75rem;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        border: 1px solid #bc13fe !important; color: #bc13fe !important; box-shadow: 0 0 15px rgba(188,19,254,0.4);
    }

    /* Journal Colors */
    .journal-win { border-left: 5px solid #00ffcc; background: rgba(0, 255, 204, 0.05); padding:10px; border-radius:10px; margin-bottom:10px; }
    .journal-loss { border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); padding:10px; border-radius:10px; margin-bottom:10px; }
    
    .perf-card { background: rgba(20, 20, 30, 0.8); border: 1px solid #bc13fe33; padding: 15px; border-radius: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-TRACKER & DATABASE ---
with st.sidebar:
    st.markdown('<div style="font-family:Orbitron; color:#bc13fe; font-size:1.2rem; text-align:center;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    # الصورة الأولى: إدخال اسم الحساب والرصيد يدوياً
    custom_acc_name = st.text_input("📝 Account Name", "My Tracker")
    init_amount = st.number_input("💰 Initial Amount ($)", value=1000.0)
    
    db_name = f"tracker_{custom_acc_name.replace(' ', '_').lower()}.db"
    conn = sqlite3.connect(db_name, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, 
                  outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, 
                  setup TEXT, comment TEXT, setup_desc TEXT, image TEXT)''')
    conn.commit()

# --- 3. DATA PREP ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    current_bal = init_amount + df['pnl'].sum()
    d_pnl = df[df['date'] == datetime.now().strftime('%Y-%m-%d')]['pnl'].sum()
else:
    current_bal = init_amount
    d_pnl = 0.0

# --- 4. SIDEBAR MENU ---
with st.sidebar:
    st.markdown(f"""
    <div class="equity-box">
        <div style="font-family:Orbitron; font-size:0.6rem; color:#bc13fe;">EQUITY STATUS</div>
        <div style="font-size:1.4rem; font-weight:bold; color:#fff;">${current_bal:,.2f}</div>
        <div style="font-size:0.8rem; color:{'#00ffcc' if d_pnl >= 0 else '#ff4b4b'}; font-family:Orbitron;">
            {d_pnl:+.2f} USD TODAY
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("MENU", ["TERMINAL", "CALENDAR", "PERFORMANCE", "12 MONTHS PERF", "JOURNAL", "ARCHIVE"])

st.markdown('<div class="welcome-text">WHAT\'S UP SHADOW, LET\'S SEE WHAT HAPPENED TODAY.</div>', unsafe_allow_html=True)

# --- 5. MAIN CONTENT ---

if choice == "TERMINAL":
    c1, c2 = st.columns([1, 2.3])
    with c1:
        with st.form("entry_form"):
            st.markdown("### 📥 LOG ENTRY")
            d_in = st.date_input("Date", datetime.now())
            asset = st.text_input("Pair", "NAS100").upper()
            res = st.selectbox("Outcome", ["WIN", "LOSS", "BE"])
            p_val = st.number_input("P&L ($)", value=0.0)
            r_val = st.number_input("RR Ratio", value=0.0)
            setup = st.text_input("Setup Name").upper()
            # إضافة الخانات الجديدة المطلوبة
            setup_desc = st.text_area("Setup Description")
            comment = st.text_area("Comment / Note")
            mind = st.selectbox("Mindset", ["Focused", "Impulsive", "Revenge", "Bored"])
            img_file = st.file_uploader("Screenshot", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("LOCK TRADE"):
                img_data = base64.b64encode(img_file.read()).decode() if img_file else None
                c.execute("""INSERT INTO trades (date, pair, outcome, pnl, rr, balance, mindset, setup, comment, setup_desc, image) 
                          VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                          (str(d_in), asset, res, p_val, r_val, current_bal, mind, setup, comment, setup_desc, img_data))
                conn.commit()
                st.rerun()
    with c2:
        if not df.empty:
            df = df.sort_values(by='date_dt')
            df['equity_curve'] = init_amount + df['pnl'].cumsum()
            fig = px.line(df, x='date', y='equity_curve', title="GROWTH CURVE")
            fig.update_traces(line_color='#bc13fe')
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

elif choice == "PERFORMANCE":
    # الصورة الثانية: إضافة المقاييس الجديدة وتلوين الربح/الخسارة
    if not df.empty:
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] < 0]
        wr = (len(wins)/len(df))*100
        avg_rr = df['rr'].mean()
        # Trade Factor (Profit Factor)
        tf = abs(wins['pnl'].sum() / losses['pnl'].sum()) if not losses.empty else 0
        best = df['pnl'].max()
        worst = df['pnl'].min()

        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = wr,
            number = {'suffix': "%", 'font': {'color': '#fff'}},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#00ffcc"},
                'bgcolor': "rgba(255, 75, 75, 0.2)",
                'steps': [{'range': [0, wr], 'color': 'rgba(0, 255, 204, 0.1)'}]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # عرض المقاييس المطلوبة
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="perf-card"><h3>{avg_rr:.2f}</h3><p>AVG RR</p></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="perf-card"><h3>{tf:.2f}</h3><p>TRADE FACTOR</p></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="perf-card"><h3 style="color:#00ffcc;">${best:,.0f}</h3><p>BEST TRADE</p></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="perf-card"><h3 style="color:#ff4b4b;">${worst:,.0f}</h3><p>WORST TRADE</p></div>', unsafe_allow_html=True)
        
        # تلوين الرقم السفلي (صافي الربح)
        total_pnl = df['pnl'].sum()
        pnl_color = "#00ffcc" if total_pnl >= 0 else "#ff4b4b"
        st.markdown(f"""
            <div style="text-align:center; margin-top:20px;">
                <h1 style="color:{pnl_color}; font-family:Orbitron;">${total_pnl:,.2f}</h1>
                <p style="letter-spacing:2px;">NET PROFIT</p>
            </div>
        """, unsafe_allow_html=True)

elif choice == "12 MONTHS PERF":
    # ميزة إضافية: أداء 12 شهر بشارت أعمدة
    if not df.empty:
        df['month_name'] = df['date_dt'].dt.strftime('%b %Y')
        m_perf = df.groupby('month_name')['pnl'].sum().reset_index()
        # ترتيب حسب الوقت وليس أبجدياً
        m_perf['sort_date'] = pd.to_datetime(m_perf['month_name'])
        m_perf = m_perf.sort_values('sort_date')
        
        fig_month = px.bar(m_perf, x='month_name', y='pnl', 
                           title="Monthly Performance (Last 12 Months)",
                           color='pnl', color_continuous_scale=['#ff4b4b', '#00ffcc'])
        fig_month.update_layout(template="plotly_dark")
        st.plotly_chart(fig_month, use_container_width=True)

elif choice == "JOURNAL":
    # تلوين الجورنال بناءً على الربح أو الخسارة
    if not df.empty:
        for idx, row in df.sort_values('id', ascending=False).iterrows():
            status_class = "journal-win" if row['pnl'] >= 0 else "journal-loss"
            with st.container():
                st.markdown(f'<div class="{status_class}">', unsafe_allow_html=True)
                with st.expander(f"● {row['date']} | {row['pair']} | P&L: ${row['pnl']:,.2f}"):
                    c_j1, c_j2 = st.columns([1, 1.5])
                    with c_j1:
                        st.write(f"**Setup:** {row['setup']}")
                        st.write(f"**Description:** {row['setup_desc']}")
                        st.write(f"**Comment:** {row['comment']}")
                    with c_j2:
                        if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

elif choice == "ARCHIVE":
    # الصورة الثالثة: Tracker الشهر كامل
    if not df.empty:
        df['month_year'] = df['date_dt'].dt.strftime('%B %Y')
        selected_month = st.selectbox("Select Month to Track", df['month_year'].unique())
        month_data = df[df['month_year'] == selected_month]
        
        st.markdown(f"### 📊 Tracker for {selected_month}")
        st.dataframe(month_data[['date', 'pair', 'outcome', 'pnl', 'rr', 'setup', 'mindset']], use_container_width=True)
        
        # ملخص سريع للشهر
        st.write(f"**Total Trades:** {len(month_data)} | **Month P&L:** ${month_data['pnl'].sum():,.2f}")
