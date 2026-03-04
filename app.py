import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------
# 🌌 ELITE SYSTEM CONFIG
# -----------------------------
st.set_page_config(page_title="ELITE OPERATOR OS", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Cyber-Industrial Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; background-color: #050505; }
    
    .stMetric {
        background: linear-gradient(135deg, #0f0f12 0%, #1a1a1f 100%);
        border-left: 5px solid #7B2FF7;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#66FCF1, #7B2FF7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(123, 47, 247, 0.3);
    }
    
    .status-card {
        background: #111;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 💾 DATABASE CORE (Persistent Connection)
# -----------------------------
def init_db():
    conn = sqlite3.connect("elite_v2.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY, name TEXT, balance REAL, max_daily_loss REAL, risk_per_trade REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, asset TEXT, setup TEXT,
        entry REAL, sl REAL, tp REAL, exit REAL, pnl REAL,
        emotion TEXT, rule_break INTEGER, comment TEXT)""")
    conn.commit()
    return conn

conn = init_db()

# -----------------------------
# 🧠 LOGIC & CALCULATIONS
# -----------------------------
def get_trades():
    df = pd.read_sql("SELECT * FROM trades", conn)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
    return df

def get_account():
    return pd.read_sql("SELECT * FROM accounts LIMIT 1", conn)

# -----------------------------
# 📟 SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.markdown("<h1 style='color:#66FCF1'>⚡ OPERATOR OS</h1>", unsafe_allow_html=True)
nav = st.sidebar.radio("COMMAND", ["STRATEGIC DASHBOARD", "MISSION JOURNAL", "PSYCH-LAB", "SYSTEM CONFIG"])

acc_data = get_account()

if acc_data.empty and nav != "SYSTEM CONFIG":
    st.warning("🚨 SYSTEM OFFLINE: Configure account in SYSTEM CONFIG first.")
    st.stop()

# -----------------------------
# 📊 PAGE 1: STRATEGIC DASHBOARD
# -----------------------------
if nav == "STRATEGIC DASHBOARD":
    st.markdown("<p class='main-header'>CONTROL CENTER</p>", unsafe_allow_html=True)
    trades_df = get_trades()
    
    if trades_df.empty:
        st.info("Awaiting mission data... No trades logged.")
    else:
        # Metrics Row
        total_pnl = trades_df['pnl'].sum()
        win_rate = (len(trades_df[trades_df['pnl'] > 0]) / len(trades_df)) * 100
        profit_factor = abs(trades_df[trades_df['pnl'] > 0]['pnl'].sum() / trades_df[trades_df['pnl'] < 0]['pnl'].sum()) if any(trades_df['pnl'] < 0) else 1.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("NET PROFIT", f"${total_pnl:,.2f}")
        m2.metric("WIN RATE", f"{win_rate:.1f}%")
        m3.metric("PROFIT FACTOR", f"{profit_factor:.2f}")
        m4.metric("AVG RRR", f"{trades_df['pnl'].mean():,.2f}")

        # Equity Curve
        st.subheader("📈 Equity Progression")
        trades_df = trades_df.sort_values('date')
        trades_df['cum_pnl'] = acc_data.iloc[0]['balance'] + trades_df['pnl'].cumsum()
        
        fig = px.area(trades_df, x='date', y='cum_pnl', color_discrete_sequence=['#66FCF1'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

        # Performance Heatmap (The "Calendar" Art)
        st.subheader("📅 Performance Heatmap")
        trades_df['date_only'] = trades_df['date'].dt.date
        daily_pnl = trades_df.groupby('date_only')['pnl'].sum().reset_index()
        
        fig_heat = px.bar(daily_pnl, x='date_only', y='pnl', color='pnl',
                         color_continuous_scale=['#FF3131', '#000000', '#39FF14'])
        st.plotly_chart(fig_heat, use_container_width=True)

# -----------------------------
# 📝 PAGE 2: MISSION JOURNAL
# -----------------------------
elif nav == "MISSION JOURNAL":
    st.markdown("<p class='main-header'>MISSION LOG</p>", unsafe_allow_html=True)
    
    with st.expander("📝 NEW EXECUTION ENTRY"):
        with st.form("trade_entry"):
            c1, c2, c3 = st.columns(3)
            date = c1.date_input("Date", datetime.now())
            asset = c2.text_input("Asset (e.g. NQ, Gold)")
            setup = c3.selectbox("Setup", ["Break & Retest", "Liquidity Sweep", "FVG Fill", "Order Block"])
            
            c4, c5, c6, c7 = st.columns(4)
            entry = c4.number_input("Entry", format="%.5f")
            sl = c5.number_input("Stop Loss", format="%.5f")
            tp = c6.number_input("Take Profit", format="%.5f")
            exit_p = c7.number_input("Exit Price", format="%.5f")
            
            emotion = st.select_slider("Emotional State", ["Extreme Fear", "Anxious", "Neutral", "Confident", "Greedy"])
            rule_break = st.checkbox("Protocol Breach (Rule Broken)")
            comment = st.text_area("Debrief / Notes")
            
            if st.form_submit_button("LOCK MISSION"):
                pnl = exit_p - entry # Simple math; scale with contracts/lots as needed
                conn.execute("INSERT INTO trades (date, asset, setup, entry, sl, tp, exit, pnl, emotion, rule_break, comment) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                             (str(date), asset, setup, entry, sl, tp, exit_p, pnl, emotion, int(rule_break), comment))
                conn.commit()
                st.success("Mission data stored.")
                st.rerun()

    trades_df = get_trades()
    if not trades_df.empty:
        st.dataframe(trades_df.style.background_gradient(subset=['pnl'], cmap='RdYlGn'), use_container_width=True)

# -----------------------------
# 🧠 PAGE 3: PSYCH-LAB
# -----------------------------
elif nav == "PSYCH-LAB":
    st.markdown("<p class='main-header'>PSYCHOLOGY LAB</p>", unsafe_allow_html=True)
    df = get_trades()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Profit/Loss by Emotion")
            emo_stats = df.groupby('emotion')['pnl'].sum().reset_index()
            fig_emo = px.pie(emo_stats, values='pnl', names='emotion', hole=.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_emo)
            
        with col2:
            st.subheader("🚫 Discipline Impact")
            rules = df.groupby('rule_break')['pnl'].sum().reset_index()
            rules['Status'] = rules['rule_break'].map({1: "Breached", 0: "Disciplined"})
            fig_rules = px.bar(rules, x='Status', y='pnl', color='Status', color_discrete_map={"Breached":"#FF3131", "Disciplined":"#39FF14"})
            st.plotly_chart(fig_rules)
            
        st.divider()
        st.subheader("Critical Insight")
        breached_sum = df[df['rule_break'] == 1]['pnl'].sum()
        if breached_sum < 0:
            st.error(f"⚠️ Lack of discipline has cost you **${abs(breached_sum):,.2f}** total.")
        else:
            st.success("✅ You are maintaining high discipline.")

# -----------------------------
# ⚙️ PAGE 4: SYSTEM CONFIG
# -----------------------------
elif nav == "SYSTEM CONFIG":
    st.markdown("<p class='main-header'>SYSTEM CONFIG</p>", unsafe_allow_html=True)
    
    with st.form("settings"):
        name = st.text_input("Operator Name", value=acc_data.iloc[0]['name'] if not acc_data.empty else "")
        bal = st.number_input("Starting Capital", value=acc_data.iloc[0]['balance'] if not acc_data.empty else 10000.0)
        mdl = st.number_input("Max Daily Loss Cap", value=acc_data.iloc[0]['max_daily_loss'] if not acc_data.empty else 500.0)
        
        if st.form_submit_button("UPDATE SYSTEM"):
            conn.execute("DELETE FROM accounts")
            conn.execute("INSERT INTO accounts (name, balance, max_daily_loss) VALUES (?,?,?)", (name, bal, mdl))
            conn.commit()
            st.success("System updated.")
            st.rerun()

    if st.button("🔴 FACTORY RESET (Delete All Data)"):
        conn.execute("DELETE FROM trades")
        conn.execute("DELETE FROM accounts")
        conn.commit()
        st.rerun()

