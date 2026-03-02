import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import calendar
import base64

# --- SETTINGS & NEON UI ---
st.set_page_config(page_title="369 SHADOW V44", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');

.stApp { background: #05070a; color: #e6edf3; font-family: 'Inter', sans-serif; }

/* Welcome Message */
.welcome-text { font-family: 'Orbitron'; color: #00d4ff; font-size: 2rem; text-align: center; margin-bottom: 25px; text-shadow: 0 0 25px rgba(0,212,255,0.8); letter-spacing: 2px; }

/* Animation 0.5s */
.content-fade { animation: slideUp 0.5s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* Sidebar Styling */
[data-testid="stSidebar"] { background-color: #080b10; border-right: 2px solid #00d4ff33; padding-top:20px; }

/* Sidebar Buttons Neon */
div[data-testid="stSidebar"] .stRadio > label { display: none; }
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 20px; }
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(255,255,255,0.03);
    border: 2px solid rgba(0,212,255,0.2);
    padding: 25px !important;
    border-radius: 50% !important;
    width: 100%;
    height: 100px;
    color: #8b949e;
    font-family: 'Orbitron';
    font-size: 1rem;
    text-transform: uppercase;
    text-align:center;
    line-height: 50px;
    transition: all 0.3s;
    box-shadow: 0 0 15px rgba(128,0,255,0.2);
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(128,0,255,0.2) !important;
    border-color: #bf00ff !important;
    color: #bf00ff !important;
    box-shadow: 0 0 25px rgba(191,0,255,0.7);
}

/* Journal Colors */
.journal-win { border-left: 5px solid #34d399 !important; background: rgba(52,211,153,0.05) !important; }
.journal-loss { border-left: 5px solid #ef4444 !important; background: rgba(239,68,68,0.05) !important; }
.journal-be { border-left: 5px solid #fbbf24 !important; background: rgba(251,191,36,0.05) !important; }

/* Performance Cards */
.perf-card { background: rgba(22,27,34,0.6); border: 1px solid rgba(128,0,255,0.2); padding: 20px; border-radius: 20px; text-align: center; transition: all 0.3s; box-shadow: 0 0 15px rgba(191,0,255,0.3); }
.perf-card:hover { border-color: #bf00ff; box-shadow: 0 0 25px rgba(191,0,255,0.5); }
.perf-val { font-size: 1.8rem; font-weight: bold; font-family: 'Orbitron'; color: #e6edf3; }
.perf-label { font-size: 0.8rem; color: #bf00ff; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }

</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
conn = sqlite3.connect('elite_v44.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, setup TEXT, image TEXT)''')
conn.commit()

# --- DATA PREP ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
current_balance, daily_net_pnl, initial_bal = 0.0, 0.0, 1000.0

if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date_dt','id'])
    initial_bal = df['balance'].iloc[0]
    df['cum_pnl'] = df['pnl'].cumsum()
    df['equity_curve'] = initial_bal + df['cum_pnl']
    current_balance = df['equity_curve'].iloc[-1]
    daily_net_pnl = df[df['date']==datetime.now().strftime('%Y-%m-%d')]['pnl'].sum()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div style="text-align:center; font-family:Orbitron; font-size:1.5rem; color:#bf00ff; text-shadow:0 0 15px #bf00ff66;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    st.divider()
    account_balance = st.number_input("Account Balance ($)", value=current_balance if current_balance>0 else 1000.0)
    st.divider()
    choice = st.radio("MENU", ["TERMINAL","CALENDAR","PERFORMANCE","JOURNAL","LAST 12 MONTHS"])
    st.divider()
    st.metric("EQUITY STATUS", f"${current_balance:,.2f}", f"{daily_net_pnl:+.2f} USD")

# --- WELCOME ---
st.markdown('<div class="welcome-text">WHAT\'S UP SHADOW, LET\'S SEE WHAT HAPPENED TODAY.</div>', unsafe_allow_html=True)
st.markdown('<div class="content-fade">', unsafe_allow_html=True)

# --- MAIN CONTENT ---

# ---------- TERMINAL ----------
if choice=="TERMINAL":
    c1,c2 = st.columns([1,2.3])
    with c1:
        with st.form("entry_form"):
            st.markdown("### 📥 LOG ENTRY")
            d_in = st.date_input("Date", datetime.now())
            asset = st.text_input("Pair", "NAS100").upper()
            res = st.selectbox("Outcome", ["WIN","LOSS","BE"])
            p_val = st.number_input("P&L ($)", value=0.0)
            r_val = st.number_input("RR Ratio", value=0.0)
            setup = st.text_input("Setup").upper()
            mind = st.selectbox("Mindset", ["Focused","Impulsive","Revenge","Bored"])
            img_file = st.file_uploader("Screenshot", type=['png','jpg','jpeg'])
            if st.form_submit_button("LOCK TRADE"):
                img_data = base64.b64encode(img_file.read()).decode() if img_file else None
                c.execute("INSERT INTO trades (date,pair,outcome,pnl,rr,balance,mindset,setup,image) VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(d_in), asset, res, p_val, r_val, account_balance, mind, setup, img_data))
                conn.commit()
                st.rerun()
    with c2:
        if not df.empty:
            # --- EQUITY CURVE PROFESSIONNEL ---
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date_dt'],
                y=df['equity_curve'],
                mode='lines+markers',
                line=dict(color='#bf00ff', width=4, shape='spline'),
                marker=dict(size=6, color='#ff00ff'),
                fill='tonexty',
                fillcolor='rgba(191,0,255,0.1)'
            ))
            fig.update_layout(
                template="plotly_dark",
                height=480,
                title="ACCOUNT EQUITY CURVE",
                xaxis_title="Date",
                yaxis_title="Balance ($)",
                font=dict(family="Orbitron", size=12, color="#e6edf3"),
                hovermode="x unified",
                xaxis=dict(showgrid=True, gridcolor='rgba(191,0,255,0.2)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(191,0,255,0.2)')
            )
            st.plotly_chart(fig,use_container_width=True)

# ---------- PERFORMANCE ----------
elif choice=="PERFORMANCE":
    if not df.empty:
        wins = df[df['pnl']>0]; losses = df[df['pnl']<0]
        wr = (len(wins)/len(df))*100 if len(df)>0 else 0
        pf = wins['pnl'].sum()/abs(losses['pnl'].sum()) if not losses.empty else 0

        st.markdown("#### ⚡ PRIMARY METRICS")
        g1,g2,g3,g4 = st.columns(4)
        for col,label,val in zip([g1,g2,g3,g4], ["Win Rate","Profit Factor","Avg RR","Net P&L"],
                                 [f"{wr:.1f}%", f"{pf:.2f}", f"{df['rr'].mean():.2f}", f"${df['pnl'].sum():,.0f}"]):
            col.markdown(f'<div class="perf-card"><div class="perf-val">{val}</div><div class="perf-label">{label}</div></div>',unsafe_allow_html=True)

# ---------- JOURNAL ----------
elif choice=="JOURNAL":
    if not df.empty:
        st.markdown("### 📜 TRADE ARCHIVE BY MONTHS")
        # تجميع شهري
        df['month_year'] = df['date_dt'].dt.to_period('M')
        months = df['month_year'].sort_values(ascending=False).unique()
        for month in months:
            st.markdown(f"#### {month.strftime('%B %Y')}")
            month_df = df[df['month_year']==month]
            for idx,row in month_df.sort_values('id',ascending=False).iterrows():
                j_class = "journal-win" if row['pnl']>0 else "journal-loss" if row['pnl']<0 else "journal-be"
                with st.container():
                    st.markdown(f'<div class="{j_class}" style="padding:10px; border-radius:0 10px 10px 0; margin-bottom:10px;">',unsafe_allow_html=True)
                    with st.expander(f"● {row['date']} | {row['pair']} | P&L: ${row['pnl']:,.2f} | Setup: {row['setup']}"):
                        tx,im = st.columns([1,2])
                        with tx:
                            st.write(f"**Outcome:** {row['outcome']}")
                            st.write(f"**RR:** {row['rr']} | **Mindset:** {row['mindset']}")
                        with im:
                            if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)
                    st.markdown('</div>',unsafe_allow_html=True)

# ---------- CALENDAR ----------
elif choice=="CALENDAR":
    if not df.empty:
        active_df = df.copy()
        first_day = active_df['date_dt'].min().replace(day=1)
        month_name = first_day.strftime('%B %Y')
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        st.markdown(f"<h3 style='text-align:center; color:#00d4ff; font-family:Orbitron;'>{month_name}</h3>", unsafe_allow_html=True)
        weekdays = ["MON","TUE","WED","THU","FRI","SAT","SUN"]
        header_cols = st.columns(7)
        for i, wd in enumerate(weekdays):
            header_cols[i].markdown(f"<center style='color:#00ffcc; font-size:0.8rem; font-family:Orbitron;'>{wd}</center>", unsafe_allow_html=True)
        month_days = pd.date_range(start=first_day, periods=last_day_num)
        start_padding = month_days[0].weekday()
        cols = st.columns(7)
        for i in range(start_padding):
            cols[i].write("")
        for day in month_days:
            current_col = (day.day + start_padding - 1) % 7
            with cols[current_col]:
                day_str = day.strftime('%Y-%m-%d')
                trades_today = active_df[active_df['date_dt'].dt.strftime('%Y-%m-%d')==day_str]
                daily_pnl = trades_today['pnl'].sum()
                num_trades = len(trades_today)
                bg, border_color, text_color = "rgba(255,255,255,0.02)", "rgba(255,255,255,0.1)", "#8b949e"
                if num_trades > 0:
                    if daily_pnl > 0: bg, border_color, text_color = "rgba(0,255,204,0.1)", "#00ffcc", "#00ffcc"
                    elif daily_pnl < 0: bg, border_color, text_color = "rgba(255,75,75,0.1)", "#ff4b4b", "#ff4b4b"
                    else: bg, border_color, text_color = "rgba(255,204,0,0.1)", "#ffcc00", "#ffcc00"
                st.markdown(f"""
                <div style="background:{bg}; border:1px solid {border_color}; border-radius:8px; padding:8px; height:110px; text-align:center; margin-bottom:10px;">
                    <div style="font-size:0.75rem; opacity:0.6; color:#fff;">{day.day}</div>
                    <div style="color:{text_color}; font-weight:bold; font-size:1rem; margin-top:5px;">
                        {f'${daily_pnl:,.0f}' if num_trades > 0 else ''}
                    </div>
                    <div style="font-size:0.65rem; color:#00d4ff; margin-top:5px; font-family:Orbitron;">
                        {f'{num_trades} TRADES' if num_trades > 0 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            if current_col == 6 and day.day != last_day_num: cols = st.columns(7)

st.markdown('</div>', unsafe_allow_html=True)
