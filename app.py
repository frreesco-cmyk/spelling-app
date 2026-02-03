import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# Конфиг
st.set_page_config(page_title="SPELLING ELITE", page_icon="⚡")

# БД
conn = sqlite3.connect('v26_final.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ЛОГИКА ВХОДА ---
if not st.session_state.auth:
    st.title("⚡ SPELLING ELITE v26")
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    c1, c2 = st.columns(2)
    if c1.button("🔑 ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True, "user":u, "role":res[0]})
                st.rerun()
            else: st.error("Ошибка доступа")
    if c2.button("📝 РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit()
            st.success("ОК! Входи")
        except: st.error("Ник занят")

# --- ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👤 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    # Показ баланса (Фикс TypeError)
    st.subheader("💰 Мой счет")
    if role == "admin":
        st.info("👑 Администратор (Безлимит)")
    else:
        row = cursor.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()
        balance = row[0] if row else 0
        st.metric("Баланс", f"{balance} ₽")

    st.divider()

    # ТАЙМЕР
    if 'work' not in st.session_state: st.session_state.work = False
    
    if not st.session_state.work:
        if st.button("▶ НАЧАТЬ СМЕНУ", use_container_width=True):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        # Авто-обновление (Живой таймер)
        dur = datetime.now() - st.session_state.start
        time_str = str(dur).split('.')[0]
        
        st.error(f"⏱ ВРЕМЯ В РАБОТЕ: {time_str}")
        
        if st.button("⏹ ЗАКОНЧИТЬ ВОРК", use_container_width=True):
            m = max(1, int(dur.total_seconds()/60))
            pay = m * 100
            if role != "admin":
                cursor.execute("UPDATE users SET balance=balance+? WHERE username=?",(pay,user))
