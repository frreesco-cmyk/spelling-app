import streamlit as st
import sqlite3

# --- БАЗА ДАННЫХ ---
def get_connection():
    return sqlite3.connect('v72_final.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT 'worker', status TEXT DEFAULT 'active', message TEXT DEFAULT 'НЕТ ПРИКАЗОВ')")
cur.execute("CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)")
if not cur.execute("SELECT * FROM global_cfg").fetchone():
    cur.execute("INSERT INTO global_cfg (id, news) VALUES (1, 'СИСТЕМА РАБОТАЕТ')")
conn.commit()

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="SYSTEM v72", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #0f0; } .stButton>button { border: 1px solid #0f0; color: #0f0; background: transparent; }</style>", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- ВХОД ---
if not st.session_state['auth']:
    st.title("👁️ ВХОД В СИСТЕМУ")
    u = st.text_input("ЛОГИН").strip()
    p = st.text_input("ПАРОЛЬ", type='password').strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth": True, "user": "admin", "role": "admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
                if res and res[0] != 'banned':
                    st.session_state.update({"auth": True, "user": u, "role": "worker"})
                    st.rerun()
                else: st.error("ОТКАЗАНО")
    with col2:
        if st.button("РЕГИСТРАЦИЯ"):
            try:
                cur.execute("INSERT INTO users(username,password) VALUES (?,?)", (u, p))
                conn.commit()
                st.success("ГОТОВО")
            except: st.error("ЗАНЯТО")

# --- ПОСЛЕ ВХОДА ---
else:
    role = st.session_state['role']
    user = st.session_state['user']
    
    if st.sidebar.button("ВЫХОД"):
        st.session_state['auth'] = False
        st.rerun()

    # --- ИНТЕРФЕЙС ВОРКЕРА ---
    if role == "worker":
        st.title(f"ЮНИТ: {user}")
        
        # Глобальное инфо
        news = cur.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()[0]
        st.info(f"📢 ОБЩЕЕ: {news}")
        
        # Личные данные
        d = cur.execute("SELECT balance, message FROM users WHERE username=?", (user,)).fetchone()
        if d:
            st.metric("БАЛАНС", f"{d[0]} руб")
            st.warning(f"📩 ПРИКАЗ: {d[1]}")

    # --- ИНТЕРФЕЙС АДМИНА ---
    else:
        st.title("👑 ПАНЕЛЬ УПРАВЛЕНИЯ")
        
        # Глобальный приказ
        g_news = cur.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()[0]
        new_g = st.text_input("ОБНОВИТЬ ОБЩЕЕ ОБЪЯВЛЕНИЕ", value=g_news)
        if st.button("ОБНОВИТЬ ДЛЯ ВСЕХ"):
            cur.execute("UPDATE global_cfg SET news=? WHERE id=1", (new_g,))
            conn.commit()
            st.rerun()

        st.divider()
        
        # Список всех воркеров
        rows = cur.execute("SELECT username,
