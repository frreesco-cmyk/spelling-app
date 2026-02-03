import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="CONTROL PRO v34", page_icon="🚫", layout="wide")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('v34_final.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("🔐 ВХОД")
    u = st.text_input("Логин").strip()
    p = st.text_input("Пароль", type='password').strip()
    if st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True, "user":u, "role":res[0]})
                st.rerun()
            else: st.error("❌ ОШИБКА ИЛИ БАН")
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            cur.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit(); st.success("✅ ОК")
        except: st.error("⚠️ Логин занят")

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # ПРОВЕРКА БАНА В РЕАЛЬНОМ ВРЕМЕНИ
    if role != "admin":
        check = cur.execute("SELECT status FROM users WHERE username=?",(user,)).fetchone()
        if not check or check[0] == "banned":
            st.session_state.auth = False
            st.error("🛑 ВЫ ЗАБАНЕНЫ АДМИНИСТРАТОРОМ")
            time.sleep(3)
            st.rerun()

    # САЙДБАР
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    st.header(f"👋 Привет, {user}!")
    
    # БАЛАНС
    if role != "admin":
        r = cur.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()
        st.metric("Твой баланс", f"{r[0] if r else 0} ₽")
    
    st.divider()

    # ТАЙМЕР
    if 'work' not in st.session_state: st.session_state.work = False
    
    c_t1, c_t2 = st.columns([1, 2])
    if not st.session_state.work:
        if c_t1.button("▶ НАЧАТЬ ВОРК", type="primary"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        diff = datetime.now() - st.session_state.start
        t_str = str(diff).split('.')[0]
        c_t2.markdown(f"### 🚀 ВРЕМЯ: `{t_str}`")
        if c_t1.button("⏹ ЗАКОНЧИТЬ", type="secondary"):
            m = max(1, int(diff.total_seconds()/60))
            pay = m * 100
            if role != "admin":
                cur.execute("UPDATE users SET balance=balance+? WHERE username=?",(pay,user))
                cur.execute("INSERT INTO logs VALUES (?,?,?,?)",(user,t_str,datetime.now().strftime("%H:%M"),pay))
                conn.commit()
            st.session_state.work = False
            st.rerun()
        time.sleep(1)
        st.rerun() # Здесь происходит авто-проверка статуса бана

    # АДМИНКА
    if role == "admin":
        st.divider()
        st.header("👑 АДМИНКА")
        workers = cur.execute("SELECT username, balance, status FROM users WHERE role='worker'").fetchall()
        for wn, wb, ws in workers:
            with st.expander(f"👤 {wn} | {wb} ₽ | Статус: {ws}"):
                c1, c2 = st.columns(2)
                # Кнопка БАНА
                b_lbl = "✅ РАЗБАНИТЬ" if ws == "banned" else "🚫 ЗАБАНИТЬ"
                if c1.button(b_lbl, key=f"b_{wn}"):
                    ns = "active" if ws == "banned" else "banned"
                    cur.execute("UPDATE users SET status=? WHERE username=?",(ns,wn))
                    conn.commit()
                    st.rerun()
                # СБРОС
                if c2.button(f"🗑 СБРОС БАЛАНСА", key=f"p_{wn}"):
                    cur.execute("UPDATE users SET balance=0 WHERE username=?",(wn,))
                    conn.commit()
                    st.rerun()
