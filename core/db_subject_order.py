from supabase import create_client, Client
import os
from dotenv import load_dotenv
import httpx
import streamlit as st

load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Safe execution helper
def _safe_execute(request):
    try:
        resp = request.execute()
        return resp.data or []
    except httpx.ConnectError:
        raise RuntimeError("Database unreachable")
    except Exception as e:
        raise RuntimeError(str(e))


# Fetch ordered subjects for a class
def get_subject_order_for_class(class_id: str):
    """
    Returns list of subjects with their sort_order for a class.
    """
    return _safe_execute(
        supabase.table("class_subject_order")
        .select("subject_id, sort_order, subjects(id, subject_name)")
        .eq("class_id", class_id)
        .order("sort_order")
    )


# Save (replace) subject order
def save_subject_order(class_id: str, ordered_subject_ids: list[str]):
    """
    Replace existing subject order for a class.
    """
    if not ordered_subject_ids:
        raise ValueError("No subject IDs provided to save.")

    # Delete existing order
    _safe_execute(
        supabase.table("class_subject_order").delete().eq("class_id", class_id)
    )

    # Prepare payload
    payload = [
        {"class_id": class_id, "subject_id": subject_id, "sort_order": index + 1}
        for index, subject_id in enumerate(ordered_subject_ids)
    ]

    # Debug: print payload
    print("DEBUG: Saving class_subject_order payload:", payload)

    # Insert new order
    return _safe_execute(supabase.table("class_subject_order").insert(payload))
