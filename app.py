import streamlit as st
import sqlite3
from datetime import datetime

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="CONTROL v66", page_icon="👁️", layout="wide")

def get_connection():
    return sqlite3.connect('v66_final.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание таблиц
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                last_act TEXT, message TEXT DEFAULT "Указаний нет")''')
cur.execute('CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)')
if not cur.execute('SELECT * FROM global_cfg').fetchone():
    cur.execute('INSERT INTO global_cfg (id, news) VALUES (1, "Система запущена")')
conn.commit()

# --- СТИЛЬ ---
st.markdown("""<style>
    .stApp { background: #000; color: #fff; }
    .stButton>button { border-radius: 0; border: 1px solid #fff; color: #fff; background: transparent; width: 100%; }
    .stButton>button:hover { background: #fff; color: #000; }
    .global-news { background: #222; padding: 10px; border: 1px dashed #fff; margin-bottom: 20px; text-align: center; }
    .order-box { background: #111; padding: 15px; border-left: 5px solid #ff0000; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("👁️ СИСТЕМА v66")
    u = st.text_input("ЛОГИН").strip()
    p = st.text_input("ПАРОЛЬ", type='password').strip()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("ВХОД"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
                if res and res[0] != "banned":
                    st.session_state.update({"auth":True, "user
