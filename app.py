import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import calendar
import base64
import os

# --- 1. SETTINGS & ADVANCED VIOLET NEON UI ---
st.set_page_config(page_title="369 SHADOW V43", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    
    .stApp { background: #050508; color: #e6edf3; font-family: 'Inter', sans-serif; }
    
    /* Welcome Message - NEON BLUE */
    .welcome-text { 
        font-family: 'Orbitron'; color: #00d4ff; font-size: 1.4rem; text-align: center; 
        margin-bottom: 25px; text-shadow: 0 0 15px rgba(0,212,255,0.7); letter-spacing: 2px; 
    }
    
    /* Sidebar Styling - Rounded Neon Rectangles */
    [data-testid="stSidebar"] { background-color: #080810; border-right: 2px solid #bc13fe33; }
    
    .equity-box { 
        background: rgba(188, 19, 254, 0.05); border: 1px solid #bc13fe; 
        border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px; 
        box-shadow: 0 0 10px rgba(188,19,254,0.2);
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(188, 19, 254, 0.02) !important;
        border: 1px solid rgba(188, 19, 254, 0.3) !important;
        padding: 12px 20px !important;
        border-radius: 15px !important;
        color: #8b949e; font-family: 'Orbitron'; font-size: 0.75rem;
        margin-bottom: 8px; transition: 0.3s;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        border: 1px solid #bc13fe !important; color: #bc13fe !important; 
        box-shadow: 0 0 15px rgba(188,19,254,0.4); background: rgba(188, 19, 254, 0.1) !important;
    }

    /* Performance Cards - Rounded */
    .perf-card { 
        background: rgba(20, 20, 30, 0.8); border: 1px solid #bc13fe33; 
        padding: 15px; border-radius: 20px; text-align: center; transition: 0.3s;
    }
    .perf-card:hover { border-color: #bc13fe; box-shadow: 0 0 10px rgba(188,19,254,0.2); }

    /* Journal Entry Colors */
    .journal-win { border-left: 5px solid #00ffcc; background: rgba(0, 255, 204, 0.05); padding:10px; border-radius:15px; margin-bottom:10px; }
    .journal-loss { border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); padding:10px; border-radius:15px; margin-bottom:10px; }
    
    /* Inputs Rounded */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-TRACKER MANAGER ---
with st.sidebar:
    st.markdown('<div style="font-family:Orbitron; color:#bc13fe; font-size:1.2rem; text-align:center;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    # قائمة الحسابات الموجودة
    existing_dbs = [f.replace('tracker_', '').replace('.db', '') for f in os.listdir() if f.startswith('tracker_') and f.endswith('.db')]
    
    acc_name_input = st.text_input("📝 ACCOUNT NAME", value="Main_Tracker")
    init_amount = st.number_input("💰 INITIAL AMOUNT ($)", value=1000.0)
    
    db_name = f"tracker_{acc_name_input.lower().replace(' ', '_')}.db"
    conn = sqlite3.connect(db_name, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, 
                  outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, 
                  setup TEXT, comment TEXT, setup_desc TEXT, image TEXT)''')
    conn.commit()

# --- 3. DATA PREP ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
current_bal = init_amount
daily_pnl = 0.0

if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    current_bal = init_amount + df['pnl'].sum()
    daily_pnl = df[df['date'] == datetime.now().strftime('%Y-%m-%d')]['pnl'].sum()

# --- 4. SIDEBAR EQUITY & MENU ---
with st.sidebar:
    st.markdown(f"""
    <div class="equity-box">
        <div style="font-family:Orbitron; font-size:0.6rem; color:#bc13fe;">EQUITY STATUS</div>
        <div style="font-size:1.4rem; font-weight:bold; color:#fff;">${current_bal:,.2f}</div>
        <div style="font-size:0.8rem; color:{'#00ffcc' if daily_pnl >= 0 else '#ff4b4b'}; font-family:Orbitron;">
            {daily_pnl:+.2f} USD TODAY
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("MENU", ["TERMINAL", "CALENDAR", "PERFORMANCE", "12 MONTHS PERF", "JOURNAL", "ARCHIVE"])

st.markdown('<div class="welcome-text">WHAT\'S UP SHADOW, LET\'S SEE WHAT HAPPENED TODAY.</div>', unsafe_allow_html=True)

# --- 5. MAIN LOGIC ---

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
            df_chart = df.sort_values(by='date_dt')
            df_chart['equity_curve'] = init_amount + df_chart['pnl'].cumsum()
            fig = px.line(df_chart, x='date', y='equity_curve', title="GROWTH CURVE")
            fig.update_traces(line_color='#bc13fe', line_width=3)
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

elif choice == "CALENDAR":
    if not df.empty:
        df['date_dt'] = pd.to_datetime(df['date'])
        current_month_date = df['date_dt'].max().replace(day=1)
        month_label = current_month_date.strftime('%B %Y')
        _, last_day_num = calendar.monthrange(current_month_date.year, current_month_date.month)
        
        st.markdown(f"<h2 style='text-align:center; color:#bc13fe; font-family:Orbitron;'>{month_label.upper()}</h2>", unsafe_allow_html=True)
        
        weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        h_cols = st.columns(7)
        for i, wd in enumerate(weekdays):
            h_cols[i].markdown(f"<div style='text-align:center; color:#888; font-size:0.7rem; font-family:Orbitron;'>{wd}</div>", unsafe_allow_html=True)
        
        start_padding = current_month_date.weekday() 
        total_slots = start_padding + last_day_num
        
        for row in range(0, total_slots, 7):
            cols = st.columns(7)
            for i in range(7):
                idx = row + i
                with cols[i]:
                    if start_padding <= idx < total_slots:
                        d_num = idx - start_padding + 1
                        curr_d = current_month_date.replace(day=d_num)
                        day_trades = df[df['date_dt'].dt.date == curr_d.date()]
                        d_pnl = day_trades['pnl'].sum()
                        
                        bg, border, txt = "rgba(255,255,255,0.02)", "rgba(188,19,254,0.1)", "#444"
                        p_str = ""
                        if len(day_trades) > 0:
                            if d_pnl > 0: bg, border, txt = "rgba(0,255,204,0.05)", "#00ffcc", "#00ffcc"; p_str = f"+${d_pnl:,.0f}"
                            elif d_pnl < 0: bg, border, txt = "rgba(255,75,75,0.05)", "#ff4b4b", "#ff4b4b"; p_str = f"-${abs(d_pnl):,.0f}"
                            else: bg, border, txt = "rgba(188,19,254,0.1)", "#bc13fe", "#bc13fe"; p_str = "$0"

                        st.markdown(f'<div style="background:{bg}; border:1px solid {border}; border-radius:12px; padding:10px; height:85px; text-align:center; margin-bottom:8px;"><div style="font-size:0.6rem; color:#888; text-align:left;">{d_num}</div><div style="color:{txt}; font-weight:bold; font-size:0.85rem; margin-top:5px;">{p_str}</div><div style="font-size:0.5rem; color:#bc13fe; margin-top:3px; font-family:Orbitron;">{f"{len(day_trades)} T" if len(day_trades)>0 else ""}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:rgba(188,19,254,0.2)'>", unsafe_allow_html=True)
        sel_day = st.selectbox("🔍 SELECT DAY TO INSPECT", sorted(df['date_dt'].dt.day.unique()))
        day_df = df[df['date_dt'].dt.day == sel_day]
        st.dataframe(day_df[['pair', 'outcome', 'pnl', 'rr', 'setup']], use_container_width=True)

elif choice == "PERFORMANCE":
    if not df.empty:
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] < 0]
        wr = (len(wins)/len(df))*100
        avg_rr = df['rr'].mean()
        sum_w, sum_l = wins['pnl'].sum(), abs(losses['pnl'].sum())
        tf = sum_w / sum_l if sum_l != 0 else sum_w
        
        # Consistency Score Calculation
        if len(df) > 2:
            cv = df['pnl'].std() / abs(df['pnl'].mean()) if df['pnl'].mean() != 0 else 1
            consistency = max(0, min(100, 100 - (cv * 10)))
        else: consistency = 0

        c_gauge, c_stats = st.columns([1, 1.5])
        with c_gauge:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=wr, number={'suffix': "%", 'font':{'family':'Orbitron'}},
                gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#00ffcc"}, 'bgcolor':"rgba(255,75,75,0.2)",
                       'steps':[{'range':[0,wr], 'color':'rgba(0,255,204,0.1)'}]}))
            fig_g.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_g, use_container_width=True)
        
        with c_stats:
            st.markdown("<br>", unsafe_allow_html=True)
            r1 = st.columns(3)
            r1[0].markdown(f'<div class="perf-card"><h3>{avg_rr:.2f}</h3><p>AVG RR</p></div>', unsafe_allow_html=True)
            r1[1].markdown(f'<div class="perf-card"><h3>{tf:.2f}</h3><p>TRADE FACTOR</p></div>', unsafe_allow_html=True)
            r1[2].markdown(f'<div class="perf-card" style="border-color:#00d4ff"><h3>{consistency:.0f}%</h3><p>CONSISTENCY</p></div>', unsafe_allow_html=True)
            
            r2 = st.columns(2)
            r2[0].markdown(f'<div class="perf-card"><h3 style="color:#00ffcc">${df["pnl"].max():,.0f}</h3><p>BEST TRADE</p></div>', unsafe_allow_html=True)
            r2[1].markdown(f'<div class="perf-card"><h3 style="color:#ff4b4b">${df["pnl"].min():,.0f}</h3><p>WORST TRADE</p></div>', unsafe_allow_html=True)

        total_p = df['pnl'].sum()
        p_color = "#00ffcc" if total_p >= 0 else "#ff4b4b"
        st.markdown(f'<div style="text-align:center; margin-top:30px;"><p style="color:#888; font-family:Orbitron;">TOTAL NET PROFIT</p><h1 style="color:{p_color}; font-size:3.5rem; font-family:Orbitron;">${total_p:,.2f}</h1></div>', unsafe_allow_html=True)

elif choice == "12 MONTHS PERF":
    if not df.empty:
        df['month_yr'] = df['date_dt'].dt.strftime('%b %Y')
        m_perf = df.groupby('month_yr')['pnl'].sum().reset_index()
        m_perf['sort'] = pd.to_datetime(m_perf['month_yr'])
        m_perf = m_perf.sort_values('sort')
        fig_m = px.bar(m_perf, x='month_yr', y='pnl', color='pnl', color_continuous_scale=['#ff4b4b', '#00ffcc'])
        fig_m.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_m, use_container_width=True)

elif choice == "JOURNAL":
    if not df.empty:
        for idx, row in df.sort_values('id', ascending=False).iterrows():
            j_style = "journal-win" if row['pnl'] >= 0 else "journal-loss"
            st.markdown(f'<div class="{j_style}">', unsafe_allow_html=True)
            with st.expander(f"● {row['date']} | {row['pair']} | P&L: ${row['pnl']:,.2f}"):
                tx, im = st.columns([1, 1.5])
                with tx:
                    st.write(f"**Setup:** {row['setup']}")
                    st.write(f"**Desc:** {row['setup_desc']}")
                    st.write(f"**Comment:** {row['comment']}")
                with im:
                    if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif choice == "ARCHIVE":
    if not df.empty:
        df['month_name'] = df['date_dt'].dt.strftime('%B %Y')
        for month in df.sort_values('date_dt', ascending=False)['month_name'].unique():
            m_data = df[df['month_name'] == month]
            with st.expander(f"📁 {month.upper()} | Trades: {len(m_data)} | Net: ${m_data['pnl'].sum():,.2f}"):
                st.dataframe(m_data[['date', 'pair', 'outcome', 'pnl', 'rr', 'setup', 'mindset', 'comment']], use_container_width=True)
    else: st.info("No archive data yet.")
