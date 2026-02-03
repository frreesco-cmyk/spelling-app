import streamlit as st
import sqlite3

# 1. ТЕМА
st.set_page_config(page_title="GOD_MODE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;padding:5px;background:#111;}</style>", unsafe_allow_html=True)

# 2. БАЗА
conn = sqlite3.connect('v82_final.db', check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, r TEXT DEFAULT 'w', s TEXT DEFAULT 'a', m TEXT DEFAULT 'НЕТ')")
conn.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not conn.execute("SELECT t FROM news WHERE id=1").fetchone():
    conn.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА ЗАПУЩЕНА')")
conn.commit()

if 'auth' not in st.session_state:
    st.session_state.auth = False

# 3. ЛОГИН
if not st.session_state.auth:
    st.title("📟 ВХОД В ТЕРМИНАЛ")
    l = st.text_input("ЛОГИН (ID)").strip()
    p = st.text_input("ПАРОЛЬ (KEY)", type="password").strip()
    c1, c2 = st.columns(2)
    
    if c1.button("ВОЙТИ"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = conn.execute("SELECT s FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res and res[0] != 'banned':
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ОШИБКА ДОСТУПА")
            
    if c2.button("РЕГИСТРАЦИЯ"):
        if l and p:
            try:
                conn.execute("INSERT INTO users (u, p, b) VALUES (?, ?, 0)", (l, p))
                conn.commit()
                st.success("ЮНИТ СОЗДАН")
            except:
                st.error("ЛОГИН ЗАНЯТ")

# 4. ИНТЕРФЕЙС
else:
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False
        st.rerun()
    
    # --- ВОРКЕР ---
    if st.session_state.role == "worker":
        st.title("ЮНИТ: " + str(st.session_state.user))
        gn = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info("ГЛОБАЛЬНО: " + str(gn))
        
        d = conn.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        val_b = d[0] if d else 0
        val_m = d[1] if d else "НЕТ"
        st.metric("БАЛАНС", str(val_b) + " RUB")
        st.warning("ПРИКАЗ: " + str
