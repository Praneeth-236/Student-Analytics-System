import sys

from data_manager import DataManager


def run_smoke_test():
    manager = DataManager()
    srn = manager.get_all_students()[0]
    semester = 3
    actor = "smoke_test"
    session = {
        "subjects": {"Test Subject": "A"},
        "subjects_list": ["Test Subject"],
        "grades": ["A"],
        "grades_numeric": [9],
        "behavior": {
            "StudyHours": 6,
            "SleepHours": 7,
            "Attendance": 90,
            "Assignments": 8,
            "ProjectSubmissions": 4,
            "ScreenTime": 2,
        },
        "growth": {
            "ClubsScore": 1.0,
            "EventsScore": 2.0,
            "Certifications": 1,
            "LinkedInScore": 3.5,
        },
    }
    try:
        ok, message = manager.add_session(srn, semester, session, actor=actor)
        if not ok:
            raise RuntimeError(message)
        sessions = manager.get_sessions(srn, semester)
        if not sessions:
            raise RuntimeError("Session not saved.")
        issues = manager.get_validation_issues()
        return {
            "saved": True,
            "session_count": len(sessions),
            "issues": issues,
        }
    finally:
        manager.remove_sessions_by_actor(actor)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "reset":
        manager = DataManager()
        removed = manager.remove_sessions_by_actor("smoke_test")
        print({"removed": removed})
    else:
        result = run_smoke_test()
        print(result)
