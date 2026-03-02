import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import calendar
import base64

# --- 1. SETTINGS & VIOLET NEON UI ---
st.set_page_config(page_title="369 SHADOW V43", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    
    .stApp { background: #050508; color: #e6edf3; font-family: 'Inter', sans-serif; }
    
    /* Neon Purple Styling */
    .welcome-text { font-family: 'Orbitron'; color: #bc13fe; font-size: 1.4rem; text-align: center; margin-bottom: 25px; text-shadow: 0 0 15px rgba(188,19,254,0.6); letter-spacing: 2px; }
    
    /* Equity Status Top Box - حواف منحنية */
    .equity-box { 
        background: rgba(188, 19, 254, 0.05); 
        border: 1px solid #bc13fe; 
        border-radius: 20px; 
        padding: 15px; 
        text-align: center; 
        margin-bottom: 20px; 
        box-shadow: 0 0 10px rgba(188,19,254,0.2); 
    }

    /* Sidebar Neon Rectangles - مستطيلات بحواف منحنية */
    [data-testid="stSidebar"] { background-color: #080810; border-right: 2px solid #bc13fe33; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 12px; padding-top: 10px; }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(188, 19, 254, 0.02) !important;
        border: 1px solid rgba(188, 19, 254, 0.3) !important;
        padding: 12px 20px !important;
        border-radius: 15px !important; /* انحناء الحواف */
        transition: 0.3s all;
        width: 100%;
        color: #8b949e;
        font-family: 'Orbitron';
        text-transform: uppercase;
        font-size: 0.75rem;
        cursor: pointer;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(188, 19, 254, 0.1) !important;
        border: 1px solid #bc13fe !important;
        color: #bc13fe !important;
        box-shadow: 0 0 15px rgba(188, 19, 254, 0.4);
        border-radius: 15px !important;
    }

    /* Selectbox Styling */
    div[data-baseweb="select"] > div { border-radius: 15px !important; border-color: #bc13fe33 !important; }
    
    /* Performance Card */
    .perf-card { background: rgba(20, 20, 30, 0.8); border: 1px solid #bc13fe33; padding: 15px; border-radius: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-TRACKER & DATABASE ---
with st.sidebar:
    st.markdown('<div style="font-family:Orbitron; color:#bc13fe; font-size:1.2rem; text-align:center; padding-bottom:10px;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    # ميزة التنقل بين الحسابات
    trackers = ["Personal Fund", "Apex Eval", "Topstep", "MFF"]
    active_tracker = st.selectbox("📂 SELECT TRACKER", trackers)
    
    db_name = f"tracker_{active_tracker.replace(' ', '_').lower()}.db"
    conn = sqlite3.connect(db_name, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, 
                  outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, setup TEXT, image TEXT)''')
    conn.commit()

# --- 3. DATA PREP ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
cur_bal, d_pnl = 1000.0, 0.0 # قيم افتراضية
if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    cur_bal = df['balance'].iloc[0] + df['pnl'].sum()
    d_pnl = df[df['date'] == datetime.now().strftime('%Y-%m-%d')]['pnl'].sum()

# --- 4. EQUITY STATUS (TOP) ---
with st.sidebar:
    st.markdown(f"""
    <div class="equity-box">
        <div style="font-family:Orbitron; font-size:0.6rem; color:#bc13fe; letter-spacing:1px;">EQUITY STATUS</div>
        <div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:5px 0;">${cur_bal:,.2f}</div>
        <div style="font-size:0.8rem; color:{'#00ffcc' if d_pnl >= 0 else '#ff4b4b'}; font-family:Orbitron;">
            {d_pnl:+.2f} USD TODAY
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("MENU", ["TERMINAL", "CALENDAR", "PERFORMANCE", "JOURNAL", "ARCHIVE"])

# --- 5. TOP WELCOME ---
st.markdown('<div class="welcome-text">WHAT\'S UP SHADOW, LET\'S SEE WHAT HAPPENED TODAY.</div>', unsafe_allow_html=True)

# --- 6. MAIN CONTENT ---
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
            setup = st.text_input("Setup").upper()
            mind = st.selectbox("Mindset", ["Focused", "Impulsive", "Revenge", "Bored"])
            img_file = st.file_uploader("Screenshot", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("LOCK TRADE"):
                img_data = base64.b64encode(img_file.read()).decode() if img_file else None
                c.execute("INSERT INTO trades (date, pair, outcome, pnl, rr, balance, mindset, setup, image) VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(d_in), asset, res, p_val, r_val, cur_bal, mind, setup, img_data))
                conn.commit()
                st.rerun()
    with c2:
        if not df.empty:
            df = df.sort_values(by=['date_dt', 'id'])
            df['cum_pnl'] = df['pnl'].cumsum()
            df['equity_curve'] = 1000.0 + df['cum_pnl']
            fig = go.Figure(go.Scatter(x=list(range(len(df))), y=df['equity_curve'], mode='lines+markers', line=dict(color='#bc13fe', width=3, shape='spline'), fill='tonexty', fillcolor='rgba(188,19,254,0.05)'))
            fig.update_layout(template="plotly_dark", height=480, title="ACCOUNT GROWTH CURVE", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

elif choice == "CALENDAR":
    if not df.empty:
        df['date_dt'] = pd.to_datetime(df['date'])
        first_day = df['date_dt'].max().replace(day=1)
        month_name = first_day.strftime('%B %Y')
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        st.markdown(f"<h3 style='text-align:center; color:#bc13fe; font-family:Orbitron;'>{month_name.upper()}</h3>", unsafe_allow_html=True)
        
        weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        h_cols = st.columns(7)
        for i, wd in enumerate(weekdays): h_cols[i].markdown(f"<center style='color:#bc13fe; font-size:0.8rem; font-family:Orbitron;'>{wd}</center>", unsafe_allow_html=True)
        
        start_padding = first_day.weekday() 
        total_slots = start_padding + last_day_num
        for row in range(0, total_slots, 7):
            cols = st.columns(7)
            for i in range(7):
                idx = row + i
                with cols[i]:
                    if start_padding <= idx < total_slots:
                        day_num = idx - start_padding + 1
                        curr_date = first_day.replace(day=day_num)
                        trades_today = df[df['date_dt'].dt.date == curr_date.date()]
                        pnl_today = trades_today['pnl'].sum()
                        
                        bg, border, txt = "rgba(255,255,255,0.02)", "rgba(188,19,254,0.1)", "#444"
                        p_str = ""
                        if len(trades_today) > 0:
                            if pnl_today > 0: bg, border, txt = "rgba(0,255,204,0.1)", "#00ffcc", "#00ffcc"; p_str = f"+${pnl_today:,.0f}"
                            elif pnl_today < 0: bg, border, txt = "rgba(255,75,75,0.1)", "#ff4b4b", "#ff4b4b"; p_str = f"-${abs(pnl_today):,.0f}"
                            else: bg, border, txt = "rgba(188,19,254,0.1)", "#bc13fe", "#bc13fe"; p_str = "$0"

                        st.markdown(f'<div style="background:{bg}; border:1px solid {border}; border-radius:12px; padding:10px; height:90px; text-align:center; margin-bottom:10px;"><div style="font-size:0.7rem; color:#888;">{day_num}</div><div style="color:{txt}; font-weight:bold; font-size:0.9rem; margin-top:5px;">{p_str}</div></div>', unsafe_allow_html=True)

elif choice == "PERFORMANCE":
    if not df.empty:
        wins_count = len(df[df['pnl'] > 0])
        wr = (wins_count / len(df)) * 100 if len(df) > 0 else 0
        
        col1, col2 = st.columns([1, 1.5])
        with col1:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = wr,
                number = {'suffix': "%", 'font': {'color': '#fff', 'family': 'Orbitron', 'size': 30}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#bc13fe"},
                    'bar': {'color': "#00ffcc"}, # شريط التقدم أخضر
                    'bgcolor': "rgba(255, 75, 75, 0.2)", # الخلفية حمراء
                    'borderwidth': 2, 'bordercolor': "#bc13fe",
                    'steps': [{'range': [0, wr], 'color': 'rgba(0, 255, 204, 0.1)'}]
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            g1, g2 = st.columns(2)
            g1.markdown(f'<div class="perf-card"><div style="font-size:2rem; color:#bc13fe; font-family:Orbitron;">{len(df)}</div><div style="font-size:0.75rem; letter-spacing:1px;">TOTAL TRADES</div></div>', unsafe_allow_html=True)
            g2.markdown(f'<div class="perf-card"><div style="font-size:2rem; color:#00ffcc; font-family:Orbitron;">${df["pnl"].sum():,.0f}</div><div style="font-size:0.75rem; letter-spacing:1px;">NET PROFIT</div></div>', unsafe_allow_html=True)

elif choice == "ARCHIVE":
    st.markdown('<div class="welcome-text">MONTHLY TRADING ARCHIVE</div>', unsafe_allow_html=True)
    if not df.empty:
        df['month'] = df['date_dt'].dt.strftime('%B %Y')
        for month, m_df in df.groupby('month', sort=False):
            with st.expander(f"📁 {month.upper()} | Net P&L: ${m_df['pnl'].sum():,.2f}"):
                st.table(m_df[['date', 'pair', 'outcome', 'pnl', 'setup']])
    else: st.info("No data found in archive.")

elif choice == "JOURNAL":
    if not df.empty:
        for idx, row in df.sort_values('id', ascending=False).iterrows():
            color = "#00ffcc" if row['pnl'] > 0 else "#ff4b4b" if row['pnl'] < 0 else "#bc13fe"
            with st.expander(f"● {row['date']} | {row['pair']} | P&L: ${row['pnl']:,.2f}"):
                st.write(f"**Setup:** {row['setup']} | **Mindset:** {row['mindset']}")
                if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)

# هل تود إضافة أي تحسينات برمجية أخرى لهذا النظام؟
