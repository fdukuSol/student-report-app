# pages/admin/admin_conduct_interest.py
import streamlit as st
from core.auth import get_current_user
from core.db_admin_settings import (
    get_all_conduct, add_conduct, update_conduct, delete_conduct,
    get_all_interest, add_interest, update_interest, delete_interest
)

def admin_conduct_interest_page():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.warning("You do not have permission to access this page.")
        return

    st.title("Admin: Conduct & Interest Settings")

    state = st.session_state
    # ---------------------------
    # Initialize session state
    # ---------------------------
    state.setdefault("conduct_edit_mode", False)
    state.setdefault("conduct_edit_id", None)
    state.setdefault("conduct_confirm_delete", None)
    state.setdefault("conduct_confirm_name", "")

    state.setdefault("interest_edit_mode", False)
    state.setdefault("interest_edit_id", None)
    state.setdefault("interest_confirm_delete", None)
    state.setdefault("interest_confirm_name", "")

    # ---------------------------
    # Load data
    # ---------------------------
    conducts = get_all_conduct()
    interests = get_all_interest()

    col_form, col_table = st.columns([1, 2])

    # ===========================================
    # Conduct Section
    # ===========================================
    with col_form:
        st.subheader("Add / Edit Conduct")
        if state.conduct_edit_mode:
            conduct_name = st.text_input(
                "Conduct Name",
                value=state.get("conduct_edit_name", ""),
                key="input_conduct_edit"
            )
        else:
            conduct_name = st.text_input("New Conduct", key="input_conduct_add")

        if state.conduct_edit_mode:
            if st.button("Update Conduct"):
                update_conduct(state.conduct_edit_id, conduct_name.strip())
                st.success("Conduct updated successfully!")
                state.conduct_edit_mode = False
                state.conduct_edit_id = None
                st.rerun()

            if st.button("Cancel"):
                state.conduct_edit_mode = False
                state.conduct_edit_id = None
                st.rerun()
        else:
            if st.button("Add Conduct"):
                if conduct_name.strip():
                    add_conduct(conduct_name.strip())
                    st.success("Conduct added successfully!")
                    st.rerun()
                else:
                    st.warning("Conduct name is required.")

    with col_table:
        st.subheader("Existing Conducts")
        if not conducts:
            st.info("No conduct values yet — add one!")
        else:
            for c in conducts:
                cid = c["id"]
                cname = c["conduct_name"]
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"**{cname}**")
                if c2.button("✏️", key=f"edit_conduct_{cid}"):
                    state.conduct_edit_mode = True
                    state.conduct_edit_id = cid
                    state.conduct_edit_name = cname
                    st.rerun()
                if c3.button("🗑️", key=f"delete_conduct_{cid}"):
                    state.conduct_confirm_delete = cid
                    state.conduct_confirm_name = cname
                    st.rerun()

        if state.conduct_confirm_delete:
            st.warning(f"Are you sure you want to delete **{state.conduct_confirm_name}**?")
            b1, b2 = st.columns(2)
            if b1.button("Yes, Delete"):
                delete_conduct(state.conduct_confirm_delete)
                st.success("Conduct deleted!")
                state.conduct_confirm_delete = None
                state.conduct_confirm_name = ""
                st.rerun()
            if b2.button("Cancel"):
                state.conduct_confirm_delete = None
                state.conduct_confirm_name = ""
                st.rerun()

    # ===========================================
    # Interest Section
    # ===========================================
    col_form_i, col_table_i = st.columns([1, 2])
    with col_form_i:
        st.subheader("Add / Edit Interest")
        if state.interest_edit_mode:
            interest_name = st.text_input(
                "Interest Name",
                value=state.get("interest_edit_name", ""),
                key="input_interest_edit"
            )
        else:
            interest_name = st.text_input("New Interest", key="input_interest_add")

        if state.interest_edit_mode:
            if st.button("Update Interest"):
                update_interest(state.interest_edit_id, interest_name.strip())
                st.success("Interest updated successfully!")
                state.interest_edit_mode = False
                state.interest_edit_id = None
                st.rerun()

            if st.button("Cancel"):
                state.interest_edit_mode = False
                state.interest_edit_id = None
                st.rerun()
        else:
            if st.button("Add Interest"):
                if interest_name.strip():
                    add_interest(interest_name.strip())
                    st.success("Interest added successfully!")
                    st.rerun()
                else:
                    st.warning("Interest name is required.")

    with col_table_i:
        st.subheader("Existing Interests")
        if not interests:
            st.info("No interest values yet — add one!")
        else:
            for i in interests:
                iid = i["id"]
                iname = i["interest_name"]
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"**{iname}**")
                if c2.button("✏️", key=f"edit_interest_{iid}"):
                    state.interest_edit_mode = True
                    state.interest_edit_id = iid
                    state.interest_edit_name = iname
                    st.rerun()
                if c3.button("🗑️", key=f"delete_interest_{iid}"):
                    state.interest_confirm_delete = iid
                    state.interest_confirm_name = iname
                    st.rerun()

        if state.interest_confirm_delete:
            st.warning(f"Are you sure you want to delete **{state.interest_confirm_name}**?")
            b1, b2 = st.columns(2)
            if b1.button("Yes, Delete"):
                delete_interest(state.interest_confirm_delete)
                st.success("Interest deleted!")
                state.interest_confirm_delete = None
                state.interest_confirm_name = ""
                st.rerun()
            if b2.button("Cancel"):
                state.interest_confirm_delete = None
                state.interest_confirm_name = ""
                st.rerun()
