import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import calendar
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="ELITE OPERATOR LAB", layout="wide", initial_sidebar_state="expanded")

# -----------------------------
# DATABASE & DATA LOADING
# -----------------------------
def get_connection():
    return sqlite3.connect("elite_lab.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

# Initialize Tables
c.execute("""CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, starting_balance REAL, max_daily_loss REAL,
    max_trades INTEGER, min_rr REAL)""")

c.execute("""CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER,
    date TEXT, asset TEXT, market_type TEXT, session TEXT, setup TEXT,
    entry REAL, sl REAL, tp REAL, exit REAL, pnl REAL,
    rr_planned REAL, rr_achieved REAL, emotion TEXT, rule_break INTEGER,
    rating TEXT, comment TEXT, screenshot TEXT)""")

conn.commit()

# -----------------------------
# CSS – Neon Cyberpunk Style
# -----------------------------
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {background-color: #0B0C10;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .stMetric {
        background-color: #111217; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #7B2FF7;
        box-shadow: 0 0 10px #7B2FF7;
    }
    h1, h2, h3 {color: #66FCF1 !important; font-family: 'Courier New', monospace;}
    .stButton>button {
        width: 100%;
        background-color: #7B2FF7; 
        color: white; 
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #66FCF1;
        color: #0B0C10;
        box-shadow: 0 0 20px #66FCF1;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATA REFRESH
# -----------------------------
accounts = pd.read_sql("SELECT * FROM accounts", conn)
trades = pd.read_sql("SELECT * FROM trades", conn)
if not trades.empty:
    trades["date"] = pd.to_datetime(trades["date"])

# -----------------------------
# SIDEBAR & ACCOUNT LOGIC
# -----------------------------
st.sidebar.title("⚡ OPERATOR TERMINAL")

if accounts.empty:
    with st.sidebar.expander("INITIALIZE ACCOUNT", expanded=True):
        name = st.text_input("Account Name")
        balance = st.number_input("Starting Balance", value=10000.0)
        max_loss = st.number_input("Max Daily Loss ($)", value=500.0)
        max_trades = st.number_input("Max Daily Trades", value=3)
        min_rr = st.number_input("Min Target RR", value=2.0)
        if st.button("DEPLOY ACCOUNT"):
            c.execute("INSERT INTO accounts (name,starting_balance,max_daily_loss,max_trades,min_rr) VALUES (?,?,?,?,?)",
                      (name, balance, max_loss, max_trades, min_rr))
            conn.commit()
            st.rerun()
    st.stop()
else:
    account = accounts.iloc[-1] # Use the latest account created
    st.sidebar.success(f"ACTIVE: {account['name']}")
    
    # Quick Risk Check
    if not trades.empty:
        today_pnl = trades[trades['date'].dt.date == datetime.now().date()]['pnl'].sum()
        risk_color = "red" if today_pnl <= -account['max_daily_loss'] else "#66FCF1"
        st.sidebar.markdown(f"**Daily P&L:** <span style='color:{risk_color}'>${today_pnl:.2f}</span>", unsafe_allow_html=True)

page = st.sidebar.radio("GO TO", ["Dashboard", "Trade Journal", "Analytics", "Psychology", "Terminal"])

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":
    st.title("OPERATOR DASHBOARD")
    
    if not trades.empty:
        # Equity Calculation
        trades = trades.sort_values("date")
        trades["cumulative"] = account['starting_balance'] + trades["pnl"].cumsum()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Balance", f"${trades['cumulative'].iloc[-1]:,.2f}")
        col2.metric("Total Trades", len(trades))
        
        win_rate = len(trades[trades['pnl'] > 0]) / len(trades) * 100
        col3.metric("Win Rate", f"{win_rate:.1f}%")
        
        pf = abs(trades[trades['pnl'] > 0]['pnl'].sum() / trades[trades['pnl'] < 0]['pnl'].sum()) if len(trades[trades['pnl']<0]) > 0 else 0
        col4.metric("Profit Factor", f"{pf:.2f}")

        # Plotly Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trades["date"], y=trades["cumulative"], 
                                 line=dict(color='#66FCF1', width=3),
                                 fill='tozeroy', name="Equity"))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Awaiting execution data. Log your first trade in the Journal.")

# -----------------------------
# TRADE JOURNAL
# -----------------------------
elif page == "Trade Journal":
    st.title("LOG MISSION")
    
    with st.expander("NEW TRADE ENTRY", expanded=False):
        with st.form("trade_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            date = c1.date_input("Date")
            asset = c2.text_input("Asset (e.g., NQ, BTC)")
            m_type = c3.selectbox("Market", ["Futures", "Forex", "Crypto"])
            
            c4, c5, c6 = st.columns(3)
            entry = c4.number_input("Entry Price", format="%.5f")
            sl = c5.number_input("Stop Loss", format="%.5f")
            exit_p = c6.number_input("Exit Price", format="%.5f")
            
            emo = st.select_slider("Predominant Emotion", ["Revenge", "FOMO", "Anxious", "Calm", "Focused"])
            comment = st.text_area("Trade Notes / Post-Mortem")
            
            submit = st.form_submit_button("LOCK IN TRADE")
            
            if submit:
                # Basic Math
                risk = abs(entry - sl)
                pnl = exit_p - entry # Simple P&L; adjust if using lot sizes/contracts
                rr_achieved = abs(pnl / risk) if risk != 0 else 0
                
                c.execute("""INSERT INTO trades 
                    (account_id, date, asset, market_type, entry, sl, exit, pnl, rr_achieved, emotion, comment) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (int(account['id']), str(date), asset, m_type, entry, sl, exit_p, pnl, rr_achieved, emo, comment))
                conn.commit()
                st.success("Trade Recorded.")
                st.rerun()

    if not trades.empty:
        st.subheader("Recent Missions")
        # Reverse chronological
        st.dataframe(trades.sort_values("date", ascending=False), use_container_width=True)

# -----------------------------
# TERMINAL (RISK SETTINGS)
# -----------------------------
elif page == "Terminal":
    st.title("SYSTEM PARAMETERS")
    st.write(f"**Operator:** {account['name']}")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Risk Ceiling (Daily)", f"${account['max_daily_loss']}")
    with col2:
        st.metric("Minimum RR Threshold", f"{account['min_rr']}R")
    
    if st.button("PURGE DATA (Reset All Trades)"):
        c.execute("DELETE FROM trades")
        conn.commit()
        st.warning("Data wiped.")
        st.rerun()

