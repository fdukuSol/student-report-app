# pages/teacher/teacher_dashboard.py
import streamlit as st
from core.auth import get_current_user, logout_user
from . import teacher_score_entry
from . import teacher_conduct_interest
from . import student_results_viewer

# from . import teacher_subject_order
from core.db_teachers import get_teachers
from core.db_classes import get_classes


def teacher_dashboard_page():
    # -------------------------
    # Current user
    # -------------------------
    user = get_current_user()
    if not user or user.get("role") != "teacher":
        st.warning("You do not have permission to access this page.")
        return

    # -------------------------
    # Fetch teacher profile from public.profiles
    # -------------------------
    teachers = get_teachers()
    teacher_profile = next(
        (t for t in teachers if t.get("auth_user_id") == user.get("auth_user_id")),
        None,
    )

    if not teacher_profile:
        st.error("Teacher profile not found.")
        return

    assigned_class_names = teacher_profile.get("assigned_classes", [])
    classes = [c for c in get_classes() if c["class_name"] in assigned_class_names]

    if not classes:
        st.info("No classes assigned.")
        return

    class_map = {c["class_name"]: c for c in classes}

    # -------------------------
    # Sidebar navigation
    # -------------------------
    sidebar_items = ["Dashboard"]
    for cls in classes:
        sidebar_items.append(f"Enter Scores - {cls['class_name']}")
        sidebar_items.append(f"Enter Conduct/Interest - {cls['class_name']}")
        sidebar_items.append(f"View Student Results - {cls['class_name']}")
    sidebar_items.append("Logout")  # Logout at the bottom

    # Display sidebar and get selection
    page = st.sidebar.radio("Go to", sidebar_items, key="teacher_sidebar")

    # -------------------------
    # Handle Logout
    # -------------------------
    if page == "Logout":
        logout_user()  # Clear session and logout from Supabase
        st.rerun()  # Refresh to login screen
        return

    # -------------------------
    # Dashboard landing
    # -------------------------
    if page == "Dashboard":
        st.title("📘 Teacher Dashboard")
        st.write(f"Welcome, {teacher_profile.get('full_name', 'Teacher')}!")
        st.write("Select a class from the sidebar to manage subjects or enter scores.")

    # -------------------------
    # Score Entry pages
    # -------------------------
    elif page.startswith("Enter Scores"):
        class_name = page.replace("Enter Scores - ", "")
        cls = class_map[class_name]
        st.session_state.update(
            {"class_id": cls["id"], "class_name": cls["class_name"]}
        )
        teacher_score_entry.enter_student_scores_page()
    
    # -------------------------
    # Conduct / Interest / Attendance entry
    # -------------------------
    elif page.startswith("Enter Conduct/Interest"):
        class_name = page.replace("Enter Conduct/Interest - ", "")
        cls = class_map[class_name]
        st.session_state.update(
            {"class_id": cls["id"], "class_name": cls["class_name"]}
        )
        teacher_conduct_interest.teacher_conduct_interest_page()
        
    # -------------------------
    # Student Results Viewer
    # -------------------------
    elif page.startswith("View Student Results"):
        class_name = page.replace("View Student Results - ", "")
        cls = class_map[class_name]
        st.session_state.update(
            {"class_id": cls["id"], "class_name": cls["class_name"]}
        )
        student_results_viewer.student_results_viewer_page()
