import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="SPELLING CONTROL v33", page_icon="👑", layout="wide")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('v33_final.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# --- CSS ДИЗАЙН ---
st.markdown("""<style>
    .stMetric { background-color: #1e212b; padding: 15px; border-radius: 10px; border: 1px solid #3e4451; }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; width: 100%; }
    </style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("🔐 ДОСТУП В СИСТЕМУ")
    u = st.text_input("Логин").strip()
    p = st.text_input("Пароль", type='password').strip()
    c1, c2 = st.columns(2)
    if c1.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True, "user":u, "role":res[0]})
                st.rerun()
            else: st.error("❌ Ошибка или Блокировка")
    if c2.button("РЕГИСТРАЦИЯ"):
        try:
            cur.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit(); st.success("✅ Аккаунт создан!")
        except: st.error("⚠️ Логин занят")

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👤 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    st.header(f"👋 Привет, {user}!")
    
    # СЕКЦИЯ СТАТИСТИКИ
    col_bal, col_role = st.columns(2)
    with col_role:
        st.metric("Твой статус", "👑 ГЛАВНЫЙ" if role == "admin" else "🛠 ВОРКЕР")
    with col_bal:
        if role != "admin":
            bal = cur.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()[0]
            st.metric("Твой баланс", f"{bal} ₽")
        else:
            st.metric("Баланс системы", "♾️")

    st.divider()

    # СЕКЦИЯ ТАЙМЕРА (Доступна всем для теста)
    st.subheader("⌛ УПРАВЛЕНИЕ СМЕНОЙ")
    if 'work' not in st.session_state: st.session_state.work = False
    
    c_t1, c_t2 = st.columns([1, 2])
    
    if not st.session_state.work:
        if c_t1.button("▶ НАЧАТЬ ВОРК", type="primary"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        diff = datetime.now() - st.session_state.start
        time_str = str(diff).split('.')[0]
        c_t2.markdown(f"### 🚀 ВРЕМЯ: `{time_str}`")
        if c_t1.button("⏹ ЗАКОНЧИТЬ", type="secondary"):
            m = max(1, int(diff.total_seconds()/60))
            pay = m * 0.1
            if role != "admin":
                cur.execute("UPDATE users SET balance=balance+? WHERE username=?",(pay,user))
                cur.execute("INSERT INTO logs VALUES (?,?,?,?)",(user,time_str,datetime.now().strftime("%H:%M"),pay))
                conn.commit()
            st.session_state.work = False
            st.balloons(); st.rerun()
        time.sleep(1)
        st.rerun()

    # СЕКЦИЯ АДМИНА (МЕНЮ)
    if role == "admin":
        st.divider()
        st.header("👑 МЕНЮ АДМИНИСТРАТОРА")
        
        tab_users, tab_logs = st.tabs(["👥 СПИСОК ВОРКЕРОВ", "📜 ИСТОРИЯ ВЫПЛАТ"])
        
        with tab_users:
            workers = cur.execute("SELECT username, balance, status FROM users WHERE role='worker'").fetchall()
            if not workers:
                st.info("Воркеров пока нет. Пусть кто-нибудь зарегистрируется.")
            else:
                for wn, wb, ws in workers:
                    with st.expander(f"👤 {wn} | 💰 {wb} ₽ | Статус: {ws}"):
                        cb, cp = st.columns(2)
                        # Бан
                        b_label = "✅ РАЗБАНИТЬ" if ws == "banned" else "🚫 ЗАБАНИТЬ"
                        if cb.button(b_label, key=f"ban_{wn}"):
                            new_s = "active" if ws == "banned" else "banned"
                            cur.execute("UPDATE users SET status=? WHERE username=?",(new_s,wn))
                            conn.commit(); st.rerun()
                        # Сброс денег
                        if cp.button(f"🗑 ОБНУЛИТЬ {wn}", key=f"clear_{wn}"):
                            cur.execute("UPDATE users SET balance=0 WHERE username=?",(wn,))
                            conn.commit(); st.rerun()
        
        with tab_logs:
            st.write("Последние завершенные смены:")
            logs_df = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn)
            st.dataframe(logs_df, use_container_width=True)

