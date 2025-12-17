# core/db_grading_scales.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx

load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Safe execution helper
# -----------------------------
def _safe_execute(request):
    try:
        resp = request.execute()
        return resp.data or []
    except httpx.ConnectError:
        st.warning("⚠️ Database unreachable.")
        return []
    except Exception as e:
        st.error(f"⚠️ Database error: {e}")
        return []

# -----------------------------
# Grading Scales CRUD
# -----------------------------
def get_grading_scales():
    return _safe_execute(
        supabase.table("grading_scales")
        .select("*")
        .order("min_score", desc=False)
    )

def create_grading_scale(min_score, max_score, grade, remark):
    if min_score > max_score:
        st.error("Min score cannot exceed max score.")
        return []

    return _safe_execute(
        supabase.table("grading_scales").insert({
            "min_score": min_score,
            "max_score": max_score,
            "grade": grade,
            "remark": remark
        })
    )

def update_grading_scale(scale_id: str, data: dict):
    return _safe_execute(
        supabase.table("grading_scales")
        .update(data)
        .eq("id", scale_id)
    )

def delete_grading_scale(scale_id: str):
    return _safe_execute(
        supabase.table("grading_scales")
        .delete()
        .eq("id", scale_id)
    )
