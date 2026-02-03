import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# 1. ГЛАВНЫЕ НАСТРОЙКИ
st.set_page_config(page_title="SPELLING CONTROL PRO", page_icon="📈", layout="wide")

# 2. БАЗА ДАННЫХ (v27)
conn = sqlite3.connect('control_v27.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# 3. ЛОГИКА СЕССИИ
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "worker"
if 'work' not in st.session_state: st.session_state.work = False

# 4. СТИЛЬ (ТЕМНАЯ ТЕМА)
st.markdown("""<style>
    .stMetric { background-color: #1e212b; padding: 15px; border-radius: 10px; border: 1px solid #3e4451; }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; }
    </style>""", unsafe_allow_html=True)

# --- ОКНО ВХОДА ---
if not st.session_state.auth:
    st.title("🛡️ ВХОД В СИСТЕМУ")
    col1, col2 = st.columns(2)
    with col1:
        u = st.text_input("Username")
        p = st.text_input("Password", type='password')
        if st.button("🔓 ВОЙТИ", use_container_width=True):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
                st.rerun()
            else:
                res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res:
                    if res[1] == "banned": st.error("🛑 Твой аккаунт заблокирован!")
                    else:
                        st.session_state.update({"auth":True, "user":u, "role":res[0]})
                        st.rerun()
                else: st.error("❌ Неверный логин или пароль")
    with col2:
        st.info("Новый здесь? Заполни поля слева и нажми кнопку ниже")
        if st.button("📝 СОЗДАТЬ АККАУНТ", use_container_width=True):
            try:
                cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
                conn.commit()
                st.success("✅ Аккаунт создан! Теперь жми ВОЙТИ")
            except: st.warning("⚠️ Этот логин уже занят или пуст")

# --- РАБОЧИЙ ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # Сайдбар с выходом
    st.sidebar.title(f"👾 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    # СЕКЦИЯ 1: БАЛАНС
    st.header(f"Добро пожаловать, {user}!")
    c_bal, c_info = st.columns([1, 2])
    
    with c_bal:
        if role == "admin":
            st.metric("Твой статус", "👑 ГЛАВНЫЙ")
        else:
            row = cursor.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()
            curr_bal = row[0] if row else 0
            st.metric("Твой баланс", f"{curr_bal} ₽")

    st.divider()

    # СЕКЦИЯ 2: ЖИВОЙ ТАЙМЕР
    st.subheader("⏳ ТАЙМЕР СМЕНЫ")
    t_btn, t_display = st.columns([1, 2])

    if not st.session_state.work:
        if t_btn.button("▶ НАЧАТЬ РАБОТУ", type="primary", use_container_width=True):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        # Цикл обновления времени
        diff = datetime.now() - st.session_state.start
        time_str = str(diff).split('.')[0]
        
        t_display.markdown(f"### 🚀 В работе: `{time_str}`")
        
        if t_btn.button("⏹ ЗАВЕРШИТЬ", type="secondary", use_container_width=True):
            mins = max(1, int(diff.total_seconds()/60))
            cash = mins * 100 # Настройка: 100р за минуту
            if role != "admin":
                cursor.execute("UPDATE users SET balance=balance+? WHERE username=?",(cash,user))
                cursor.execute("INSERT INTO logs VALUES (?,?,?,?)",(user,time_str,datetime.now().strftime("%H:%M"),cash))
                conn.commit()
            st.session_state.work = False
            st.balloons()
            st.rerun()
        
        time.sleep(1)
        st.rerun()

    # СЕКЦИЯ 3: АДМИНКА
    if role == "admin":
        st.write("---")
        st.header("👑 ПАНЕЛЬ УПРАВЛЕНИЯ")
        
        tab1, tab2 = st.tabs(["👤 СОСТАВ", "📜 ЛОГИ"])
        
        with tab1:
            workers_df = pd.read_sql_query("SELECT username, balance, status FROM users WHERE role='worker'", conn)
            st.dataframe(workers_df, use_container_width=True)
            
            st.write("#### Быстрые действия")
            target = st.selectbox("Выбери воркера", workers_df['username'] if not workers_df.empty else ["-"])
            col_b1, col_b2 = st.columns(2)
            
            if col_b1.button("⛔ БАН / РАЗБАН"):
                s = cursor.execute("SELECT status FROM users WHERE username=?",(target,)).fetchone()[0]
                new_s = "banned" if s == "active" else "active"
                cursor.execute("UPDATE users SET status=? WHERE username=?",(new_s, target))
                conn.commit()
                st.success(f"Статус {target} изменен!")
                st.rerun()
                
            if col_b2.button("💰 ОБНУЛИТЬ БАЛАНС"):
                cursor.execute("UPDATE users SET balance=0 WHERE username=?",(target,))
                conn.commit()
                st.warning(f"Баланс {target} сброшен!")
                st.rerun()
        
        with tab2:
            logs_df = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn)
            st.table(logs_df)
