import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="SPELLING SYSTEM", layout="wide")

# Подключение к БД
def get_db():
    conn = sqlite3.connect('team_v2.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, xp INTEGER DEFAULT 0, role TEXT DEFAULT "worker")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, xp_gain INTEGER)')
conn.commit()

# --- СТИЛИЗАЦИЯ ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1a1c24; border-radius: 5px; color: #00f2ff; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border-left: 5px solid #00f2ff; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = "worker"

# --- АВТОРИЗАЦИЯ ---
if st.session_state.user is None:
    st.title("⚡ ВХОД В СИСТЕМУ")
    tab1, tab2 = st.tabs(["ВХОД", "РЕГИСТРАЦИЯ"])
    
    with tab1:
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ"):
            res = cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res:
                st.session_state.user = u
                st.session_state.role = res[0]
                st.rerun()
            elif u == "admin" and p == "admin777": # Технический вход админа
                st.session_state.user = "GLOBAL_ADMIN"
                st.session_state.role = "admin"
                st.rerun()
            else: st.error("Неверные данные")

    with tab2:
        nu = st.text_input("Новый логин")
        np = st.text_input("Новый пароль", type="password")
        if st.button("ЗАРЕГИСТРИРОВАТЬСЯ"):
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (nu, np))
                conn.commit()
                st.success("Аккаунт создан!")
            except: st.error("Ник занят")

# --- РАБОЧАЯ ЗОНА ---
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.info(f"Доступ: {st.session_state.role.upper()}")
    
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.user = None
        st.rerun()

    # --- ПАНЕЛЬ АДМИНА ---
    if st.session_state.role == "admin":
        st.title("👑 ADMIN CONTROL PANEL")
        
        t1, t2, t3 = st.tabs(["📊 СТАТИСТИКА КОМАНДЫ", "👥 УПРАВЛЕНИЕ", "📜 ВСЕ ЛОГИ"])
        
        with t1:
            all_users = pd.read_sql_query("SELECT username, xp FROM users WHERE role='worker'", conn)
            st.subheader("Общий профит команды")
            st.bar_chart(all_users.set_index('username'))
            
            col1, col2 = st.columns(2)
            col1.metric("Всего воркеров", len(all_users))
            col2.metric("Общий XP команды", all_users['xp'].sum())

        with t2:
            st.subheader("Редактирование воркеров")
            target_user = st.selectbox("Выбери юзера", all_users['username'])
            new_xp = st.number_input("Изменить XP (можно в минус)", value=0)
            if st.button("ПРИМЕНИТЬ"):
                cursor.execute("UPDATE users SET xp = xp + ? WHERE username = ?", (new_xp, target_user))
                conn.commit()
                st.success(f"XP юзера {target_user} обновлен")
                st.rerun()

        with t3:
            all_logs = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn)
            st.dataframe(all_logs, use_container_width=True)

    # --- ПАНЕЛЬ ВОРКЕРА ---
    else:
        st.title("🚀 WORKER DASHBOARD")
        
        w1, w2 = st.tabs(["💻 РАБОТА", "🏆 ТОП"])
        
        with w1:
            user_xp = cursor.execute("SELECT xp FROM users WHERE username=?", (st.session_state.user,)).fetchone()[0]
            st.metric("ТВОЙ ОПЫТ (XP)", user_xp)
            
            if 'work' not in st.session_state: st.session_state.work = False
            
            if not st.session_state.work:
                if st.button("▶ НАЧАТЬ СМЕНУ"):
                    st.session_state.start = datetime.now()
                    st.session_state.work = True
                    st.rerun()
            else:
                dur = datetime.now() - st.session_state.start
                st.warning(f"Смена идет: {str(dur).split('.')[0]}")
                if st.button("⏹ ЗАКОНЧИТЬ"):
                    mins = max(1, int(dur.total_seconds() / 60))
                    gain = mins * 5 # Админ может настроить множитель
                    dt = datetime.now().strftime("%d.%m %H:%M")
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?)", (st.session_state.user, str(dur).split('.')[0], dt, gain))
                    cursor.execute("UPDATE users SET xp = xp + ? WHERE username=?", (gain, st.session_state.user))
                    conn.commit()
                    st.session_state.work = False
                    st.success(f"Заработано {gain} XP!")
                    st.balloons()

        with w2:
            top = pd.read_sql_query("SELECT username, xp FROM users WHERE role='worker' ORDER BY xp DESC", conn)
            st.table(top)
