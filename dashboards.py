import csv
import io

import numpy as np
import streamlit as st

from alerts import detect_alerts
from analysis import (
    academic_strengths,
    behavior_alignment,
    behavior_deviation,
    behavior_insights,
    build_student_matrix,
    compute_covariance,
    compute_scores_matrix,
    distance_from_mean,
    distance_thresholds,
    eigen_analysis,
    growth_score,
    mean_profile_vector,
    overall_score,
    risk_level,
    semester_comparison,
    EIGEN_FEATURE_LABELS,
    STUDENT_FEATURE_LABELS,
    top_skill_gaps,
)
from college import college_suggestions, domain_distribution, semester_averages, weak_subjects
from constants import BEHAVIOR_LABELS, GROUP_WEIGHTS, SEARCH_PAGE_SIZE, SUBJECTS_BY_SEMESTER
from domain import recommend_domain
from linear_algebra import norm
from ui_layout import _format_timestamp, _semester_sort_key
from utils import color_label, format_list, risk_color, tags


def analysis_dashboard():
    st.subheader("Analysis Dashboard")
    srn = st.session_state.student
    if not srn:
        st.info("Select a student first.")
        return
    if st.session_state.role == "mentor" and not st.session_state.data.can_access_student(
        st.session_state.mentor,
        srn,
    ):
        st.error("You are not assigned to this student.")
        return

    semester = st.selectbox("Semester for Analysis", sorted(SUBJECTS_BY_SEMESTER.keys()))
    sessions = st.session_state.data.get_sessions(srn, semester)
    current = sessions[-1] if sessions else None
    if not current:
        st.info("No sessions for this semester.")
        return

    student_info = st.session_state.data.get_student(srn) or {}
    st.markdown(
        f"""
<div class="section-card">
  <span class="metric-pill">SRN: {srn}</span>
  <span class="metric-pill">Student: {student_info.get('name', 'Unknown')}</span>
  <span class="metric-pill">Semester: {semester}</span>
  <span class="metric-pill">Sessions: {len(sessions)}</span>
</div>
""",
        unsafe_allow_html=True,
    )

    prev = st.session_state.data.get_latest_session(srn, semester - 1) if semester > 1 else None

    subjects_list = current.get("subjects_list") or list(current.get("subjects", {}).keys())
    score = overall_score(current["grades_numeric"], current["behavior"], current["growth"])
    risk = risk_level(score)
    strengths, weaknesses = academic_strengths(subjects_list, current["grades_numeric"])
    behavior_str, behavior_weak = behavior_insights(current["behavior"])
    behavior_gap = behavior_deviation(current["behavior"]) * 100.0
    final_growth_score = growth_score(current["growth"])
    alerts = detect_alerts(current, prev)

    st.markdown(
        f"<div style='padding:12px; border-radius:12px; background:#f8f9fb;'>"
        f"<b>Overall Score:</b> {score:.1f} &nbsp; | &nbsp;"
        f"{color_label(f'Risk: {risk}', risk_color(risk))}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Academic Strengths / Weaknesses")
    st.markdown("**Strengths**")
    st.markdown(tags(strengths), unsafe_allow_html=True)
    st.markdown("**Weaknesses**")
    st.markdown(tags(weaknesses), unsafe_allow_html=True)

    st.markdown("### Behavior Insights")
    align_score = behavior_alignment(current["behavior"]) * 100.0
    st.write(f"Behavior Alignment: {align_score:.1f}%")
    st.write(f"Behavior Deviation: {behavior_gap:.1f}%")
    behavior_payload = current.get("behavior", {})
    if isinstance(behavior_payload, dict):
        study_value = behavior_payload.get("StudyHours", 0)
        sleep_value = behavior_payload.get("SleepHours", 0)
        screen_value = behavior_payload.get("ScreenTime", 0)
    else:
        try:
            study_value = behavior_payload[BEHAVIOR_LABELS.index("StudyHours")]
            sleep_value = behavior_payload[BEHAVIOR_LABELS.index("SleepHours")]
            screen_value = behavior_payload[BEHAVIOR_LABELS.index("ScreenTime")]
        except (IndexError, ValueError, TypeError):
            study_value = 0
            sleep_value = 0
            screen_value = 0

    st.caption(
        f"Final Study Hours: {study_value:.2f} | "
        f"Final Sleep Score: {sleep_value:.2f} | "
        f"Final Screen Score: {screen_value:.2f}"
    )
    st.markdown("**Strong Areas**")
    st.markdown(tags(behavior_str), unsafe_allow_html=True)
    st.markdown("**Needs Attention**")
    st.markdown(tags(behavior_weak), unsafe_allow_html=True)

    st.markdown("### Growth Score")
    st.progress(min(1.0, final_growth_score / 10.0))
    st.write(f"Growth Score: {final_growth_score:.1f} / 10")

    st.markdown("### Domain Recommendation")
    ranked_domains = recommend_domain(
        subjects_list,
        current["grades_numeric"],
        studied_subjects=subjects_list,
    )
    best_domain = ranked_domains[0] if ranked_domains else None
    second_domain = ranked_domains[1] if len(ranked_domains) > 1 else None
    if best_domain:
        st.write(f"Best Domain: {best_domain['domain']}")
    if second_domain:
        st.write(f"Second Best Domain: {second_domain['domain']}")
    if ranked_domains:
        for entry in ranked_domains:
            final_pct = round(entry["score"] * 100.0)
            potential_pct = round(entry["potential"] * 100.0)
            st.write(
                f"{entry['domain']}: {final_pct}% | "
                f"Potential: {potential_pct}% | "
                f"Confidence: {entry['confidence']}"
            )

        risk_color_hex = risk_color(risk)
        best_domain_score = best_domain["score"] * 100.0 if best_domain else 0.0
        st.markdown(
            f"""
<div class="section-card">
    <span class="metric-pill">🎯 Overall: {score:.1f}</span>
    <span class="metric-pill" style="background: #fff7ed; color: {risk_color_hex};">⚠️ Risk: {risk}</span>
    <span class="metric-pill">🧭 Domain: {best_domain_score:.1f}%</span>
    <span class="metric-pill">🌐 Growth: {final_growth_score:.1f} / 10</span>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("### Suggested Improvements")
    suggestions = []
    if weaknesses:
        suggestions.append("Strengthen: " + ", ".join(weaknesses[:3]))
    if behavior_weak:
        suggestions.append("Improve behavior: " + ", ".join(behavior_weak[:3]))
    if suggestions:
        st.write(format_list(suggestions))
    else:
        st.write("None")

    st.markdown("### Top 3 Skills to Build")
    skills = top_skill_gaps(subjects_list, current["grades_numeric"], count=3)
    st.write(format_list(skills))

    st.markdown("### Alerts")
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.write("None")

    with st.expander("How scores are computed"):
        st.write(
            "Overall score = 0.30 * Behavior + 0.30 * Skill + 0.20 * Growth + 0.20 * CGPA. "
            "Behavior alignment uses cosine similarity with the ideal vector. "
            "Domain confidence is cosine similarity multiplied by subject coverage."
        )
        st.write("Alert thresholds: Attendance < 75, ScreenTime > 6, DSA/OS < 7.")

    st.markdown("### Session Timeline")
    if sessions:
        timeline_rows = []
        sorted_sessions = sorted(
            sessions,
            key=lambda item: item.get("created_at", ""),
            reverse=True,
        )
        for session in sorted_sessions:
            sem_score = overall_score(
                session.get("grades_numeric", []),
                session.get("behavior", []),
                session.get("growth", []),
            )
            timeline_rows.append(
                {
                    "Session": session.get("session_no", "-"),
                    "Created At": _format_timestamp(session.get("created_at")),
                    "Created By": session.get("created_by", "-"),
                    "Score": round(sem_score, 1),
                }
            )
        st.dataframe(timeline_rows, width="stretch")
    else:
        st.write("No sessions recorded.")

    if prev:
        prev_score = overall_score(prev["grades_numeric"], prev["behavior"], prev["growth"])
        trend, delta = semester_comparison(prev_score, score)
        st.markdown("### Semester Comparison")
        st.write(f"Previous: {prev_score:.1f} | Current: {score:.1f} | {trend} ({delta:+.1f})")
        current_vec = current.get("grades_numeric", [])
        prev_vec = prev.get("grades_numeric", [])
        min_len = min(len(current_vec), len(prev_vec))
        if min_len:
            diff = [current_vec[i] - prev_vec[i] for i in range(min_len)]
            change = norm(diff)
            if change < 1.5:
                change_label = "Stable"
            elif change < 3.5:
                change_label = "Moderate change"
            else:
                change_label = "Large change"
            st.write(f"Vector Change: {change_label} (‖Δ‖ = {change:.2f})")
            st.caption("Matrix-based trend: norm of the difference vector.")

    trend_sessions = st.session_state.data.get_latest_by_semester(srn)
    if trend_sessions:
        trend_rows = []
        for sem_no in sorted(trend_sessions.keys(), key=_semester_sort_key):
            session = trend_sessions[sem_no]
            sem_score = overall_score(
                session.get("grades_numeric", []),
                session.get("behavior", []),
                session.get("growth", []),
            )
            trend_rows.append({"Semester": sem_no, "Score": sem_score})
        if trend_rows:
            st.markdown("### Improvement Trend")
            st.line_chart(trend_rows, x="Semester", y="Score")

    st.markdown("### Subject Performance")
    chart_rows = [
        {"Subject": name, "Grade": float(val)}
        for name, val in zip(subjects_list, current["grades_numeric"])
    ]
    st.bar_chart(chart_rows, x="Subject", y="Grade")


def mentor_dashboard():
    st.subheader("Mentor Dashboard")
    mentor = st.session_state.mentor
    if not mentor:
        st.info("Select a mentor first.")
        return

    query = st.text_input("Search by SRN or Name", key="mentor_search")
    page_index = st.number_input("Page", min_value=1, value=1, step=1, key="mentor_page")
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

    all_srns = st.session_state.data.students_for_mentor(mentor)
    latest_by_student = {
        srn: st.session_state.data.get_latest_by_semester(srn)
        for srn in all_srns
    }
    matrix, srn_order = build_student_matrix(latest_by_student)
    scores = compute_scores_matrix(matrix, GROUP_WEIGHTS)
    score_by_srn = dict(zip(srn_order, scores))
    mean_vec = mean_profile_vector(matrix)
    distance_by_srn = {}
    classification_by_srn = {}
    distances = []
    for idx, srn in enumerate(srn_order):
        student_vec = matrix[:, idx].tolist() if matrix.size else []
        distance = distance_from_mean(student_vec, mean_vec)
        distance_by_srn[srn] = distance
        distances.append(distance)

    low_cutoff, high_cutoff = distance_thresholds(distances)
    for srn in srn_order:
        distance = distance_by_srn.get(srn, 0.0)
        if distance < low_cutoff:
            classification_by_srn[srn] = "Normal"
        elif distance < high_cutoff:
            classification_by_srn[srn] = "Needs Attention"
        else:
            classification_by_srn[srn] = "Outlier"
    st.markdown(
        f"""
<div class="section-card">
    <span class="metric-pill">Mentor: {mentor}</span>
    <span class="metric-pill">Assigned Students: {len(all_srns)}</span>
    <span class="metric-pill">Showing: {len(srns)}</span>
</div>
""",
        unsafe_allow_html=True,
    )
    st.caption("Scores below are computed via matrix multiplication (Wᵀ · A).")
    rows = []
    domain_counts = {}
    for srn in all_srns:
        student = st.session_state.data.get_student(srn)
        latest_sessions = st.session_state.data.get_latest_by_semester(srn)
        if not latest_sessions:
            continue
        latest_sem = max(latest_sessions.keys(), key=_semester_sort_key)
        session = latest_sessions[latest_sem]
        subjects_list = session.get("subjects_list") or list(session.get("subjects", {}).keys())
        score = score_by_srn.get(
            srn,
            overall_score(session["grades_numeric"], session["behavior"], session["growth"]),
        )
        risk = risk_level(score)
        ranked = recommend_domain(
            subjects_list,
            session["grades_numeric"],
            studied_subjects=subjects_list,
        )
        domain = ranked[0]["domain"] if ranked else None
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

    for srn in srns:
        student = st.session_state.data.get_student(srn)
        latest_sessions = st.session_state.data.get_latest_by_semester(srn)
        if not latest_sessions:
            continue
        latest_sem = max(latest_sessions.keys(), key=_semester_sort_key)
        session = latest_sessions[latest_sem]
        subjects_list = session.get("subjects_list") or list(session.get("subjects", {}).keys())
        score = score_by_srn.get(
            srn,
            overall_score(session["grades_numeric"], session["behavior"], session["growth"]),
        )
        risk = risk_level(score)
        ranked = recommend_domain(
            subjects_list,
            session["grades_numeric"],
            studied_subjects=subjects_list,
        )
        domain = ranked[0]["domain"] if ranked else None
        rows.append(
            {
                "SRN": srn,
                "Name": student["name"],
                "Latest Semester": latest_sem,
                "Score": round(score, 1),
                "Risk": risk,
                "Domain": domain or "Unavailable",
                "Profile": classification_by_srn.get(srn, "Unavailable"),
                "Distance": round(distance_by_srn.get(srn, 0.0), 3),
            }
        )

    st.dataframe(rows, width="stretch")

    if domain_counts:
        st.markdown("### Domain Distribution")
        st.vega_lite_chart(
            {
                "data": {
                    "values": [
                        {"domain": domain, "count": count}
                        for domain, count in domain_counts.items()
                    ]
                },
                "mark": {"type": "arc", "innerRadius": 30},
                "encoding": {
                    "theta": {"field": "count", "type": "quantitative"},
                    "color": {"field": "domain", "type": "nominal"},
                },
            },
            width="stretch",
        )


def admin_reports():
    st.subheader("Admin Reports")
    issues = st.session_state.data.get_validation_issues()
    if issues:
        st.markdown("### Data Validation Issues")
        st.dataframe([{"Issue": issue} for issue in issues], width="stretch")
    else:
        st.success("No validation issues detected.")

    st.markdown("### Audit Log (Latest 200)")
    audit_lines = st.session_state.data.read_audit_log(limit=200)
    if audit_lines:
        st.text("".join(audit_lines))
    else:
        st.write("Audit log is empty.")

    st.markdown("### Export Student Summary")
    rows = []
    latest_by_student = {
        srn: st.session_state.data.get_latest_by_semester(srn)
        for srn in st.session_state.data.get_all_students()
    }
    for srn, sessions in latest_by_student.items():
        if not sessions:
            continue
        latest_sem = max(sessions.keys(), key=_semester_sort_key)
        session = sessions[latest_sem]
        subjects_list = session.get("subjects_list") or list(session.get("subjects", {}).keys())
        score = overall_score(session["grades_numeric"], session["behavior"], session["growth"])
        risk = risk_level(score)
        ranked = recommend_domain(
            subjects_list,
            session["grades_numeric"],
            studied_subjects=subjects_list,
        )
        domain = ranked[0]["domain"] if ranked else None
        rows.append(
            {
                "SRN": srn,
                "Name": st.session_state.data.get_student(srn).get("name", ""),
                "Mentor": st.session_state.data.get_student(srn).get("mentor", ""),
                "Latest Semester": latest_sem,
                "Score": round(score, 1),
                "Risk": risk,
                "Domain": domain or "Unavailable",
            }
        )

    if rows:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        st.download_button(
            "Download CSV",
            data=buffer.getvalue(),
            file_name="student_summary.csv",
            mime="text/csv",
        )
        st.session_state.data.log_event("export", st.session_state.user, "student_summary.csv")
    else:
        st.write("No student data available for export.")


def admin_setup():
    st.subheader("Admin Setup")
    st.markdown("### Add Mentor")
    mentor_name = st.text_input("Mentor Name")
    st.markdown("### Map Student to Mentor")
    query = st.text_input("Search by SRN or Name", key="admin_search")
    page_index = st.number_input("Page", min_value=1, value=1, step=1, key="admin_page")
    offset = (page_index - 1) * SEARCH_PAGE_SIZE
    srns, total = st.session_state.data.search_students(
        None,
        query,
        offset=offset,
        limit=SEARCH_PAGE_SIZE,
    )
    total_pages = max(1, (total + SEARCH_PAGE_SIZE - 1) // SEARCH_PAGE_SIZE)
    if page_index > total_pages:
        page_index = total_pages
        offset = (page_index - 1) * SEARCH_PAGE_SIZE
        srns, total = st.session_state.data.search_students(
            None,
            query,
            offset=offset,
            limit=SEARCH_PAGE_SIZE,
        )
    st.caption(f"Results: {total} | Page {page_index} of {total_pages}")
    if not srns:
        st.warning("No students found.")
        return
    options = [f"{srn} - {st.session_state.data.get_student(srn)['name']}" for srn in srns]
    selected = st.selectbox("Student", options)
    if st.button("Assign Mentor"):
        if not mentor_name.strip():
            st.error("Enter a mentor name.")
            return
        srn = selected.split(" - ")[0]
        ok, message = st.session_state.data.assign_student_to_mentor(
            srn,
            mentor_name.strip(),
            actor=st.session_state.user,
        )
        if ok:
            st.success(message)
        else:
            st.warning(message)


def college_insights():
    st.subheader("College Insights")
    latest_by_student = {
        srn: st.session_state.data.get_latest_by_semester(srn)
        for srn in st.session_state.data.get_all_students()
    }

    matrix, srn_order = build_student_matrix(latest_by_student)
    mean_vec = mean_profile_vector(matrix)
    if mean_vec:
        st.markdown("### Average Student Profile")
        profile_rows = [
            {"Feature": label, "Value": round(value, 3)}
            for label, value in zip(STUDENT_FEATURE_LABELS, mean_vec)
        ]
        st.dataframe(profile_rows, width="stretch")

        if matrix.size and srn_order:
            st.markdown("### Student Matrix (Features x Students)")
            max_cols = 8
            visible_srns = srn_order[:max_cols]
            col_indices = [srn_order.index(srn) for srn in visible_srns]
            matrix_rows = []
            for row_idx, label in enumerate(STUDENT_FEATURE_LABELS):
                row = {"Feature": label}
                for srn, col_idx in zip(visible_srns, col_indices):
                    row[srn] = round(float(matrix[row_idx, col_idx]), 3)
                matrix_rows.append(row)
            st.dataframe(matrix_rows, width="stretch")
            if len(srn_order) > max_cols:
                st.caption(f"Showing first {max_cols} students in the matrix view.")

        ranked = sorted(profile_rows, key=lambda item: item["Value"], reverse=True)
        strongest = ", ".join([f"{item['Feature']}" for item in ranked[:3]])
        weakest = ", ".join([f"{item['Feature']}" for item in ranked[-3:]])
        st.caption(f"Top 3 strongest features: {strongest}")
        st.caption(f"Top 3 weakest features: {weakest}")

    eigen_matrix, _ = build_student_matrix(latest_by_student, mode="detailed")
    cov = compute_covariance(eigen_matrix)
    values, vectors = eigen_analysis(cov)
    if len(values):
        dominant_index = int(np.argmax(values))
        dominant_vector = vectors[:, dominant_index]
        top_indices = np.argsort(np.abs(dominant_vector))[-3:][::-1]
        top_features = [EIGEN_FEATURE_LABELS[idx] for idx in top_indices]
        st.markdown("### 📊 Performance Drivers (Eigen Analysis)")
        st.write("Most Influential Factors for Student Performance:")
        for feature in top_features:
            st.write(f"- {feature}")
        st.caption(
            "These features contribute most to overall student performance based on data patterns."
        )

    averages = semester_averages(latest_by_student)
    if averages:
        st.markdown("### Average Performance per Semester")
        avg_rows = [
            {"Semester": k, "Average Score": v}
            for k, v in sorted(averages.items(), key=lambda item: _semester_sort_key(item[0]))
        ]
        st.line_chart(avg_rows, x="Semester", y="Average Score")

    weak = weak_subjects(latest_by_student)
    if weak:
        st.markdown("### Weak Subjects Across Students")
        st.dataframe(
            [{"Subject": subject, "Average Grade": round(avg, 2)} for subject, avg in weak],
            width="stretch",
        )

    domain_counts = domain_distribution(latest_by_student)
    if domain_counts:
        st.markdown("### Domain Trends")
        st.vega_lite_chart(
            {
                "data": {
                    "values": [
                        {"domain": domain, "count": count}
                        for domain, count in domain_counts.items()
                    ]
                },
                "mark": "bar",
                "encoding": {
                    "x": {"field": "domain", "type": "nominal"},
                    "y": {"field": "count", "type": "quantitative"},
                },
            },
            width="stretch",
        )

    suggestions = college_suggestions(latest_by_student)
    if suggestions:
        st.markdown("### Suggestions")
        st.write(format_list(suggestions))
