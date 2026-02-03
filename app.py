import streamlit as st
import sqlite3

# 1. НАСТРОЙКИ
st.set_page_config(page_title="GOD_MODE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} input{background:#111!important;color:#0f0!important;}</style>", unsafe_allow_html=True)

# 2. БАЗА
conn = sqlite3.connect('v78_data.db', check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, r TEXT DEFAULT 'w', s TEXT DEFAULT 'a', m TEXT DEFAULT 'НЕТ')")
conn.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not conn.execute("SELECT t FROM news WHERE id=1").fetchone():
    conn.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА АКТИВНА')")
conn.commit()

# 3. АВТОРИЗАЦИЯ
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("📟 LOGIN")
    l, p = st.text_input("ID"), st.text_input("KEY", type="password")
    c1, c2 = st.columns(2)
    if c1.button("LOG"):
        res = conn.execute("SELECT s, r FROM users WHERE u=? AND p=?", (l, p)).fetchone()
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        elif res and res[0] != 'banned':
            st.session_state.update({"auth":True, "user":l, "role":"worker"})
            st.rerun()
        else: st.error("ERR")
    if c2.button("REG"):
        try:
            conn.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            conn.commit(); st.success("OK")
        except: st.error("ERR")

# 4. КОНТРОЛЬ
else:
    role, user = st.session_state.role, st.session_state.user
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False
        st.rerun()

    if role == "worker":
        st.title(f"UNIT: {user}")
        n = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info(f"📢 {n}")
        d = conn.execute("SELECT b, m FROM users WHERE u=?", (user,)).fetchone()
