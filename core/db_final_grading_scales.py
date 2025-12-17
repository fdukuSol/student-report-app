# core/db_final_grading_scales.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------
# Safe execute
# ---------------------------------------------------
def _safe_execute(request):
    try:
        resp = request.execute()
        return resp.data or []
    except httpx.ConnectError:
        st.warning("⚠️ Unable to reach database.")
        return []
    except Exception as e:
        st.error(f"⚠️ Database error: {e}")
        return []

# ---------------------------------------------------
# Final grading scales CRUD
# ---------------------------------------------------
def get_final_grading_scales(level: str):
    return _safe_execute(
        supabase.table("final_grading_scales")
        .select("*")
        .eq("level", level)
        .order("min_value", desc=False)
    )

def create_final_grading_scale(
    level: str,
    min_value: int,
    max_value: int,
    final_grade: str,
    remark: str,
    descriptor: str | None = None
):
    if min_value > max_value:
        st.error("Min value cannot exceed Max value.")
        return []

    data = {
        "level": level,
        "min_value": min_value,
        "max_value": max_value,
        "final_grade": final_grade.strip(),
        "remark": remark.strip(),
        "descriptor": descriptor
    }

    return _safe_execute(
        supabase.table("final_grading_scales").insert(data)
    )

def update_final_grading_scale(
    scale_id: str,
    min_value: int,
    max_value: int,
    final_grade: str,
    remark: str,
    descriptor: str | None = None
):
    if min_value > max_value:
        st.error("Min value cannot exceed Max value.")
        return []

    data = {
        "min_value": min_value,
        "max_value": max_value,
        "final_grade": final_grade.strip(),
        "remark": remark.strip(),
        "descriptor": descriptor
    }

    return _safe_execute(
        supabase.table("final_grading_scales")
        .update(data)
        .eq("id", scale_id)
    )

def delete_final_grading_scale(scale_id: str):
    return _safe_execute(
        supabase.table("final_grading_scales")
        .delete()
        .eq("id", scale_id)
    )
