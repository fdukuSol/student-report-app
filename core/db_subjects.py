# core/db_subjects.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------------------------
# Internal helper for safe requests
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Subjects CRUD
# -------------------------------------------------------------------
def get_subjects():
    return _safe_execute(
        supabase.table("subjects")
        .select("*")
        .order("subject_name", desc=False)
    )

def create_subject(subject_name: str, subject_type: str = "core"):
    if not subject_name.strip():
        st.error("Subject name is required.")
        return []

    return _safe_execute(
        supabase.table("subjects")
        .insert({
            "subject_name": subject_name.strip(),
            "subject_type": subject_type
        })
    )

def update_subject(subject_id: str, subject_name: str, subject_type: str = "core"):
    if not subject_name.strip():
        st.error("Subject name is required.")
        return []

    return _safe_execute(
        supabase.table("subjects")
        .update({
            "subject_name": subject_name.strip(),
            "subject_type": subject_type
        })
        .eq("id", subject_id)
    )

def delete_subject(subject_id: str):
    return _safe_execute(
        supabase.table("subjects")
        .delete()
        .eq("id", subject_id)
    )
