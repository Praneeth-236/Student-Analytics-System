import streamlit as st
from auth import login_panel
from constants import APP_TITLE, ROLE_PAGES
from data_manager import DataManager
from dashboards import (
    admin_reports,
    admin_setup,
    analysis_dashboard,
    college_insights,
    mentor_dashboard,
)
from inputs import mentor_selection, semester_input, student_selection
from ui_layout import _hero, _load_css


st.set_page_config(page_title=APP_TITLE, layout="wide")

if "data" not in st.session_state:
    st.session_state.data = DataManager()

if "mentor" not in st.session_state:
    st.session_state.mentor = None

if "student" not in st.session_state:
    st.session_state.student = None

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

if "failed_logins" not in st.session_state:
    st.session_state.failed_logins = {}

st.title(APP_TITLE)


_load_css()


if not st.session_state.user:
    login_panel()
    st.stop()

if st.sidebar.button("Sign out"):
    st.session_state.data.log_event("logout", st.session_state.user or "unknown", "")
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.mentor = None
    st.session_state.student = None
    st.stop()

if st.session_state.role in {"admin", "hod"}:
    issues = st.session_state.data.get_validation_issues()
    if issues:
        st.sidebar.warning("Data validation issues detected.")
        st.sidebar.caption(f"Issues: {len(issues)}")

pages = ROLE_PAGES.get(st.session_state.role, ["Student Selection"])
page = st.sidebar.selectbox("Page", pages)
st.session_state.data.log_event("page_view", st.session_state.user, page)

hero_subtitles = {
    "Mentor Selection": "Assign mentors and scope the mentoring workflow.",
    "Student Selection": "Search and select a student for guided review.",
    "Semester Input": "Capture syllabus-aligned grades and behavioral metrics.",
    "Analysis Dashboard": "AI-grade insights with explainable linear algebra.",
    "Mentor Dashboard": "Track cohort risk, trends, and domain distribution.",
    "College Insights": "Macro trends across batches and semesters.",
    "Admin Reports": "Audit, validate, and export institutional summaries.",
    "Admin Setup": "Create mentors and map students to mentors.",
}
_hero(hero_subtitles.get(page, "Mentor-driven academic intelligence."))




if page == "Mentor Selection":
    mentor_selection()
elif page == "Student Selection":
    student_selection()
elif page == "Semester Input":
    semester_input()
elif page == "Analysis Dashboard":
    analysis_dashboard()
elif page == "Mentor Dashboard":
    mentor_dashboard()
elif page == "Admin Reports":
    admin_reports()
elif page == "Admin Setup":
    admin_setup()
else:
    college_insights()
