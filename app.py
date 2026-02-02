import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="SPELLING TOTAL CONTROL v5", layout="wide")

def get_db():
    conn = sqlite3.connect('team_ultimate_v5.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()

# Создаем таблицы (добавлен статус пользователя)
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

# --- СТИЛЬ ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ffcc; }
    .stButton>button { background: #00ffcc; color: black; font-weight: bold; border-radius: 5px; width: 100%; }
    .status-active { color: #00ff00; font-weight: bold; }
    .status-banned { color: #ff0000; font-weight: bold; }
    .status-strike { color: #ffff00; font-weight: bold; }
    .metric-card { background: #111; padding: 15px; border: 1px solid #333; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user = None

# --- АВТОРИЗАЦИЯ ---
if st.session_state.user is None:
    st.title("⚡ SPELLING SECURITY SYSTEM")
    t_in, t_reg = st.tabs(["ВХОД", "РЕГИСТРАЦИЯ"])
    
    with t_in:
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("LOG IN"):
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res:
                if res[1] == "banned":
                    st.error("❌ ВАШ АККАУНТ ЗАБЛОКИРОВАН АДМИНИСТРАЦИЕЙ")
                else:
                    st.session_state.user, st.session_state.role, st.session_state.status = u, res[0], res[1]
                    st.rerun()
            elif u == "admin" and p == "admin777":
                st.session_state.user, st.session_state.role, st.session_state.status = "CHIEF_ADMIN", "admin", "active"
                st.rerun()
            else: st.error("Ошибка доступа")
    
    with t_reg:
        nu = st.text_input("Новый воркер")
        np = st.text_input("Пароль")
        if st.button("ЗАРЕГИСТРИРОВАТЬ"):
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (nu, np))
                conn.commit()
                st.success("Аккаунт создан!")
            except: st.error("Ник занят")

# --- ГЛАВНАЯ ПАНЕЛЬ ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # Проверка статуса в реальном времени
    current_status = cursor.execute("SELECT status FROM users WHERE username=?", (user,)).fetchone()
    status = current_status[0] if current_status else "active"

    st.sidebar.title(f"👾 {user}")
    st.sidebar.write(f"Доступ: {role.upper()}")
    if st.sidebar.button("ВЫХОД"):
        st.session_state.user = None
        st.rerun()

    # --- ОБЩИЙ ТАЙМЕР (ДЛЯ ВСЕХ, КРОМЕ ЗАБАНЕННЫХ) ---
    st.markdown("### ⏳ РАБОЧАЯ СМЕНА")
    
    if status == "strike":
        st.error("⚠️ ВАМ ВЫДАН ВРЕМЕННЫЙ БЛОК. ВОРК НЕДОСТУПЕН.")
    else:
        c1, c2 = st.columns([1, 2])
        if 'active' not in st.session_state: st.session_state.active = False
        
        with c1:
            if not st.session_state.active:
                if st.button("▶ НАЧАТЬ ВОРК"):
                    st.session_state.start_t = datetime.now()
                    st.session_state.active = True
                    st.rerun()
            else:
                if st.button("⏹ ЗАКОНЧИТЬ И СОХРАНИТЬ"):
                    dur = datetime.now() - st.session_state.start_t
                    mins = max(1, int(dur.total_seconds() / 60))
                    money = mins * 100 # Ставка 100 за минуту (настрой как хочешь)
                    dt = datetime.now().strftime("%d.%m %H:%M")
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?)", (user, str(dur).split('.')[0], dt, money))
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE username=?", (money, user))
                    conn.commit()
                    st.session_state.active = False
                    st.balloons()
                    st.rerun()
        
        with c2:
            if st.session_state.active:
                elapsed = datetime.now() - st.session_state.start_t
                st.markdown(f"<h1 style='color: #ff4b4b;'>В ПРОЦЕССЕ: {str(elapsed).split('.')[0]}</h1>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()

    st.write("---")

    # --- ПАНЕЛЬ АДМИНА ---
    if role == "admin":
        st.title("👑 АДМИНИСТРИРОВАНИЕ")
        tab_users, tab_money, tab_logs = st.tabs(["👥 ВОРКЕРЫ И БАНЫ", "💰 ФИНАНСЫ", "📜 ВСЕ ЛОГИ"])
        
        with tab_users:
            st.subheader("Управление составом")
            all_users = pd.read_sql_query("SELECT username, status, balance FROM users", conn)
            
            for index, row in all_users.iterrows():
                col1, col2, col3 = st.columns([2, 2, 3])
                with col1:
                    st.write(f"**{row['username']}**")
                with col2:
                    st.write(f"Статус: {row['status']}")
                with col3:
                    new_st = st.selectbox("Сменить статус", ["active", "strike", "banned"], key=f"st_{row['username']}", index=["active", "strike", "banned"].index(row['status']))
                    if st.button("Применить", key=f"btn_{row['username']}"):
                        cursor.execute("UPDATE users SET status=? WHERE username=?", (new_st, row['username']))
                        conn.commit()
                        st.success(f"Обновлено!")
                        st.rerun()
                st.write("---")

        with tab_money:
            st.subheader("Изменение баланса")
            target = st.selectbox("Воркер", all_users['username'])
            amt = st.number_input("Сумма (можно минус)", value=0)
            if st.button("ОБНОВИТЬ КЭШ"):
                cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amt, target))
                conn.commit()
                st.rerun()

        with tab_logs:
            st.dataframe(pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn), use_container_width=True)

    # --- ПАНЕЛЬ ВОРКЕРА ---
    else:
        st.title("🚀 ТВОЯ СТАТИСТИКА")
        u_bal = cursor.execute("SELECT balance FROM users WHERE username=?", (user,)).fetchone()[0]
        st.markdown(f"<div class='metric-card'><h2>💰 МОЙ БАЛАНС: {u_bal} руб.</h2></div>", unsafe_allow_html=True)
        
        with st.expander("История моих смен"):
            my_l = pd.read_sql_query(f"SELECT date, duration, money_gain FROM logs WHERE user='{user}'", conn)
            st.table(my_l)
