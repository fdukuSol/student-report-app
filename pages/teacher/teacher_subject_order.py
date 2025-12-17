import streamlit as st
from core.auth import get_current_user
from core.db_classes import get_classes
from core.db_subject_assignments import get_subjects_for_class
from core.db_subject_order import get_subject_order_for_class, save_subject_order
from core.db_teachers import get_teachers


def manage_subject_order_page():
    user = get_current_user()
    if not user or user.get("role") != "teacher":
        st.warning("Access denied.")
        return

    st.subheader("📑 Arrange Subjects Per Class")

    # Teacher profile & assigned classes
    teacher = next(
        (t for t in get_teachers() if t["auth_user_id"] == user["auth_user_id"]),
        None,
    )
    if not teacher:
        st.error("Teacher profile not found.")
        return

    assigned_class_names = teacher.get("assigned_classes", [])
    classes = [c for c in get_classes() if c["class_name"] in assigned_class_names]
    if not classes:
        st.info("No classes assigned.")
        return

    # Select class
    class_map = {c["class_name"]: c["id"] for c in classes}
    class_name = st.selectbox("Select Class", list(class_map.keys()))
    class_id = class_map[class_name]

    # Subjects for class
    assigned = get_subjects_for_class(class_id)
    if not assigned:
        st.info("No subjects assigned to this class.")
        return

    subjects = [
        {"id": r["subjects"]["id"], "name": r["subjects"]["subject_name"]}
        for r in assigned
    ]

    # Load existing order
    existing = get_subject_order_for_class(class_id)
    existing_map = {}
    if existing:
        for row in existing:
            existing_map[row["subject_id"]] = row["sort_order"]

    # Order input form
    st.markdown("### Enter Subject Order")
    with st.form("subject_order_form"):
        order_inputs = {}
        for subj in subjects:
            default_order = existing_map.get(subj["id"], len(order_inputs) + 1)
            order_inputs[subj["id"]] = st.number_input(
                label=subj["name"],
                min_value=1,
                max_value=len(subjects),
                step=1,
                value=default_order,
                key=f"order_{subj['id']}",
            )

        submitted = st.form_submit_button("💾 Save Subject Order")

    # Validation & Save
    if submitted:
        orders = list(order_inputs.values())

        # Unique validation
        if len(set(orders)) != len(orders):
            st.error("❌ Order numbers must be unique.")
            return

        # Continuous check
        expected = list(range(1, len(orders) + 1))
        if sorted(orders) != expected:
            st.error(f"❌ Order numbers must be continuous from 1 to {len(orders)}.")
            return

        # Sort subjects by input order
        ordered_ids = [
            subject_id
            for subject_id, order in sorted(order_inputs.items(), key=lambda x: x[1])
        ]

        # Debug: show payload before saving
        st.write("DEBUG: class_id =", class_id)
        st.write("DEBUG: ordered_ids =", ordered_ids)

        try:
            save_subject_order(class_id, ordered_ids)
            st.success("✅ Subject order saved successfully.")
        except Exception as e:
            st.error(f"❌ Failed to save subject order: {e}")
