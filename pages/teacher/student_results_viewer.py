import streamlit as st
import pandas as pd
from core.auth import get_current_user
from core.db_classes import get_classes
from core.db_students import get_students
from core.db_teachers import get_teachers
from core.db_student_final_results import get_final_results
from core.db_student_scores import supabase, _safe_execute  # helper for fetching scores

def get_student_scores_with_subjects(student_id: str, class_id: str):
    """
    Fetch student scores with subject names included.
    """
    rows = _safe_execute(
        supabase.table("student_scores")
        .select("*, subjects(id, subject_name)")
        .eq("student_id", student_id)
        .eq("class_id", class_id)
    )
    scores = []
    for r in rows:
        scores.append({
            "subject_id": r["subject_id"],
            "subject_name": r.get("subjects", {}).get("subject_name") if r.get("subjects") else None,
            "class_score": r.get("class_score"),
            "exam_score": r.get("exam_score"),
            "weighted_class_score": r.get("weighted_class_score"),
            "weighted_exam_score": r.get("weighted_exam_score"),
            "total_score": r.get("total_score")
        })
    return scores

def student_results_viewer_page():
    user = get_current_user()
    if not user:
        st.warning("Access denied.")
        return

    st.subheader("📄 Student Detailed Results Viewer")

    # ------------------------------ Determine accessible classes ------------------------------
    all_classes = get_classes()
    if user["role"] == "admin":
        accessible_classes = all_classes
    else:
        teacher_profile = next((t for t in get_teachers() if t["auth_user_id"] == user["auth_user_id"]), None)
        assigned_class_ids = teacher_profile.get("assigned_classes", [])
        accessible_classes = [c for c in all_classes if c["class_name"] in assigned_class_ids]

    if not accessible_classes:
        st.info("No accessible classes found.")
        return

    # ------------------------------ Select Class ------------------------------
    class_map = {c["class_name"]: c for c in accessible_classes}
    class_name = st.selectbox("Select Class", list(class_map.keys()))
    class_row = class_map[class_name]
    class_id = class_row["id"]
    academic_level = class_row["academic_level"]

    # ------------------------------ Select Term ------------------------------
    term = st.selectbox("Select Term", [1, 2, 3], index=0)

    # ------------------------------ Filter Students ------------------------------
    students_in_class = [s for s in get_students() if s["assigned_class"] == class_name]
    if not students_in_class:
        st.info("No students found in this class.")
        return

    student_map = {s["id"]: s for s in students_in_class}
    student_names = ["All Students"] + [s["full_name"] for s in students_in_class]
    selected_student_name = st.selectbox("Select Student", student_names)

    if selected_student_name == "All Students":
        student_ids = [s["id"] for s in students_in_class]
    else:
        student_obj = next(s for s in students_in_class if s["full_name"] == selected_student_name)
        student_ids = [student_obj["id"]]

    # ------------------------------ Display Final Results ------------------------------
    final_results_data = []
    for sid in student_ids:
        final_results = get_final_results(student_id=sid, class_id=class_id, term=term)
        if not final_results:
            continue
        fr = final_results[0]
        final_results_data.append({
            "Student Name": student_map[sid]["full_name"],
            "Class": class_name,
            "Term": term,
            "Grand Total": fr.get("grand_total"),
            "Aggregate": fr.get("aggregate"),
            "Final Grade": fr.get("final_grade"),
            "Descriptor": fr.get("descriptor"),
            "Remark": fr.get("remark")
        })

    if final_results_data:
        st.markdown("### 🏆 Final Results")
        df_final = pd.DataFrame(final_results_data)
        st.table(df_final)
    else:
        st.info("No final results found for selected student(s).")

    # ------------------------------ Display Subject-Level Scores ------------------------------
    for sid in student_ids:
        st.markdown(f"### 📊 Subject Scores: {student_map[sid]['full_name']}")
        scores = get_student_scores_with_subjects(student_id=sid, class_id=class_id)
        if not scores:
            st.info("No subject-level scores found.")
            continue

        df_scores = pd.DataFrame(scores)
        # Reorder columns for clarity
        df_scores = df_scores[
            ["subject_name", "class_score", "exam_score", "weighted_class_score", "weighted_exam_score", "total_score"]
        ].rename(columns={
            "subject_name": "Subject",
            "class_score": "Class Score",
            "exam_score": "Exam Score",
            "weighted_class_score": "Weighted Class Score",
            "weighted_exam_score": "Weighted Exam Score",
            "total_score": "Total Score"
        })

        st.dataframe(df_scores, width="stretch")

        # CSV download per student
        csv_data = df_scores.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 Download {student_map[sid]['full_name']} Scores CSV",
            data=csv_data,
            file_name=f"{student_map[sid]['full_name'].replace(' ', '_')}_scores_term{term}.csv",
            mime="text/csv"
        )
