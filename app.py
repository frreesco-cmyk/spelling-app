import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="СИНДИКАТ v55", page_icon="🦾", layout="wide")

# Создаем новую БД v55, чтобы избежать старых ошибок
def get_connection():
    return sqlite3.connect('v55_ultimate.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание таблиц
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                is_working INTEGER DEFAULT 0, last_act TEXT, xp INTEGER DEFAULT 0)''')
cur.execute('CREATE TABLE IF NOT EXISTS config (tax REAL DEFAULT 15, msg TEXT DEFAULT "РАБОТАТЬ!")')
cur.execute('CREATE TABLE IF NOT EXISTS vault (total_tax REAL DEFAULT 0)')
if not cur.execute('SELECT * FROM vault').fetchone(): cur.execute('INSERT INTO vault VALUES (0)')
if not cur.execute('SELECT * FROM config').fetchone(): cur.execute('INSERT INTO config (tax) VALUES (15)')
conn.commit()

# --- СТИЛИ ---
st.markdown("""<style>
    .stApp { background: #000; color: #0f0; }
    .stMetric { background: #0a0a0a; border: 1px solid #0f0; border-radius: 5px; }
    .stButton>button { border: 1px solid #0f0; color: #0f0; background: transparent; width: 100%; }
    .stButton>button:hover { background: #0f0; color: #000; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ЛОГИКА ВХОДА ---
if not st.session_state.auth:
    st.title("🦾 ВХОД В СИСТЕМУ v55")
    u = st.text_input("ЛОГИН").strip()
    p = st.text_input("ПАРОЛЬ", type='password').strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"АДМИН", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error("ОТКАЗАНО В ДОСТУПЕ")
    with col2:
        if st.button("РЕГИСТРАЦИЯ"):
            try:
                cur.execute('INSERT INTO users(username,password,last_act) VALUES (?,?,?)',(u,p,"-"))
                conn.commit(); st.success("ЮНИТ СОЗДАН")
            except: st.error("ОШИБКА РЕГИСТРАЦИИ")

# --- ГЛАВНОЕ ОКНО ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # Проверка на бан в реальном времени
    if role != "admin":
        s_check = cur.execute("SELECT status FROM users WHERE username=?",(user,)).fetchone()
        if not s_check or s_check[0] == "banned":
            st.session_state.auth = False
            st.rerun()

    if st.sidebar.button("ВЫХОД"):
        cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
        conn.commit()
        st.session_state.auth = False
        st.rerun()

    # ИНТЕРФЕЙС ВОРКЕРА
    if role != "admin":
        st.header(f"⚒️ РАБОЧИЙ ЮНИТ: {user}")
        
        # БЕЗОПАСНОЕ ПОЛУЧЕНИЕ ДАННЫХ (Защита от TypeError)
        raw_data = cur.execute("SELECT balance, xp FROM users WHERE username=?",(user,)).fetchone()
        u_bal = raw_data[0] if raw_data else 0
        u_xp = raw_data[1] if raw_data else 0
        
        c1, c2 = st.columns(2)
        c1.metric("💰 ТВОЙ БАЛАНС", f"{round(u_bal, 2)} ₽")
        c2.metric("🧬 ОПЫТ", u_xp)

        if 'working' not in st.session_state: st.session_state.working = False
        
        if not st.session_state.working:
            if st.button("▶ НАЧАТЬ ДОБЫЧУ"):
                st.session_state.working = True
                cur.execute("UPDATE users SET is_working=1 WHERE username=?", (user,))
                conn.commit(); st.rerun()
        else:
            st.warning("⛏ ИДЕТ ПРОЦЕСС НАЧИСЛЕНИЯ...")
            tax_rate = cur.execute("SELECT tax FROM config").fetchone()[0]
            gain = 2.0
            tax_v = gain * (tax_rate/100)
            
            cur.execute("UPDATE users SET balance = balance + ?, xp = xp + 1 WHERE username=?", (gain - tax_v, user))
            cur.execute("UPDATE vault SET total_tax = total_tax + ?", (tax_v,))
            conn.commit()
            
            if st.button("⏹ ОСТАНОВИТЬ"):
                st.session_state.working = False
                cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
                conn.commit(); st.rerun()
            time.sleep(1); st.rerun()

    # ИНТЕРФЕЙС АДМИНА
    else:
        st.title("👑 ПАНЕЛЬ УПРАВЛЕНИЯ")
        v_bal = cur.execute("SELECT total_tax FROM vault").fetchone()[0]
        st.metric("🏦 МОЙ СЕЙФ", f"{round(v_bal, 2)} ₽")
        
        tax_val = cur.execute("SELECT tax FROM config").fetchone()[0]
        new_tax = st.slider("НАЛОГ БОССА (%)", 0, 100, int(tax_val))
        if st.button("ОБНОВИТЬ НАЛОГ"):
            cur.execute("UPDATE config SET tax=?", (new_tax,))
            conn.commit(); st.success("ПРИНЯТО")

        st.divider()
        st.subheader("👥 СПИСОК РАБОВ")
        workers = cur.execute("SELECT username, balance, is_working, status FROM users WHERE role='worker'").fetchall()
        
        for wn, wb, is_w, ws in workers:
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"{'🟢' if is_w else '⚪'} **{wn}** | {round(wb, 1)} ₽")
            if col2.button("🚫 БАН", key=f"b_{wn}"):
                cur.execute("UPDATE users SET status='banned', is_working=0 WHERE username=?",(wn,))
                conn.commit(); st.rerun()
            if col3.button("♻️ СБРОС", key=f"r_{wn}"):
                cur.execute("UPDATE users SET balance=0 WHERE username=?",(wn,))
                conn.commit(); st.rerun()
        
        time.sleep(2); st.rerun()
