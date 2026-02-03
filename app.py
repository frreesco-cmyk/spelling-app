import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="SPELLING ELITE", page_icon="⚡", layout="wide")

# Подключение БД
conn = sqlite3.connect('team_elite_v23.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Off")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# Кастомный CSS для красоты
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; border: 1px solid #4x4x4x; }
    .stButton>button:hover { border-color: #ff4b4b; color: #ff4b4b; }
    .stat-box { padding: 20px; border-radius: 10px; background-color: #161b22; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ЛОГИКА ВХОДА ---
if not st.session_state.auth:
    st.title("⚡ SPELLING ELITE SYSTEM")
    col1, col2 = st.columns(2)
    with col1:
        u = st.text_input("👤 Логин")
        p = st.text_input("🔑 Пароль", type='password')
        if st.button("🚀 ВОЙТИ В СИСТЕМУ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True,"user":"ADMIN","role":"admin"})
                st.rerun()
            else:
                res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True,"user":u,"role":res[0]})
                    st.rerun()
                else: st.error("❌ Отказано в доступе")
    with col2:
        st.info("Регистрация новых воркеров")
        if st.button("📝 СОЗДАТЬ АККАУНТ"):
            try:
                cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
                conn.commit()
                st.success("✅ Аккаунт создан! Теперь жми войти.")
            except: st.error("⚠️ Логин занят")

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # Сайдбар
    st.sidebar.title("⚡ MENU")
    st.sidebar.markdown(f"**Вы вошли как:**\n`{user}`")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    # Основная панель
    st.header(f"👋 Привет, {user}!")
    
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.subheader("📊 Твой Баланс")
        bal = cursor.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()[0]
        st.title(f"{bal} ₽")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_stat2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.subheader("🕹 Управление статусом")
        c_on, c_afk = st.columns(2)
        if c_on.button("🟢 ONLINE"):
            cursor.execute("UPDATE users SET user_state='Online' WHERE username=?",(user,))
            conn.commit()
            st.toast("Статус: В сети")
        if c_afk.button("🟡 AFK"):
            cursor.execute("UPDATE users SET user_state='AFK' WHERE username=?",(user,))
            conn.commit()
            st.toast("Статус: Отошел")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")

    # ТАЙМЕР
    st.subheader("⌛ РАБОЧАЯ СМЕНА")
    if 'work' not in st.session_state: st.session_state.work = False
    
    t_col1, t_col2 = st.columns([1, 2])
    if not st.session_state.work:
        if t_col1.button("▶ НАЧАТЬ ВОРК"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        dur = datetime.now() - st.session_state.start
        t_col2.error(f"⏱ ТЕКУЩЕЕ ВРЕМЯ: {str(dur).split('.')[0]}")
        if t_col1.button("⏹ ЗАКОНЧИТЬ"):
            m = max(1, int(dur.total_seconds()/60))
            pay = m * 100 # 100р в минуту
            cursor.execute("UPDATE users SET balance=balance+? WHERE username=?",(pay,user))
            cursor.execute("INSERT INTO logs VALUES (?,?,?,?)",(user,str(dur).split('.')[0],datetime.now().strftime("%H:%M"),pay))
            conn.commit()
            st.session_state.work = False
            st.balloons()
            st.rerun()

    # АДМИНКА
    if role == "admin":
        st.write("---")
        st.header("👑 ПАНЕЛЬ УПРАВЛЕНИЯ")
        
        tab_users, tab_logs = st.tabs(["👥 Воркеры", "📜 Логи смен"])
        
        with tab_users:
            df = pd.read_sql_query("SELECT username, user_state, balance, status FROM users WHERE role='worker'", conn)
            st.dataframe(df, use_container_width=True)
            
            st.subheader("🚫 Управление доступом")
            t_user = st.selectbox("Выбери воркера", df['username'] if not df.empty else ["Пусто"])
            if st.button("БАН / РАЗБАН"):
                curr_s = cursor.execute("SELECT status FROM users WHERE username=?",(t_user,)).fetchone()[0]
                new_s = "banned" if curr_s == "active" else "active"
                cursor.execute("UPDATE users SET status=? WHERE username=?",(new_s, t_user))
                conn.commit()
                st.rerun()
        
        with tab_logs:
            logs = pd.read_sql_query("SELECT * FROM logs", conn)
            st.table(logs)
