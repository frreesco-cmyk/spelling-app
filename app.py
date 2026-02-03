import streamlit as st
import sqlite3

# --- 1. ЧИСТАЯ НАСТРОЙКА ---
st.set_page_config(page_title="GOD_MODE", layout="wide")

# Стили (Зеленый на черном)
st.markdown("""
<style>
    .stApp {background-color: #000; color: #0f0;}
    section[data-testid="stSidebar"] {background-color: #111;}
    .stMetric {background-color: #111; border: 1px solid #0f0; padding: 10px;}
    button {border: 1px solid #0f0 !important; color: #0f0 !important;}
</style>
""", unsafe_allow_html=True)

# --- 2. БАЗА (БЕЗ ВЫЛЕТОВ) ---
def init_db():
    conn = sqlite3.connect('final_v75.db', check_same_thread=False)
    # Создаем таблицы
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT 'worker', status TEXT DEFAULT 'active', message TEXT DEFAULT 'НЕТ ПРИКАЗОВ')")
    conn.execute("CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)")
    # Проверка новостей
    check = conn.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()
    if not check:
        conn.execute("INSERT INTO global_cfg (id, news) VALUES (1, 'СИСТЕМА АКТИВИРОВАНА')")
    conn.commit()
    return conn

db = init_db()

# --- 3. ЛОГИКА ВХОДА ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("📟 ВХОД В ТЕРМИНАЛ")
    u = st.text_input("USER ID").strip()
    p = st.text_input("PASSWORD", type="password").strip()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("UPLINK (ВХОД)"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
                st.rerun()
            else:
                user_data = db.execute("SELECT status, role FROM users WHERE username=? AND password=?", (u, p)).fetchone()
                if user_data:
                    if user_data[0] != 'banned':
                        st.session_state.update({"auth":True, "user":u, "role":"worker"})
                        st.rerun()
                    else: st.error("TERMINATED (БАН)")
                else: st.error("ACCESS DENIED")
    with c2:
        if st.button("CREATE (РЕГ)"):
            if u and p:
                try:
                    db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
                    db.commit()
                    st.success("SUCCESS")
                except: st.error("ID EXISTS")

# --- 4. РАБОЧАЯ ЗОНА ---
else:
    user = st.session_state.user
    role = st.session_state.role
    
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False
        st.rerun()

    # --- ИНТЕРФЕЙС ВОРКЕРА ---
    if role == "worker":
        st.title(f"UNIT: {user}")
        
        # Глобальное сообщение
        gn = db.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()
        st.info(f"📢 ГЛОБАЛЬНО: {gn[0] if gn else '---'}")
        
        # Данные юзера
        ud = db.execute("SELECT balance, message FROM users WHERE username=?", (user,)).fetchone()
        if ud:
            st.metric("ВАШ СЧЕТ", f"{ud[0]} RUB")
            st.warning(f"📩 ПРИКАЗ: {ud[1]}")
        else:
            st.error("ОШИБКА ДАННЫХ")

    # --- ИНТЕРФЕЙС АДМИНА ---
    else:
        st.title("👑 GOD CONTROL PANEL")
        
        # Общая новость
        current_g = db.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()
        new_g = st.text_input("ОБЩЕЕ ОБЪЯВЛЕНИЕ", value=current_g[0] if current_g else "")
        if st.button("ОБНОВИТЬ ДЛЯ ВСЕХ"):
            db.execute("UPDATE global_cfg SET news=? WHERE id=1", (new_g,))
            db.commit()
            st.rerun()

        st.divider()
        st.subheader("СПИСОК ЮНИТОВ")
        
        # Список воркеров
        rows = db.execute("SELECT username, balance, status, message FROM users WHERE role='worker'").fetchall()
        
        if not rows:
            st.write("НЕТ ЗАРЕГИСТРИРОВАННЫХ ЮНИТОВ")
        
        for un, ub, us, um in rows:
            with st.expander(f"👤 {un} | {ub} руб | {us}"):
                # Баланс
                nb = st.number_input(f"Сумма для {un}", value=float(ub), key=f"b{un}")
                if st.button(f"ИЗМЕНИТЬ БАЛАНС {un}", key=f"btnb{un}"):
                    db.execute("UPDATE users SET balance=? WHERE username=?", (nb, un))
                    db.commit()
                    st.rerun()
                
                # Сообщение
                nm = st.text_area(f"Приказ для {un}", value=um, key=f"m{un}")
                if st.button(f"ОТПРАВИТЬ ПРИКАЗ {un}", key=f"btnm{un}"):
                    db.execute("UPDATE users SET message=? WHERE username=?", (nm, un))
                    db.commit()
                    st.rerun()

                # Управление
                c1, c2 = st.columns(2)
                with c1:
                    status_text = "РАЗБАНИТЬ" if us == 'banned' else "ЗАБАНИТЬ"
                    if st.button(f"{status_text} {un}", key=f"s{un}"):
                        new_s = 'active' if us == 'banned' else 'banned'
                        db.execute("UPDATE users SET status=? WHERE username=?", (new_s, un))
                        db.commit()
                        st.rerun()
                with c2:
                    if st.button(f"УДАЛИТЬ {un}", key=f"d{un}"):
                        db.execute("DELETE FROM users WHERE username=?", (un,))
                        db.commit()
                        st.rerun()
