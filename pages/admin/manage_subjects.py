import streamlit as st
from core.auth import get_current_user
from core.db_subjects import (
    get_subjects,
    create_subject,
    update_subject,
    delete_subject
)

SUBJECT_TYPES = ["core", "elective"]

def manage_subjects_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("You do not have permission to access this page.")
        return

    st.subheader("Manage Subjects")

    state = st.session_state
    state.setdefault("edit_mode", False)
    state.setdefault("edit_id", None)
    state.setdefault("confirm_delete", None)
    state.setdefault("confirm_name", "")
    state.setdefault("edit_subject_type", "core")  # added

    subjects = get_subjects()

    # -------------------
    # Handle edit/delete clicks
    # -------------------
    for row in subjects:
        sid = row["id"]
        sname = row["subject_name"]
        stype = row.get("subject_type", "core")

        if state.get(f"edit_press_{sid}", False):
            state.edit_mode = True
            state.edit_id = sid
            state.edit_subject_name = sname
            state.edit_subject_type = stype
            state[f"edit_press_{sid}"] = False
            st.rerun()

        if state.get(f"delete_press_{sid}", False):
            state.confirm_delete = sid
            state.confirm_name = sname
            state[f"delete_press_{sid}"] = False
            st.rerun()

    col_form, col_table = st.columns([1, 2])

    # -------------------
    # Add/Edit Form
    # -------------------
    with col_form:
        st.markdown("### Add / Edit Subject")

        if state.edit_mode:
            subject_name = st.text_input(
                "Subject Name",
                value=state.get("edit_subject_name", ""),
                key="input_subject_edit"
            )
            subject_type = st.selectbox(
                "Subject Type",
                options=SUBJECT_TYPES,
                index=SUBJECT_TYPES.index(state.get("edit_subject_type", "core")),
                key="select_subject_type_edit"
            )
        else:
            subject_name = st.text_input("Subject Name", key="input_subject_add")
            subject_type = st.selectbox("Subject Type", options=SUBJECT_TYPES, key="select_subject_type_add")

        if state.edit_mode:
            if st.button("Update Subject"):
                update_subject(state.edit_id, subject_name, subject_type)
                st.success("Subject updated successfully!")
                state.edit_mode = False
                state.edit_id = None
                st.rerun()

            if st.button("Cancel"):
                state.edit_mode = False
                state.edit_id = None
                st.rerun()
        else:
            if st.button("Add Subject"):
                if subject_name.strip():
                    create_subject(subject_name, subject_type)
                    st.success("Subject added!")
                    st.rerun()
                else:
                    st.warning("Subject name is required.")

    # -------------------
    # Subject List Table
    # -------------------
    with col_table:
        st.markdown("### Existing Subjects")

        if not subjects:
            st.info("No subjects yet — add one!")
        else:
            for row in subjects:
                sid = row["id"]
                sname = row["subject_name"]
                stype = row.get("subject_type", "core")

                c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                c1.write(f"**{sname}**")
                c2.write(f"*{stype.capitalize()}*")

                if c3.button("✏️", key=f"edit_{sid}"):
                    state[f"edit_press_{sid}"] = True
                    st.rerun()

                if c4.button("🗑️", key=f"delete_{sid}"):
                    state[f"delete_press_{sid}"] = True
                    st.rerun()

        # Delete confirmation
        if state.confirm_delete:
            st.warning(f"Are you sure you want to delete **{state.confirm_name}**?")
            b1, b2 = st.columns(2)
            if b1.button("Yes, Delete"):
                delete_subject(state.confirm_delete)
                st.success("Subject deleted!")
                state.confirm_delete = None
                state.confirm_name = ""
                st.rerun()
            if b2.button("Cancel"):
                state.confirm_delete = None
                state.confirm_name = ""
                st.rerun()
