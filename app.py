# =====================================
# ELITE OPERATOR LAB – FULL STREAMLIT FILE
# Neon UI + Right Slide Panel + Trade Journal Module
# =====================================

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
st.set_page_config(page_title="ELITE OPERATOR LAB", layout="wide")

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("elite_lab.db", check_same_thread=False)
c = conn.cursor()

# Tables
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

c.execute("""CREATE TABLE IF NOT EXISTS breaches (
    id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER,
    date TEXT, breach_type TEXT, description TEXT)""")

conn.commit()

# -----------------------------
# CSS – Neon Style
# -----------------------------
st.markdown("""
<style>
body {background-color:#0B0C10; color:white;}
div[data-testid="stMetric"] {background-color:#111217; padding:20px; border-radius:15px; border:1px solid #7B2FF7;}
.stButton>button {background-color:#7B2FF7; color:white; border-radius:10px;}
.stSidebar {background-color:#111217;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR – Right Slide Panel
# -----------------------------
st.sidebar.title("ELITE OPERATOR LAB")
page = st.sidebar.radio("Navigation", ["Dashboard","Trades","Calendar","Analytics","Psychology","Breach Log","Terminal"])

# -----------------------------
# ACCOUNT SETUP (DYNAMIC)
# -----------------------------
accounts = pd.read_sql("SELECT * FROM accounts", conn)
if accounts.empty:
    st.sidebar.subheader("Create Account")
    name = st.sidebar.text_input("Account Name")
    balance = st.sidebar.number_input("Starting Balance", value=10000.0, step=100.0)
    max_loss = st.sidebar.number_input("Max Daily Loss", value=50.0, step=1.0)
    max_trades = st.sidebar.number_input("Max Trades Per Day", value=1, step=1)
    min_rr = st.sidebar.number_input("Minimum RR", value=2.0, step=0.1)
    if st.sidebar.button("Create Account"):
        if name.strip()=="":
            st.sidebar.error("Account Name cannot be empty!")
        else:
            c.execute("INSERT INTO accounts (name,starting_balance,max_daily_loss,max_trades,min_rr) VALUES (?,?,?,?,?)",
                      (name,balance,max_loss,max_trades,min_rr))
            conn.commit()
            st.experimental_rerun()
else:
    account = accounts.iloc[0]

# -----------------------------
# LOAD TRADES
# -----------------------------
trades = pd.read_sql("SELECT * FROM trades", conn)
if not trades.empty:
    trades["date"] = pd.to_datetime(trades["date"])

# -----------------------------
# SCORING
# -----------------------------
def execution_score(trade, account):
    score = 100
    if trade["rr_achieved"] < account["min_rr"]:
        score -= 20
    if trade["rule_break"]==1:
        score -= 25
    if trade["emotion"] in ["Revenge","FOMO"]:
        score -= 15
    if score<0:
        score=0
    if score>=90:
        verdict="ELITE"
    elif score>=75:
        verdict="PROFESSIONAL"
    elif score>=60:
        verdict="UNSTABLE"
    else:
        verdict="LIABILITY"
    return score, verdict

# -----------------------------
# ANALYTICS
# -----------------------------
def equity_curve(trades):
    trades["cumulative"] = trades["pnl"].cumsum()
    trades["drawdown"] = trades["cumulative"] - trades["cumulative"].cummax()
    return trades

def win_rate(trades):
    if len(trades)==0: return 0
    return round(len(trades[trades["pnl"]>0])/len(trades)*100,2)

def profit_factor(trades):
    wins = trades[trades["pnl"]>0]["pnl"].sum()
    losses = trades[trades["pnl"]<0]["pnl"].sum()
    if losses==0: return 0
    return round(abs(wins/losses),2)

def asset_breakdown(trades):
    return trades.groupby("asset")["pnl"].agg(["count","sum"])

# -----------------------------
# PAGES
# -----------------------------
# DASHBOARD
if page=="Dashboard":
    st.title("CONTROL CENTER")
    if not trades.empty:
        trades = equity_curve(trades)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trades["date"], y=trades["cumulative"], mode="lines", name="Equity"))
        fig.add_trace(go.Scatter(x=trades["date"], y=trades["drawdown"], mode="lines", name="Drawdown"))
        st.plotly_chart(fig, use_container_width=True)
        col1,col2,col3 = st.columns(3)
        col1.metric("Net P&L", round(trades["pnl"].sum(),2))
        col2.metric("Win Rate", win_rate(trades))
        col3.metric("Profit Factor", profit_factor(trades))
    else:
        st.info("No trades yet.")

# TRADES PAGE
elif page=="Trades":
    st.title("TRADE JOURNAL")
    with st.form("trade_form"):
        date = st.date_input("Date")
        asset = st.text_input("Asset")
        market_type = st.selectbox("Market Type", ["Futures","Forex","Crypto"])
        session = st.selectbox("Session", ["Asia","London","NY"])
        setup = st.text_input("Setup")
        entry = st.number_input("Entry Price")
        sl = st.number_input("Stop Loss")
        tp = st.number_input("Take Profit")
        exit_price = st.number_input("Exit Price")
        emotion = st.selectbox("Emotion", ["Calm","FOMO","Revenge","Hesitation"])
        rule_break = st.checkbox("Rule Break")
        rating = st.selectbox("Rating", ["A+","A","B","C"])
        comment = st.text_area("Comment")
        screenshot = st.text_input("Screenshot URL / Path")
        submit = st.form_submit_button("Add Trade")
        if submit:
            rr_planned = abs((tp-entry)/(entry-sl)) if entry!=sl else 0
            rr_achieved = abs((exit_price-entry)/(entry-sl)) if entry!=sl else 0
            pnl = exit_price-entry
            c.execute("""INSERT INTO trades
            (account_id,date,asset,market_type,session,setup,entry,sl,tp,exit,pnl,rr_planned,rr_achieved,emotion,rule_break,rating,comment,screenshot)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (account["id"],str(date),asset,market_type,session,setup,
                       entry,sl,tp,exit_price,pnl,rr_planned,rr_achieved,emotion,int(rule_break),
                       rating,comment,screenshot))
            conn.commit()
            st.experimental_rerun()
    if not trades.empty:
        # Color-coded display
        def color_row(row):
            if row["pnl"]>0: return 'background-color:green;color:white'
            elif row["pnl"]<0: return 'background-color:red;color:white'
            else: return 'background-color:yellow;color:black'
        st.dataframe(trades.style.applymap(color_row, subset=["pnl"]))

