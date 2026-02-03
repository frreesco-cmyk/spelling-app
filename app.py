import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- ИНИЦИАЛИЗАЦИЯ (ФИКС ОШИБКИ) ---
db = sqlite3.connect('syndicate_v112.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'WAIT', s TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT)")

# Проверка: если новости нет, создаем её принудительно
check_news = db.execute("SELECT news FROM config WHERE id=1").fetchone()
if not check_news:
    db.execute("INSERT INTO config (id, news) VALUES (1, 'SYSTEM ONLINE')")
    db.commit()

# --- ТЕМА ---
st.set_page_config(page_title="SYNDICATE PANEL", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:15px;}</style>", unsafe_allow_html=True)

# --- ЛОГИКА РАНГОВ ---
def get_rank(xp):
    if xp < 500: return "RECRUIT", 0.2
    if xp < 2000: return "OPERATIVE", 0.5
    return "LEGEND", 1.0

if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

# --- АВТОРИЗАЦИЯ ---
if not st.session_state.auth:
    st.title("📟 ACCESS TERMINAL")
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
        else: st.error("DENIED")
    if c2.button("JOIN"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("TAKEN")
else:
    # --- ВОРКЕР ---
    if st.session_state.role == "worker":
        st.title("UNIT: " + str(st.session_state.user))
        
        # Безопасное получение новости
        news_data = db.execute("SELECT news FROM config WHERE id=1").fetchone()
        news_text = news_data[0] if news_data else "NO DATA"
        st.info("DISPATCH: " + str(news_text))
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        rn, pr = get_rank(ud[1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CASH", str(ud[0]))
        c2.metric("XP", str(ud[1]))
        c3.metric("RANK", rn)
        st.progress(pr)

        st.divider()
        if not st.session_state.shift:
            if st.button("▶️ START SHIFT"):
                st.session_state.shift, st.session_state.st = True, time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.st)
            st.error("PROCESS: " + str(el) + "s")
            if st.button("🛑 STOP"):
                gain = max(5, el // 4)
                db.execute("UPDATE users SET xp=xp+? WHERE u=?", (gain, st.session_state.user))
                db.commit(); st.session_state.shift = False
                st.rerun()
            time.
