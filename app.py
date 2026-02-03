import streamlit as st
import sqlite3
import time
from datetime import datetime

# 1. СТИЛЬ И КОНФИГ
st.set_page_config(page_title="CORE ULTIMATE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# 2. БАЗА ДАННЫХ
db = sqlite3.connect('ultra_v3.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'НЕТ', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT)")
if not db.execute("SELECT news FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, news) VALUES (1, 'СИСТЕМА ONLINE')")
db.commit()

# 3. ФУНКЦИИ
def get_rank(xp_val):
    if xp_val < 100: return "РЕКРУТ", 0.1
    if xp_val < 500: return "БОЕЦ", 0.4
    if xp_val < 1500: return "ЭЛИТА", 0.7
    return "ЛЕГЕНДА", 1.0

# 4. ЛОГИКА СЕССИИ
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False
if 'stime' not in st.session_state: st.session_state.stime = 0

# --- ВХОД ---
if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l, p = st.text_input("ID").strip(), st.text_input("KEY", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u, status FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res and res[1] != 'banned':
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ОТКАЗАНО / БАН")
    if c2.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("ЗАНЯТО")

else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()

    # --- ИНТЕРФЕЙС ВОРКЕРА ---
    if st.session_state.role == "worker":
        st.title("👤 UNIT: " + str(st.session_state.user))
        gn = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info("📢 GLOBAL: " + str(gn))
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        rank_name, prog = get_rank(ud[1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CASH", str(ud[0]) + " RUB")
        c2.metric("XP", str(ud[1]))
        c3.metric("RANK", rank_name)
        st.progress(prog)

        st.divider()
        st.subheader("⏱ СМЕНА")
        if not st.session_state.shift:
            if st.button("▶️ ЗАПУСТИТЬ ТАЙМЕР"):
                st.session_state.shift = True
                st.session_state.stime = time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.stime)
            st.write("⏳ ВРЕМЯ В РАБОТЕ: " + str(el) + " сек.")
            if st.button("🛑 ЗАВЕРШИТЬ СМЕНУ"):
                nxp = max(1, el // 10)
                db.execute("UPDATE users SET xp=xp+? WHERE u=?", (nxp, st.session_state.user))
                db.commit()
                st.session_state.shift = False
                st.success("ПОЛУЧЕНО: " + str(nxp) + " XP")
                time.sleep(1); st.rerun()
            time.sleep(1); st.rerun() # Авто-обновление таймера
        
        st.warning("📩 ПРИКАЗ: " + str(ud[2]))
        
        st.divider()
        st.subheader("💬 ЧАТ С АДМИНОМ")
        m_txt = st.text_input("Ваше сообщение")
        if st.button("ОТПРАВИТЬ"):
            db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", (st.session_state.user, m_txt, datetime.now().strftime("%H:%M")))
            db.commit(); st.rerun()
        
        for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 5").fetchall():
            st.text("[" + cd + "] " + cu + ": " + cm)

    # --- ИНТЕРФЕЙС АДМИНА ---
    else:
        st.title("👑 SUPREME ADMIN")
        t1, t2 = st.tabs(["УПРАВЛЕНИЕ", "ЧАТ"])
        
        with t1:
            nn = st.text_input("ОБЩАЯ НОВОСТЬ")
            if st.button("ОБНОВИТЬ НОВОСТЬ"):
                db.execute("UPDATE config SET news=? WHERE id=1", (nn,))
                db.commit(); st.rerun()
            
            for u, b, xp, m, stat, p in db.execute("SELECT u, b, xp, m, status, p FROM users").fetchall():
                with st.expander("UNIT: " + str(u) + " [" + stat + "]"):
                    nb = st.number_input("CASH", value=float(b), key="b"+u)
                    nx = st.number_input("XP", value=int(xp), key="x"+u)
                    np = st.text_input("PASS", value=str(p), key="p"+u)
                    nm = st.text_area("TASK", value=str(m), key="m"+u)
                    if st.button("SAVE DATA", key="s"+u):
                        db.execute("UPDATE users SET b=?, xp=?, m=?, p=? WHERE u=?", (nb, nx, nm, np, u))
                        db.commit(); st.rerun()
                    if st.button("BAN/UNBAN", key="bn"+u):
                        ns = 'banned' if stat == 'active' else 'active'
                        db.execute("UPDATE users SET status=? WHERE u=?", (ns, u))
                        db.commit(); st.rerun()
                    if st.button("DELETE USER", key="del"+u):
                        db.execute("DELETE FROM users WHERE u=?", (u,))
                        db.commit(); st.rerun()
        
        with t2:
            st.subheader("ОБЩИЙ ЧАТ")
            adm_m = st.text_input("Ответ в чат")
            if st.button("ОТПРАВИТЬ ВСЕМ"):
                db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", ("ADMIN", adm_m, datetime.now().strftime("%H:%M")))
                db.commit(); st.rerun()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 20").fetchall():
                st.text("[" + cd + "] " + cu + ": " + cm)
