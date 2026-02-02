import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# --- КОНФИГ СТРАНИЦЫ ---
st.set_page_config(page_title="SPELLING TEAM", page_icon="⚡", layout="wide")

# --- БАЗА ДАННЫХ ---
def get_db():
    conn = sqlite3.connect('spelling_team.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, xp INTEGER DEFAULT 0, rank TEXT DEFAULT "Новичок")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, xp_gain INTEGER)')
conn.commit()

# --- НЕОНОВЫЙ СТИЛЬ (СЕРЫЙ/ГОЛУБОЙ) ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    .neon-text { color: #00f2ff; text-shadow: 0 0 10px #00f2ff; font-weight: bold; }
    .stButton>button { background-color: #111; color: #00f2ff; border: 1px solid #00f2ff; width: 100%; border-radius: 10px; transition: 0.3s; }
    .stButton>button:hover { background-color: #00f2ff; color: #000; box-shadow: 0 0 20px #00f2ff; }
    .stTextInput>div>div>input { background-color: #1a1a1a; color: white; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None

# --- ЭКРАН ВХОДА ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center;' class='neon-text'>🔒 SPELLING TEAM TERMINAL</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    
    with col:
        mode = st.tabs(["ВХОД", "РЕГИСТРАЦИЯ"])
        
        with mode[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("LOG IN"):
                res = cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
                if res:
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Ошибка доступа")
        
        with mode[1]:
            ru = st.text_input("New Username", key="r_u")
            rp = st.text_input("New Password", type="password", key="r_p")
            if st.button("CREATE ACCOUNT"):
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (ru, rp))
                    conn.commit()
                    st.success("Аккаунт создан! Входи.")
                except: st.error("Ник уже занят")

# --- РАБОЧАЯ ЗОНА ---
else:
    user = st.session_state.user
    # Получаем инфу о юзере
    u_info = cursor.execute("SELECT xp, rank FROM users WHERE username=?", (user,)).fetchone()
    xp, rank = u_info[0], u_info[1]

    st.sidebar.markdown(f"<h2 class='neon-text'>👾 {user}</h2>", unsafe_allow_html=True)
    st.sidebar.write(f"🏆 Ранг: **{rank}**")
    st.sidebar.write(f"💎 XP: **{xp}**")
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.user = None
        st.rerun()

    st.markdown(f"<h1 style='text-align: center;' class='neon-text'>⚡ SPELLING WORKSPACE</h1>", unsafe_allow_html=True)
    
    tab_work, tab_top, tab_logs = st.tabs(["🚀 ВОРК", "🏆 ТОП", "📜 ИСТОРИЯ"])
    
    with tab_work:
        col1, col2 = st.columns([2, 1])
        with col1:
            if 'timer_on' not in st.session_state: st.session_state.timer_on = False
            
            if not st.session_state.timer_on:
                if st.button("▶ НАЧАТЬ СМЕНУ"):
                    st.session_state.start_t = datetime.now()
                    st.session_state.timer_on = True
                    st.rerun()
            else:
                now = datetime.now()
                dur = now - st.session_state.start_t
                st.metric("ВРЕМЯ В РАБОТЕ", str(dur).split('.')[0])
                if st.button("⏹ ЗАКОНЧИТЬ ВОРК"):
                    minutes = int(dur.total_seconds() / 60)
                    xp_gain = minutes * 2 # 2 XP за минуту
                    dt = now.strftime("%d.%m.%Y %H:%M")
                    
                    cursor.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (user, str(dur).split('.')[0], dt, xp_gain))
                    cursor.execute("UPDATE users SET xp = xp + ? WHERE username = ?", (xp_gain, user))
                    
                    # Апгрейд ранга
                    new_xp = xp + xp_gain
                    new_rank = rank
                    if new_xp > 500: new_rank = "🔥 Машина"
                    elif new_xp > 100: new_rank = "⚡ Воркер"
                    cursor.execute("UPDATE users SET rank = ? WHERE username = ?", (new_rank, user))
                    
                    conn.commit()
                    st.session_state.timer_on = False
                    st.balloons()
                    st.rerun()
                time.sleep(1)
                st.rerun()
        
        with col2:
            st.info("Правила: 1 минута = 2 XP. Чем больше XP, тем выше ранг в топе.")

    with tab_top:
        st.subheader("🏆 ЛУЧШИЕ ВОРКЕРЫ")
        df = pd.read_sql_query("SELECT username as Ник, rank as Ранг, xp as Опыт FROM users ORDER BY xp DESC", conn)
        st.table(df)

    with tab_logs:
        st.subheader("📜 ПОСЛЕДНИЕ СМЕНЫ")
        df_logs = pd.read_sql_query(f"SELECT duration as Время, xp_gain as Доход, date as Дата FROM logs WHERE user='{user}' ORDER BY date DESC", conn)
        st.dataframe(df_logs, use_container_width=True)