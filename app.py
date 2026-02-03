import streamlit as st
import sqlite3

# 1. СТИЛЬ
st.set_page_config(page_title="SYSTEM", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# 2. БАЗА
db = sqlite3.connect('final_v90.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, m TEXT DEFAULT 'НЕТ', t TEXT DEFAULT '00:00')")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, n TEXT)")
if not db.execute("SELECT n FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, n) VALUES (1, 'ONLINE')")
db.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# 3. ВХОД
if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l, p = st.text_input("ID").strip(), st.text_input("KEY", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ERR")
    if c2.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("TAKEN")

# 4. ИНТЕРФЕЙС
else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        st.title("👤 ЮНИТ: " + str(st.session_state.user))
        gn = db.execute("SELECT n FROM config WHERE id=1").fetchone()[0]
        st.info("📢 ОБЩЕЕ: " + str(gn))
        ud = db.execute("SELECT b, m, t FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        c1, c2 = st.columns(2)
        c1.metric("БАЛАНС", str(ud[0]) + " RUB")
        c2.metric("ТАЙМЕР", str(ud[2]))
        st.warning("📩 ПРИКАЗ: " + str(ud[1]))
    else:
        st.title("👑 АДМИН")
        gn = db.execute("
