# core/db_subject_assignments.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx

load_dotenv()

SUPABASE_URL = st.secrets("SUPABASE_URL")
SUPABASE_KEY = st.secrets("SUPABASE_SERVICE_ROLE_KEY")

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
# Subject assignments
# -----------------------------
def get_subjects_for_class(class_id: str):
    return _safe_execute(
        supabase.table("class_subjects")
        .select("id, subjects(id, subject_name)")
        .eq("class_id", class_id)
    )


def assign_subject_to_class(class_id: str, subject_id: str):
    return _safe_execute(
        supabase.table("class_subjects").insert(
            {"class_id": class_id, "subject_id": subject_id}
        )
    )


def remove_subject_from_class(assignment_id: str):
    return _safe_execute(
        supabase.table("class_subjects").delete().eq("id", assignment_id)
    )


def assign_subjects_to_class_bulk(class_id: str, subject_ids: list[str]):
    """
    Assign multiple subjects to a class at once.
    Duplicate assignments are ignored by DB unique constraint.
    """
    if not subject_ids:
        return []

    payload = [
        {"class_id": class_id, "subject_id": subject_id} for subject_id in subject_ids
    ]

    return _safe_execute(supabase.table("class_subjects").insert(payload))
