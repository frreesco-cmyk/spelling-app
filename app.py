import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# База
conn = sqlite3.connect('team_v25.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

st.title("⚡ SPELLING ELITE v25")

if 'auth' not in st.session_state: st.session_state.auth = False

# ВХОД
if not st.session_state.auth:
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    if st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True,"user":"ADMIN","role":"admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True,"user":u,"role":res[0]})
                st.rerun()
            else: st.error("Отказ")
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit()
            st.success("ОК")
        except: st.error("Занято")

# ИНТЕРФЕЙС
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.write(f"Юзер: {user}")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    # БАЛАНС
    bal = cursor.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()[0]
    st.metric("Твой баланс", f"{bal} ₽")

    # ТАЙМЕР
    st.write("---")
    if 'work' not in st.session_state: st.session_state.work = False
    
    if not st.session_state.work:
        if st.button("▶ НАЧАТЬ РАБОТУ"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        # Авто-обновление времени
        dur = datetime.now() - st.session_state.start
        time_str = str(dur).split('.')[0]
        st.error(f"⏱ ВРЕМЯ СМЕНЫ: {time_str}")
        
        if st.button("⏹ ЗАКОНЧИТЬ"):
            m = max(1, int(dur.total_seconds()/60))
            pay = m * 100
            cursor.execute("UPDATE users SET balance=balance+? WHERE username=?",(pay,user))
            cursor.execute("INSERT INTO logs VALUES (?,?,?,?)",(user,time_str,datetime.now().strftime("%H:%M"),pay))
            conn.commit()
            st.session_state.work = False
            st.rerun()
        
        time.sleep(1)
        st.rerun()

    # АДМИНКА
    if role == "admin":
        st.write("---")
        st.subheader("👑 АДМИН-ПАНЕЛЬ")
        df = pd.read_sql_query("SELECT username, balance, status FROM users WHERE role='worker'", conn)
        st.dataframe(df)
        
        t = st.text_input("Ник для бана")
        if st.button("БАН / РАЗБАН"):
            s = cursor.execute("SELECT status FROM users WHERE username=?",(t,)).fetchone()
            if s:
                ns = "banned" if s[0] == "active" else "active"
                cursor.execute("UPDATE users SET status=? WHERE username=?",(ns,t))
                conn.commit()
                st.rerun()
