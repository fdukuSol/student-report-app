# core/db_admin_settings.py
from supabase import Client, create_client
import os
from dotenv import load_dotenv
import streamlit as st
import httpx

# Load environment variables
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

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
# Conduct CRUD
# -----------------------------
def get_all_conduct():
    return _safe_execute(
        supabase.table("conduct_settings").select("*").order("conduct_name")
    )

def add_conduct(conduct_name: str):
    name = conduct_name.strip()
    if not name:
        return
    # check if exists
    existing = _safe_execute(
        supabase.table("conduct_settings").select("*").eq("conduct_name", name)
    )
    if existing:
        st.info(f"Conduct '{name}' already exists.")
        return
    # insert
    return _safe_execute(
        supabase.table("conduct_settings").insert({"conduct_name": name})
    )


def update_conduct(conduct_id: int, conduct_name: str):
    return _safe_execute(
        supabase.table("conduct_settings").update({"conduct_name": conduct_name.strip()}).eq("id", conduct_id)
    )

def delete_conduct(conduct_id: int):
    return _safe_execute(
        supabase.table("conduct_settings").delete().eq("id", conduct_id)
    )

# -----------------------------
# Interest CRUD
# -----------------------------
def get_all_interest():
    return _safe_execute(
        supabase.table("interest_settings").select("*").order("interest_name")
    )

def add_interest(interest_name: str):
    name = interest_name.strip()
    if not name:
        return
    # check if exists
    existing = _safe_execute(
        supabase.table("interest_settings").select("*").eq("interest_name", name)
    )
    if existing:
        st.info(f"Interest '{name}' already exists.")
        return
    # insert
    return _safe_execute(
        supabase.table("interest_settings").insert({"interest_name": name})
    )

def update_interest(interest_id: int, interest_name: str):
    return _safe_execute(
        supabase.table("interest_settings").update({"interest_name": interest_name.strip()}).eq("id", interest_id)
    )

def delete_interest(interest_id: int):
    return _safe_execute(
        supabase.table("interest_settings").delete().eq("id", interest_id)
    )
