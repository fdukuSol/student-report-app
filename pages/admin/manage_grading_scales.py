import streamlit as st
from core.auth import get_current_user
from core.db_grading_scales import (
    get_grading_scales,
    create_grading_scale,
    update_grading_scale,
    delete_grading_scale,
)


def manage_grading_scales_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("Access denied.")
        return

    st.subheader("Grading Scales")

    # -----------------------------
    # ADD SCALE
    # -----------------------------
    with st.form("add_grade_form"):
        min_score = st.number_input("Min Score", 0)
        max_score = st.number_input("Max Score", 0)
        grade = st.number_input("Grade", 0)
        remark = st.text_input("Remark")

        if st.form_submit_button("Add Grade"):
            create_grading_scale(min_score, max_score, grade, remark)
            st.success("Grade added.")
            st.rerun()

    st.divider()

    # -----------------------------
    # EXISTING SCALES
    # -----------------------------
    for row in get_grading_scales():
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 3, 1])
        c1.write(f"{row['min_score']} – {row['max_score']}")
        c2.write(f"Grade {row['grade']}")
        c3.write("")
        c4.write(row["remark"])

        if c5.button("🗑️", key=row["id"]):
            delete_grading_scale(row["id"])
            st.rerun()
