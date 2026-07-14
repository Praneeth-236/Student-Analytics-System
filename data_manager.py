import json
import os
import shutil
import time
from datetime import datetime, timezone
from copy import deepcopy

from constants import (
    AUDIT_LOG_FILE,
    DATA_BACKUP_FILE,
    DATA_FILE,
    DATA_VERSION,
    LOCK_FILE,
    LOCK_TIMEOUT_SECONDS,
    MENTOR_ASSIGNMENTS,
    SESSION_LIMIT_PER_SEMESTER,
    STUDENTS,
)


class DataManager:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
        self.backup_path = os.path.join(os.path.dirname(__file__), DATA_BACKUP_FILE)
        self.audit_path = os.path.join(os.path.dirname(__file__), AUDIT_LOG_FILE)
        self.lock_path = os.path.join(os.path.dirname(__file__), LOCK_FILE)
        self.data_version = DATA_VERSION
        self.students = self._load_data()
        self._ensure_structure()
        self.validation_issues = self._validate_data()
        self._build_indexes()

    def _build_indexes(self):
        self.mentor_index = {}
        for srn, info in self.students.items():
            mentor = info.get("mentor")
            if not mentor:
                mentor = self._mentor_from_assignments(srn)
                if mentor:
                    info["mentor"] = mentor
            if mentor:
                self.mentor_index.setdefault(mentor, []).append(srn)
        for mentor in self.mentor_index:
            self.mentor_index[mentor].sort()

    def _mentor_from_assignments(self, srn):
        for mentor, srns in MENTOR_ASSIGNMENTS.items():
            if srn in srns:
                return mentor
        return None

    def _load_data(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as file:
                    payload = json.load(file)
                    if isinstance(payload, dict) and "students" in payload:
                        self.data_version = payload.get("version", DATA_VERSION)
                        return payload.get("students", {})
                    return payload
            except (json.JSONDecodeError, OSError):
                pass
        return deepcopy(STUDENTS)

    def _ensure_structure(self):
        for srn in self.students:
            if "semesters" not in self.students[srn]:
                self.students[srn]["semesters"] = {}
            self._migrate_semesters(self.students[srn]["semesters"])

    def _validate_data(self):
        issues = []
        if not isinstance(self.students, dict):
            return ["Students data is not a dictionary."]
        for srn, info in self.students.items():
            if not isinstance(info, dict):
                issues.append(f"Student {srn} is not a record.")
                continue
            if "name" not in info:
                issues.append(f"Student {srn} missing name.")
            if "mentor" not in info:
                issues.append(f"Student {srn} missing mentor.")
            semesters = info.get("semesters", {})
            if not isinstance(semesters, dict):
                issues.append(f"Student {srn} semesters invalid.")
                continue
            for sem, data in semesters.items():
                if not isinstance(data, dict) or "sessions" not in data:
                    issues.append(f"Student {srn} semester {sem} invalid.")
                    continue
                sessions = data.get("sessions", [])
                if len(sessions) > SESSION_LIMIT_PER_SEMESTER:
                    issues.append(f"Student {srn} semester {sem} has >2 sessions.")
        return issues

    def _migrate_semesters(self, semesters):
        for sem, data in list(semesters.items()):
            if isinstance(data, dict) and "sessions" in data:
                continue
            if data:
                semesters[sem] = {"sessions": [data]}
            else:
                semesters[sem] = {"sessions": []}

    def _save_data(self):
        lock_handle = self._acquire_lock()
        if not lock_handle:
            return False
        try:
            if os.path.exists(self.data_path):
                shutil.copy2(self.data_path, self.backup_path)
            temp_path = f"{self.data_path}.tmp"
            payload = {"version": DATA_VERSION, "students": self.students}
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2)
            os.replace(temp_path, self.data_path)
            self.validation_issues = self._validate_data()
            self._build_indexes()
        except OSError:
            return False
        finally:
            self._release_lock(lock_handle)
        return True

    def _acquire_lock(self):
        start = time.time()
        while time.time() - start < LOCK_TIMEOUT_SECONDS:
            try:
                handle = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(handle, str(os.getpid()).encode("utf-8"))
                return handle
            except FileExistsError:
                time.sleep(0.1)
        return None

    def _release_lock(self, handle):
        try:
            os.close(handle)
            os.remove(self.lock_path)
        except OSError:
            pass

    def _log_event(self, action, actor, details):
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            line = f"{timestamp} | {actor} | {action} | {details}\n"
            with open(self.audit_path, "a", encoding="utf-8") as file:
                file.write(line)
        except OSError:
            pass

    def log_event(self, action, actor, details):
        self._log_event(action, actor, details)

    def list_mentors(self):
        return sorted(self.mentor_index.keys())

    def students_for_mentor(self, mentor):
        return list(self.mentor_index.get(mentor, []))

    def get_student(self, srn):
        return self.students.get(srn)

    def assign_student_to_mentor(self, srn, mentor_name, actor=None):
        student = self.get_student(srn)
        if not student:
            return False, "Student not found."
        old_mentor = student.get("mentor")
        student["mentor"] = mentor_name
        if not self._save_data():
            student["mentor"] = old_mentor
            return False, "Mapping could not be persisted."
        self._log_event(
            "assign_mentor",
            actor or "unknown",
            f"{srn} | {old_mentor} -> {mentor_name}",
        )
        return True, "Mentor mapping updated."

    def add_session(self, srn, semester, session_data, actor=None):
        student = self.get_student(srn)
        if not student:
            return False, "Student not found."
        semesters = student["semesters"]
        if semester not in semesters or "sessions" not in semesters[semester]:
            semesters[semester] = {"sessions": []}
        sessions = semesters[semester]["sessions"]
        if len(sessions) >= SESSION_LIMIT_PER_SEMESTER:
            return False, "Only 2 sessions allowed per semester."
        session_data = dict(session_data)
        session_data["created_at"] = datetime.now(timezone.utc).isoformat()
        session_data["created_by"] = actor or "unknown"
        session_data["session_no"] = len(sessions) + 1
        sessions.append(session_data)
        if not self._save_data():
            if sessions:
                sessions.pop()
            return False, "Session could not be persisted."
        self._log_event("add_session", actor or "unknown", f"{srn} | sem {semester}")
        return True, "Session saved."

    def get_sessions(self, srn, semester):
        student = self.get_student(srn)
        if not student:
            return []
        data = student.get("semesters", {}).get(semester, {})
        if isinstance(data, dict) and "sessions" in data:
            return data.get("sessions", [])
        return []

    def get_latest_session(self, srn, semester):
        sessions = self.get_sessions(srn, semester)
        return sessions[-1] if sessions else None

    def list_semesters(self, srn):
        student = self.get_student(srn)
        if not student:
            return []
        return sorted(student.get("semesters", {}).keys())

    def get_latest_by_semester(self, srn):
        student = self.get_student(srn)
        if not student:
            return {}
        latest = {}
        for sem, data in student.get("semesters", {}).items():
            if isinstance(data, dict) and data.get("sessions"):
                latest[sem] = data["sessions"][-1]
        return latest

    def get_all_students(self):
        return list(self.students.keys())

    def get_validation_issues(self):
        return list(self.validation_issues)

    def read_audit_log(self, limit=200):
        if not os.path.exists(self.audit_path):
            return []
        try:
            with open(self.audit_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            return lines[-limit:]
        except OSError:
            return []

    def can_access_student(self, mentor, srn):
        return srn in self.mentor_index.get(mentor, [])

    def search_students(self, mentor, query, offset=0, limit=50):
        srns = self.students_for_mentor(mentor) if mentor else self.get_all_students()
        if query:
            lowered = query.lower()
            srns = [
                srn
                for srn in srns
                if lowered in srn.lower()
                or lowered in self.students.get(srn, {}).get("name", "").lower()
            ]
        total = len(srns)
        page = srns[offset : offset + limit]
        return page, total

    def remove_sessions_by_actor(self, actor):
        removed = 0
        for info in self.students.values():
            semesters = info.get("semesters", {})
            for data in semesters.values():
                if not isinstance(data, dict):
                    continue
                sessions = data.get("sessions", [])
                if not sessions:
                    continue
                kept = [session for session in sessions if session.get("created_by") != actor]
                removed += len(sessions) - len(kept)
                data["sessions"] = kept
        if removed:
            self._save_data()
            self._log_event("cleanup_sessions", actor, f"removed {removed} sessions")
        return removed
