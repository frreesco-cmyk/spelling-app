import streamlit as st
import sqlite3

# 1. СТИЛЬ
st.set_page_config(page_title="GOD_MODE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;padding:5px;background:#111;}</style>", unsafe_allow_html=True)

# 2. БАЗА
conn = sqlite3.connect('v79_final.db', check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, r TEXT DEFAULT 'w', s TEXT DEFAULT 'a', m TEXT DEFAULT 'ЖДИТЕ ПРИКАЗА')")
conn.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not conn.execute("SELECT t FROM news WHERE id=1").fetchone():
    conn.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА ОНЛАЙН')")
conn.commit()

# 3. ЛОГИКА
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("📟 АВТОРИЗАЦИЯ")
    l = st.text_input("ID (Логин)")
    p = st.text_input("KEY (Пароль)", type="password")
    c1, c2 = st.columns(2)
    if c1.button("LOG (ВХОД)"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = conn.execute("SELECT s FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res and res[0] != 'banned':
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ОТКАЗАНО / БАН")
    if c2.button("REG (РЕГИСТРАЦИЯ)"):
        try:
            conn.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            conn.commit(); st.success("ЮНИТ СОЗДАН")
        except: st.error("ЛОГИН ЗАНЯТ")
else:
    if st.sidebar.button("EXIT (ВЫХОД)"):
        st.session_state.auth = False; st.rerun()
    
    if st.session_state.role == "worker":
        st.title(f"UNIT: {st.session_state.user}")
        n = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info(f"📢 ОБЩЕЕ СООБЩЕНИЕ: {n}")
        d = conn.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        st.metric("ВАШ БАЛАНС", f"{d[0]} RUB")
        st.warning(f"📩 ВАШ ПРИКАЗ: {d[1]}")
    else:
        st.title("👑 ПАНЕЛЬ АДМИНИСТРАТОРА")
        gn = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        new_n = st.text_input("ОБЩЕЕ СООБЩЕНИЕ ДЛЯ ВСЕХ", value=gn)
        if st.button("ОБНОВИТЬ ОБЩЕЕ"):
            conn.execute("UPDATE news SET t=? WHERE id=1", (new_n,))
            conn.commit(); st.rerun()
        
        st.header("УПРАВЛЕНИЕ ЮНИТАМИ")
        rows = conn.execute("SELECT u, b, s, m FROM users WHERE r='w'").fetchall()
        if not rows: st.write("Воркеров пока нет. Зарегистрируй кого-нибудь.")
        for u, b, s, m in rows:
            with st.expander(f"ЮНИТ: {u} | Счёт: {b} | Статус: {s}"):
                nb = st.number_input(f"Сумма для {u}", value=float(b), key=f"b{u}")
                if st.button(f"СОХРАНИТЬ ДЕНЬГИ {u}", key=f"sb{u}"):
                    conn.execute("UPDATE users SET b=? WHERE u=?", (nb, u))
                    conn.commit(); st.rerun()
                nm = st.text_area(f"Приказ для {u}", value=m, key=f"m{u}")
                if st.button(f"ОТПРАВИТЬ ПРИКАЗ {u}", key=f"sm{u}"):
                    conn.execute("UPDATE users SET m=? WHERE u=?", (nm, u))
                    conn.commit(); st.rerun()
                c1, c2 = st.columns(2)
                if c1.button(f"БАН/РАЗБАН {u}", key=f"bn{u}"):
                    ns = 'banned' if s == 'active' else 'active'
                    conn.execute("UPDATE users SET s=? WHERE u=?", (ns, u))
                    conn.commit(); st.rerun()
                if c2.button(f"УДАЛИТЬ {u}", key=f"dl{u}"):
                    conn.execute("DELETE FROM users WHERE u=?", (u,))
                    conn.commit(); st.rerun()
