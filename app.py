import streamlit as st
import sqlite3
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="CONTROL v67", page_icon="🚫", layout="wide")

def get_connection():
    return sqlite3.connect('v67_final.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание таблиц
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                last_act TEXT, message TEXT DEFAULT "Указаний нет")''')

cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, action TEXT, date TEXT)')

cur.execute('CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)')
if not cur.execute('SELECT * FROM global_cfg').fetchone():
    cur.execute('INSERT INTO global_cfg (id, news) VALUES (1, "СИСТЕМА АКТИВНА")')
conn.commit()

# --- СТИЛЬ ---
st.markdown("""<style>
    .stApp { background: #000; color: #fff; }
    .stButton>button { border-radius: 0; border: 1px solid #fff; color: #fff; background: transparent; width: 100%; }
    .stButton>button:hover { background: #fff; color: #000; }
    .log-text { font-family: monospace; font-size: 12px; color: #0f0; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- ВХОД В СИСТЕМУ ---
if not st.session_state.auth:
    st.title("🚫 ТЕРМИНАЛ КОНТРОЛЯ v67")
    u_input = st.text_input("ЛОГИН").strip()
    p_input = st.text_input("ПАРОЛЬ", type='password').strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ВХОД"):
            if u_input == "admin" and p_input == "admin777":
                st.session_state.auth = True
                st.session_state.user = "admin"
                st.session_state.role = "admin"
                st.rerun()
            else:
                q = "SELECT status FROM users WHERE username=? AND password=?"
                res = cur.execute(q, (u_input, p_input)).fetchone()
                if res and res[0] != "banned":
                    st.session_state.auth = True
                    st.session_state.user = u_input
                    st.session_state.role = "worker
