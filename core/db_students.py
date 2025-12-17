# core/db_students.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import httpx

# Load environment variables
load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Internal helper for safe requests
# -----------------------------
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

# -----------------------------
# Students CRUD
# -----------------------------
def get_students():
    """Return all student records."""
    return _safe_execute(
        supabase.table("students")
        .select("*")
    )

def create_student(full_name: str, assigned_class: str):
    """Create a new student record."""
    if not full_name or not assigned_class:
        st.error("Full Name and Class are required.")
        return []

    data = {
        "full_name": full_name.strip(),
        "assigned_class": assigned_class.strip()
    }

    return _safe_execute(supabase.table("students").insert(data))

def update_student(student_id: str, full_name: str, assigned_class: str):
    """Update an existing student record."""
    data = {
        "full_name": full_name.strip(),
        "assigned_class": assigned_class.strip()
    }
    return _safe_execute(supabase.table("students").update(data).eq("id", student_id))

def delete_student(student_id: str):
    """Delete a student record."""
    return _safe_execute(supabase.table("students").delete().eq("id", student_id))

# -----------------------------
# Bulk upload students
# -----------------------------
def bulk_create_students(df: pd.DataFrame):
    """
    Bulk create students from a DataFrame.
    Expected columns: full_name, assigned_class
    Returns number of successfully added students.
    """
    added_count = 0
    for _, row in df.iterrows():
        full_name = str(row.get("full_name", "")).strip()
        assigned_class = str(row.get("assigned_class", "")).strip()

        if full_name and assigned_class:
            create_student(full_name, assigned_class)
            added_count += 1
    return added_count
