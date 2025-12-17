#core/db_student_scores.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import httpx
import streamlit as st

load_dotenv()

SUPABASE_URL = st.secrets("SUPABASE_URL")
SUPABASE_KEY = st.secrets("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------
# Safe execution helper
# -------------------------------------------------
def _safe_execute(request):
    try:
        resp = request.execute()
        return resp.data or []
    except httpx.ConnectError:
        raise RuntimeError("Database unreachable")
    except Exception as e:
        raise RuntimeError(str(e))

# -------------------------------------------------
# SCORE SETTINGS
# -------------------------------------------------
def get_score_setting_for_level(academic_level: str):
    result = _safe_execute(
        supabase.table("score_settings")
        .select("*")
        .eq("academic_level", academic_level)
        .limit(1)
    )
    return result[0] if result else None

# -------------------------------------------------
# GRADING SCALE
# -------------------------------------------------
def resolve_grade_and_remark(total_score: float):
    rows = _safe_execute(
        supabase.table("grading_scales")
        .select("grade, remark")
        .lte("min_score", total_score)
        .gte("max_score", total_score)
        .limit(1)
    )

    if not rows:
        raise ValueError(f"No grading scale for score {total_score}")

    return rows[0]["grade"], rows[0]["remark"]

# -------------------------------------------------
# SCORE COMPUTATION
# -------------------------------------------------
def compute_scores(
    academic_level: str,
    class_score: int | None,
    exam_score: int | None
):
    setting = get_score_setting_for_level(academic_level)
    if not setting:
        raise ValueError("Score settings not found for academic level")

    # No components (KG, Nursery, JHS)
    if not setting["has_components"]:
        total = int(exam_score or 0)
        grade, remark = resolve_grade_and_remark(total)

        return {
            "weighted_class_score": None,
            "weighted_exam_score": None,
            "total_score": total,
            "grade": int(grade),
            "remark": remark
        }

    # Weighted computation
    wc = (class_score / setting["max_class_score"]) * setting["class_weight"]
    we = (exam_score / setting["max_exam_score"]) * setting["exam_weight"]

    total = wc + we

    # 🔒 FORCE INTEGERS
    wc_i = int(round(wc))
    we_i = int(round(we))
    total_i = int(round(total))

    grade, remark = resolve_grade_and_remark(total_i)

    return {
        "weighted_class_score": wc_i,
        "weighted_exam_score": we_i,
        "total_score": total_i,
        "grade": int(grade),
        "remark": remark
    }

# -------------------------------------------------
# UPSERT STUDENT SUBJECT SCORE
# -------------------------------------------------
def save_student_subject_score(
    *,
    student_id: str,
    class_id: str,
    subject_id: str,
    academic_level: str,
    class_score: float | None,
    exam_score: float | None
):
    computed = compute_scores(
        academic_level,
        class_score,
        exam_score
    )

    payload = {
        "student_id": student_id,
        "class_id": class_id,
        "subject_id": subject_id,
        "academic_level": academic_level,

        "class_score": class_score,
        "exam_score": exam_score,

        **computed
    }

    return _safe_execute(
        supabase.table("student_scores")
        .upsert(
            payload,
            on_conflict="student_id,subject_id"
        )
    )

# -------------------------------------------------
# BULK SAVE (MULTIPLE SUBJECTS AT ONCE)
# -------------------------------------------------
def save_student_scores_bulk(
    *,
    student_id: str,
    class_id: str,
    academic_level: str,
    subject_scores: list[dict]
):
    """
    subject_scores = [
      {
        "subject_id": "...",
        "class_score": 30,
        "exam_score": 70
      }
    ]
    """

    payload = []

    for row in subject_scores:
        computed = compute_scores(
            academic_level,
            row.get("class_score"),
            row.get("exam_score")
        )

        payload.append({
            "student_id": student_id,
            "class_id": class_id,
            "subject_id": row["subject_id"],
            "academic_level": academic_level,

            "class_score": row.get("class_score"),
            "exam_score": row.get("exam_score"),

            **computed
        })

    return _safe_execute(
        supabase.table("student_scores")
        .upsert(
            payload,
            on_conflict="student_id,subject_id"
        )
    )

# -------------------------------------------------
# FETCH STUDENT SCORES
# -------------------------------------------------
def get_student_scores(*, student_id: str, class_id: str) -> list[dict]:
    """
    Fetch all scores for a student in a given class and term.
    Returns a list of dicts containing:
    - subject_id
    - subject_name
    - total_score
    - grade
    - remark
    - subject_type (core/elective/other)
    """

    rows = _safe_execute(
        supabase.table("student_scores")
        .select("student_id, class_id, subject_id, total_score, grade, remark, academic_level, subject_id (subject_name, subject_type)")
        .eq("student_id", student_id)
        .eq("class_id", class_id)
    )

    # Flatten the nested subject info
    for r in rows:
        subject_info = r.pop("subject_id", {})
        r["subject_name"] = subject_info.get("subject_name")
        r["subject_type"] = subject_info.get("subject_type", "other")

    return rows
