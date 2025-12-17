# admin/manage_teachers.py
import streamlit as st
from core.auth import get_current_user
import pandas as pd
from core.db_teachers import (
    get_teachers,
    create_teacher,
    update_teacher,
    delete_teacher,
    bulk_create_teachers,
    ROLES,
)
from core.db_classes import get_classes
import io
import csv


# --- Reset form and session state ---
def reset_form():
    keys_to_clear = [
        "add_full_name_input",
        "add_email_input",
        "add_password_input",
        "add_classes_input",
        "edit_teacher_selected_id",
        "edit_full_name",
        "edit_email",
        "edit_role",
        "edit_classes",
        "edit_password",
        "update_pressed",
        "delete_pressed",
        "bulk_upload_file",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def manage_teachers_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("You do not have permission to access this page.")
        return

    st.subheader("Manage Teachers")

    teachers = get_teachers()
    classes = get_classes()
    class_options = [c["class_name"] for c in classes]

    col_form, col_table = st.columns([1, 2])

    # =====================
    # TEACHER TABLE + REFRESH BUTTON
    # =====================
    with col_table:
        st.markdown("### Teacher List")

        # Refresh Page button (only clears page/form keys, keeps login)
        if st.button("🔄 Refresh Page"):
            keys_to_reset = [
                "add_full_name_input",
                "add_email_input",
                "add_password_input",
                "add_classes_input",
                "edit_teacher_selected_id",
                "edit_full_name",
                "edit_email",
                "edit_role",
                "edit_classes",
                "edit_password",
                "update_pressed",
                "delete_pressed",
                "bulk_upload_file",
            ]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        if not teachers:
            st.info("No teachers found.")
            df = pd.DataFrame(columns=["_id", "Full Name", "Email", "Role", "Classes"])
        else:
            df = pd.DataFrame(
                [
                    {
                        "_id": t["id"],
                        "Full Name": t["full_name"],
                        "Email": t.get("email", ""),
                        "Role": t.get("role", "teacher"),
                        "Classes": ", ".join(t.get("assigned_classes", [])),
                    }
                    for t in teachers
                ]
            )

        st.data_editor(
            df,
            num_rows="dynamic",
            column_config={
                "Role": st.column_config.SelectboxColumn("Role", options=ROLES),
                "Classes": st.column_config.TextColumn(
                    "Classes", help="Comma-separated class names"
                ),
            },
            width="stretch",
            key="teachers_editor",
        )

    # =====================
    # ADD / UPDATE FORM
    # =====================
    with col_form:
        st.markdown("### Add / Update Teacher")
        st.session_state.setdefault("edit_teacher_selected_id", "")

        # Dropdown for edit
        edit_options = [""] + [str(t["id"]) for t in teachers]
        selected_id = st.selectbox(
            "Select a teacher to update/delete",
            edit_options,
            index=(
                edit_options.index(st.session_state.get("edit_teacher_selected_id", ""))
                if st.session_state.get("edit_teacher_selected_id", "") in edit_options
                else 0
            ),
            format_func=lambda x: (
                ""
                if x == ""
                else next(t["full_name"] for t in teachers if str(t["id"]) == x)
            ),
        )
        st.session_state["edit_teacher_selected_id"] = selected_id

        # Prefill edit fields
        if selected_id:
            teacher = next(t for t in teachers if str(t["id"]) == selected_id)
            st.session_state.setdefault("edit_full_name", teacher["full_name"])
            st.session_state.setdefault("edit_email", teacher["email"])
            st.session_state.setdefault("edit_role", teacher.get("role", "teacher"))
            st.session_state.setdefault(
                "edit_classes", teacher.get("assigned_classes", [])
            )
            st.session_state.setdefault("edit_password", "")

        # =====================
        # EDIT MODE
        # =====================
        if selected_id:
            with st.form("edit_form"):
                full_name = st.text_input(
                    "Full Name", st.session_state["edit_full_name"]
                )
                email = st.text_input("Email", st.session_state["edit_email"])
                role = st.selectbox(
                    "Role", ROLES, index=ROLES.index(st.session_state["edit_role"])
                )
                assigned_classes = st.multiselect(
                    "Assign Classes",
                    class_options,
                    default=st.session_state["edit_classes"],
                )
                password = st.text_input("Password (optional)", type="password")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.form_submit_button("Update Teacher"):
                        update_teacher(
                            user_id=selected_id,
                            full_name=(full_name or "").strip(),
                            email=(email or "").strip(),
                            role=role,
                            classes=assigned_classes,
                            password=password if password else None,
                        )
                        st.success("Teacher updated successfully!")
                        reset_form()
                        st.rerun()

                with col2:
                    if st.form_submit_button("Delete Teacher"):
                        delete_teacher(selected_id)
                        st.success("Teacher deleted successfully!")
                        reset_form()
                        st.rerun()

                with col3:
                    if st.form_submit_button("Cancel"):
                        reset_form()
                        st.rerun()

        # =====================
        # ADD MODE
        # =====================
        else:
            with st.form("add_form"):
                full_name = st.text_input("Full Name", key="add_full_name_input")
                email = st.text_input("Email", key="add_email_input")
                role = st.selectbox("Role", ROLES, key="add_role_input")
                password = st.text_input(
                    "Password", type="password", key="add_password_input"
                )
                assigned_classes = st.multiselect(
                    "Assign Classes", class_options, key="add_classes_input"
                )

                if st.form_submit_button("➕ Add Teacher"):
                    if full_name.strip() and email.strip() and password.strip():
                        create_teacher(
                            full_name=full_name.strip(),
                            email=email.strip(),
                            password=password.strip(),
                            classes=assigned_classes,
                        )
                        st.success("Teacher added successfully!")
                        reset_form()
                        st.rerun()

    # =====================
    # BULK UPLOAD (CSV or Excel)
    # =====================
    st.markdown("### Bulk Upload Teachers (CSV or Excel)")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file", type=["csv", "xlsx"], key="bulk_upload_file"
    )

    # Preview and process immediately
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Preview table
            st.write("### File Preview:")
            st.dataframe(df, width="stretch")

            # Process rows
            added_count = 0
            for _, row in df.iterrows():
                full_name = str(row.get("full_name", "")).strip()
                email = str(row.get("email", "")).strip()
                password = str(row.get("password", "")).strip()
                classes_raw = str(row.get("classes", "")).strip()
                classes = [c.strip() for c in classes_raw.split(",") if c.strip()]

                if full_name and email and password:
                    create_teacher(
                        full_name=full_name,
                        email=email,
                        password=password,
                        classes=classes,
                    )
                    added_count += 1

            st.success(f"Bulk upload completed! {added_count} teachers added.")

        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")
