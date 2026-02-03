import streamlit as st
import sqlite3

# --- КОНФИГУРАЦИЯ И СТИЛЬ ---
st.set_page_config(page_title="SYSTEM CONTROL", layout="wide")
st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00FF00;}
    .stButton>button {border: 2px solid #00FF00; background-color: transparent; color: #00FF00; width: 100%;}
    .stTextInput>div>div>input {background-color: #111; color: #00FF00; border: 1px solid #00FF00;}
    .stMetric {background-color: #111; border: 1px solid #00FF00; padding: 15px; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('main_system.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, message TEXT DEFAULT 'НЕТ ЗАДАНИЙ')")
cursor.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, news TEXT)")
if not cursor.execute("SELECT news FROM settings WHERE id=1").fetchone():
    cursor.execute("INSERT INTO settings (id, news) VALUES (1, 'СИСТЕМА АКТИВИРОВАНА')")
conn.commit()

# --- СИСТЕМА ВХОДА ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("📟 ТЕРМИНАЛ ДОСТУПА")
    user_id = st.text_input("ИДЕНТИФИКАТОР").strip()
    user_key = st.text_input("КЛЮЧ ДОСТУПА", type="password").strip()
    
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button("ВХОД В СИСТЕМУ"):
            if user_id == "admin" and user_key == "admin777":
                st.session_state.update({"logged_in": True, "user": "admin", "role": "admin"})
                st.rerun()
            else:
                res = cursor.execute("SELECT username FROM users WHERE username=? AND password=?", (user_id, user_key)).fetchone()
                if res:
                    st.session_state.update({"logged_in": True, "user": user_id, "role": "worker"})
                    st.rerun()
                else:
                    st.error("ОШИБКА: ДОСТУП ЗАПРЕЩЕН")
    with col_r:
        if st.button("РЕГИСТРАЦИЯ НОВОГО ЮНИТА"):
            if user_id and user_key:
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user_id, user_key))
                    conn.commit()
                    st.success("ЮНИТ ЗАРЕГИСТРИРОВАН")
                except:
                    st.error("ОШИБКА: ИМЯ ЗАНЯТО")

# --- ИНТЕРФЕЙС ПОСЛЕ ВХОДА ---
else:
    if st.sidebar.button("ЗАВЕРШИТЬ СЕАНС"):
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.role == "worker":
        # --- ПАНЕЛЬ ВОРКЕРА ---
        st.title(f"👤 ЮНИТ: {st.session_state.user}")
        global_news = cursor.execute("SELECT news FROM settings WHERE id=1").fetchone()[0]
        st.info(f"📢 ОБЩЕЕ УВЕДОМЛЕНИЕ: {global_news}")
        
        data = cursor.execute("SELECT balance, message FROM users WHERE username=?", (st.session_state.user,)).fetchone()
        st.metric("ТЕКУЩИЙ БАЛАНС", f"{data[0]} RUB")
        st.warning(f"📝 ТЕКУЩЕЕ ЗАДАНИЕ: {data[1]}")

    else:
        # --- ПАНЕЛЬ АДМИНИСТРАТОРА ---
        st.title("👑 ГЛАВНЫЙ УЗЕЛ УПРАВЛЕНИЯ")
        
        # Глобальное сообщение
        current_news = cursor.execute("SELECT news FROM settings WHERE id=1").fetchone()[0]
        new_news = st.text_input("ОБНОВИТЬ ОБЩЕЕ СООБЩЕНИЕ", value=current_news)
        if st.button("РАЗОСЛАТЬ ВСЕМ"):
            cursor.execute("UPDATE settings SET news=? WHERE id=1", (new_news,))
            conn.commit()
            st.rerun()
        
        st.markdown("---")
        st.subheader("УПРАВЛЕНИЕ ПЕРСОНАЛОМ")
        
        all_workers = cursor.execute("SELECT username, balance, message FROM users").fetchall()
        
        if not all_workers:
            st.write("СПИСОК ЮНИТОВ ПУСТ")
            
        for name, balance, message in all_workers:
            with st.expander(f"⚙️ УПРАВЛЕНИЕ: {name} | БАЛАНС: {balance} RUB"):
                # Изменение баланса
                new_balance = st.number_input(f"Изменить баланс для {name}", value=float(balance), key=f"bal_{name}")
                if st.button(f"ОБНОВИТЬ СЧЕТ {name}", key=f"btn_bal_{name}"):
                    cursor.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, name))
                    conn.commit()
                    st.rerun()
                
                # Изменение задания
