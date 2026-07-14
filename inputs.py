import streamlit as st

from analysis import grades_to_numeric, growth_score
from constants import (
    CLUB_TYPE_WEIGHTS,
    EVENT_TYPE_WEIGHTS,
    GRADE_OPTIONS,
    MAX_CERTIFICATIONS,
    MAX_CLUBS,
    MAX_EVENTS,
    MAX_LINKEDIN_CONNECTIONS,
    MAX_LINKEDIN_POSTS,
    SEARCH_PAGE_SIZE,
    SUBJECTS_BY_SEMESTER,
)


def mentor_selection():
    st.subheader("Mentor Selection")
    if st.session_state.role == "mentor":
        st.info(f"Mentor is locked to your account: {st.session_state.mentor}")
        return
    mentors = st.session_state.data.list_mentors()
    mentor = st.selectbox("Mentor", mentors)
    st.session_state.mentor = mentor
    st.success(f"Mentor selected: {mentor}")


def student_selection():
    st.subheader("Student Selection")
    mentor = st.session_state.mentor
    if not mentor:
        st.info("Select a mentor first.")
        return
    query = st.text_input("Search by SRN or Name", key="student_search")
    page_index = st.number_input("Page", min_value=1, value=1, step=1, key="student_page")
    offset = (page_index - 1) * SEARCH_PAGE_SIZE
    srns, total = st.session_state.data.search_students(
        mentor,
        query,
        offset=offset,
        limit=SEARCH_PAGE_SIZE,
    )
    total_pages = max(1, (total + SEARCH_PAGE_SIZE - 1) // SEARCH_PAGE_SIZE)
    if page_index > total_pages:
        page_index = total_pages
        offset = (page_index - 1) * SEARCH_PAGE_SIZE
        srns, total = st.session_state.data.search_students(
            mentor,
            query,
            offset=offset,
            limit=SEARCH_PAGE_SIZE,
        )
    st.caption(f"Results: {total} | Page {page_index} of {total_pages}")
    if not srns:
        st.warning("No students assigned to this mentor.")
        return
    options = [f"{srn} - {st.session_state.data.get_student(srn)['name']}" for srn in srns]
    choice = st.selectbox("Student", options)
    st.session_state.student = choice.split(" - ")[0]


def semester_input():
    st.subheader("Semester Input")
    srn = st.session_state.student
    if not srn:
        st.info("Select a student first.")
        return

    semester = st.selectbox("Semester", sorted(SUBJECTS_BY_SEMESTER.keys()))
    existing_sessions = st.session_state.data.get_sessions(srn, semester)
    st.caption(f"Sessions saved: {len(existing_sessions)} / 2")
    if len(existing_sessions) >= 2:
        st.warning("Maximum sessions reached for this semester.")

    st.markdown("### 🧠 Skills")
    subjects = SUBJECTS_BY_SEMESTER.get(semester, [])
    grades = []
    for idx, name in enumerate(subjects, start=1):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input(f"Subject {idx}", value=name, disabled=True)
        with col2:
            grades.append(st.selectbox(f"Grade {idx}", GRADE_OPTIONS, index=1))

    st.markdown("### 📊 Behavior")
    study_normal = st.slider("Study Hours (Normal)", 0.0, 12.0, 6.0, 0.5)
    study_exam = st.slider("Study Hours (Exam)", 0.0, 12.0, 8.0, 0.5)
    sleep_normal = st.slider("Sleep (Normal)", 0.0, 10.0, 7.0, 0.5)
    sleep_exam = st.slider("Sleep (Exam)", 0.0, 10.0, 6.0, 0.5)
    screen_normal = st.slider("Screen Time (Normal)", 0.0, 12.0, 4.0, 0.5)
    screen_exam = st.slider("Screen Time (Exam)", 0.0, 12.0, 4.0, 0.5)
    screen_holiday = st.slider("Screen Time (Holiday)", 0.0, 12.0, 6.0, 0.5)
    attendance = st.slider("Attendance", 0, 100, 85)
    assignments = st.slider("Assignments", 0, 10, 6)
    project_submissions = st.slider("Project Submissions", 0, 10, 5)

    study_hours = round((study_normal * 0.6) + (study_exam * 0.4), 2)
    sleep_hours = round((sleep_normal * 0.7) + (sleep_exam * 0.3), 2)
    screen_time = round(
        (screen_normal * 0.5) + (screen_exam * 0.3) + (screen_holiday * 0.2),
        2,
    )
    behavior = {
        "StudyHours": study_hours,
        "SleepHours": sleep_hours,
        "Attendance": attendance,
        "Assignments": assignments,
        "ProjectSubmissions": project_submissions,
        "ScreenTime": screen_time,
    }

    st.caption(
        f"Final Study Hours: {study_hours:.2f} | "
        f"Final Sleep Score: {sleep_hours:.2f} | "
        f"Final Screen Score: {screen_time:.2f}"
    )

    st.markdown("### 🌐 Growth")
    club_count = st.number_input(
        "Number of new clubs joined",
        min_value=0,
        max_value=MAX_CLUBS,
        value=0,
        step=1,
    )
    club_type = st.selectbox("Club Type", list(CLUB_TYPE_WEIGHTS.keys()))
    event_count = st.number_input(
        "Number of events attended",
        min_value=0,
        max_value=MAX_EVENTS,
        value=0,
        step=1,
    )
    event_type = st.selectbox("Event Type", list(EVENT_TYPE_WEIGHTS.keys()))
    certifications = st.number_input(
        "Number of new certifications",
        min_value=0,
        max_value=MAX_CERTIFICATIONS,
        value=0,
        step=1,
    )
    linkedin_connections = st.number_input(
        "LinkedIn connections increased",
        min_value=0,
        max_value=MAX_LINKEDIN_CONNECTIONS,
        value=0,
        step=10,
    )
    linkedin_posts = st.number_input(
        "LinkedIn posts made",
        min_value=0,
        max_value=MAX_LINKEDIN_POSTS,
        value=0,
        step=1,
    )

    clubs_score = club_count * CLUB_TYPE_WEIGHTS.get(club_type, 1.0)
    events_score = event_count * EVENT_TYPE_WEIGHTS.get(event_type, 1.0)
    linkedin_score = (linkedin_connections / 50.0) + (linkedin_posts * 0.5)
    growth = {
        "ClubsScore": round(clubs_score, 2),
        "EventsScore": round(events_score, 2),
        "Certifications": float(certifications),
        "LinkedInScore": round(linkedin_score, 2),
    }
    final_growth_score = growth_score(growth)
    st.caption(f"Growth Score: {final_growth_score:.1f} / 10")

    if st.button("Save Session", disabled=len(existing_sessions) >= 2):
        grades_numeric = grades_to_numeric(grades)
        subject_grades = {name: grade for name, grade in zip(subjects, grades)}
        session = {
            "subjects": subject_grades,
            "subjects_list": subjects,
            "grades": grades,
            "grades_numeric": grades_numeric,
            "behavior": behavior,
            "growth": growth,
            "behavior_details": {
                "StudyHoursNormal": study_normal,
                "StudyHoursExam": study_exam,
                "SleepNormal": sleep_normal,
                "SleepExam": sleep_exam,
                "ScreenTimeNormal": screen_normal,
                "ScreenTimeExam": screen_exam,
                "ScreenTimeHoliday": screen_holiday,
            },
            "growth_details": {
                "ClubCount": int(club_count),
                "ClubType": club_type,
                "EventCount": int(event_count),
                "EventType": event_type,
                "Certifications": int(certifications),
                "LinkedInConnections": int(linkedin_connections),
                "LinkedInPosts": int(linkedin_posts),
            },
        }
        if st.session_state.role == "mentor" and not st.session_state.data.can_access_student(
            st.session_state.mentor,
            srn,
        ):
            st.error("You are not assigned to this student.")
            return
        ok, message = st.session_state.data.add_session(
            srn,
            semester,
            session,
            actor=st.session_state.user,
        )
        if ok:
            st.success(message)
        else:
            st.warning(message)
