import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time
import random

# --- SETTINGS ---
st.set_page_config(page_title="OVERSEER v50", page_icon="🧿", layout="wide")

# --- DATABASE ---
conn = sqlite3.connect('v50_overseer.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                is_working INTEGER DEFAULT 0, last_act TEXT, xp INTEGER DEFAULT 0, last_bonus TEXT)''')
cur.execute('CREATE TABLE IF NOT EXISTS vault (total_tax REAL DEFAULT 0)')
cur.execute('CREATE TABLE IF NOT EXISTS global_config (tax_rate REAL DEFAULT 15, announcement TEXT)')
if not cur.execute('SELECT * FROM vault').fetchone(): cur.execute('INSERT INTO vault VALUES (0)')
if not cur.execute('SELECT * FROM global_config').fetchone(): cur.execute('INSERT INTO global_config VALUES (15, "ДОБРО ПОЖАЛОВАТЬ В ИМПЕРИЮ")')
conn.commit()

# --- NEON DESIGN ---
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&display=swap');
    .stApp { background: #08080a; color: #fff; }
    .stMetric { background: rgba(0, 255, 255, 0.05); border: 1px solid #00ffff33; border-radius: 10px; }
    h1 { font-family: 'Syncopate'; color: #00ffff; text-shadow: 0 0 10px #00ffff; text-align: center; }
    .stButton>button { border-radius: 5px; border: 1px solid #00ffff; background: transparent; color: #00ffff; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background: #00ffff; color: #000; box-shadow: 0 0 20px #00ffff; }
    .rank-card { padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; border: 1px solid #333; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- AUTH ---
if not st.session_state.auth:
    st.title("🧿 OVERSEER CORE")
    u = st.text_input("IDENTIFIER")
    p = st.text_input("ACCESS KEY", type='password')
    if st.button("CONNECT"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True, "user":u, "role":res[0]})
                st.rerun()
            else: st.error("ACCESS DENIED")
    if st.button("CREATE NEW UNIT"):
        try:
            cur.execute('INSERT INTO users(username,password,last_act) VALUES (?,?,?)',(u,p,datetime.now().strftime("%H:%M:%S")))
            conn.commit(); st.success("REGISTERED")
        except: st.error("ID TAKEN")

else:
    user, role = st.session_state.user, st.session_state.role
    # Update activity
    cur.execute("UPDATE users SET last_act=? WHERE username=?", (datetime.now().strftime("%H:%M:%S"), user))
    conn.commit()

    # Admin Announcement
    ann = cur.execute("SELECT announcement FROM global_config").fetchone()[0]
    st.info(f"📡 СВЯЗЬ: {ann}")

    st.sidebar.title(f"USER: {user}")
    if st.sidebar.button("LOGOUT"):
        cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
        conn.commit(); st.session_state.auth = False; st.rerun()

    # --- WORKER ---
    if role != "admin":
        st.title(f"⚡ ТЕРМИНАЛ ЮНИТА")
        u_data = cur.execute("SELECT balance, xp, last_bonus FROM users WHERE username=?",(user,)).fetchone()
        bal, xp, l_bonus = u_data
        
        # Ранги
        rank = "НОВИЧОК" if xp < 100 else "СПЕЦИАЛИСТ" if xp < 500 else "МАСТЕР" if xp < 1500 else "АРХИТЕКТОР"
        color = "#aaa" if xp < 100 else "#00ff00" if xp < 500 else "#00ffff" if xp < 1500 else "#ffd700"

        st.markdown(f'<div class="rank-card" style="color:{color}; border-color:{color}">РАНГ: {rank} (XP: {xp})</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.metric("💰 БАЛАНС", f"{round(bal, 2)} ₽")
        c2.metric("📈 ДОХОД", "150 ₽ / мин")

        t1, t2 = st.tabs(["⚒️ ДОБЫЧА", "🎁 БОНУСЫ"])
        
        with t1:
            if 'work' not in st.session_state: st.session_state.work = False
            if not st.session_state.work:
                if st.button("▶ ЗАПУСТИТЬ ПРОЦЕСС"):
                    st.session_state.start = datetime.now()
                    st.session_state.work = True
                    cur.execute("UPDATE users SET is_working=1 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
            else:
                diff = datetime.now() - st.session_state.start
                st.warning(f"⛏ В ПРОЦЕССЕ: {str(diff).split('.')[0]}")
                tax = cur.execute("SELECT tax_rate FROM global_config").fetchone()[0]
                gain = 2.5
                tax_val = gain * (tax/100)
                cur.execute("UPDATE users SET balance = balance + ?, xp = xp + 1 WHERE username=?", (gain - tax_val, user))
                cur.execute("UPDATE vault SET total_tax = total_tax + ?", (tax_val,))
                conn.commit()
                if st.button("⏹ ОСТАНОВИТЬ"):
                    st.session_state.work = False
                    cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
                time.sleep(1); st.rerun()
        
        with t2:
            st.subheader("ЕЖЕДНЕВНЫЙ ПОДАРОК")
            today = datetime.now().strftime("%Y-%m-%d")
            if l_bonus != today:
                if st.button("🎁 ПОЛУЧИТЬ БОНУС"):
                    gift = random.randint(50, 500)
                    cur.execute("UPDATE users SET balance = balance + ?, last_bonus=? WHERE username=?", (gift, today, user))
                    conn.commit(); st.success(f"Вы получили {gift} ₽!"); time.sleep(1); st.rerun()
            else:
                st.info("Бонус уже получен. Возвращайтесь завтра!")

    # --- ADMIN ---
    else:
        st.title("👑 ПУЛЬТ ВСЕВИДЯЩЕГО")
        v_cash = cur.execute("SELECT total_tax FROM vault").fetchone()[0]
        config = cur.execute("SELECT tax_rate, announcement FROM global_config").fetchone()
        workers = cur.execute("SELECT username, balance, status, is_working, last_act, xp FROM users WHERE role='worker'").fetchall()

        c1, c2, c3 = st.columns(3)
        c1.metric("🏦 МОЙ ПРОФИТ", f"{round(v_cash, 2)} ₽")
        c2.metric("⚙️ ТЕКУЩИЙ НАЛОГ", f"{config[0]}%")
        c3.metric("🟢 В СЕТИ", len([w for w in workers if w[3] == 1]))

        adm_t1, adm_t2 = st.tabs(["👁️ МОНИТОРИНГ", "🛠 ГЛОБАЛЬНО"])
        
        with adm_t1:
            for wn, wb, ws, is_w, last, wxp in workers:
                with st.expander(f"{'🟢' if is_w else '⚪'} {wn} | {round(wb, 1)} ₽ | XP: {wxp}"):
                    st.write(f"Last signal: {last} | Rank: {wxp}")
                    ca, cb, cc = st.columns(3)
                    if ca.button("🚫 BAN", key=f"b_{wn}"):
                        ns = "banned" if ws == "active" else "active"
                        cur.execute("UPDATE users SET status=?, is_working=0 WHERE username=?",(ns,wn))
                        conn.commit(); st.rerun()
                    if cb.button("💸 PAY", key=f"p_{wn}"):
                        cur.execute("UPDATE users SET balance=0 WHERE username=?",(wn,))
                        conn.commit(); st.rerun()
                    if cc.button("🎁 BONUS 500", key=f"g_{wn}"):
                        cur.execute("UPDATE users SET balance=balance+500 WHERE username=?",(wn,))
                        conn.commit(); st.rerun()

        with adm_t2:
            new_tax = st.slider("УСТАНОВИТЬ НАЛОГ (%)", 0, 100, int(config[0]))
            new_ann = st.text_input("ОБЪЯВЛЕНИЕ ДЛЯ ВСЕХ", config[1])
            if st.button("ОБНОВИТЬ СИСТЕМУ"):
                cur.execute("UPDATE global_config SET tax_rate=?, announcement=?", (new_tax, new_ann))
                conn.commit(); st.success("Данные обновлены")
        
        time.sleep(2); st.rerun()
