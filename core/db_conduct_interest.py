# core/db_conduct_interest.py
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
# Student Conduct/Interest/Attendance CRUD
# -------------------------------------------------------------------
def get_student_conduct_interest(student_id=None, class_id=None, term=None):
    """
    Fetch student conduct/interest/attendance entries.
    Optional filters: student_id, class_id, term
    """
    query = supabase.table("student_conduct_interest").select("*")
    if student_id:
        query = query.eq("student_id", student_id)
    if class_id:
        query = query.eq("class_id", class_id)
    if term:
        query = query.eq("term", term)
    return _safe_execute(query)

def save_student_conduct_interest(student_id, class_id, term, conduct_id, interest_id, attendance):
    """
    Insert or update a student_conduct_interest entry.
    """
    # Check if entry exists
    existing = get_student_conduct_interest(student_id, class_id, term)
    
    data = {
        "student_id": student_id,
        "class_id": class_id,
        "term": term,
        "conduct_id": conduct_id,
        "interest_id": interest_id,
        "attendance": attendance
    }
    
    if existing:
        return _safe_execute(
            supabase.table("student_conduct_interest")
            .update(data)
            .eq("student_id", student_id)
            .eq("class_id", class_id)
            .eq("term", term)
        )
    else:
        return _safe_execute(
            supabase.table("student_conduct_interest")
            .insert(data)
        )

def delete_student_conduct_interest(student_id, class_id, term):
    """
    Delete a student_conduct_interest entry.
    """
    return _safe_execute(
        supabase.table("student_conduct_interest")
        .delete()
        .eq("student_id", student_id)
        .eq("class_id", class_id)
        .eq("term", term)
    )
