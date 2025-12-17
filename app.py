import streamlit as st
from core.auth import is_authenticated, get_current_user
from core.auth import login

# ----CSS FOR WHOLE APP ---- 
st.markdown(
    """
    <style>
    /* ===============================
       App Background
    =============================== */
    .stApp {
        background-color: #f3f4f6; /* light grey */
    }

    section[data-testid="stSidebar"] {
        background-color: #e5e7eb;
    }

    html, body, [class*="css"] {
        color: #111827;
    }

    /* ===============================
       Text Inputs & Textareas
    =============================== */
    input, textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px;
    }

    input:focus, textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 1px #2563eb !important;
    }

    /* ===============================
       Number Inputs (BaseWeb)
    =============================== */
    div[data-baseweb="input"] input {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px;
    }

    /* ===============================
       Selectbox / Dropdown (BaseWeb)
    =============================== */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px;
    }

    div[data-baseweb="select"] span {
        color: #111827 !important;
    }

    /* Dropdown menu container */
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px;
    }

    /* Dropdown options */
    li[role="option"] {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    li[role="option"]:hover {
        background-color: #e0e7ff !important;
    }

    /* ===============================
       Buttons
    =============================== */
    button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 6px;
        border: none;
    }

    button:hover {
        background-color: #1d4ed8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- END OF CSS FOR WHOLE APP ----

# --- Force full-width layout for all pages ---
st.set_page_config(page_title="Student Report App", layout="wide")

# --- Show login if not authenticated ---
if not is_authenticated():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user, error = login(email, password)
        if error:
            st.error(error)
        else:
            st.success("Login successful!")
            st.rerun()
    st.stop()  # stop execution until logged in

# --- Authenticated user ---
user = get_current_user()

# --- Route to the correct dashboard based on role ---
if user["role"] == "admin":
    from pages.admin.admin_dashboard import admin_dashboard_page

    admin_dashboard_page()
elif user["role"] == "teacher":
    from pages.teacher.teacher_dashboard import teacher_dashboard_page

    teacher_dashboard_page()
