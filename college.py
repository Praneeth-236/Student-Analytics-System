from collections import defaultdict

from analysis import overall_score
from constants import BEHAVIOR_LABELS
from domain import recommend_domain


def semester_averages(latest_sessions_by_student):
    semester_scores = defaultdict(list)
    for sessions in latest_sessions_by_student.values():
        for sem, session in sessions.items():
            score = overall_score(
                session.get("grades_numeric", []),
                session.get("behavior", []),
                session.get("growth", []),
            )
            semester_scores[sem].append(score)
    return {
        sem: sum(scores) / len(scores) if scores else 0.0
        for sem, scores in semester_scores.items()
    }


def weak_subjects(latest_sessions_by_student):
    subject_totals = defaultdict(list)
    for sessions in latest_sessions_by_student.values():
        for session in sessions.values():
            subjects = session.get("subjects", [])
            if isinstance(subjects, dict):
                subjects = list(subjects.keys())
            grades = session.get("grades_numeric", [])
            for subject, grade in zip(subjects, grades):
                subject_totals[subject].append(grade)
    averages = {
        subject: sum(scores) / len(scores) if scores else 0.0
        for subject, scores in subject_totals.items()
    }
    sorted_subjects = sorted(averages.items(), key=lambda item: item[1])
    return sorted_subjects


def domain_distribution(latest_sessions_by_student):
    counts = defaultdict(int)
    for sessions in latest_sessions_by_student.values():
        for session in sessions.values():
            subjects = session.get("subjects", [])
            if isinstance(subjects, dict):
                subjects = list(subjects.keys())
            grades = session.get("grades_numeric", [])
            ranked = recommend_domain(subjects, grades, studied_subjects=subjects)
            domain = ranked[0]["domain"] if ranked else None
            if domain:
                counts[domain] += 1
    return dict(counts)


def college_suggestions(latest_sessions_by_student):
    suggestions = []
    weak = weak_subjects(latest_sessions_by_student)
    if weak:
        weak_names = [subject for subject, avg in weak if avg < 7.0]
        if weak_names:
            suggestions.append("Improve focus on: " + ", ".join(weak_names[:5]))

    attendance_scores = []
    screen_scores = []
    for sessions in latest_sessions_by_student.values():
        for session in sessions.values():
            behavior = session.get("behavior", [])
            if not behavior:
                continue
            if isinstance(behavior, dict):
                attendance_scores.append(behavior.get("Attendance", 0))
                screen_scores.append(behavior.get("ScreenTime", 0))
            else:
                attendance_scores.append(behavior[BEHAVIOR_LABELS.index("Attendance")])
                screen_scores.append(behavior[BEHAVIOR_LABELS.index("ScreenTime")])

    if attendance_scores:
        avg_attendance = sum(attendance_scores) / len(attendance_scores)
        if avg_attendance < 80:
            suggestions.append("Boost attendance with mentoring and tracking.")

    if screen_scores:
        avg_screen = sum(screen_scores) / len(screen_scores)
        if avg_screen > 6:
            suggestions.append("Promote digital wellbeing to reduce screen time.")

    return suggestions
