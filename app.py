import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# --- ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ---
st.set_page_config(page_title="SPELLING TOTAL CONTROL", layout="wide")

def get_db():
    conn = sqlite3.connect('team_final_v4.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()
# Создаем таблицы с балансом в деньгах
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

# --- ДИЗАЙН ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #00ffcc; }
    .stButton>button { background: #00ffcc; color: black; font-weight: bold; border-radius: 5px; border: none; }
    .stat-box { background: #111; padding: 20px; border: 1px solid #00ffcc; border-radius: 10px; text-align: center; }
    h1, h2, h3 { text-shadow: 0 0 10px #00ffcc; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user = None

# --- ЛОГИКА ВХОДА ---
if st.session_state.user is None:
    st.title("⚡ СИСТЕМА УЧЕТА SPELLING")
    tab_in, tab_reg = st.tabs(["ВХОД", "РЕГИСТРАЦИЯ"])
    
    with tab_in:
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ"):
            res = cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res:
                st.session_state.user, st.session_state.role = u, res[0]
                st.rerun()
            elif u == "admin" and p == "admin777":
                st.session_state.user, st.session_state.role = "ГЛАВНЫЙ", "admin"
                st.rerun()
            else: st.error("Ошибка!")
    
    with tab_reg:
        nu = st.text_input("Новый ник")
        np = st.text_input("Новый пароль", type="password")
        if st.button("СОЗДАТЬ"):
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (nu, np))
                conn.commit()
                st.success("Успех! Входи.")
            except: st.error("Ник занят")

# --- РАБОЧАЯ ПАНЕЛЬ ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👤 {user}")
    st.sidebar.write(f"Доступ: {role.upper()}")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.user = None
        st.rerun()

    # --- ОБЩИЙ БЛОК: ТАЙМЕР ВОРКА (ДЛЯ ВСЕХ) ---
    st.markdown("### ⏳ ТАЙМЕР СМЕНЫ")
    col_t1, col_t2 = st.columns([1, 2])
    
    if 'active' not in st.session_state: st.session_state.active = False
    
    with col_t1:
        if not st.session_state.active:
            if st.button("▶ НАЧАТЬ РАБОТУ"):
                st.session_state.start_t = datetime.now()
                st.session_state.active = True
                st.rerun()
        else:
            if st.button("⏹ ЗАКОНЧИТЬ И ПОЛУЧИТЬ КЭШ"):
                dur = datetime.now() - st.session_state.start_t
                mins = max(1, int(dur.total_seconds() / 60))
                
                # НАСТРОЙКА ОПЛАТЫ: например, 50 рублей за минуту
                money = mins * 0.01 
                
                dt = datetime.now().strftime("%d.%m %H:%M")
                cursor.execute("INSERT INTO logs VALUES (?,?,?,?)", (user, str(dur).split('.')[0], dt, money))
                cursor.execute("UPDATE users SET balance = balance + ? WHERE username=?", (money, user))
                conn.commit()
                st.session_state.active = False
                st.balloons()
                st.rerun()
                
    with col_t2:
        if st.session_state.active:
            elapsed = datetime.now() - st.session_state.start_t
            st.markdown(f"<h1 style='color: #ff4b4b;'>ВОРКАЕМ: {str(elapsed).split('.')[0]}</h1>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        else:
            st.write("Таймер ждет запуска...")

    st.write("---")

    # --- ПАНЕЛЬ АДМИНА ---
    if role == "admin":
        st.title("👑 АДМИН-ПАНЕЛЬ")
        adm_tab1, adm_tab2 = st.tabs(["📊 Финансы Команды", "🔧 Управление"])
        
        with adm_tab1:
            all_u = pd.read_sql_query("SELECT username, balance FROM users", conn)
            st.subheader("Балансы всех сотрудников")
            st.table(all_u)
            st.subheader("История всех выплат")
            all_l = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn)
            st.dataframe(all_l, use_container_width=True)
            
        with adm_tab2:
            st.subheader("Корректировка баланса")
            t_user = st.selectbox("Выбери юзера", all_u['username'])
            t_money = st.number_input("Добавить/Списать (руб)", value=0)
            if st.button("ИЗМЕНИТЬ"):
                cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (t_money, t_user))
                conn.commit()
                st.success("Баланс обновлен")
                st.rerun()

    # --- ПАНЕЛЬ ВОРКЕРА ---
    else:
        st.title("🚀 КАБИНЕТ ВОРКЕРА")
        u_bal = cursor.execute("SELECT balance FROM users WHERE username=?", (user,)).fetchone()[0]
        
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='stat-box'><h3>💰 ТВОЙ БАЛАНС</h3><h1 style='color:#00ffcc'>{u_bal} руб.</h1></div>", unsafe_allow_html=True)
        
        with st.expander("📜 Мои последние выплаты"):
            my_l = pd.read_sql_query(f"SELECT date, duration, money_gain FROM logs WHERE user='{user}'", conn)
            st.table(my_l)

