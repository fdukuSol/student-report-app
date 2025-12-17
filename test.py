import streamlit as st
from core.auth import get_current_user
from core.db_students import get_students
from core.db_classes import get_classes
from core.db_subject_assignments import get_subjects_for_class
from core.db_score_settings import get_score_setting_for_level
from core.db_student_scores import save_student_subject_score, _safe_execute, supabase
from core.db_teachers import get_teachers


def enter_student_scores_page():
    user = get_current_user()
    if not user or user["role"] != "teacher":
        st.warning("Access denied.")
        return

    st.subheader("✏️ Enter Student Scores")

    # -------------------------
    # Teacher assigned classes
    # -------------------------
    teacher_profile = next(
        (t for t in get_teachers() if t["auth_user_id"] == user["auth_user_id"]), None
    )
    assigned_class_ids = teacher_profile.get("assigned_classes", [])

    classes = [c for c in get_classes() if c["class_name"] in assigned_class_ids]
    if not classes:
        st.info("No classes assigned.")
        return

    # -------------------------
    # Select class
    # -------------------------
    class_map = {c["class_name"]: c for c in classes}
    class_name = st.selectbox("Select Class", list(class_map.keys()))
    class_row = class_map[class_name]
    class_id = class_row["id"]
    academic_level = class_row["academic_level"]

    # -------------------------
    # Select student
    # -------------------------
    students = [s for s in get_students() if s["assigned_class"] == class_name]
    if not students:
        st.info("No students in this class.")
        return

    student_map = {s["full_name"]: s for s in students}
    student_name = st.selectbox("Select Student", list(student_map.keys()))
    student_id = student_map[student_name]["id"]

    # -------------------------
    # Load subjects (NORMALIZED)
    # -------------------------
    raw_subjects = get_subjects_for_class(class_id)
    if not raw_subjects:
        st.info("No subjects assigned.")
        return

    subjects = []

    for s in raw_subjects:
        # Case 1: already joined object
        if isinstance(s, dict) and "subjects" in s:
            subjects.append({
                "id": s["subjects"]["id"],
                "subject_name": s["subjects"]["subject_name"]
            })
        # Case 2: direct subject dict
        elif isinstance(s, dict) and "id" in s:
            subjects.append(s)
        # Case 3: subject name string
        elif isinstance(s, str):
            row = (
                supabase.table("subjects")
                .select("id, subject_name")
                .eq("subject_name", s)
                .single()
                .execute()
            )
            if row.data:
                subjects.append(row.data)

    if not subjects:
        st.error("Subjects could not be resolved.")
        return

    # -------------------------
    # Load score settings
    # -------------------------
    settings = get_score_setting_for_level(academic_level)
    if not settings:
        st.error("Score settings not configured for this academic level.")
        return

    # -------------------------
    # Existing scores
    # -------------------------
    existing_scores = _safe_execute(
        supabase.table("student_scores")
        .select("*")
        .eq("student_id", student_id)
        .eq("class_id", class_id)
    )
    existing_map = {s["subject_id"]: s for s in existing_scores}

    # -------------------------
    # GRID HEADER
    # -------------------------
    st.markdown("### Enter Scores")

    if settings.get("has_components"):
        h1, h2, h3 = st.columns([2, 1, 1])
        h1.markdown("**Subject**")
        h2.markdown("**Class Score**")
        h3.markdown("**Exam Score**")
    else:
        h1, h2 = st.columns([2, 1])
        h1.markdown("**Subject**")
        h2.markdown("**Exam Score**")

    class_scores = {}
    exam_scores = {}

    # -------------------------
    # SUBJECT ROWS
    # -------------------------
    for idx, subj in enumerate(subjects):
        subj_id = subj["id"]
        subj_name = subj["subject_name"]
        existing = existing_map.get(subj_id, {})

        if settings.get("has_components"):
            col_s, col_c, col_e = st.columns([2, 1, 1])

            col_s.markdown(subj_name)

            class_scores[subj_id] = col_c.number_input(
                "**Class Score**",
                min_value=0,
                max_value=int(settings["max_class_score"]),
                value=int(existing.get("class_score") or 0),
                step=1,
                key=f"class_{idx}_{subj_id}_{student_id}",
                label_visibility="collapsed"
            )

            exam_scores[subj_id] = col_e.number_input(
                "**Exam Score**",
                min_value=0,
                max_value=int(settings["max_exam_score"]),
                value=int(existing.get("exam_score") or 0),
                step=1,
                key=f"exam_{idx}_{subj_id}_{student_id}",
                label_visibility="collapsed"
            )
        else:
            col_s, col_e = st.columns([2, 1])

            col_s.markdown(subj_name)

            class_scores[subj_id] = None

            exam_scores[subj_id] = col_e.number_input(
                "**Exam Score**",
                min_value=0,
                max_value=int(settings["max_exam_score"]),
                value=int(existing.get("exam_score") or 0),
                step=1,
                key=f"exam_{idx}_{subj_id}_{student_id}",
                label_visibility="collapsed"
            )

    # -------------------------
    # SAVE BUTTON
    # -------------------------
    st.divider()
    if st.button("💾 Save All Scores", use_container_width=True):
        for subj in subjects:
            subj_id = subj["id"]
            save_student_subject_score(
                student_id=student_id,
                class_id=class_id,
                subject_id=subj_id,
                academic_level=academic_level,
                class_score=class_scores.get(subj_id),
                exam_score=exam_scores.get(subj_id)
            )

        st.success("Scores saved successfully!")
        st.rerun()

    # -------------------------
    # BACK BUTTON
    # -------------------------
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "teacher_dashboard"
        st.rerun()
