import streamlit as st
from core.auth import get_current_user
from core.db_final_grading_scales import (
    get_final_grading_scales,
    create_final_grading_scale,
    update_final_grading_scale,
    delete_final_grading_scale
)

def manage_final_grading_scales_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("Access denied.")
        return

    st.subheader("Manage Final Grading Scales")

    state = st.session_state
    state.setdefault("edit_mode", False)
    state.setdefault("edit_id", None)
    state.setdefault("confirm_delete", None)
    state.setdefault("confirm_grade", "")

    # UI → DB mapping
    LEVEL_MAP = {
        "Lower / Upper Primary": "primary",
        "JHS": "jhs"
    }

    ui_level = st.selectbox("Select Level", list(LEVEL_MAP.keys()))
    db_level = LEVEL_MAP[ui_level]

    scales = get_final_grading_scales(db_level)

    col_form, col_table = st.columns([1, 2])

    # ---------------- FORM ----------------
    with col_form:
        st.markdown("### Add / Edit Scale")

        min_value = st.number_input(
            "Min Value",
            value=state.get("edit_min_value", 0),
            min_value=0,
            max_value=2000
        )
        max_value = st.number_input(
            "Max Value",
            value=state.get("edit_max_value", 0),
            min_value=0,
            max_value=2000
        )
        final_grade = st.text_input(
            "Final Grade",
            value=state.get("edit_final_grade", "")
        )
        descriptor = st.text_input(
            "Descriptor",
            value=state.get("edit_descriptor", "")
        )
        remark = st.text_input(
            "Remark",
            value=state.get("edit_remark", "")
        )

        if state.edit_mode:
            if st.button("Update Scale"):
                update_final_grading_scale(
                    state.edit_id,
                    min_value,
                    max_value,
                    final_grade,
                    remark,
                    descriptor
                )
                state.edit_mode = False
                st.rerun()

            if st.button("Cancel"):
                state.edit_mode = False
                st.rerun()
        else:
            if st.button("Add Scale"):
                create_final_grading_scale(
                    db_level,
                    min_value,
                    max_value,
                    final_grade,
                    remark,
                    descriptor
                )
                st.rerun()

    # ---------------- TABLE ----------------
    with col_table:
        st.markdown(f"### Existing Scales — {ui_level}")

        if not scales:
            st.info("No grading scales defined.")
        else:
            for s in scales:
                c1, c2, c3 = st.columns([4, 1, 1])

                c1.write(
                    f"**{s['final_grade']}** | "
                    f"{s['min_value']}–{s['max_value']} | "
                    f"{s.get('descriptor','')} | "
                    f"{s.get('remark','')}"
                )

                if c2.button("✏️", key=f"edit_{s['id']}"):
                    state.edit_mode = True
                    state.edit_id = s["id"]
                    state.edit_min_value = s["min_value"]
                    state.edit_max_value = s["max_value"]
                    state.edit_final_grade = s["final_grade"]
                    state.edit_descriptor = s.get("descriptor", "")
                    state.edit_remark = s.get("remark", "")
                    st.rerun()

                if c3.button("🗑️", key=f"delete_{s['id']}"):
                    state.confirm_delete = s["id"]
                    state.confirm_grade = s["final_grade"]
                    st.rerun()

        if state.confirm_delete:
            st.warning(f"Delete grade **{state.confirm_grade}**?")
            if st.button("Yes, Delete"):
                delete_final_grading_scale(state.confirm_delete)
                state.confirm_delete = None
                st.rerun()
