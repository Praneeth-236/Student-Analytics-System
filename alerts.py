from constants import (
    ALERT_ATTENDANCE_LOW,
    ALERT_DSA_LOW,
    ALERT_GRADE_DROP,
    ALERT_OS_LOW,
    ALERT_SCREEN_HIGH,
    ALERT_STUDY_LOW,
    BEHAVIOR_LABELS,
)


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
                alerts.append("Drop in grades")

    dsa_score = _find_subject_grade(subjects, grades, ["data structures", "dsa"])
    if dsa_score is not None and dsa_score < ALERT_DSA_LOW:
        alerts.append("Low DSA performance")

    os_score = _find_subject_grade(subjects, grades, ["operating systems", "os"])
    if os_score is not None and os_score < ALERT_OS_LOW:
        alerts.append("Low OS performance")

    behavior = current_session.get("behavior", [])
    if behavior:
        attendance = _behavior_value(behavior, "Attendance")
        screen_time = _behavior_value(behavior, "ScreenTime")
        study_hours = _behavior_value(behavior, "StudyHours")
        if attendance < ALERT_ATTENDANCE_LOW:
            alerts.append("Low attendance")
        if screen_time > ALERT_SCREEN_HIGH:
            alerts.append("High screen time")
        if study_hours < ALERT_STUDY_LOW:
            alerts.append("Low study hours")

    return alerts
