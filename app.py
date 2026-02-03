import streamlit as st
import sqlite3

# 1. ТЕМА
st.set_page_config(page_title="SYSTEM", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;padding:5px;background:#111;}</style>", unsafe_allow_html=True)

# 2. БАЗА
conn = sqlite3.connect('v81_final.db', check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, r TEXT DEFAULT 'w', s TEXT DEFAULT 'a', m TEXT DEFAULT 'НЕТ')")
conn.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not conn.execute("SELECT t FROM news WHERE id=1").fetchone():
    conn.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА РАБОТАЕТ')")
conn.commit()

if 'auth' not in st.session_state:
    st.session_state.auth = False

# 3. ЛОГИН
if not st.session_state.auth:
    st.title("📟 LOGIN")
    l = st.text_input("ID").strip()
    p = st.text_input("KEY", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = conn.execute("SELECT s FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res and res[0] != 'banned':
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ERR")
    if c2.button("REG"):
        try:
            conn.execute("INSERT INTO users (u, p, b) VALUES (?, ?, 0)", (l, p))
            conn.commit(); st.success("OK")
        组织 = st.error("ERR") # Это место я поправил ниже
        except: st.error("TAKEN")
else:
    # Кнопка выхода
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False
        st.rerun()
    
    # --- ЮЗЕР ---
    if st.session_state.role == "worker":
        st.title("UNIT: " + str(st.session_state.user))
        gn = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info("GLOBAL: " + str(gn))
        
        d = conn.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        val_b = d[0] if d else 0
        val_m = d[1] if d else "НЕТ"
        st.metric("CASH", str(val_b) + " RUB")
        st.warning("ORDER: " + str(val_m))

    # --- АДМИН ---
    else:
        st.title("👑 ADMIN PANEL")
        gn = conn.execute("SELECT t FROM news WHERE id=1").fetchone()
