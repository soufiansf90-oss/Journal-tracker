import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import calendar
import base64
import os
import plotly.express as px
import plotly.graph_objects as go

# ================================
# 369 SHADOW PRO – FULL ELITE LAB
# ================================

# --- 1. SETTINGS & NEON UI ---
st.set_page_config(page_title="369 SHADOW PRO", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Lexend:wght@300;500&display=swap');
.stApp { background: #050508; color: #eef2f6; font-family: 'Lexend', sans-serif; }
.welcome-text { font-family: 'Rajdhani'; color: #00d4ff; font-size: 1.6rem; text-align: center; font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 10px rgba(0,212,255,0.4); }
[data-testid="stSidebar"] { background-color: #080810; border-right: 2px solid #bc13fe33; }
.equity-box { background: rgba(188, 19, 254, 0.05); border: 1px solid #bc13fe; border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 10px rgba(188,19,254,0.2); }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(188, 19, 254, 0.02) !important; border: 1px solid rgba(188, 19, 254, 0.3) !important;
    padding: 12px 20px !important; border-radius: 15px !important; color: #8b949e; font-family: 'Rajdhani'; font-size: 1rem; margin-bottom: 8px; transition: 0.3s;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    border: 1px solid #bc13fe !important; color: #bc13fe !important; 
    box-shadow: 0 0 15px rgba(188,19,254,0.4); background: rgba(188, 19, 254, 0.1) !important;
}
.journal-win { border-left: 5px solid #00ffcc; background: rgba(0, 255, 204, 0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
.journal-loss { border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
.journal-be { border-left: 5px solid #ffcc00; background: rgba(255, 204, 0, 0.05); padding:15px; border-radius:15px; margin-bottom:15px; }
.perf-card { background: rgba(20, 20, 30, 0.8); border: 1px solid #bc13fe33; padding: 20px; border-radius: 20px; text-align: center; }
.perf-card h4 { font-family: 'Rajdhani'; color: #bc13fe; font-size: 1.8rem; margin:0; }
.perf-card p { font-size: 0.8rem; color: #64748b; text-transform: uppercase; margin-top:5px; }
</style>
""", unsafe_allow_html=True)

# --- 2. MULTI-ACCOUNT SYSTEM ---
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani; color:#bc13fe; font-size:1.5rem; font-weight:700; text-align:center; padding-bottom:15px;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    # List existing DBs
    existing_accounts = [f.replace('tracker_', '').replace('.db', '') for f in os.listdir() if f.startswith('tracker_') and f.endswith('.db')]
    selected_acc = st.selectbox("📂 ACCOUNT", options=list(set(existing_accounts + ["+ New Account"])))
    
    # New account creation
    if selected_acc == "+ New Account":
        acc_name_input = st.text_input("Account Name", "Main_Tracker").strip().replace(" ","_")
        init_amount = st.number_input("💰 INITIAL AMOUNT ($)", value=1000.0)
        if st.button("CREATE ACCOUNT"):
            db_path = f"tracker_{acc_name_input.lower()}.db"
            if not os.path.exists(db_path):
                conn = sqlite3.connect(db_path, check_same_thread=False)
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS trades 
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, 
                              outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, 
                              setup TEXT, comment TEXT, setup_desc TEXT, image TEXT)''')
                conn.commit()
                st.success(f"Account '{acc_name_input}' created!")
                st.experimental_rerun()
            else:
                st.warning("Account already exists.")
        st.stop()
    else:
        acc_name_input = selected_acc

# Connect DB for selected account
db_path = f"tracker_{acc_name_input.lower()}.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()
df = pd.read_sql_query("SELECT * FROM trades", conn)
if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])

# Compute dynamic balances
current_bal = df['balance'].iloc[-1] if not df.empty else init_amount
daily_pnl = df[df['date'] == datetime.now().strftime('%Y-%m-%d')]['pnl'].sum() if not df.empty else 0.0

# --- 3. SIDEBAR EQUITY + MENU ---
with st.sidebar:
    st.markdown(f"""
    <div class="equity-box">
        <div style="font-family:Rajdhani; font-size:0.7rem; color:#bc13fe;">{acc_name_input.upper()} EQUITY</div>
        <div style="font-size:1.8rem; font-weight:700;">${current_bal:,.2f}</div>
        <div style="font-size:0.8rem; color:{'#00ffcc' if daily_pnl >= 0 else '#ff4b4b'};">
            {daily_pnl:+.2f} USD TODAY
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("MENU", ["TERMINAL", "CALENDAR", "PERFORMANCE", "JOURNAL", "ARCHIVE"])

st.markdown('<div class="welcome-text">SYSTEM ONLINE. ANALYZING SHADOW PERFORMANCE.</div>', unsafe_allow_html=True)

# --- 4. TERMINAL PAGE ---
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
            img_file = st.file_uploader("Screenshot", type=['png','jpg'])
            if st.form_submit_button("LOCK TRADE"):
                img_data = base64.b64encode(img_file.read()).decode() if img_file else None
                current_bal_new = current_bal + p_val
                c.execute("INSERT INTO trades (date, pair, outcome, pnl, rr, balance, setup, comment, image) VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(d_in), asset, res, p_val, r_val, current_bal_new, setup, comment, img_data))
                conn.commit()
                st.experimental_rerun()
    with c2:
        if not df.empty:
            df_chart = df.sort_values('date_dt')
            df_chart['equity_curve'] = df_chart['balance']
            fig = px.line(df_chart, x='date_dt', y='equity_curve', title="GROWTH CURVE")
            fig.update_traces(line_color='#bc13fe', line_width=3)
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', font_family="Rajdhani")
            st.plotly_chart(fig, use_container_width=True)

# --- 5. CALENDAR ---
elif choice == "CALENDAR":
    if not df.empty:
        first_day = df['date_dt'].min().replace(day=1)
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        st.markdown(f"<h2 style='text-align:center; color:#00d4ff; font-family:Rajdhani;'>{first_day.strftime('%B %Y').upper()}</h2>", unsafe_allow_html=True)
        cols_h = st.columns(7)
        for i, wd in enumerate(["MON","TUE","WED","THU","FRI","SAT","SUN"]):
            cols_h[i].markdown(f"<div style='text-align:center; color:#00ffcc; font-size:0.8rem; border-bottom:1px solid #333;'>{wd}</div>", unsafe_allow_html=True)
        start_padding = first_day.weekday()
        for row in range(0, start_padding+last_day_num, 7):
            cols = st.columns(7)
            for i in range(7):
                idx = row + i
                with cols[i]:
                    if start_padding <= idx < start_padding + last_day_num:
                        d_num = idx - start_padding + 1
                        curr_date = first_day.replace(day=d_num)
                        day_trades = df[df['date_dt'].dt.date == curr_date.date()]
                        d_pnl = day_trades['pnl'].sum()
                        bg, border, txt = "rgba(255,255,255,0.02)", "rgba(255,255,255,0.05)", "#444"
                        p_str = ""
                        if len(day_trades) > 0:
                            if d_pnl > 0: bg,border,txt="rgba(0,255,204,0.1)","#00ffcc","#00ffcc"; p_str=f"+${d_pnl:,.0f}"
                            elif d_pnl < 0: bg,border,txt="rgba(255,75,75,0.1)","#ff4b4b","#ff4b4b"; p_str=f"-${abs(d_pnl):,.0f}"
                            else: bg,border,txt="rgba(255,204,0,0.1)","#ffcc00","#ffcc00"; p_str="$0"
                        st.markdown(f'<div style="background:{bg}; border:1px solid {border}; border-radius:12px; padding:10px; height:90px; text-align:center; margin-bottom:5px;"><div style="font-size:0.7rem; color:#888;">{d_num}</div><div style="color:{txt}; font-weight:bold; font-size:0.85rem;">{p_str}</div><div style="font-size:0.5rem; color:#00d4ff;">{f"{len(day_trades)} T" if len(day_trades)>0 else ""}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        sel_day = st.selectbox("Review Day:", sorted(df['date_dt'].dt.day.unique()))
        st.dataframe(df[df['date_dt'].dt.day == sel_day][['date','pair','outcome','pnl','rr']], use_container_width=True)

# --- 6. PERFORMANCE ---
elif choice == "PERFORMANCE":
    if not df.empty:
        wins = df[df['pnl']>0]
        losses = df[df['pnl']<0]
        wr = (len(wins)/len(df))*100 if len(df)>0 else 0
        avg_rr = df['rr'].mean() if len(df)>0 else 0
        sum_w,sum_l = wins['pnl'].sum(), abs(losses['pnl'].sum())
        tf = sum_w/sum_l if sum_l!=0 else sum_w
        consistency = max(0,min(100,100 - ((df['pnl'].std()/abs(df['pnl'].mean()))*10))) if len(df)>2 else 0

        c_g,c_s = st.columns([1,1.5])
        with c_g:
            fig_g = go.Figure(go.Indicator(mode="gauge+number", value=wr, number={'suffix':"%", 'font':{'family':'Rajdhani'}}, gauge={'bar':{'color':"#00ffcc"}}))
            fig_g.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_g, use_container_width=True)
        with c_s:
            r1=st.columns(3)
            r1[0].markdown(f'<div class="perf-card"><h4>{avg_rr:.2f}</h4><p>Avg RR</p></div>',unsafe_allow_html=True)
            r1[1].markdown(f'<div class="perf-card"><h4>{tf:.2f}</h4><p>Factor</p></div>',unsafe_allow_html=True)
            r1[2].markdown(f'<div class="perf-card"><h4>{consistency:.0f}%</h4><p>Consistency</p></div>',unsafe_allow_html=True)
            r2=st.columns(2)
            r2[0].markdown(f'<div class="perf-card"><h4 style="color:#00ffcc">${df["pnl"].max():,.0f}</h4><p>Best</p></div>',unsafe_allow_html=True)
            r2[1].markdown(f'<div class="perf-card"><h4 style="color:#ff4b4b">${df["pnl"].min():,.0f}</h4><p>Worst</p></div>',unsafe_allow_html=True)
        net=df['pnl'].sum()
        st.markdown(f'<div style="text-align:center; margin-top:30px;"><p style="color:#888;">TOTAL NET PROFIT</p><h1 style="color:{"#00ffcc" if net>=0 else "#ff4b4b"}; font-size:3.5rem; font-family:Rajdhani;">${net:,.2f}</h1></div>',unsafe_allow_html=True)

# --- 7. JOURNAL ---
elif choice=="JOURNAL":
    if not df.empty:
        for _,row in df.sort_values('id',ascending=False).iterrows():
            j_class = "journal-win" if row['outcome']=="WIN" else "journal-loss" if row['outcome']=="LOSS" else "journal-be"
            st.markdown(f'<div class="{j_class}">', unsafe_allow_html=True)
            with st.expander(f"● {row['date']} | {row['pair']} | ${row['pnl']:,.2f}"):
                tx,im = st.columns([1,1.5])
                with tx:
                    st.write(f"**Setup:** {row['setup']}")
                    st.info(f"Comment: {row['comment']}")
                with im:
                    if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 9. ARCHIVE FULL DETAIL + STATS ---
elif page=="ARCHIVE":
    if not df.empty:
        # إنشاء عمود الشهر لكل صفقة
        df['m'] = df['date_dt'].dt.strftime('%B %Y')
        
        for m in df['m'].unique():
            month_df = df[df['m'] == m]
            net = month_df['pnl'].sum()
            wins = month_df[month_df['pnl'] > 0]
            losses = month_df[month_df['pnl'] < 0]
            wr = (len(wins)/len(month_df))*100 if len(month_df) > 0 else 0
            avg_rr = month_df['rr'].mean() if len(month_df) > 0 else 0
            
            with st.expander(f"📁 {m.upper()} | Net: ${net:,.2f} | Win Rate: {wr:.2f}% | Avg RR: {avg_rr:.2f}"):
                # عرض كل التفاصيل لكل صفقة
                st.dataframe(
                    month_df[['date','pair','outcome','pnl','rr','balance','setup','comment','mindset','setup_desc','image']],
                    use_container_width=True
                             )
