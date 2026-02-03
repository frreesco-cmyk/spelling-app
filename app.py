import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="PRO PANEL", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# --- DATABASE ---
db = sqlite3.connect('pro_v8.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'WAIT', s TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT DEFAULT 'ONLINE')")
db.commit()

# --- LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

if not st.session_state.auth:
    st.title("LOGIN TERMINAL")
    l = st.text_input("ID").strip()
    p = st.text_input("KEY", type="password").strip()
    col1, col2 = st.columns(2)
    if col1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        res = db.execute("SELECT u, s FROM users WHERE u=? AND p=?", (l, p)).fetchone()
        if res and res[1] == 'active':
            st.session_state.update({"auth":True, "role":"worker", "user":l})
            st.rerun()
        elif res: st.error("BANNED")
        else: st.error("ERROR")
    if col2.button("REGISTER"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("SUCCESS")
            except: st.error("TAKEN")
else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()

    # --- WORKER ---
    if st.session_state.role == "worker":
        st.title("UNIT: " + str(st.session_state.user))
        news = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info("NEWS: " + str(news))
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        c1, c2 = st.columns(
