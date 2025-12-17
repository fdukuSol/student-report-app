import streamlit as st
from core.auth import get_current_user

from . import manage_teachers  # admin pages
from . import manage_classes

def admin_dashboard_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("You do not have permission to access this page.")
        return

    # Sidebar navigation for admin pages
    page = st.sidebar.radio("Go to", ["Dashboard", "Manage Teachers", "Manage Classes"])

    # Clear old contents (optional)

    # Dynamic page heading
    if page == "Dashboard":
        st.title("📊 Admin Dashboard")
        st.write(f"Welcome, {user['full_name']}!")
        st.write("Admin overview and stats here...")
    elif page == "Manage Teachers":
        #st.title("🧑‍🏫 Manage Teachers")
        manage_teachers.manage_teachers_page()
    elif page == "Manage Classes":
        #st.title("🏫 Manage Classes")
        manage_classes.manage_classes_page()
