import streamlit as st
from core.auth import get_current_user
from core.db_score_settings import (
    get_score_settings,
    create_score_setting,
    update_score_setting,
    delete_score_setting,
    ACADEMIC_LEVELS
)

def manage_score_settings_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("Access denied.")
        return

    st.subheader("Score Settings (Per Academic Level)")

    settings = get_score_settings()
    settings_map = {s["academic_level"]: s for s in settings}

    # -----------------------------
    # SELECT ACADEMIC LEVEL
    # -----------------------------
    selected_level = st.selectbox("Academic Level", ACADEMIC_LEVELS)

    existing = settings_map.get(selected_level)

    # -----------------------------
    # FORM (ADD OR EDIT)
    # -----------------------------
    with st.form("score_settings_form"):
        has_components = st.checkbox(
            "Has Class & Exam Components",
            value=existing["has_components"] if existing else False
        )

        class_weight = st.number_input(
            "Class Weight (%)",
            0, 100,
            value=int(existing["class_weight"]) if existing else 0
        )

        exam_weight = st.number_input(
            "Exam Weight (%)",
            0, 100,
            value=int(existing["exam_weight"]) if existing else 100
        )

        max_class_score = st.number_input(
            "Max Class Score",
            value=int(existing["max_class_score"]) if existing else 0
        )

        max_exam_score = st.number_input(
            "Max Exam Score",
            value=int(existing["max_exam_score"]) if existing else 100
        )

        submitted = st.form_submit_button("Save Settings")

        if submitted:
            if class_weight + exam_weight != 100:
                st.error("Class weight + Exam weight must equal 100%.")
                return

            payload = {
                "has_components": has_components,
                "class_weight": class_weight,
                "exam_weight": exam_weight,
                "max_class_score": max_class_score,
                "max_exam_score": max_exam_score
            }

            if existing:
                # UPDATE
                update_score_setting(existing["id"], payload)
                st.success("Score settings updated.")
            else:
                # CREATE
                create_score_setting(
                    selected_level,
                    has_components,
                    class_weight,
                    exam_weight,
                    max_class_score,
                    max_exam_score
                )
                st.success("Score settings created.")

            st.rerun()

    st.divider()

    # -----------------------------
    # READ-ONLY VIEW
    # -----------------------------
    st.markdown("### Current Configuration")

    if not settings:
        st.info("No score settings configured yet.")
        return

    for row in settings:
        st.markdown(
            f"""
            **{row['academic_level']}**
            - Components: {row['has_components']}
            - Class: {row['class_weight']}% (Max {row['max_class_score']})
            - Exam: {row['exam_weight']}% (Max {row['max_exam_score']})
            """
        )

        if st.button("🗑️ Delete", key=f"del_{row['id']}"):
            delete_score_setting(row["id"])
            st.warning("Score settings deleted.")
            st.rerun()
