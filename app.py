import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- СТИЛЬ ТОП-ТИМЫ ---
st.set_page_config(page_title="SYNDICATE HQ", layout="wide")
st.markdown("<style>.stApp{background:#050505;color:#0f0;font-family:monospace;} .stMetric{background:#111;border:1px solid #0f0;padding:15px;}</style>", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ ---
db = sqlite3.connect('syndicate_final.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'НЕТ ЗАДАЧИ', s TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT DEFAULT 'СИСТЕМА СТАБИЛЬНА')")
if not db.execute("SELECT id FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, news) VALUES (1, 'ДОБРО ПОЖАЛОВАТЬ')")
db.commit()

# --- ЛОГИКА РАНГОВ ---
def get_rank_info(xp):
    if xp < 500: return "🌑 РЕКРУТ", 0.2
    if xp < 2000: return "⚔️ ОПЕРАТИВНИК", 0.5
    if xp < 5000: return "💎 ЭЛИТА", 0.8
    return "🔥 ЛЕГЕНДА", 1.0

# --- СЕССИЯ ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

# --- АВТОРИЗАЦИЯ ---
if not st.session_state.auth:
    st.title("📟 ACCESS TERMINAL")
    l, p = st.text_input("ID").strip(), st.text_input("PASSWORD", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        res = db.execute("SELECT u, s FROM users WHERE u=? AND p=?", (l, p)).fetchone()
        if res and res[1] == 'active':
            st.session_state.update({"auth":True, "role":"worker", "user":l})
            st.rerun()
        else: st.error("ОТКАЗАНО / БАН")
    if c2.button("JOIN TEAM"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("ЮНИТ ЗАРЕГИСТРИРОВАН")
            except: st.error("ID ЗАНЯТ")
else:
    # --- ВОРКЕР ---
    if st.session_state.role == "worker":
        st.title("👤 UNIT: " + str(st.session_state.user))
        news = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info("📢 GLOBAL: " + str(news))
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        rn, pr = get_rank_info(ud[1])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("БАЛАНС", str(ud[0]) + " RUB")
        col2.metric("ОПЫТ (XP)", str(ud[1]))
        col3.metric("РАНГ", rn)
        st.progress(pr)

        st.divider()
        st.subheader("⏱ СМЕНА")
        if not st.session_state.shift:
            if st.button("▶️ НАЧАТЬ РАБОТУ"):
                st.session_state.shift, st.session_state.st = True, time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.st)
            st.error("⏳ В РАБОТЕ: " + str(el) + " сек.")
            if st.button("🛑 ЗАКОНЧИТЬ СМЕНУ"):
                gain = max(10, el // 3)
                db.execute("UPDATE users SET xp=xp+? WHERE u=?", (gain, st.session_state.user))
                db.commit(); st.session_state.shift = False
                st.success("ПОЛУЧЕНО: " + str(gain) + " XP")
                time.sleep(1); st.rerun()
            time.sleep(1); st.rerun()

        st.warning("📩 ЗАДАЧА: " + str(ud[2]))
        
        with st.expander("💬 ЧАТ С АДМИНОМ"):
            m_in = st.text_input("Сообщение")
            if st.button("ОТПРАВИТЬ"):
                db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", (st.session_state.user, m_in, datetime.now().strftime("%H:%M")))
                db.commit(); st.rerun()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 5").fetchall():
                st.text("[" + str(cd) + "] " + str(cu) + ": " + str(cm))

    # --- АДМИН ---
    else:
        st.title("👑 SUPREME COMMANDER")
        t1, t2, t3 = st.tabs(["ЮНИТЫ", "СИСТЕМА", "ТОП"])
        with t1:
            for u, b, x, m, s, p in db.execute("SELECT * FROM users").fetchall():
                with st.expander("UNIT: " + str(u) + " | XP: " + str(x)):
                    nb = st.number_input("БАЛАНС", value=float(b), key="b"+u)
                    nx = st.number_input("XP", value=int(x), key="x"+u)
                    nm = st.text_area("ЗАДАЧА", value=str(m), key="m"+u)
                    np = st.text_input("ПАРОЛЬ", value=str(p), key="p"+u)
                    c1, c2, c3 = st.columns(3)
                    if c1.button("SAVE", key="s"+u):
                        db.execute("UPDATE users SET b=?, xp=?, m=?, p=? WHERE u=?", (nb, nx, nm, np, u))
                        db.commit(); st.rerun()
                    if c2.button("BAN/UNBAN", key="bn"+u):
                        ns = 'banned' if s == 'active' else 'active'
                        db.execute("UPDATE users SET s=? WHERE u=?", (ns, u))
                        db.commit(); st.rerun()
                    if c3.button("DELETE", key="d"+u):
                        db.execute("DELETE FROM users WHERE u=?", (u,))
                        db.commit(); st.rerun()
        with t2:
            nn = st.text_input("НОВАЯ ОБЩАЯ НОВОСТЬ")
            if st.button("ОБНОВИТЬ"):
                db.execute("UPDATE config SET news=? WHERE id=1", (nn,))
                db.commit(); st.rerun()
            st.divider()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 20").fetchall():
                st.text("[" + str(cd) + "] " + str(cu) + ": " + str(cm))
        with t3:
            st.subheader("ТОП ВОРКЕРОВ")
            for i, (tu, tx) in enumerate(db.execute("SELECT u,
