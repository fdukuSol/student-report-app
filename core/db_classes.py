# core/db_classes.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx

# Load environment variables
load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ACADEMIC_LEVELS = ["Nursery", "KG", "Lower Primary", "Upper Primary", "JHS"]


# -------------------------------------------------------------------
# Internal helper for safe requests
# -------------------------------------------------------------------
def _safe_execute(request):
    try:
        resp = request.execute()
        return resp.data or []
    except httpx.ConnectError:
        st.warning("⚠️ Unable to reach database — please check your internet connection.")
        return []
    except Exception as e:
        st.error(f"⚠️ Database error: {str(e)}")
        return []


# -------------------------------------------------------------------
# Classes CRUD
# -------------------------------------------------------------------
def get_classes():
    return _safe_execute(
        supabase.table("classes")
        .select("*")
        .order("academic_level", desc=False)
        .order("class_name", desc=False)
    )


def create_class(class_name: str, academic_level: str):
    if academic_level not in ACADEMIC_LEVELS:
        st.error("Invalid academic level selected.")
        return []

    return _safe_execute(
        supabase.table("classes")
        .insert({
            "class_name": class_name.strip(),
            "academic_level": academic_level
        })
    )


def update_class(class_id: str, class_name: str, academic_level: str):
    if academic_level not in ACADEMIC_LEVELS:
        st.error("Invalid academic level selected.")
        return []

    return _safe_execute(
        supabase.table("classes")
        .update({
            "class_name": class_name.strip(),
            "academic_level": academic_level
        })
        .eq("id", class_id)
    )


def delete_class(class_id: str):
    return _safe_execute(
        supabase.table("classes")
        .delete()
        .eq("id", class_id)
    )
