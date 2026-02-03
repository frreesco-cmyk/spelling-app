import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- PREMIUM UI ---
st.set_page_config(page_title="OFFICE ELITE", layout="wide")
st.markdown("""
<style>
    .stApp {background: #000; color: #00ff41; font-family: 'Consolas', monospace;}
    .stMetric {background: #0a0a0a; border: 1px solid #00ff41; padding: 15px; border-radius: 5px; box-shadow: 0 0 5px #00ff41;}
    .stButton>button {background: #000; color: #00ff41; border: 1px solid #00ff41; font-weight: bold;}
    .stButton>button:hover {background: #00ff41; color: #000; box-shadow: 0 0 15px #00ff41;}
    .status-active {color: #00ff41; font-weight: bold;}
    .status-banned {color: #ff0000; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- DATABASE ENGINE ---
db = sqlite3.connect('elite_v7.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'ОЖИДАНИЕ ПРИКАЗА', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT DEFAULT 'СИСТЕМА СТАБИЛЬНА')")
db.commit()

# --- RANK LOGIC ---
def get_rank(xp):
    if xp < 300: return "🌑 НОВИЧОК", 0.2
    if xp < 1000: return "⚔️ БОЕЦ", 0.5
    if xp < 3000: return "💎 ЭЛИТА", 0.8
    return "🔥 ЛЕГЕНДА", 1.0

# --- AUTH SYSTEM ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

if not st.session_state.auth:
    st.title("🔒 ACCESS TERMINAL")
    l, p = st.text_input("UNIT ID").strip(), st.text_input("PASSKEY", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("AUTHORIZE"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        res = db.execute("SELECT u, status FROM users WHERE u=? AND p=?", (l, p)).fetchone()
        if res and res[1] == 'active':
            st.session_state.update({"auth":True, "role":"worker", "user":l})
            st.rerun()
        elif res: st.error("ACCESS DENIED: BANNED")
        else: st.error("INVALID DATA")
    if c2.button("REGISTER"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("UNIT REGISTERED")
            except: st.error("ID ALREADY TAKEN")
else:
    if st.sidebar.button("TERMINATE SESSION"):
        st.session_state.auth = False; st.rerun()

    # --- WORKER INTERFACE ---
    if st.session_state.role == "worker":
        st.title(f"USER: {st.session_state.user}")
        news = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info(f"⚡️ SYSTEM NEWS: {news}")
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        rank, progress = get_rank(ud[1])

        c1, c2, c3 = st.columns(3)
        c1.metric("BALANCE", f"{ud[0]} RUB")
        c2.metric("EXPERIENCE", f"{ud[1]} XP")
        c3.metric("RANK", rank)
        st.progress(progress)

        st.divider()
        st.subheader("🛠 WORK PROTOCOL")
        if not st.session_state.shift:
            if st.button("▶️ START SHIFT"):
                st.session_state.shift, st.session_state.st = True, time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.st)
            st.error(f"⌛️ PROCESS ACTIVE: {el} SEC")
            if st.button("🛑 STOP SHIFT"):
                gain = max(5, el // 2)
                db.execute("UPDATE users SET xp=xp+? WHERE u=?", (gain, st.session_state.user))
                db.commit(); st.session_state.shift = False
                st.success(f"PROFIT: +{gain} XP"); time.sleep(1); st.rerun()
            time.sleep(1); st.rerun()

        st.warning(f"🎯
