# core/auth.py
from supabase import create_client
import streamlit as st
import os

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        user = response.user
        session = response.session

        if not user:
            return None, "Invalid email or password"

        # ✅ SAFE profile fetch (no single / maybe_single)
        resp = (
            supabase.table("profiles")
            .select("*")
            .eq("auth_user_id", user.id)
            .limit(1)
            .execute()
        )

        profiles = resp.data or []

        if not profiles:
            return None, "User profile not found. Contact administrator."

        profile = profiles[0]

        st.session_state["auth"] = {
            "auth_user_id": user.id,
            "profile_id": profile["id"],
            "email": user.email,
            "role": profile["role"],
            "full_name": profile["full_name"],
            "session": session,
        }

        return user, None

    except Exception as e:
        return None, str(e)


def logout():
    """Logout the current user"""
    supabase.auth.sign_out()
    st.session_state.clear()


def is_authenticated():
    """Check if user is logged in"""
    return "auth" in st.session_state


def get_current_user():
    """Return current logged-in user info"""
    return st.session_state.get("auth") if is_authenticated() else None

def logout_user():
    """Clear Streamlit session and logout from Supabase"""
    supabase.auth.sign_out()
    st.session_state.clear()
