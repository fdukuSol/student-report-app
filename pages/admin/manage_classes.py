import streamlit as st
from core.auth import get_current_user
from core import get_classes, create_class, update_class, delete_class, ACADEMIC_LEVELS





def manage_classes_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("You do not have permission to access this page.")
        return


    st.subheader("Manage Classes")
    #st.title("🏫 Manage Classes")

    # Initialize session state variables
    state = st.session_state
    state.setdefault("edit_mode", False)
    state.setdefault("edit_id", None)
    state.setdefault("confirm_delete", None)
    state.setdefault("confirm_cname", "")

    # Fetch classes first
    classes = get_classes()

    # ===========================================
    # PRE-HANDLE EDIT & DELETE BUTTON CLICKS
    # ===========================================
    for row in classes:
        cid = row["id"]
        cname = row["class_name"]
        clevel = row["academic_level"]

        if state.get(f"edit_press_{cid}", False):
            state.edit_mode = True
            state.edit_id = cid
            state.edit_class_name = cname
            state.edit_academic_level = clevel
            state[f"edit_press_{cid}"] = False
            st.rerun()

        if state.get(f"delete_press_{cid}", False):
            state.confirm_delete = cid
            state.confirm_cname = cname
            state[f"delete_press_{cid}"] = False
            st.rerun()

    col_form, col_table = st.columns([1, 2])

    # ===========================================
    # CLASS FORM SECTION
    # ===========================================
    with col_form:
        st.markdown("### Add / Edit Class")

        if state.edit_mode:
            class_name = st.text_input(
                "Class Name",
                value=state.get("edit_class_name", ""),
                key="input_class_name_edit"
            )
            academic_level = st.selectbox(
                "Academic Level",
                ACADEMIC_LEVELS,
                index=ACADEMIC_LEVELS.index(state.get("edit_academic_level", ACADEMIC_LEVELS[0])),
                key="input_level_edit"
            )
        else:
            class_name = st.text_input("Class Name", key="input_class_name_add")
            academic_level = st.selectbox("Academic Level", ACADEMIC_LEVELS, key="input_level_add")

        if state.edit_mode:
            if st.button("Update Class"):
                if class_name.strip():
                    update_class(state.edit_id, class_name, academic_level)
                    st.success("Class updated successfully!")

                state.edit_mode = False
                state.edit_id = None
                st.rerun()

            if st.button("Cancel"):
                state.edit_mode = False
                state.edit_id = None
                st.rerun()

        else:
            if st.button("Add Class"):
                if class_name.strip():
                    create_class(class_name, academic_level)
                    st.success("Class added!")
                    st.rerun()
                else:
                    st.warning("Class name is required.")

    # ===========================================
    # CLASS LIST TABLE
    # ===========================================
    with col_table:
        st.markdown("### Existing Classes")

        if not classes:
            st.info("No classes yet — add one!")
        else:
            for row in classes:
                cid = row["id"]
                cname = row["class_name"]
                clevel = row["academic_level"]

                c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                c1.write(f"**{cname}**")
                c2.write(clevel)

                if c3.button("✏️", key=f"edit_{cid}"):
                    state[f"edit_press_{cid}"] = True
                    st.rerun()

                if c4.button("🗑️", key=f"delete_{cid}"):
                    state[f"delete_press_{cid}"] = True
                    st.rerun()

        # ===========================================
        # DELETE CONFIRMATION
        # ===========================================
        if state.confirm_delete:
            st.warning(f"Are you sure you want to delete: **{state.confirm_cname}**?")
            b1, b2 = st.columns(2)

            if b1.button("Yes, Delete"):
                delete_class(state.confirm_delete)
                st.success("Class deleted!")
                state.confirm_delete = None
                state.confirm_cname = ""
                st.rerun()

            if b2.button("Cancel"):
                state.confirm_delete = None
                state.confirm_cname = ""
                st.rerun()
