# core/services/final_result_engine.py

from core.db_student_scores import get_student_scores
from core.db_final_grading_scales import get_final_grading_scales

# -------------------------------
# Configuration
# -------------------------------
EXCLUDED_LEVELS = ["kg", "nursery"]

# Map class academic levels to allowed 'level' values in student_final_results table
LEVEL_MAP = {
    "kg": None,
    "nursery": None,
    "lower primary": "primary",
    "upper primary": "primary",
    "primary": "primary",
    "jhs": "jhs"
}

CORE_SUBJECT_TYPE = "core"
ELECTIVE_SUBJECT_TYPE = "elective"


def generate_final_result(*, student_id: str, class_id: str, term: int, level: str) -> dict | None:
    """
    Generate final result for one student based on numeric grades.
    Returns a dict ready for DB insert OR None if excluded level (KG/Nursery).
    """

    # Normalize level
    level_key = level.lower()
    normalized_level = LEVEL_MAP.get(level_key)
    if not normalized_level:
        # Excluded level
        return None

    # --------------------------------------------------
    # Fetch student scores
    # --------------------------------------------------
    scores = get_student_scores(student_id=student_id, class_id=class_id)
    if not scores:
        return None

    # --------------------------------------------------
    # Compute grand total
    # --------------------------------------------------
    grand_total = sum(s.get("total_score", 0) for s in scores)

    # --------------------------------------------------
    # Compute aggregate for JHS
    # --------------------------------------------------
    aggregate = None
    if normalized_level == "jhs":
        core_scores = [s["grade"] for s in scores if s.get("subject_type") == CORE_SUBJECT_TYPE]
        elective_scores = [s["grade"] for s in scores if s.get("subject_type") == ELECTIVE_SUBJECT_TYPE]

        core_sum = sum(core_scores) if core_scores else 0
        best_electives = sorted(elective_scores)[:2] if elective_scores else []
        elective_sum = sum(best_electives)

        aggregate = core_sum + elective_sum

    # --------------------------------------------------
    # Resolve final grading scale
    # --------------------------------------------------
    grading_scales = get_final_grading_scales(normalized_level)

    final_grade = "N/A"
    descriptor = None
    remark = None

    # Use aggregate for JHS, grand_total for primary
    compare_value = aggregate if normalized_level == "jhs" else grand_total

    for scale in grading_scales:
        if scale["min_value"] <= compare_value <= scale["max_value"]:
            final_grade = scale["final_grade"]
            descriptor = scale.get("descriptor")
            remark = scale.get("remark")
            break

    # --------------------------------------------------
    # Return structured result
    # --------------------------------------------------
    return {
        "student_id": student_id,
        "class_id": class_id,
        "term": term,
        "level": normalized_level,
        "grand_total": grand_total,
        "aggregate": aggregate,
        "final_grade": final_grade,
        "descriptor": descriptor,
        "remark": remark
    }


def generate_final_results_for_class(class_id: str, term: int, level: str, student_ids: list[str]) -> list[dict]:
    """
    Generate final results for multiple students in a class.
    Returns a list of structured result dicts.
    """
    results = []
    for sid in student_ids:
        res = generate_final_result(student_id=sid, class_id=class_id, term=term, level=level)
        if res:
            results.append(res)
    return results
