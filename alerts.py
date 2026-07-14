from constants import (
    ALERT_ATTENDANCE_LOW,
    ALERT_DSA_LOW,
    ALERT_GRADE_DROP,
    ALERT_OS_LOW,
    ALERT_SCREEN_HIGH,
    ALERT_STUDY_LOW,
    BEHAVIOR_LABELS,
)
from analysis import growth_score, overall_score


def _find_subject_grade(subjects, grades_numeric, keywords):
    for name, score in zip(subjects, grades_numeric):
        lowered = name.lower()
        if any(keyword in lowered for keyword in keywords):
            return score
    return None


def _behavior_value(behavior, label):
    if isinstance(behavior, dict):
        return behavior.get(label, 0)
    try:
        index = BEHAVIOR_LABELS.index(label)
    except ValueError:
        return 0
    if isinstance(behavior, (list, tuple)) and index < len(behavior):
        return behavior[index]
    return 0


def detect_alerts(current_session, prev_session):
    if not current_session:
        return []

    alerts = []
    subjects = current_session.get("subjects", [])
    if isinstance(subjects, dict):
        subjects = list(subjects.keys())
    grades = current_session.get("grades_numeric", [])
    if prev_session:
        prev_grades = prev_session.get("grades_numeric", [])
        if grades and prev_grades:
            drop = (sum(prev_grades) / len(prev_grades)) - (sum(grades) / len(grades))
            if drop >= ALERT_GRADE_DROP:
                alerts.append(f"Grade drop detected: {drop:.1f} point(s) below the previous semester average")

    academic_score = overall_score(
        current_session.get("grades_numeric", []),
        current_session.get("behavior", []),
        current_session.get("growth", []),
    )
    if academic_score < 50:
        alerts.append(f"Overall performance is at risk: {academic_score:.1f}/100")

    dsa_score = _find_subject_grade(subjects, grades, ["data structures", "dsa"])
    if dsa_score is not None and dsa_score < ALERT_DSA_LOW:
        alerts.append(f"Low DSA performance: {dsa_score:.1f}/10")

    os_score = _find_subject_grade(subjects, grades, ["operating systems", "os"])
    if os_score is not None and os_score < ALERT_OS_LOW:
        alerts.append(f"Low OS performance: {os_score:.1f}/10")

    behavior = current_session.get("behavior", [])
    if behavior:
        attendance = _behavior_value(behavior, "Attendance")
        screen_time = _behavior_value(behavior, "ScreenTime")
        study_hours = _behavior_value(behavior, "StudyHours")
        if attendance < ALERT_ATTENDANCE_LOW:
            alerts.append(f"Low attendance: {attendance:.0f}%")
        if screen_time > ALERT_SCREEN_HIGH:
            alerts.append(f"High screen time: {screen_time:.1f} hours")
        if study_hours < ALERT_STUDY_LOW:
            alerts.append(f"Low study hours: {study_hours:.1f} hours")

    growth = current_session.get("growth", [])
    if growth:
        growth_value = growth_score(growth)
        if growth_value < 3.5:
            alerts.append(f"Low growth activity: {growth_value:.1f}/10")

    return alerts


def recommend_interventions(current_session, prev_session=None):
    alerts = detect_alerts(current_session, prev_session)
    if not alerts:
        return ["No immediate intervention required. Continue the current plan and monitor next session."]

    recommendations = []
    score = overall_score(
        current_session.get("grades_numeric", []),
        current_session.get("behavior", []),
        current_session.get("growth", []),
    )
    behavior = current_session.get("behavior", [])
    growth = current_session.get("growth", [])

    if score < 50:
        recommendations.append("Schedule a mentor review and create a 2-week improvement plan.")

    for alert in alerts:
        lowered = alert.lower()
        if "attendance" in lowered:
            recommendations.append("Set weekly attendance tracking and inform the student about class priority.")
        elif "study hours" in lowered:
            recommendations.append("Assign a daily study block and verify progress in the next review.")
        elif "screen time" in lowered:
            recommendations.append("Reduce non-academic screen time and replace it with focused study sessions.")
        elif "dsa" in lowered or "os" in lowered:
            recommendations.append("Give a subject-specific practice sheet and short remedial quiz.")
        elif "growth activity" in lowered:
            recommendations.append("Ask the student to complete one certification, club task, or event participation this month.")
        elif "grade drop" in lowered:
            recommendations.append("Compare the last two semesters and identify subjects that need immediate remediation.")

    if behavior:
        attendance = _behavior_value(behavior, "Attendance")
        study_hours = _behavior_value(behavior, "StudyHours")
        screen_time = _behavior_value(behavior, "ScreenTime")
        if attendance >= ALERT_ATTENDANCE_LOW and study_hours >= ALERT_STUDY_LOW and screen_time <= ALERT_SCREEN_HIGH:
            recommendations.append("Keep the current routine and review only the weakest subject areas.")

    if growth:
        growth_value = growth_score(growth)
        if growth_value >= 6:
            recommendations.append("Encourage the student to document achievements for portfolio and placement readiness.")

    cleaned = []
    for item in recommendations:
        if item not in cleaned:
            cleaned.append(item)
    return cleaned