# CALENDAR
elif page=="Calendar":
    st.title("Performance Calendar")
    if not trades.empty:
        grouped = trades.groupby(trades["date"].dt.date)["pnl"].sum()
        month = datetime.now().month
        year = datetime.now().year
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day==0: cols[i].write("")
                else:
                    date_obj = datetime(year, month, day).date()
                    pnl = grouped.get(date_obj,0)
                    color = "green" if pnl>0 else "red" if pnl<0 else "yellow"
                    cols[i].markdown(f"""
                        <div style='background-color:{color}; padding:20px; border-radius:10px'>
                        <b>{day}</b><br>{round(pnl,2)}
                        </div>""", unsafe_allow_html=True)
    else:
        st.info("No data for calendar.")

# ANALYTICS
elif page=="Analytics":
    st.title("Scientific Breakdown")
    if not trades.empty:
        st.subheader("Asset Performance")
        st.dataframe(asset_breakdown(trades))

# PSYCHOLOGY
elif page=="Psychology":
    st.title("Psychology Lab")
    if not trades.empty:
        st.dataframe(trades.groupby("emotion")["pnl"].agg(["count","sum"]))
        if "Revenge" in trades["emotion"].values:
            st.warning("Revenge trades detected!")

# BREACH LOG
elif page=="Breach Log":
    st.title("Protocol Breaches")
    breaches = pd.read_sql("SELECT * FROM breaches", conn)
    st.dataframe(breaches)

# TERMINAL
elif page=="Terminal":
    st.title("Risk Control Panel")
    st.write("Max Daily Loss:", account["max_daily_loss"])
    st.write("Max Trades Per Day:", account["max_trades"])
    st.write("Minimum RR:", account["min_rr"])
    if not trades.empty:
        today = datetime.now().date()
        today_trades = trades[pd.to_datetime(trades["date"]).dt.date==today]
        if today_trades["pnl"].sum() < -account["max_daily_loss"]:
            st.error("Daily Risk Cap Violated.")
        if len(today_trades) > account["max_trades"]:
            st.error("Max Trades Exceeded.")
