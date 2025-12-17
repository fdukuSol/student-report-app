# core/db_teachers.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx
import csv
import io

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ROLES = ["admin", "teacher"]

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
# Teachers CRUD
# -----------------------------
def get_teachers():
    """Return all teacher profiles with assigned classes."""
    return _safe_execute(
        supabase.table("profiles")
        .select("*")
        .eq("role", "teacher")
    )

def create_teacher(full_name: str, email: str, password: str, classes: list = None):
    """
    Create a new teacher: 
    1. Create auth user via Service Role
    2. Insert profile with role=teacher and assigned classes
    """
    if not full_name or not email or not password:
        st.error("Full Name, Email, and Password are required.")
        return []

    try:
        # 1️⃣ Create auth user
        user_resp = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })
        user_id = user_resp.user.id

        # 2️⃣ Insert profile
        data = {
            "id": user_id,
            "full_name": full_name.strip(),
            "role": "teacher",
            "assigned_classes": classes or []
        }

        return _safe_execute(supabase.table("profiles").insert(data))
    except Exception as e:
        st.error(f"⚠️ Failed to create teacher: {str(e)}")
        return []

def update_teacher(user_id: str, full_name: str, email: str = None, password: str = None, classes: list = None, role: str = "teacher"):
    """Update teacher profile and optionally password."""
    if role not in ROLES:
        st.error("Invalid role selected.")
        return []

    try:
        # Update profile
        data = {"full_name": full_name.strip(), "role": role}
        if classes is not None:
            data["assigned_classes"] = classes
        if email:
            data["email"] = email.strip()

        _safe_execute(supabase.table("profiles").update(data).eq("id", user_id))

        # Update password if provided
        if password:
            supabase.auth.admin.update_user(user_id, password=password)

        return True
    except Exception as e:
        st.error(f"⚠️ Failed to update teacher: {str(e)}")
        return []

def delete_teacher(user_id: str):
    """Delete teacher from profiles and auth.users."""
    try:
        _safe_execute(supabase.table("profiles").delete().eq("id", user_id))
        supabase.auth.admin.delete_user(user_id)
        return True
    except Exception as e:
        st.error(f"⚠️ Failed to delete teacher: {str(e)}")
        return []

# -----------------------------
# Bulk upload
# -----------------------------
def bulk_create_teachers(csv_file):
    """
    CSV columns: full_name,email,password,classes (comma-separated class names)
    """
    if not csv_file:
        st.error("No file provided.")
        return []

    try:
        decoded = io.StringIO(csv_file.getvalue().decode())
        reader = csv.DictReader(decoded)
        results = []
        for row in reader:
            class_list = [c.strip() for c in row.get("classes", "").split(",") if c.strip()]
            res = create_teacher(
                full_name=row["full_name"],
                email=row["email"],
                password=row["password"],
                classes=class_list
            )
            results.append(res)
        st.success(f"{len(results)} teachers added successfully!")
        return results
    except Exception as e:
        st.error(f"⚠️ Bulk upload error: {str(e)}")
        return []
