import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="СИНДИКАТ v54", page_icon="⚔️", layout="wide")

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('v54_syndicate.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                    role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                    is_working INTEGER DEFAULT 0, last_act TEXT, xp INTEGER DEFAULT 0)''')
    cur.execute('CREATE TABLE IF NOT EXISTS snitch_reports (sender TEXT, target TEXT, reason TEXT, date TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS system_config (tax REAL DEFAULT 15, reg_open INTEGER DEFAULT 1, msg TEXT DEFAULT "РАБОТАТЬ!")')
    cur.execute('CREATE TABLE IF NOT EXISTS vault (total_tax REAL DEFAULT 0)')
    if not cur.execute('SELECT * FROM vault').fetchone(): cur.execute('INSERT INTO vault VALUES (0)')
    if not cur.execute('SELECT * FROM system_config').fetchone(): cur.execute('INSERT INTO system_config (tax, reg_open) VALUES (15, 1)')
    conn.commit()
    return conn

conn = init_db()
cur = conn.cursor()

# --- СТИЛИ ---
st.markdown("""<style>
    .stApp { background: #000; color: #0f0; }
    .stMetric { background: #111; border: 1px solid #0f0; border-radius: 5px; }
    .stButton>button { border: 1px solid #0f0; color: #0f0; background: transparent; transition: 0.3s; }
    .stButton>button:hover { background: #0f0; color: #000; box-shadow: 0 0 20px #0f0; }
    input { background-color: #0a0a0a !important; color: #0f0 !important; border: 1px solid #0f0 !important; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("⚔️ ТЕРМИНАЛ СИНДИКАТА v54")
    tab_log, tab_reg = st.tabs(["🔐 ВХОД", "📝 РЕГИСТРАЦИЯ"])
    
    with tab_log:
        u = st.text_input("ЛОГИН").strip()
        p = st.text_input("ПАРОЛЬ", type='password').strip()
        if st.button("ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ЦАРЬ", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res:
                    if res[1] != "banned":
                        st.session_state.update({"auth":True, "user":u, "role":res[0]})
                        st.rerun()
                    else: st.error("ТЫ ИЗГНАН")
                else: st.error("НЕВЕРНЫЕ ДАННЫЕ")
    
    with tab_reg:
        reg_open = cur.execute("SELECT reg_open FROM system_config").fetchone()[0]
        if reg_open:
            nu = st.text_input("НОВЫЙ ЮНИТ").strip()
            np = st.text_input("НОВЫЙ ПАРОЛЬ").strip()
            if st.button("СОЗДАТЬ"):
                try:
                    cur.execute('INSERT INTO users(username,password,last_act) VALUES (?,?,?)',(nu,np,"-"))
                    conn.commit(); st.success("ГОТОВО")
                except: st.error("ЛОГИН ЗАНЯТ")
        else: st.warning("РЕГИСТРАЦИЯ ЗАКРЫТА")

# --- ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    cur.execute("UPDATE users SET last_act=? WHERE username=?", (datetime.now().strftime("%H:%M:%S"), user))
    conn.commit()

    if st.sidebar.button("ВЫХОД"):
        cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
        conn.commit(); st.session_state.auth = False; st.rerun()

    if role != "admin":
        st.header(f"⚒️ СЕКТОР ЮНИТА: {user}")
        u_data = cur.execute("SELECT balance, xp FROM users WHERE username=?",(user,)).fetchone()
        conf = cur.execute("SELECT tax, msg FROM system_config").fetchone()
        
        st.info(f"📜 ПРИКАЗ: {conf[1]}")
        st.metric("💰 БАЛАНС", f"{round(u_data[0], 2)} ₽")
        
        t1, t2, t3 = st.tabs(["РАБОТА", "ДОНОС", "РЕЙТИНГ"])
        with t1:
            if 'work' not in st.session_state: st.session_state.work = False
            if not st.session_state.work:
                if st.button("НАЧАТЬ"):
                    st.session_state.start, st.session_state.work = datetime.now(), True
                    cur.execute("UPDATE users SET is_working=1 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
            else:
                st.warning("ВОРК ИДЕТ...")
                tax_v = 3.0 * (conf[0]/100)
                cur.execute("UPDATE users SET balance=balance+?, xp=xp+1 WHERE username=?", (3.0-tax_v, user))
                cur.execute("UPDATE vault SET total_tax=total_tax+?", (tax_v,))
                conn.commit()
                if st.button("СТОП"):
                    st.session_state.work = False
                    cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
                time.sleep(1); st.rerun()
        
        with t2:
            target = st.selectbox("НА КОГО СТУЧИМ?", [u[0] for u in cur.execute("SELECT username FROM users WHERE role='worker' AND username!=?",(user,)).fetchall()])
            reason = st.text_area("СУТЬ ПРЕТЕНЗИИ")
            if st.button("СТУКНУТЬ"):
                cur.execute("INSERT INTO snitch_reports VALUES (?,?,?,?)", (user, target, reason, datetime.now().strftime("%H:%M")))
                conn.commit(); st.success("ДОНОС ПРИНЯТ")
        
        with t3:
            st.subheader("🏆 ТОП ЛОЯЛЬНОСТИ")
            top = cur.execute("SELECT username, xp FROM users WHERE role='worker' ORDER BY xp DESC LIMIT 5").fetchall()
            for i, (un, ux) in enumerate(top): st.write(f"{i+1}. {un} — {ux} XP")

    else:
        st.title("👑 ПУЛЬТ УПРАВЛЕНИЯ")
        v_bal = cur.execute("SELECT total_tax FROM vault").fetchone()[0]
        tax_n, reg_n, msg_n = cur.execute("SELECT tax, reg_open, msg FROM system_config").fetchone()
        
        st.metric("🏦 МОЙ СЕЙФ", f"{round(v_bal, 2)} ₽")
        
        tabs = st.tabs(["👥 ВОРКЕРЫ", "🐀 ДОНОСЫ", "⚙️ НАСТРОЙКИ", "💀 КАЗНИ"])
        
        with tabs[0]:
            for wn, wb, is_w, ws in cur.execute("SELECT username, balance, is_working, status FROM users WHERE role='worker'").fetchall():
                with st.expander(f"{'🟢' if is_w else '⚪'} {wn} | {round(wb, 1)} ₽"):
                    ca, cb = st.columns(2)
                    if ca.button("🚫 БАН", key=f"b_{wn}"):
                        cur.execute("UPDATE users SET status='banned', is_working=0 WHERE username=?", (wn,))
                        conn.commit(); st.rerun()
                    if cb.button("💸 ОБНУЛИТЬ", key=f"r_{wn}"):
                        cur.execute("UPDATE users SET balance=0 WHERE username=?", (wn,))
                        conn.commit(); st.rerun()

        with tabs[1]:
            for s, t, r, d in cur.execute("SELECT * FROM snitch_reports").fetchall():
                st.error(f"[{d}] {s} -> {t}: {r}")

        with tabs[2]:
            nt = st.slider("НАЛОГ (%)", 0, 100, int(tax_n))
            nm = st.text_input("ПРИКАЗ", msg_n)
            nr = st.checkbox("РЕГИСТРАЦИЯ", value=bool(reg_n))
            if st.button("СОХРАНИТЬ"):
                cur.execute("UPDATE system_config SET tax=?, reg_open=?, msg=?", (nt, int(nr), nm))
                conn.commit(); st.rerun()

        with tabs[3]:
            st.subheader("СПИСОК ИЗГНАННЫХ")
            for bu in cur.execute("SELECT username FROM users WHERE status='banned'").fetchall():
                st.write(f"💀 {bu[0]}")

        time.sleep(2); st.rerun()
