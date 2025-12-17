# admin/manage_subject_assignments.py
import streamlit as st
from core.auth import get_current_user
from core.db_classes import get_classes
from core.db_subjects import get_subjects
from core.db_subject_assignments import (
    get_subjects_for_class,
    assign_subjects_to_class_bulk,
    remove_subject_from_class,
)


def manage_subject_assignments_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("You do not have permission to access this page.")
        return

    st.subheader("Assign Subjects to Classes")

    classes = get_classes()
    subjects = get_subjects()

    if not classes or not subjects:
        st.info("Please ensure classes and subjects exist first.")
        return

    # -----------------------------
    # Select Class
    # -----------------------------
    class_map = {c["class_name"]: c["id"] for c in classes}
    selected_class_name = st.selectbox("Select Class", list(class_map.keys()))
    selected_class_id = class_map[selected_class_name]

    st.divider()

    # -----------------------------
    # Assign Multiple Subjects
    # -----------------------------
    subject_map = {s["subject_name"]: s["id"] for s in subjects}

    selected_subjects = st.multiselect(
        "Select Subjects to Assign", options=list(subject_map.keys())
    )

    if st.button("➕ Assign Selected Subjects"):
        if not selected_subjects:
            st.warning("Please select at least one subject.")
        else:
            subject_ids = [subject_map[name] for name in selected_subjects]
            assign_subjects_to_class_bulk(selected_class_id, subject_ids)
            st.success("Subjects assigned successfully!")
            st.rerun()

    st.divider()

    # -----------------------------
    # Assigned Subjects Table
    # -----------------------------
    st.markdown("### Assigned Subjects")

    assigned = get_subjects_for_class(selected_class_id)

    if not assigned:
        st.info("No subjects assigned to this class yet.")
        return

    for row in assigned:
        assignment_id = row["id"]
        subject_name = row["subjects"]["subject_name"]

        c1, c2 = st.columns([4, 1])
        c1.write(subject_name)
        if c2.button("🗑️", key=f"remove_{assignment_id}"):
            remove_subject_from_class(assignment_id)
            st.success("Subject removed.")
            st.rerun()
