# pages/admin/admin_dashboard.py
import streamlit as st
from core.auth import get_current_user, logout_user

from . import manage_teachers  # admin pages
from . import manage_classes
from . import manage_students
from . import manage_subjects
from . import manage_subject_assignments
from . import manage_grading_scales
from . import manage_score_settings
from . import admin_conduct_interest
from . import manage_final_grading_scales


def admin_dashboard_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("You do not have permission to access this page.")
        return

    # -------------------------
    # Sidebar navigation
    # -------------------------
    sidebar_items = [
        "Dashboard",
        "Manage Teachers",
        "Manage Classes",
        "Manage Students",
        "Manage Subjects",
        "Subject Assignments",
        "Manage Grading Scales",
        "Manage Score Settings",
        "Conduct & Interest Settings",
        "Final Grading Scales",
        "Logout",  # Logout at the bottom
    ]

    page = st.sidebar.radio("Go to", sidebar_items, key="admin_sidebar")

    # -------------------------
    # Handle Logout
    # -------------------------
    if page == "Logout":
        logout_user()  # Clears Supabase session and Streamlit state
        st.rerun()  # Refresh app to login screen
        return

    # -------------------------
    # Dynamic page heading / page routing
    # -------------------------
    if page == "Dashboard":
        st.title("📊 Admin Dashboard")
        st.write(f"Welcome, {user['full_name']}!")
        st.write("Admin overview and stats here...")

    elif page == "Manage Teachers":
        manage_teachers.manage_teachers_page()
    elif page == "Manage Classes":
        manage_classes.manage_classes_page()
    elif page == "Manage Students":
        manage_students.manage_students_page()
    elif page == "Manage Subjects":
        manage_subjects.manage_subjects_page()
    elif page == "Subject Assignments":
        manage_subject_assignments.manage_subject_assignments_page()
    elif page == "Manage Grading Scales":
        manage_grading_scales.manage_grading_scales_page()
    elif page == "Manage Score Settings":
        manage_score_settings.manage_score_settings_page()
    elif page == "Conduct & Interest Settings":
        admin_conduct_interest.admin_conduct_interest_page()
    elif page == "Final Grading Scales":
        manage_final_grading_scales.manage_final_grading_scales_page()
