# core/db_score_settings.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ACADEMIC_LEVELS = ["Nursery", "KG", "Lower Primary", "Upper Primary", "JHS"]


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
# Score Settings CRUD
# -----------------------------
def get_score_settings():
    return _safe_execute(
        supabase.table("score_settings").select("*").order("academic_level")
    )


def create_score_setting(
    academic_level: str,
    has_components: bool,
    class_weight: float,
    exam_weight: float,
    max_class_score: float,
    max_exam_score: float,
):
    if academic_level not in ACADEMIC_LEVELS:
        st.error("Invalid academic level.")
        return []

    return _safe_execute(
        supabase.table("score_settings").insert(
            {
                "academic_level": academic_level,
                "has_components": has_components,
                "class_weight": class_weight,
                "exam_weight": exam_weight,
                "max_class_score": max_class_score,
                "max_exam_score": max_exam_score,
            }
        )
    )


def update_score_setting(setting_id: str, data: dict):
    return _safe_execute(
        supabase.table("score_settings").update(data).eq("id", setting_id)
    )


def delete_score_setting(setting_id: str):
    return _safe_execute(supabase.table("score_settings").delete().eq("id", setting_id))


def get_score_setting_for_level(academic_level: str):
    rows = _safe_execute(
        supabase.table("score_settings")
        .select("*")
        .eq("academic_level", academic_level)
        .limit(1)
    )
    return rows[0] if rows else None
