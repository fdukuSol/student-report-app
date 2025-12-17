# navigation.py
from pages.login import login_page
from pages.admin.admin_dashboard import admin_dashboard_page
from pages.teacher.teacher_dashboard import teacher_dashboard_page
from core.auth import get_current_user

def go_to_dashboard():
    user = get_current_user()
    if not user:
        login_page()  # call function instead of switch_page
    elif user.get("role") == "admin":
        admin_dashboard_page()
    else:
        teacher_dashboard_page()
