import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- PREMIUM STYLING ---
st.set_page_config(page_title="SYNDICATE OS", layout="wide")
st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    .stMetric {background: #111; border-left: 5px solid #00ff41; padding: 20px;}
    .stButton>button {background: #000; color: #00ff41; border: 1px solid #00ff41; border-radius: 0px; height: 50px; font-weight: bold;}
    .stButton>button:hover {background: #00ff41; color: #000; box-shadow: 0 0 20px #00ff41;}
    .stTextInput>div>div>input {background-color: #111; color: #00ff41; border: 1px solid #333;}
</style>
""", unsafe_allow_html=True)

# --- DATABASE CORE ---
db = sqlite3.connect('syndicate_v1.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'WAITING', s TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT DEFAULT 'SYSTEM ONLINE')")
db.commit()

# --- RANK SYSTEM ---
def get_rank(xp):
    if xp < 500: return "RECRUIT", 0.2
    if xp < 2500: return "OPERATIVE", 0.5
    if xp < 7000: return "ELITE", 0.8
    return "LEGEND", 1.0

# --- AUTH LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

if not st.session_state.auth:
    st.title("📟 SYNDICATE NETWORK ACCESS")
    l = st.text_input("ID").strip()
    p = st.text_input("PASSWORD", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOGIN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        res = db.execute("SELECT u, s FROM users WHERE u=? AND p=?", (l, p)).fetchone()
        if res and res[1] == 'active':
            st.session_state.update({"auth":True, "role":"worker", "user":l})
            st.rerun()
        elif res: st.error("ACCESS DENIED: BANNED")
        else: st.error("INVALID DATA")
    if c2.button("JOIN TEAM"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("REGISTERED")
            except: st.error("ID TAKEN")
else:
    # --- WORK
