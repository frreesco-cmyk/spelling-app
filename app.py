import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- НАСТРОЙКИ ИНТЕРФЕЙСА ---
st.set_page_config(page_title="ELITE CONTROL PANEL", page_icon="💎", layout="wide")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('elite_v40.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                is_working INTEGER DEFAULT 0, last_act TEXT)''')
cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# --- ТЕМНЫЙ СТИЛЬ ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0b0e14; }
    .stMetric { background: #161b22; padding: 20px; border-radius: 12px; border-left: 5px solid #00ffcc; }
    .stButton>button { border-radius: 10px; height: 3.5em; font-weight: 700; transition: 0.4s; }
    .stButton>button:hover { box-shadow: 0 0 15px #00ffcc55; border-color: #00ffcc; }
    div[data-testid="stExpander"] { background: #161b22; border-radius: 10px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- АВТОРИЗАЦИЯ ---
if not st.session_state.auth:
    st.title("💎 ELITE SYSTEM ACCESS")
    t1, t2 = st.tabs(["🔑 ВХОД", "📝 РЕГИСТРАЦИЯ"])
    with t1:
        u = st.text_input("Логин", key="u_log").strip()
        p = st.text_input("Пароль", type='password', key="p_log").strip()
        if st.button("🚀 ВОЙТИ В ПАНЕЛЬ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error("❌ ДОСТУП ЗАБЛОКИРОВАН ИЛИ ОШИБКА")
    with t2:
        nu, np = st.text_input("Логин").strip(), st.text_input("Пароль", type='password').strip()
        if st.button("✨ СОЗДАТЬ АККАУНТ"):
            if nu and np:
                try:
                    cur.execute('INSERT INTO users(username,password,last_act) VALUES (?,?,?)',(nu,np,"-"))
                    conn.commit(); st.success("✅ Аккаунт готов! Теперь входи.")
                except: st.error("⚠️ Логин уже занят")

# --- ОСНОВНОЙ КОНТЕНТ ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # Обновляем активность
    now_time = datetime.now().strftime("%H:%M:%S")
    cur.execute("UPDATE users SET last_act=? WHERE username=?", (now_time, user))
    conn.commit()

    # Проверка бана
    if role != "admin":
        check = cur.execute("SELECT status FROM users WHERE username=?",(user,)).fetchone()
        if not check or check[0] == "banned":
            st.session_state.auth = False; st.error("🛑 ВЫ ЗАБАНЕНЫ"); time.sleep(1.5); st.rerun()

    # Sidebar
    st.sidebar.markdown(f"### 👾 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
        conn.commit(); st.session_state.auth = False; st.rerun()

    st.title(f"💎 SPELLING ELITE | {role.upper()}")
    
    # СТАТИСТИКА (ВИДЖЕТЫ)
    c1, c2, c3 = st.columns(3)
    if role == "admin":
        total_bal = cur.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0
        c1.metric("ОБЩИЙ ДОЛГ ВОРКЕРАМ", f"{total_bal} ₽")
        c2.metric("СИСТЕМА", "ADMOD")
        c3.metric("ПОТОК", "LIVE")
    else:
        bal = cur.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()[0]
        c1.metric("ТВОЙ БАЛАНС", f"{bal} ₽")
        c2.metric("СТАВКА", "100 ₽ / мин")
        c3.metric("СТАТУС", "ACTIVE")

    st.divider()

    # ТАЙМЕР
    if 'work' not in st.session_state: st.session_state.work = False
    
    st.subheader("⌛ РАБОЧАЯ СМЕНА")
    tc1, tc2 = st.columns([1, 2])
    
    if not st.session_state.work:
        if tc1.button("▶ НАЧАТЬ ВОРК", type="primary"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            cur.execute("UPDATE users SET is_working=1 WHERE username=?", (user,))
            conn.commit(); st.rerun()
    else:
        diff = datetime.now() - st.session_state.start
        ts = str(diff).split('.')[0]
        tc2.markdown(f"## 🔋 В ПРОЦЕССЕ: `{ts}`")
        if tc1.button("⏹ ЗАКОНЧИТЬ", type="secondary"):
            mins = max(1, int(diff.total_seconds()/60))
            pay = mins * 100
            if role != "admin":
                cur.execute("UPDATE users SET balance=balance+?, is_working=0 WHERE username=?",(pay,user))
                cur.execute("INSERT INTO logs VALUES (?,?,?,?)",(user,ts,datetime.now().strftime("%H:%M"),pay))
                conn.commit()
            else:
                cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
                conn.commit()
            st.session_state.work = False; st.balloons(); st.rerun()
        time.sleep(1); st.rerun()

    # --- АДМИНКА (ТОТАЛЬНЫЙ КОНТРОЛЬ) ---
    if role == "admin":
        st.divider()
        st.header("👑 ПАНЕЛЬ УПРАВЛЕНИЯ ГЛАВНОГО")
        
        tab_list, tab_log = st.tabs(["👥 КОНТРОЛЬ ВОРКЕРОВ", "📜 ИСТОРИЯ ВЫПЛАТ"])
        
        with tab_list:
            workers = cur.execute("SELECT username, balance, status, is_working, last_act FROM users WHERE role='worker'").fetchall()
            if not workers: st.info("Воркеров пока нет.")
            
            for wn, wb, ws, is_w, last in workers:
                # Динамический статус
                stat_icon = "🟢 ВОРКАЕТ" if is_w == 1 else "🟡 В СЕТИ"
                with st.expander(f"{stat_icon} | 👤 {wn} | 💰 {wb} ₽"):
                    st.write(f"**Последняя активность:** {last} | **Статус:** {ws}")
                    ac1, ac2 = st.columns(2)
                    # Кнопка бана
                    b_btn = "✅ РАЗБАНИТЬ" if ws == "banned" else "🚫 ЗАБАНИТЬ"
                    if ac1.button(b_btn, key=f"ban_{wn}"):
                        ns = "active" if ws == "banned" else "banned"
                        cur.execute("UPDATE users SET status=? WHERE username=?",(ns,wn))
                        conn.commit(); st.rerun()
                    # Кнопка сброса
                    if ac2.button(f"🗑 ОБНУЛИТЬ", key=f"clr_{wn}"):
                        cur.execute("UPDATE users SET balance=0 WHERE username=?",(wn,))
                        conn.commit(); st.rerun()
        
        with tab_log:
            logs = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn)
            st.dataframe(logs, use_container_width=True)
