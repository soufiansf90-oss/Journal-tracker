import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import calendar
import base64
import os

# --- SETTINGS & UI ---
st.set_page_config(page_title="Elite Shadow Operator Lab", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Lexend:wght@300;500&display=swap');
.stApp { background: #050508; color: #eef2f6; font-family: 'Lexend', sans-serif; }
.welcome-text { font-family: 'Rajdhani'; color: #00d4ff; font-size: 1.6rem; text-align: center; font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 10px rgba(0,212,255,0.4); }
[data-testid="stSidebar"] { background-color: #080810; border-right: 2px solid #bc13fe33; }
.equity-box { background: rgba(188, 19, 254, 0.05); border: 1px solid #bc13fe; border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 10px rgba(188,19,254,0.2);}
.stRadio label { background: rgba(188, 19, 254, 0.02); border:1px solid rgba(188,19,254,0.3); padding:12px 20px; border-radius:15px; color:#8b949e; font-family:Rajdhani; font-size:1rem; margin-bottom:8px; transition:0.3s; }
.stRadio label[data-baseweb="radio"]:has(input:checked){border:1px solid #bc13fe !important; color:#bc13fe !important; box-shadow:0 0 15px rgba(188,19,254,0.4); background: rgba(188,19,254,0.1) !important;}
.journal-win { border-left: 5px solid #00ffcc; background: rgba(0,255,204,0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
.journal-loss { border-left: 5px solid #ff4b4b; background: rgba(255,75,75,0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
.journal-be { border-left: 5px solid #ffcc00; background: rgba(255,204,0,0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
.perf-card { background: rgba(20,20,30,0.8); border:1px solid #bc13fe33; padding:20px; border-radius:20px; text-align:center; }
.perf-card h4 { font-family:Rajdhani; color:#bc13fe; font-size:1.8rem; margin:0; }
.perf-card p { font-size:0.8rem; color:#64748b; text-transform:uppercase; margin-top:5px; }
</style>
""", unsafe_allow_html=True)

# --- MULTI-ACCOUNT SYSTEM ---
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani; color:#bc13fe; font-size:1.5rem; font-weight:700; text-align:center; padding-bottom:15px;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    existing_accounts = [f.replace('tracker_', '').replace('.db','') for f in os.listdir() if f.startswith('tracker_') and f.endswith('.db')]
    selected_acc = st.selectbox("📂 ACCOUNT", list(set(existing_accounts + ["+ New Account"])))
    
    if selected_acc == "+ New Account":
        acc_name = st.text_input("Account Name", "Main_Tracker").strip().replace(" ","_")
    else:
        acc_name = selected_acc

    init_amount = st.number_input("💰 INITIAL AMOUNT ($)", value=1000.0)

    db_path = f"tracker_{acc_name.lower()}.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, setup TEXT, comment TEXT, setup_desc TEXT, image TEXT)''')
    conn.commit()

# --- LOAD DATA ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
current_bal = init_amount
daily_pnl = 0.0
if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    current_bal = init_amount + df['pnl'].sum()
    daily_pnl = df[df['date']==datetime.now().strftime('%Y-%m-%d')]['pnl'].sum()

# --- SIDEBAR EQUITY & MENU ---
with st.sidebar:
    st.markdown(f"""
    <div class="equity-box">
        <div style="font-family:Rajdhani; font-size:0.7rem; color:#bc13fe;">{acc_name.upper()} EQUITY</div>
        <div style="font-size:1.8rem; font-weight:700;">${current_bal:,.2f}</div>
        <div style="font-size:0.8rem; color:{'#00ffcc' if daily_pnl>=0 else '#ff4b4b'};">
            {daily_pnl:+.2f} USD TODAY
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("MENU", ["WELCOME","TERMINAL","DASHBOARD","JOURNAL","CALENDAR","PERFORMANCE","ARCHIVE"])

# --- WELCOME / DASHBOARD ---
if choice=="WELCOME":
    st.markdown('<div class="welcome-text">Hi Shadow, this is your dashboard!</div>', unsafe_allow_html=True)

# --- TERMINAL ---
elif choice=="TERMINAL":
    with st.form("entry_form"):
        st.markdown("### 📥 Log New Trade")
        date_in = st.date_input("Date", datetime.now())
        pair = st.text_input("Pair", "NAS100").upper()
        outcome = st.selectbox("Outcome", ["WIN","LOSS","BE"])
        entry_price = st.number_input("Entry Price")
        sl = st.number_input("Stop Loss")
        tp = st.number_input("Take Profit")
        exit_price = st.number_input("Exit Price")
        rr = abs((exit_price-entry_price)/(entry_price-sl)) if entry_price!=sl else 0
        pnl = exit_price-entry_price
        comment = st.text_area("Notes")
        img_file = st.file_uploader("Screenshot", type=['png','jpg'])
        if st.form_submit_button("Add Trade"):
            img_data = base64.b64encode(img_file.read()).decode() if img_file else None
            c.execute("INSERT INTO trades (date,pair,outcome,pnl,rr,balance,setup,comment,image) VALUES (?,?,?,?,?,?,?,?,?)",
                      (str(date_in),pair,outcome,pnl,rr,current_bal,"",comment,img_data))
            conn.commit()
            st.experimental_rerun()

# --- DASHBOARD METRICS & CHARTS ---
elif choice=="DASHBOARD":
    if not df.empty:
        wins = df[df['pnl']>0]
        losses = df[df['pnl']<0]
        wr = (len(wins)/len(df))*100 if len(df)>0 else 0
        avg_rr = df['rr'].mean() if len(df)>0 else 0
        sum_w,sum_l = wins['pnl'].sum(), abs(losses['pnl'].sum())
        tf = sum_w/sum_l if sum_l!=0 else sum_w

        st.metric("Win Rate", f"{wr:.2f}%")
        st.metric("Average RR", f"{avg_rr:.2f}")
        st.metric("Trade Factor", f"{tf:.2f}")
        df_curve = df.sort_values('date_dt')
        df_curve['equity_curve'] = init_amount + df_curve['pnl'].cumsum()
        fig = px.line(df_curve,x='date_dt',y='equity_curve',title="Equity Curve (Weekly)", markers=True)
        fig.update_traces(line_color='#bc13fe', line_width=3)
        st.plotly_chart(fig,use_container_width=True)

# --- JOURNAL ---
elif choice=="JOURNAL":
    if not df.empty:
        for _,row in df.sort_values('id',ascending=False).iterrows():
            j_class = "journal-win" if row['pnl']>0 else "journal-loss" if row['pnl']<0 else "journal-be"
            st.markdown(f'<div class="{j_class}">',unsafe_allow_html=True)
            with st.expander(f"{row['date']} | {row['pair']} | ${row['pnl']:,.2f} | {row['rr']:.2f} RR"):
                st.write(f"Entry: {row.get('entry','')}, SL: {row.get('sl','')}, TP: {row.get('tp','')}, Exit: {row.get('exit','')}")
                st.info(f"Comment: {row.get('comment','')}")
            st.markdown('</div>',unsafe_allow_html=True)

# --- CALENDAR ---
elif choice=="CALENDAR":
    if not df.empty:
        first_day = df['date_dt'].min().replace(day=1)
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        st.markdown(f"<h2 style='text-align:center; color:#00d4ff; font-family:Rajdhani;'>{first_day.strftime('%B %Y').upper()}</h2>", unsafe_allow_html=True)
        cols_h = st.columns(7)
        for i,wd in enumerate(["MON","TUE","WED","THU","FRI","SAT","SUN"]):
            cols_h[i].markdown(f"<div style='text-align:center; color:#00ffcc; font-size:0.8rem; border-bottom:1px solid #333;'>{wd}</div>",unsafe_allow_html=True)
        start_padding = first_day.weekday()
        for row in range(0,start_padding+last_day_num,7):
            cols = st.columns(7)
            for i in range(7):
                idx = row+i
                with cols[i]:
                    if start_padding<=idx<start_padding+last_day_num:
                        d_num = idx-start_padding+1
                        curr_date = first_day.replace(day=d_num)
                        day_trades = df[df['date_dt'].dt.date==curr_date.date()]
                        d_pnl = day_trades['pnl'].sum()
                        bg,border,txt="rgba(255,255,255,0.02)","rgba(255,255,255,0.05)","#444"
                        p_str=""
                        if len(day_trades)>0:
                            if d_pnl>0: bg,border,txt="rgba(0,255,204,0.1)","#00ffcc","#00ffcc"; p_str=f"+${d_pnl:,.0f}"
                            elif d_pnl<0: bg,border,txt="rgba(255,75,75,0.1)","#ff4b4b","#ff4b4b"; p_str=f"-${abs(d_pnl):,.0f}"
                            else: bg,border,txt="rgba(255,204,0,0.1)","#ffcc00","#ffcc00"; p_str="$0"
                        st.markdown(f'<div style="background:{bg}; border:1px solid {border}; border-radius:12px; padding:10px; height:90px; text-align:center; margin-bottom:5px;"><div style="font-size:0.7rem; color:#888;">{d_num}</div><div style="color:{txt}; font-weight:bold; font-size:0.85rem;">{p_str}</div><div style="font-size:0.5rem; color:#00d4ff;">{f"{len(day_trades)} T" if len(day_trades)>0 else ""}</div></div>',unsafe_allow_html=True)

# --- PERFORMANCE & ANALYTICS ---
elif choice=="PERFORMANCE":
    if not df.empty:
        wins = df[df['outcome']=="WIN"]
        losses = df[df['outcome']=="LOSS"]
        be = df[df['outcome']=="BE"]
        total = len(df)
        win_perc = len(wins)/total*100 if total>0 else 0
        loss_perc = len(losses)/total*100 if total>0 else 0
        be_perc = len(be)/total*100 if total>0 else 0
        st.plotly_chart(px.pie(names=["WIN","LOSS","BE"],values=[win_perc,loss_perc,be_perc],hole=0.4,color_discrete_map={"WIN":"#00ffcc","LOSS":"#ff4b4b","BE":"#ffcc00"}),use_container_width=True)

# --- ARCHIVE ---
elif choice=="ARCHIVE":
    if not df.empty:
        df['m'] = df['date_dt'].dt.strftime('%B %Y')
        for m in df['m'].unique():
            with st.expander(f"📁 {m.upper()} | Net: ${df[df['m']==m]['pnl'].sum():,.2f}"):
                st.dataframe(df[df['m']==m][['date','pair','outcome','pnl','rr','balance','setup','comment']],use_container_width=True)
