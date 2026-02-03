import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="SYSTEM CORE v101", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ ---
db = sqlite3.connect('system_final_v101.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, r TEXT DEFAULT 'РЕКРУТ', m TEXT DEFAULT 'НЕТ', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT)")
if not db.execute("SELECT news FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, news) VALUES (1, 'СИСТЕМА РАБОТАЕТ')")
db.commit()

# --- ФУНКЦИИ ---
def add_log(text):
    now = datetime.now().strftime("%H:%M:%S")
    db.execute("INSERT INTO logs (msg, dt) VALUES (?, ?)", (text, now))
    db.commit()

def get_rank(xp):
    if xp < 100: return "РЕКРУТ", 0.1
    if xp < 500: return "БОЕЦ", 0.4
    if xp < 1500: return "ЭЛИТА", 0.7
    return "ЛЕГЕНДА", 1.0

# --- СИСТЕМА ВХОДА ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift_active' not in st.session_state: st.session_state.shift_active = False
if 'start_time' not in st.session_state: st.session_state.start_time = None

if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l = st.text_input("ID").strip()
    p = st.text_input("KEY", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u, status FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                if res[1] == 'banned': st.error("БАН")
                else:
                    st.session_state.update({"auth":True, "user":l, "role":"worker"})
                    st.rerun()
            else: st.error("ОТКАЗАНО")
    if c2.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("ЗАНЯТО")

else:
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        # --- ИНТЕРФЕЙС ВОРКЕРА ---
        st.title(f"🛠 ЮНИТ: {st.session_state.user}")
        
        # Глобальная новость
        gn = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info(f"📢 ПРИКАЗ:
