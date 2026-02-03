import streamlit as st
import sqlite3

# --- ПОДКЛЮЧЕНИЕ ---
def get_connection():
    return sqlite3.connect('v73_final.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание таблиц без длинных строк
cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT 'worker', status TEXT DEFAULT 'active', message TEXT DEFAULT 'НЕТ ПРИКАЗОВ')")
cur.execute("CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)")
if not cur.execute("SELECT * FROM global_cfg").fetchone():
    cur.execute("INSERT INTO global_cfg (id, news) VALUES (1, 'СИСТЕМА ОНЛАЙН')")
conn.commit()

# --- ВИЗУАЛ ---
st.set_page_config(page_title="SYSTEM v73", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #0f0; } .stButton>button { border: 1px solid #0f0; color: #0f0; background: transparent; }</style>", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- ЛОГИКА ВХОДА ---
if not st.session_state['auth']:
    st.title("👁️ TERMINAL LOGIN")
    u_in = st.text_input("ID").strip()
    p_in = st.text_input("KEY", type='password').strip()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("UPLINK"):
            if u_in == "admin" and p_in == "admin777":
                st.session_state.update({"auth": True, "user": "admin", "role": "admin"})
                st.rerun()
            else:
                q = "SELECT status FROM users WHERE username=? AND password=?"
                res = cur.execute(q, (u_in, p_in)).fetchone()
                if res and res[0] != 'banned':
                    st.session_state.update({"auth": True, "user": u_in, "role": "worker"})
                    st.rerun()
                else: st.error("DENIED")
    with c2:
        if st.button("NEW USER"):
            try:
                cur.execute("INSERT INTO users(username,password) VALUES (?,?)", (u_in, p_in))
                conn.commit()
                st.success("CREATED")
            except: st.error("TAKEN")

# --- ПАНЕЛЬ УПРАВЛЕНИЯ ---
else:
    role = st.session_state['role']
    user = st.session_state['user']
    
    if st.sidebar.button("LOGOUT"):
        st.session_state['auth'] = False
        st.rerun
