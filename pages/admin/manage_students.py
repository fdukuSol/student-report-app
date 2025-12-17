# admin/manage_students.py
import streamlit as st
import pandas as pd
from core.db_classes import get_classes
from core.db_students import (
    get_students,
    create_student,
    update_student,
    delete_student,
    bulk_create_students,
)


# --- Reset form and session state ---
def reset_student_form():
    keys_to_clear = [
        "add_student_name",
        "add_student_class",
        "edit_student_selected_id",
        "edit_student_name",
        "edit_student_class",
        "bulk_student_file",
        "filter_class",
        "search_name",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def manage_students_page():
    st.subheader("Manage Students")

    students = get_students()
    classes = get_classes()
    class_options = [c["class_name"] for c in classes]

    col_form, col_table = st.columns([1, 2])

    # =====================
    # Filters
    # =====================
    with col_form:
        st.markdown("### Filter & Search")
        st.session_state.setdefault("filter_class", "")
        st.session_state.setdefault("search_name", "")

        filter_class = st.selectbox(
            "Filter by Class",
            options=[""] + class_options,
            index=(
                0
                if st.session_state["filter_class"] == ""
                else class_options.index(st.session_state["filter_class"])
            ),
            key="filter_class",
        )

        search_name = st.text_input(
            "Search by Name", value=st.session_state["search_name"], key="search_name"
        )

    # Apply filter/search
    filtered_students = students
    if filter_class:
        filtered_students = [
            s for s in filtered_students if s.get("assigned_class") == filter_class
        ]
    if search_name:
        filtered_students = [
            s
            for s in filtered_students
            if search_name.lower() in s.get("full_name", "").lower()
        ]

    # =====================
    # STUDENT TABLE + REFRESH
    # =====================
    with col_table:
        st.markdown("### Student List")

        if st.button("🔄 Refresh Page"):
            reset_student_form()
            st.rerun()

        if not filtered_students:
            st.info("No students found.")
            df = pd.DataFrame(columns=["_id", "Full Name", "Class"])
        else:
            df = pd.DataFrame(
                [
                    {
                        "_id": s["id"],
                        "Full Name": s["full_name"],
                        "Class": s["assigned_class"],
                    }
                    for s in filtered_students
                ]
            )
        st.data_editor(df, num_rows="dynamic", width="stretch", key="students_editor")

    # =====================
    # ADD / UPDATE FORM
    # =====================
    with col_form:
        st.markdown("### Add / Update Student")
        st.session_state.setdefault("edit_student_selected_id", "")

        # Dropdown for edit
        edit_options = [""] + [str(s["id"]) for s in filtered_students]
        selected_id = st.selectbox(
            "Select a student to update/delete",
            edit_options,
            index=0,
            format_func=lambda x: (
                ""
                if x == ""
                else next(
                    s["full_name"] for s in filtered_students if str(s["id"]) == x
                )
            ),
            key="edit_student_selected_id",
        )

        # Prefill edit fields
        if selected_id:
            student = next(s for s in filtered_students if str(s["id"]) == selected_id)
            st.session_state.setdefault("edit_student_name", student["full_name"])
            st.session_state.setdefault("edit_student_class", student["assigned_class"])

        # Edit mode
        if selected_id:
            with st.form("edit_student_form"):
                full_name = st.text_input(
                    "Full Name", st.session_state["edit_student_name"]
                )
                assigned_class = st.selectbox(
                    "Class",
                    class_options,
                    index=class_options.index(st.session_state["edit_student_class"]),
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.form_submit_button("Update Student"):
                        update_student(selected_id, full_name.strip(), assigned_class)
                        st.success("Student updated successfully!")
                        reset_student_form()
                        st.rerun()
                with col2:
                    if st.form_submit_button("Delete Student"):
                        delete_student(selected_id)
                        st.success("Student deleted successfully!")
                        reset_student_form()
                        st.rerun()
                with col3:
                    if st.form_submit_button("Cancel"):
                        reset_student_form()
                        st.rerun()

        # Add mode
        else:
            with st.form("add_student_form"):
                full_name = st.text_input("Full Name", key="add_student_name")
                assigned_class = st.selectbox(
                    "Class", class_options, key="add_student_class"
                )

                if st.form_submit_button("➕ Add Student"):
                    if full_name.strip() and assigned_class:
                        create_student(full_name.strip(), assigned_class)
                        st.success("Student added successfully!")
                        reset_student_form()
                        st.rerun()

    # =====================
    # BULK UPLOAD (CSV or Excel)
    # =====================
    st.markdown("### Bulk Upload Students (CSV or Excel)")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file", type=["csv", "xlsx"], key="bulk_student_file"
    )

    if uploaded_file is not None:
        try:
            # Read file
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Preview table
            st.write("### File Preview:")
            st.dataframe(df, width="stretch")

            # Process immediately (same as teachers)
            added_count = bulk_create_students(df)
            st.success(f"Bulk upload completed! {added_count} students added.")

        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")
