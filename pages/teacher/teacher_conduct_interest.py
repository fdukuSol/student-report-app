# pages/teacher/teacher_conduct_interest.py
import streamlit as st
from core.auth import get_current_user
from core.db_students import get_students
from core.db_admin_settings import get_all_conduct, get_all_interest
from core.db_conduct_interest import save_student_conduct_interest


def teacher_conduct_interest_page():
    # --------------------------------------------------
    # Auth guard
    # --------------------------------------------------
    user = get_current_user()
    if not user or user.get("role") != "teacher":
        st.warning("You do not have permission to access this page.")
        return

    # --------------------------------------------------
    # Class context (set by teacher_dashboard)
    # --------------------------------------------------
    class_id = st.session_state.get("class_id")
    class_name = st.session_state.get("class_name")

    if not class_name:
        st.error("Class context not found. Please select a class from the dashboard.")
        return

    st.subheader(f"Conduct, Interest & Attendance — {class_name}")

    # --------------------------------------------------
    # Term selection
    # --------------------------------------------------
    term = st.number_input(
        "Term",
        min_value=1,
        max_value=3,
        step=1,
        value=1,
    )

    # --------------------------------------------------
    # Load students (FILTER IN PYTHON — APP CONVENTION)
    # --------------------------------------------------
    all_students = get_students()
    students = [
        s for s in all_students
        if s.get("assigned_class") == class_name
    ]

    if not students:
        st.info("No students found in this class.")
        return

    # --------------------------------------------------
    # Load admin settings
    # --------------------------------------------------
    conducts = get_all_conduct()
    interests = get_all_interest()

    if not conducts or not interests:
        st.warning("Conduct or Interest settings have not been configured by admin.")
        return

    conduct_options = {c["conduct_name"]: c["id"] for c in conducts}
    interest_options = {i["interest_name"]: i["id"] for i in interests}

    # --------------------------------------------------
    # Header row
    # --------------------------------------------------
    h1, h2, h3 = st.columns([4, 3, 2])
    h1.markdown("**Student**")
    h2.markdown("**Conduct / Interest**")
    h3.markdown("**Attendance**")

    # --------------------------------------------------
    # Session storage
    # --------------------------------------------------
    st.session_state.setdefault("conduct_entries", {})

    # --------------------------------------------------
    # Entry rows
    # --------------------------------------------------
    for student in students:
        sid = student["id"]

        c1, c2, c3 = st.columns([4, 3, 2])

        c1.write(student["full_name"])

        conduct_choice = c2.selectbox(
            "Conduct",
            options=list(conduct_options.keys()),
            key=f"conduct_{sid}_{class_name}_{term}",
            label_visibility="collapsed",
        )

        interest_choice = c2.selectbox(
            "Interest",
            options=list(interest_options.keys()),
            key=f"interest_{sid}_{class_name}_{term}",
            label_visibility="collapsed",
        )

        attendance = c3.number_input(
            "Attendance",
            min_value=0,
            max_value=100,
            value=0,
            key=f"attendance_{sid}_{class_name}_{term}",
            label_visibility="collapsed",
        )

        st.session_state["conduct_entries"][sid] = {
            "conduct_id": conduct_options[conduct_choice],
            "interest_id": interest_options[interest_choice],
            "attendance": attendance,
        }

    # --------------------------------------------------
    # Save all
    # --------------------------------------------------
    if st.button("💾 Save All Entries"):
        for student_id, entry in st.session_state["conduct_entries"].items():
            save_student_conduct_interest(
                student_id=student_id,
                class_id=class_id,
                term=term,
                conduct_id=entry["conduct_id"],
                interest_id=entry["interest_id"],
                attendance=entry["attendance"],
            )

        st.success("Conduct, interest, and attendance saved successfully!")
