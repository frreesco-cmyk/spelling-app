import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- 1. НАСТРОЙКИ СИСТЕМЫ ---
st.set_page_config(page_title="SYSTEM CORE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# --- 2. БАЗА ДАННЫХ ---
db = sqlite3.connect('final_ultra_v1.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, r TEXT DEFAULT 'РЕКРУТ', m TEXT DEFAULT 'НЕТ', t TEXT DEFAULT '00:00:00', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT)")
if not db.execute("SELECT news FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, news) VALUES (1, 'СИСТЕМА АКТИВИРОВАНА')")
db.commit()

# --- Вспомогательные функции ---
def add_log(text):
    now = datetime.now().strftime("%H:%M:%S")
    db.execute("INSERT INTO logs (msg, dt) VALUES (?, ?)", (text, now))
    db.commit()

def get_rank(xp):
    if xp < 100: return "РЕКРУТ", 0.1
    if xp < 500: return "БОЕЦ", 0.4
    if xp < 1500: return "ЭЛИТА", 0.7
    return "ЛЕГЕНДА", 1.0

# --- 3. АВТОРИЗАЦИЯ ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("📟 ВХОД В СИСТЕМУ")
    l = st.text_input("ID ЮНИТА").strip()
    p = st.text_input("КЛЮЧ", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            add_log("АДМИН ВОШЕЛ В СИСТЕМУ")
            st.rerun()
        else:
            res = db.execute("SELECT u, status FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                if res[1] == 'banned': st.error("ВАШ АККАУНТ ЗАБЛОКИРОВАН")
                else:
                    st.session_state.update({"auth":True, "user":l, "role":"worker"})
                    add_log(f"ЮНИТ {l} ВОШЕЛ В СЕТЬ")
                    st.rerun()
            else: st.error("ОТКАЗАНО")
    if c2.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); add_log(f"НОВЫЙ ЮНИТ {l} ЗАРЕГИСТРИРОВАН")
            st.success("OK")
        except: st.error("ЗАНЯТО")

# --- 4. РАБОЧАЯ ЗОНА ---
else:
    if st.sidebar.button("ВЫХОД"):
        add_log(f"{st.session_state.user} ВЫШЕЛ")
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        # --- ИНТЕРФЕЙС ВОРКЕРА ---
        st.title(f"🛠 ТЕРМИНАЛ ЮНИТА: {st.session_state.user}")
        gn = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info(f"📢 ГЛОБАЛЬНЫЙ ПРИКАЗ: {gn}")
        
        ud = db.execute("SELECT b, xp, m, t, r FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        cur_rank, progress = get_rank(ud[1])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("БАЛАНС", f"{ud[0]} RUB")
        col2.metric("ОПЫТ (XP)", f"{ud[1]}")
        col3.metric("ТАЙМЕР СМЕНЫ", ud[3])
        
        st.write(f"**РАНГ: {cur_rank}**")
        st.progress(progress)
        
        st.warning(f"📩 ЗАДАНИЕ: {ud[2]}")
        
        st.divider()
        st.subheader("💬 ЧАТ С АДМИНОМ")
        msg = st.text_input("Написать админу...")
        if st.button("ОТПРАВИТЬ"):
            if msg:
                db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", (st.session_state.user, msg, datetime.now().strftime("%H:%M")))
                db.commit(); st.rerun()
        
        messages = db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 5").fetchall()
        for mu, mm, md in messages:
            st.text(f"[{md}] {mu}: {mm}")

    else:
        # --- ИНТЕРФЕЙС АДМИНА ---
        st.title("👑 ПАНЕЛЬ БОГА")
        tab1, tab2, tab3 = st.tabs(["ЮНИТЫ", "ЛОГИ", "ЧАТ"])
        
        with tab1:
            gn = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
            new_gn = st.text_input("ОБЩЕЕ СООБЩЕНИЕ", value=gn)
            if st.button("ОБНОВИТЬ ДЛЯ ВСЕХ"):
                db.execute("UPDATE config SET news=? WHERE id=1", (new_gn,))
                db.commit(); add_log("НОВОСТЬ ОБНОВЛЕНА"); st.rerun()
            
            rows = db.execute("SELECT u, b, xp, m, t, status, p FROM users").fetchall()
            for u, b, xp, m, t, stat, pwd in rows:
                with st.expander(f"👤 {u} | {b} RUB | {stat}"):
                    c1, c2, c3 = st.columns(3)
                    new_b = c1.number_input(f"Баланс", value=float(b), key="b"+u)
                    new_xp = c2.number_input(f"XP", value=int(xp), key="xp"+u)
                    new_p = c3.text_input(f"Сменить пароль", value=pwd, key="p"+u)
                    
                    new_t = st.text_input("Таймер", value=t, key="t"+u)
                    new_m = st.text_area("Приказ", value=m, key="m"+u)
                    
                    cc1, cc2, cc3, cc4 = st.columns(4)
                    if cc1.button("СОХРАНИТЬ", key="s"+u):
                        db.execute("UPDATE users SET b=?, xp=?, m=?, t=?, p=? WHERE u=?", (new_b, new_xp, new_m, new_t, new_p, u))
                        db.commit(); add_log(f"АДМИН ИЗМЕНИЛ ЮНИТА {u}"); st.rerun()
                    if cc2.button("BAN/UNBAN", key="bn"+u):
                        ns = 'banned' if stat == 'active' else 'active'
                        db.execute("UPDATE users SET status=? WHERE u=?", (ns, u))
                        db.commit(); add_log(f"СТАТУС {u} ИЗМЕНЕН НА {ns}"); st.rerun()
                    if cc3.button("СБРОС XP", key="rx"+u):
                        db.execute("UPDATE users SET xp=0 WHERE u=?", (u,))
                        db.commit(); st.rerun()
                    if cc4.button("УДАЛИТЬ", key="del"+u):
                        db.execute("DELETE FROM users WHERE u=?", (u,))
                        db.commit(); add_log(f"ЮНИТ {u} УДАЛЕН"); st.rerun()

        with tab2:
            st.subheader("📋 ЖУРНАЛ СОБЫТИЙ")
            logs = db.execute("SELECT dt, msg FROM logs ORDER BY id DESC LIMIT 50").fetchall()
            for ld, lm in logs:
                st.text(f"[{ld}] {lm}")

        with tab3:
            st.subheader("💬 ПЕРЕПИСКА")
            admin_msg = st.text_input("Ответить всем...")
            if st.button("ОТПРАВИТЬ В ЧАТ"):
                db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", ("ADMIN", admin_msg, datetime.now().strftime("%H:%M")))
                db.commit(); st.rerun()
            
            msgs = db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 20").fetchall()
            for mu, mm, md in msgs:
                st.text(f"[{md}] {mu}: {mm}")
