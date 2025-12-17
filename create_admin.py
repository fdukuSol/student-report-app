# utils/create_admin.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_admin(full_name: str, email: str, password: str):
    """
    Create a new admin user:
    1. Creates auth user in Supabase
    2. Inserts corresponding profile in public.profiles
    """
    if not full_name or not email or not password:
        print("Full Name, Email, and Password are required.")
        return None

    try:
        # 1️⃣ Create auth user via Service Role
        user_resp = supabase.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        auth_user_id = user_resp.user.id

        # 2️⃣ Insert profile in public.profiles
        profile_data = {
            "auth_user_id": auth_user_id,
            "full_name": full_name.strip(),
            "role": "admin",
            "email": email.strip(),
            "assigned_classes": [],  # Admin has no classes
        }

        resp = supabase.table("profiles").insert(profile_data).execute()

        if resp.error:
            print(f"Failed to create admin profile: {resp.error}")
            return None

        print(
            f"✅ Admin '{full_name}' created successfully with auth_user_id {auth_user_id}"
        )
        return auth_user_id

    except Exception as e:
        print(f"⚠️ Error creating admin: {str(e)}")
        return None


if __name__ == "__main__":
    # Replace with your desired admin credentials
    create_admin(full_name="Admin", email="admin@school.com", password="admin98765")
