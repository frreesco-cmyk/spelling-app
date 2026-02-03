import streamlit as st
import sqlite3

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="WORK", layout="wide")
st.markdown("<style>.stApp{background:#111;color:#0f0;}</style>", unsafe_allow_html=True)

# --- БАЗА ---
db = sqlite3.connect('old_school.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, m TEXT DEFAULT 'НЕТ')")
db.commit()

if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- ЛОГИКА ---
if not st.session_state.auth:
    st.title("📟 ВХОД")
    l = st.text_input("ЛОГИН")
    p = st.text_input("ПАРОЛЬ", type="password")
    
    if st.button("ВХОД"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ОШИБКА")
            
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("ОК")
        except: st.error("ЗАНЯТО")

else:
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        # ЭКРАН РАБОТЯГИ
        st.title("👤 ЮЗЕР: " + st.session_state.user)
        data = db.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        st.metric("БАЛАНС", str(data[0]) + " RUB")
        st.info("ПРИКАЗ: " + str(data[1]))
    else:
        # ЭКРАН АДМИНА
        st.title("👑 АДМИНКА")
        rows = db.execute("SELECT u, b, m FROM users").fetchall()
        for u, b, m in rows:
            with st.expander("ЮНИТ: " + u):
                nb = st.number_input("БАЛАНС", value=float(b), key="b"+u)
                nm = st.text_area("ПРИКАЗ", value=m, key="m"+u)
                if st.button("СОХРАНИ
