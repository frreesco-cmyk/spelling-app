import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- СТИЛЬ "HACKER DARK" ---
st.set_page_config(page_title="COMMAND CENTER", layout="wide")
st.markdown("""
<style>
    .stApp {background-color: #000; color: #0f0;}
    .stMetric {background-color: #111; border: 1px solid #0f0; padding: 15px; border-radius: 10px;}
    .stButton>button {border: 1px solid #0f0; background: transparent; color: #0f0; transition: 0.3s;}
    .stButton>button:hover {background: #0f0; color: #000;}
</style>
""", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ ---
db = sqlite3.connect('omega_system.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, m TEXT DEFAULT 'НЕТ ЗАДАЧ', t TEXT DEFAULT '00:00:00')")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT)")
if not db.execute("SELECT news FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, news) VALUES (1, 'СИСТЕМА ГОТОВА К РАБОТЕ')")
db.commit()

# --- ЛОГИКА ВХОДА ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("📟 ВХОД В ТЕРМИНАЛ")
    l = st.text_input("ID ЮНИТА").strip()
    p = st.text_input("КЛЮЧ ДОСТУПА", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth": True, "user": "admin", "role": "admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                st.session_state.update({"auth": True, "user": l, "role": "worker"})
                st.rerun()
            else: st.error("ДОСТУП ЗАБЛОКИРОВАН")
    if c2.button("REGISTER"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("ЮНИТ СОЗДАН")
            except: st.error("ID ЗАНЯТ")

# --- ИНТЕРФЕЙС ---
else:
    if st.sidebar.button("ВЫЙТИ ИЗ СИСТЕМЫ"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        # --- ПАНЕЛЬ ВОРКЕРА ---
        st.title(f"👤 UNIT: {st.session_state.user}")
        gn = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info(f"📢 ГЛОБАЛЬНО: {gn}")
        
        ud = db.execute("SELECT b, m, t FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("ТЕКУЩИЙ БАЛАНС", f"{ud[0]} RUB")
        with col2:
            st.metric("ВР
