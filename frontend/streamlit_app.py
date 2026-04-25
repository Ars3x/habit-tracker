import streamlit as st
import requests
from datetime import date

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Habit Tracker", page_icon="icon.png")
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
    
def api_request(method, endpoint, data=None):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
        
    url = f"{API_URL}{endpoint}"
  
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, json=data, headers=headers)

    return response

st.title(f"Habit Tracker")

if not st.session_state.token:
    tab1, tab2 = st.tabs(['Login', 'Register'])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            resp = requests.post(f"{API_URL}/auth/login", json={'email': email, 'password': password})
            if resp.status_code == 200:
                st.session_state.token = resp.json()['access_token']
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error('Invalid credentials')
    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register"):
            resp = requests.post(f"{API_URL}/auth/register", json={'email': email, 'password': password})
            if resp.status_code == 201:
                st.success('User created. Please login.')
            else:
                st.error(resp.json().get("detail", "Error"))
else:
    st.sidebar.write(f"Logged in as **{st.session_state.user_email}**")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user_email = None
        st.rerun
        
    habits_resp = api_request("GET", "/habits")
    if habits_resp.status_code == 200:
        habits = habits_resp.json()
        st.subheader('Your habits')
        if not habits:
            st.info("No habits yet. Create one below.")
        else:
            for habit in habits:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"***{habit['name']}***")
                    if habit.get('description'):
                        st.caption(habit.get('description'))
                    st.caption(f"Reminder: {habit.get('reminder_time', 'not set')} | Days: {habit.get('days_of_week', 'daily')}")
                with col2:
                    if st.button(f"✅ Complete", key=f"complete_{habit['id']}"):
                        complete_resp = api_request("POST", f"/habits/{habit['id']}/complete")
                        if complete_resp.status_code == 200:
                            st.success(complete_resp.json()["msg"])
                            st.rerun()
                        else:
                            st.error("Error completing habit")
                with col3:
                    st.caption(f"ID: {habit['id']}")
        st.divider()
        
        st.subheader("Your progress")
        st.metric("Points", "0")
        st.metric("Level", "1")
    else:
        st.error("Could not load habits")
    
    
    st.subheader("Create new habit")
    with st.form("new_habit"):
        name = st.text_input("Name")
        description = st.text_area("Description", height=68)
        reminder_time = st.time_input("Reminder time", value=None)
        days_of_week = st.text_input("Days of week (comma separated, e.g. mon,wed,fri)", placeholder="daily if empty")
        submitted = st.form_submit_button("Create")
        if submitted and name:
            data = {
                "name": name,
                "description": description if description else None,
                "reminder_time": reminder_time.strftime("%H:%M:%S") if reminder_time else None,
                "days_of_week": days_of_week if days_of_week else None
            }
            resp = api_request("POST", "/habits", data=data)
            if resp.status_code == 201:
                st.success("Habit created!")
                st.rerun()
            else:
                st.error("Failed to create habit")