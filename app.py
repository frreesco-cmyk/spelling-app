import streamlit as st
import sqlite3
import time
from datetime import datetime

# 1. ТЕМА И БАЗА
st.set_page_config(page_title="OFFICE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:15px;}</style>", unsafe_allow_html=True)

db = sqlite3.connect('core_v106.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'НЕТ', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT DEFAULT 'ONLINE')")
db.commit()

# 2. РАНГИ
def get_rank(xp):
    if xp < 500: return "РЕКРУТ", 0.2
    if xp < 2000: return "БОЕЦ", 0.5
    return "ЭЛИТА", 0.9

# 3. СЕССИЯ
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

# 4. ВХОД
if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l, p = st.text_input("ID").strip(), st.text_input("KEY", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        res = db.execute("SELECT u, status FROM users WHERE u=? AND p=?", (l, p)).fetchone()
        if res and res[1] == 'active':
            st.session_state.update({"auth":True, "role":"worker", "user":l})
            st.rerun()
        elif res: st.error("BAN")
        else: st.error("ERR")
    if c2.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("TAKEN")

# 5. ИНТЕРФЕЙС
else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        st.title("👤 UNIT: " + str(st.session_state.user))
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        rn, pr = get_rank(ud[1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CASH", str(ud[0]))
        c2.metric("XP", str(ud[1]))
        c3.metric("RANK", rn)
        st.progress(pr)

        if not st.session_state.shift:
            if st.button("▶️ START"):
                st.session_state.shift, st.session_state.st = True, time.time()
                st.rerun()
        else:
            el = int(time.time() -
