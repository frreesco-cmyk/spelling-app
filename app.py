import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time
import random

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="TYRANT v56", page_icon="👹", layout="wide")

# Новое имя БД для чистого запуска
def get_connection():
    return sqlite3.connect('v56_tyrant.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание структуры
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                is_working INTEGER DEFAULT 0, last_act TEXT, xp INTEGER DEFAULT 0)''')
cur.execute('CREATE TABLE IF NOT EXISTS snitches (sender TEXT, target TEXT, reason TEXT, date TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS config (tax REAL DEFAULT 15, msg TEXT DEFAULT "РАБОТАТЬ БЫСТРО!")')
cur.execute('CREATE TABLE IF NOT EXISTS vault (total_tax REAL DEFAULT 0)')
if not cur.execute('SELECT * FROM vault').fetchone(): cur.execute('INSERT INTO vault VALUES (0)')
if not cur.execute('SELECT * FROM config').fetchone(): cur.execute('INSERT INTO config (tax) VALUES (15)')
conn.commit()

# --- СТИЛИ (АГРЕССИВНЫЙ ТЕМНЫЙ) ---
st.markdown("""<style>
    .stApp { background: #050505; color: #ff4b4b; }
    .stMetric { background: #111; border-left: 5px solid #ff4b4b; border-radius: 5px; }
    .stButton>button { border: 1px solid #ff4b4b; color: #ff4b4b; background: transparent; width: 100%; }
    .stButton>button:hover { background: #ff4b4b; color: #fff; box-shadow: 0 0 20px #ff4b4b; }
    .rank-box { padding: 10px; border: 1px solid #444; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 15px; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ЛОГИКА ВХОДА ---
if not st.session_state.auth:
    st.title("👹 ТЕРМИНАЛ ТИРАНА v56")
    u = st.text_input("ЛОГИН").strip()
    p = st.text_input("ПАРОЛЬ", type='password').strip()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("ВОЙТИ В СИСТЕМУ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ВЛАДЫКА", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error("ДОСТУП ЗАКРЫТ")
    with c2:
        if st.button("ЗАРЕГИСТРИРОВАТЬСЯ"):
            try:
                cur.execute('INSERT INTO users(username,password,last_act,xp) VALUES (?,?,?,0)',(u,p,"-"))
                conn.commit(); st.success("ЮНИТ СОЗДАН")
            except: st.error("ИМЯ ЗАНЯТО")

# --- ГЛАВНЫЙ МОДУЛЬ ---
else:
    user, role = st.session_state.user, st.session_state.role
    cur.execute("UPDATE users SET last_act=? WHERE username=?", (datetime.now().strftime("%H:%M:%S"), user))
    conn.commit()

    if st.sidebar.button("❌ ВЫХОД"):
        cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
        conn.commit(); st.session_state.auth = False; st.rerun()

    # --- ИНТЕРФЕЙС ВОРКЕРА ---
    if role != "admin":
        st.header(f"🛠 СЕКТОР: {user}")
        
        # Получаем данные воркера
        u_data = cur.execute("SELECT balance, xp FROM users WHERE username=?",(user,)).fetchone()
        u_bal, u_xp = u_data if u_data else (0, 0)
        
        # Система рангов
        if u_xp < 100: rank, r_col = "ГРЯЗНЫЙ РАБ", "#555"
        elif u_xp < 500: rank, r_col = "ПОДМАСТЕРЬЕ", "#00ff00"
        elif u_xp < 1500: rank, r_col = "МАСТЕР ЦЕХА", "#00ffff"
        else: rank, r_col = "АРХИТЕКТОР", "#ffd700"

        st.markdown(f'<div class="rank-box" style="color:{r_col}; border-color:{r_col}">ТВОЙ РАНГ: {rank}</div>', unsafe_allow_html=True)
        
        conf = cur.execute("SELECT tax, msg FROM config").fetchone()
        st.info(f"📜 ПРИКАЗ АДМИНА: {conf[1]}")

        col_w1, col_w2 = st.columns(2)
        col_w1.metric("💰 БАЛАНС", f"{round(u_bal, 2)} ₽")
        col_w2.metric("🧬 ОПЫТ (XP)", u_xp)

        t_work, t_snitch = st.tabs(["⚒️ ДОБЫЧА", "🐀 СТУЧАТЬ"])
        
        with t_work:
            if 'working' not in st.session_state: st.session_state.working = False
            if not st.session_state.working:
                if st.button("▶ НАЧАТЬ РАБОТУ"):
                    st.session_state.working = True
                    cur.execute("UPDATE users SET is_working=1 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
            else:
                st.error("⛏ ПРОЦЕСС ИДЕТ... ТЫ ПРИНОСИШЬ ПРИБЫЛЬ")
                gain = 5.0
                tax_v = gain * (conf[0]/100)
                cur.execute("UPDATE users SET balance=balance+?, xp=xp+2 WHERE username=?", (gain-tax_v, user))
                cur.execute("UPDATE vault SET total_tax=total_tax+?", (tax_v,))
                conn.commit()
                if st.button("⏹ ОСТАНОВИТЬ"):
                    st.session_state.working = False
                    cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
                time.sleep(1); st.rerun()
        
        with t_snitch:
            target = st.selectbox("НА КОГО ДОНОС?", [u[0] for u in cur.execute("SELECT username FROM users WHERE role='worker' AND username!=?",(user,)).fetchall()])
            reason = st.text_area("В чем провинился юнит?")
            if st.button("ОТПРАВИТЬ СТУК"):
                cur.execute("INSERT INTO snitches VALUES (?,?,?,?)", (user, target, reason, datetime.now().strftime("%H:%M")))
                conn.commit(); st.success("ДОНОС ПРИНЯТ. ЦАРЬ РАЗБЕРЕТСЯ.")

    # --- ИНТЕРФЕЙС АДМИНА ---
    else:
        st.title("👑 ПУЛЬТ ВСЕДЕРЖИТЕЛЯ")
        v_bal = cur.execute("SELECT total_tax FROM vault").fetchone()[0]
        tax_n, msg_n = cur.execute("SELECT tax, msg FROM config").fetchone()
        
        st.metric("🏦 МОЙ ЧИСТЫЙ ПРОФИТ", f"{round(v_bal, 2)} ₽")
        
        at1, at2, at3, at4 = st.tabs(["👥 ВОРКЕРЫ", "🐀 ДОНОСЫ", "⚙️ НАСТРОЙКИ", "💀 КАЗНИ"])
        
        with at1:
            for wn, wb, is_w, ws, wxp in cur.execute("SELECT username, balance, is_working, status, xp FROM users WHERE role='worker'").fetchall():
                with st.expander(f"{'🟢' if is_w else '⚪'} {wn} | {round(wb, 1)} ₽ | {wxp} XP"):
                    c_a, c_b = st.columns(2)
                    if c_a.button("🚫 БАНИТЬ", key=f"b_{wn}"):
                        cur.execute("UPDATE users SET status='banned', is_working=0 WHERE username=?", (wn,))
                        conn.commit(); st.rerun()
                    if c_b.button("💸 ОБНУЛИТЬ", key=f"r_{wn}"):
                        cur.execute("UPDATE users SET balance=0 WHERE username=?", (wn,))
                        conn.commit(); st.rerun()

        with at2:
            for s, t, r, d in cur.execute("SELECT * FROM snitches").fetchall():
                st.warning(f"[{d}] {s} СТУЧИТ НА {t}: {r}")
            if st.button("ОЧИСТИТЬ ЖУРНАЛ"):
                cur.execute("DELETE FROM snitches"); conn.commit(); st.rerun()

        with at3:
            new_tax = st.slider("НАЛОГ (%)", 0, 100, int(tax_n))
            new_msg = st.text_input("НОВЫЙ ПРИКАЗ", msg_n)
            if st.button("ПРИМЕНИТЬ"):
                cur.execute("UPDATE config SET tax=?, msg=?", (new_tax, new_msg))
                conn.commit(); st.rerun()

        with at4:
            st.subheader("СПИСОК РАССТРЕЛЯННЫХ")
            for bu in cur.execute("SELECT username FROM users WHERE status='banned'").fetchall():
                st.write(f"💀 {bu[0]}")

        time.sleep(2); st.rerun()
