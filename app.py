import streamlit as st
import sqlite3
from datetime import datetime

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="SYSTEM v70", layout="wide")

def get_connection():
    return sqlite3.connect('v70_final.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание таблиц
cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT 'worker', status TEXT DEFAULT 'active', last_act TEXT, message TEXT DEFAULT 'Указаний нет')")
cur.execute("CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)")
if not cur.execute("SELECT * FROM global_cfg").fetchone():
    cur.execute("INSERT INTO global_cfg (id, news) VALUES (1, 'СИСТЕМА РАБОТАЕТ')")
conn.commit()

# --- СТИЛЬ ---
st.markdown("<style>.stApp { background: #000; color: #fff; } .stButton>button { border: 1px solid #fff; color: #fff; background: transparent; }</style>", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- ВХОД ---
if not st.session_state['auth']:
    st.title("👁️ ТЕРМИНАЛ v70")
    u_in = st.text_input("ЛОГИН").strip()
    p_in = st.text_input("ПАРОЛЬ", type='password').strip()
    
    if st.button("ВХОД"):
        if u_in == "admin" and p_in == "admin777":
            st.session_state['auth'] = True
            st.session_state['user'] = "admin"
            st.session_state['role'] = "admin"
            st.rerun()
        else:
            res = cur.execute("SELECT status FROM users WHERE username=? AND password=?", (u_in, p_in)).fetchone()
            if res:
                if res[0] != 'banned':
                    st.session_state['auth'] = True
                    st.session_state['user'] = u_in
                    st.session_state['role'] = "worker"
                    st.rerun()
                else:
                    st.error("БАН")
            else:
                st.error("ОШИБКА")
    
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            cur.execute("INSERT INTO users(username,password,last_act) VALUES (?,?,?)", (u_in, p_in, "-"))
            conn.commit()
            st.success("OK")
        except:
            st.error("ЗАНЯТО")
