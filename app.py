import streamlit as st
import sqlite3
from datetime import datetime

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="SYSTEM v68", layout="wide")

def get_connection():
    return sqlite3.connect('v68_final.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание таблиц
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT 'worker', status TEXT DEFAULT 'active', 
                last_act TEXT, message TEXT DEFAULT 'Указаний нет')''')
cur.execute('CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)')
if not cur.execute('SELECT * FROM global_cfg').fetchone():
    cur.execute('INSERT INTO global_cfg (id, news) VALUES (1, "СИСТЕМА РАБОТАЕТ")')
conn.commit()

# --- СТИЛЬ ---
st.markdown("""<style>
    .stApp { background: #000; color: #fff; }
    .stButton>button { border: 1px solid #fff; color: #fff; background: transparent; }
    .stButton>button:hover { background: #fff; color: #000; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- ВХОД ---
if not st.session_state['auth']:
    st.title("👁️ ТЕРМИНАЛ v68")
    u_in = st.text_input("ЛОГИН").strip()
    p_in = st.text_input("ПАРОЛЬ", type='password').strip()
    
    if st.button("АВТОРИЗАЦИЯ"):
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
                    st.error("ВЫ ЗАБАНЕНЫ")
            else:
                st.error("НЕВЕРНЫЕ ДАННЫЕ")
    
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            cur.execute("INSERT INTO users(username,password,last_act) VALUES (?,?,?)", (u_in, p_in, "-"))
            conn.commit()
            st.success("ГОТОВО")
        except:
            st.error("ЛОГИН ЗАНЯТ")

# --- ГЛАВНЫЙ ЭКРАН ---
else:
    u_curr = st.session_state['user']
    r_curr = st.session_state['role']
    
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state['auth'] = False
        st.rerun()

    if r_curr == "worker":
        st.header(f"ЮНИТ: {u_curr}")
        d = cur.execute("SELECT balance, message FROM users WHERE username=?", (u_curr,)).fetchone()
        n = cur.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()[0]
        st.info(f"📢 ОБЩЕЕ: {n}")
        st.metric("БАЛАНС", f"{d[0]} ₽")
        st.warning(f"📩 ПРИКАЗ: {d[1]}")

    else:
        st.title("👑 ПАНЕЛЬ УПРАВЛЕНИЯ")
        
        # Массовые действия
        c1, c2 = st.columns(2)
        if c1.button("🚫 ЗАБАНИТЬ ВСЕХ ВОРКЕРОВ"):
            cur.execute("UPDATE users SET status='banned' WHERE role='worker'")
            conn.commit()
            st.rerun()
        if c2.button("🔓 РАЗБАНИТЬ ВСЕХ ВОРКЕРОВ"):
            cur.execute("UPDATE users SET status='active' WHERE role='worker'")
            conn.commit()
            st.rerun()

        st.divider()
        users = cur.execute("SELECT username, balance, status, message FROM users WHERE role='worker'").fetchall()
        for un, ub, us, um in users:
            with st.expander(f"👤 {un
