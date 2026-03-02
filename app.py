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
st.set_page_config(page_title="369 SHADOW PRO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Lexend:wght@300;500&display=swap');
    
    .stApp { background: #050508; color: #eef2f6; font-family: 'Lexend', sans-serif; }
    
    .welcome-text { 
        font-family: 'Rajdhani'; color: #00d4ff; font-size: 1.6rem; text-align: center; 
        font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 10px rgba(0,212,255,0.4); 
    }
    
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
        color: #8b949e; font-family: 'Rajdhani'; font-size: 1rem;
        margin-bottom: 8px; transition: 0.3s;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        border: 1px solid #bc13fe !important; color: #bc13fe !important; 
        box-shadow: 0 0 15px rgba(188,19,254,0.4); background: rgba(188, 19, 254, 0.1) !important;
    }

    .journal-win { border-left: 5px solid #00ffcc; background: rgba(0, 255, 204, 0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
    .journal-loss { border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
    .journal-be { border-left: 5px solid #ffcc00; background: rgba(255, 204, 0, 0.05); padding:15px; border-radius:15px; margin-bottom:15px; }

    .perf-card { 
        background: rgba(20, 20, 30, 0.8); border: 1px solid #bc13fe33; 
        padding: 20px; border-radius: 20px; text-align: center; 
    }
    .perf-card h4 { font-family: 'Rajdhani'; color: #bc13fe; font-size: 1.8rem; margin:0; }
    .perf-card p { font-size: 0.8rem; color: #64748b; text-transform: uppercase; margin-top:5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-ACCOUNT SYSTEM ---
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani; color:#bc13fe; font-size:1.5rem; font-weight:700; text-align:center; padding-bottom:15px;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    existing_accounts = [f.replace('tracker_', '').replace('.db', '') for f in os.listdir() if f.startswith('tracker_') and f.endswith('.db')]
    selected_acc = st.selectbox("📂 ACCOUNT", options=list(set(existing_accounts + ["+ New Account"])))
    
    if selected_acc == "+ New Account":
        acc_name = st.text_input("Account Name", "Main_Tracker").strip().replace(" ", "_")
    else:
        acc_name = selected_acc

    init_amount = st.number_input("💰 INITIAL AMOUNT ($)", value=1000.0)

    db_path = f"tracker_{acc_name.lower()}.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()
    # تحديث الجدول ليشمل timestamp
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, timestamp TEXT, pair TEXT, 
                  outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, 
                  setup TEXT, comment TEXT, setup_desc TEXT, image TEXT)''')
    conn.commit()

# --- 3. DATA LOGIC ---
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
        <div style="font-family:Rajdhani; font-size:0.7rem; color:#bc13fe;">{acc_name.upper()} EQUITY</div>
        <div style="font-size:1.8rem; font-weight:700;">${current_bal:,.2f}</div>
        <div style="font-size:0.8rem; color:{'#00ffcc' if daily_pnl >= 0 else '#ff4b4b'};">
            {daily_pnl:+.2f} USD TODAY
        </div>
    </div>
    """, unsafe_allow_html=True)
    choice = st.radio("MENU", ["TERMINAL", "CALENDAR", "PERFORMANCE", "JOURNAL", "ARCHIVE"])

st.markdown('<div class="welcome-text">SYSTEM ONLINE. ANALYZING SHADOW PERFORMANCE.</div>', unsafe_allow_html=True)

# --- 5. TERMINAL (الشارت المحسن والمتحرك) ---
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
            comment = st.text_area("Notes")
            img_file = st.file_uploader("Screenshot", type=['png', 'jpg'])
            if st.form_submit_button("LOCK TRADE"):
                now_ts = datetime.now().strftime('%H:%M:%S') # تسجيل الوقت الدقيق
                img_data = base64.b64encode(img_file.read()).decode() if img_file else None
                c.execute("INSERT INTO trades (date, timestamp, pair, outcome, pnl, rr, balance, setup, comment, image) VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (str(d_in), now_ts, asset, res, p_val, r_val, current_bal, setup, comment, img_data))
                conn.commit()
                st.rerun()
    with c2:
        if not df.empty:
            # دمج التاريخ والوقت لضمان تحرك الشارت أفقياً
            df['full_time'] = df['date'] + " " + df['timestamp'].fillna("00:00:00")
            df_chart = df.sort_values(by='full_time')
            df_chart['pnl_percent'] = (df_chart['pnl'].cumsum() / init_amount) * 100
            
            last_val = df_chart['pnl_percent'].iloc[-1]
            l_color = "#00ffcc" if last_val > 0 else "#ff4b4b" if last_val < 0 else "#ffcc00"
            f_color = f"rgba({int(l_color[1:3], 16)}, {int(l_color[3:5], 16)}, {int(l_color[5:7], 16)}, 0.1)"

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_chart['full_time'], y=df_chart['pnl_percent'], mode='lines+markers',
                                     line=dict(color=l_color, width=3, shape='spline'), fill='tozeroy', fillcolor=f_color,
                                     marker=dict(size=8, color=l_color)))
            fig.add_hline(y=0, line_dash="dash", line_color="#444", line_width=1)
            fig.update_layout(title="GROWTH CURVE (%)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font_family="Rajdhani", yaxis_ticksuffix="%",
                              xaxis_title="Time Line")
            st.plotly_chart(fig, use_container_width=True)

# --- 6. PERFORMANCE (مع معادلة Profit Factor الصحيحة) ---
elif choice == "PERFORMANCE":
    if not df.empty:
        wins_df = df[df['pnl'] > 0]
        losses_df = df[df['pnl'] < 0]
        
        gross_profit = wins_df['pnl'].sum()
        gross_loss = abs(losses_df['pnl'].sum())
        
        # Profit Factor = Gross Profit / Gross Loss
        pf = gross_profit / gross_loss if gross_loss != 0 else gross_profit
        wr = (len(wins_df)/len(df))*100
        avg_rr = df['rr'].mean()
        consistency = max(0, min(100, 100 - ((df['pnl'].std() / abs(df['pnl'].mean())) * 10))) if len(df)>2 else 0

        c_g, c_s = st.columns([1, 1.5])
        with c_g:
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=wr, number={'suffix':"%", 'font':{'family':'Rajdhani'}}, 
                                                  gauge={'bar':{'color':"#00ffcc"}})).update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)'), use_container_width=True)
        with c_s:
            r1 = st.columns(3)
            r1[0].markdown(f'<div class="perf-card"><h4>{avg_rr:.2f}</h4><p>Avg RR</p></div>', unsafe_allow_html=True)
            r1[1].markdown(f'<div class="perf-card"><h4>{pf:.2f}</h4><p>Profit Factor</p></div>', unsafe_allow_html=True)
            r1[2].markdown(f'<div class="perf-card"><h4>{consistency:.0f}%</h4><p>Consistency</p></div>', unsafe_allow_html=True)
            r2 = st.columns(2)
            r2[0].markdown(f'<div class="perf-card"><h4 style="color:#00ffcc">${df["pnl"].max():,.0f}</h4><p>Best</p></div>', unsafe_allow_html=True)
            r2[1].markdown(f'<div class="perf-card"><h4 style="color:#ff4b4b">${df["pnl"].min():,.0f}</h4><p>Worst</p></div>', unsafe_allow_html=True)
        
        net = df['pnl'].sum()
        st.markdown(f'<div style="text-align:center; margin-top:30px;"><h1 style="color:{"#00ffcc" if net>=0 else "#ff4b4b"}; font-size:3.5rem; font-family:Rajdhani;">${net:,.2f}</h1><p>TOTAL NET PROFIT</p></div>', unsafe_allow_html=True)

# (باقي الأقسام Calendar و Journal و Archive تبقى كما هي لضمان عدم تغيير أي وظيفة أخرى)
elif choice == "CALENDAR":
    if not df.empty:
        first_day = df['date_dt'].min().replace(day=1)
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        st.markdown(f"<h2 style='text-align:center; color:#00d4ff; font-family:Rajdhani;'>{first_day.strftime('%B %Y').upper()}</h2>", unsafe_allow_html=True)
        cols_h = st.columns(7)
        for i, wd in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
            cols_h[i].markdown(f"<div style='text-align:center; color:#00ffcc; font-size:0.8rem;'>{wd}</div>", unsafe_allow_html=True)
        start_padding = first_day.weekday()
        for row in range(0, start_padding + last_day_num, 7):
            cols = st.columns(7)
            for i in range(7):
                idx = row + i
                with cols[i]:
                    if start_padding <= idx < start_padding + last_day_num:
                        d_num = idx - start_padding + 1
                        curr_date = first_day.replace(day=d_num)
                        d_pnl = df[df['date_dt'].dt.date == curr_date.date()]['pnl'].sum()
                        txt = "#00ffcc" if d_pnl > 0 else "#ff4b4b" if d_pnl < 0 else "#444"
                        st.markdown(f'<div style="border:1px solid #333; border-radius:10px; padding:5px; text-align:center; height:80px;"><div style="font-size:0.7rem;">{d_num}</div><div style="color:{txt}; font-weight:bold; font-size:0.8rem;">{f"${d_pnl:,.0f}" if d_pnl!=0 else ""}</div></div>', unsafe_allow_html=True)

elif choice == "JOURNAL":
    if not df.empty:
        for _, row in df.sort_values('id', ascending=False).iterrows():
            j_class = "journal-win" if row['outcome']=="WIN" else "journal-loss" if row['outcome']=="LOSS" else "journal-be"
            st.markdown(f'<div class="{j_class}">', unsafe_allow_html=True)
            with st.expander(f"● {row['date']} | {row['pair']} | ${row['pnl']:,.2f}"):
                tx, im = st.columns([1, 1.5])
                with tx: st.write(f"**Setup:** {row['setup']}"); st.info(f"Note: {row['comment']}")
                with im: 
                    if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif choice == "ARCHIVE":
    if not df.empty:
        df['m'] = df['date_dt'].dt.strftime('%B %Y')
        for m in df['m'].unique():
            with st.expander(f"📁 {m.upper()} | Net: ${df[df['m']==m]['pnl'].sum():,.2f}"):
                st.dataframe(df[df['m']==m][['date', 'pair', 'outcome', 'pnl', 'setup']], use_container_width=True)
