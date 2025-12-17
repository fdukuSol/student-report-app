# core/db_student_final_results.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import httpx
import streamlit as st

# Load environment variables
load_dotenv()
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------
# Safe execution helper
# -------------------------------------------------
def _safe_execute(request):
    try:
        resp = request.execute()
        return resp.data or []
    except httpx.ConnectError:
        st.warning("⚠️ Unable to reach database — check your internet connection.")
        return []
    except Exception as e:
        st.error(f"⚠️ Database error: {str(e)}")
        return []

# -------------------------------------------------
# UPSERT FINAL RESULT FOR ONE STUDENT
# -------------------------------------------------
def save_final_result(final_result: dict):
    """
    Upsert a final result for a student in a class and term.
    final_result should contain:
        student_id, class_id, term, level,
        grand_total, aggregate, final_grade, descriptor, remark
    """
    payload = {
        "student_id": final_result["student_id"],
        "class_id": final_result["class_id"],
        "term": final_result["term"],
        "level": final_result["level"],
        "grand_total": final_result.get("grand_total"),
        "aggregate": final_result.get("aggregate"),
        "final_grade": final_result.get("final_grade"),
        "descriptor": final_result.get("descriptor"),
        "remark": final_result.get("remark")
    }

    return _safe_execute(
        supabase.table("student_final_results")
        .upsert(
            payload,
            on_conflict="student_id,class_id,term"
        )
    )

# -------------------------------------------------
# BULK UPSERT FINAL RESULTS
# -------------------------------------------------
def save_final_results_bulk(final_results: list[dict]):
    """
    Bulk upsert multiple final results.
    """
    payload = []
    for fr in final_results:
        payload.append({
            "student_id": fr["student_id"],
            "class_id": fr["class_id"],
            "term": fr["term"],
            "level": fr["level"],
            "grand_total": fr.get("grand_total"),
            "aggregate": fr.get("aggregate"),
            "final_grade": fr.get("final_grade"),
            "descriptor": fr.get("descriptor"),
            "remark": fr.get("remark")
        })

    return _safe_execute(
        supabase.table("student_final_results")
        .upsert(payload, on_conflict="student_id,class_id,term")
    )

# -------------------------------------------------
# FETCH FINAL RESULTS
# -------------------------------------------------
def get_final_results(*, student_id: str | None = None, class_id: str | None = None, term: int | None = None):
    """
    Fetch final results filtered by optional student, class, and term.
    """
    query = supabase.table("student_final_results").select("*")
    
    if student_id:
        query = query.eq("student_id", student_id)
    if class_id:
        query = query.eq("class_id", class_id)
    if term:
        query = query.eq("term", term)
    
    return _safe_execute(query)
