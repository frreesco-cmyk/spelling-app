import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="SPELLING ELITE v38", page_icon="🏦", layout="wide")

# Подключаем новую базу, чтобы не было конфликтов
conn = sqlite3.connect('v38_database.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# --- СТИЛЬ ---
st.markdown("""<style>
    .stMetric { background: #1e212b; padding: 20px; border-radius: 15px; border: 1px solid #3e4451; }
    .stButton>button { border-radius: 12px; height: 3.5em; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { border-color: #00ffcc; color: #00ffcc; }
    h1, h2 { color: #00ffcc; text-shadow: 0 0 10px #00ffcc44; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД / РЕГ ---
if not st.session_state.auth:
    st.title("🛡️ ВХОД В ПАНЕЛЬ")
    t_in, t_up = st.tabs(["🔑 ВОЙТИ", "📝 РЕГИСТРАЦИЯ"])
    with t_in:
        u = st.text_input("Логин", key="l_u").strip()
        p = st.text_input("Пароль", type='password', key="l_p").strip()
        if st.button("🚀 ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error("🛑 ОШИБКА: НЕТ ДОСТУПА ИЛИ БАН")
    with t_up:
        nu, np = st.text_input("Новый логин").strip(), st.text_input("Новый пароль", type='password').strip()
        if st.button("✨ ЗАРЕГИСТРИРОВАТЬСЯ"):
            if nu and np:
                try:
                    cur.execute('INSERT INTO users(username,password) VALUES (?,?)',(nu,np))
                    conn.commit(); st.success("✅ Успех! Переходи во вкладку входа.")
                except: st.error("⚠️ Логин уже занят")

# --- ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # ПРОВЕРКА БАНА
    if role != "admin":
        s = cur.execute("SELECT status FROM users WHERE username=?",(user,)).fetchone()
        if not s or s[0] == "banned":
            st.session_state.auth = False; st.error("🛑 ВЫ ЗАБАНЕНЫ!"); time.sleep(2); st.rerun()

    st.sidebar.title(f"👤 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False; st.rerun()

    st.title(f"👋 С возвращением, {user}!")
    
    # СТАТИСТИКА
    c1, c2, c3 = st.columns(3)
    with c1:
        if role == "admin": st.metric("СТАТУС", "👑 ГЛАВНЫЙ")
        else:
            b = cur.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()[0]
            st.metric("БАЛАНС", f"{b} ₽")
    with c2: st.metric("СИСТЕМА", "💎 ELITE")
    with c3: st.metric("СТАТУС", "🟢 ONLINE")

    st.divider()

    # ТАЙМЕР
    st.header("⏳ РАБОЧАЯ СМЕНА")
    if 'work' not in st.session_state: st.session_state.work = False
    
    tc1, tc2 = st.columns([1, 2])
    if not st.session_state.work:
        if tc1.button("▶ НАЧАТЬ РАБОТУ", type="primary"):
            st.session_state.start = datetime.now()
            st.session_state.work = True; st.rerun()
    else:
        diff = datetime.now() - st.session_state.start
        ts = str(diff).split('.')[0]
        tc2.markdown(f"## ⏱️ В ПРОЦЕССЕ: `{ts}`")
        if tc1.button("⏹ ЗАВЕРШИТЬ", type="secondary"):
            m = max(1, int(diff.total_seconds()/60))
            pay = m * 100
            if role != "admin":
                cur.execute("UPDATE users SET balance=balance+? WHERE username=?",(pay,user))
                cur.execute("INSERT INTO logs VALUES (?,?,?,?)",(user,ts,datetime.now().strftime("%H:%M"),pay))
                conn.commit()
            st.session_state.work = False; st.balloons(); st.rerun()
        time.sleep(1); st.rerun()

    # АДМИНКА
    if role == "admin":
        st.divider()
        st.header("👑 ПАНЕЛЬ АДМИНИСТРАТОРА")
        adm_t1, adm_t2 = st.tabs(["👥 УПРАВЛЕНИЕ ВОРКЕРАМИ", "📊 ЖУРНАЛ ЛОГОВ"])
        
        with adm_t1:
            workers = cur.execute("SELECT username, balance, status FROM users WHERE role='worker'").fetchall()
            if not workers:
                st.info("ℹ️ В базе пока нет воркеров. Зарегистрируй кого-нибудь для теста.")
            for wn, wb, ws in workers:
                with st.expander(f"👤 {wn} | 💰 {wb} ₽ | Статус: {ws}"):
                    ac1, ac2 = st.columns(2)
                    label = "✅ РАЗБАНИТЬ" if ws == "banned" else "🚫 ЗАБАНИТЬ"
                    if ac1.button(label, key=f"b_{wn}"):
                        ns = "active" if ws == "banned" else "banned"
                        cur.execute("UPDATE users SET status=? WHERE username=?",(ns,wn))
                        conn.commit(); st.rerun()
                    if ac2.button(f"🗑️ СБРОС ДЕНЕГ", key=f"c_{wn}"):
                        cur.execute("UPDATE users SET balance=0 WHERE username=?",(wn,))
                        conn.commit(); st.rerun()
        
        with adm_t2:
            try:
                logs_df = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn)
                if logs_df.empty: st.warning("📋 Журнал смен пока пуст.")
                else: st.dataframe(logs_df, use_container_width=True)
            except: st.error("❌ Ошибка загрузки логов")
