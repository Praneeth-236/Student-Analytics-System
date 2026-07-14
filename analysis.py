import numpy as np

from constants import (
    BEHAVIOR_LABELS,
    BEHAVIOR_MAX,
    GRADE_TO_NUM,
    GROUP_WEIGHTS,
    GROWTH_SCORE_MAX_RAW,
    IDEAL_BEHAVIOR,
    MAX_CERTIFICATIONS,
    MAX_CLUBS,
    MAX_EVENTS,
    MAX_LINKEDIN_CONNECTIONS,
    MAX_LINKEDIN_POSTS,
)
from linear_algebra import cosine_similarity, dot_product, mean_vector


STUDENT_FEATURE_LABELS = [
    "BehaviorScore",
    "SkillScore",
    "GrowthScore",
    "CGPAScore",
]

EIGEN_FEATURE_LABELS = [
    "Math",
    "Coding",
    "Logic",
    "System",
    "Communication",
    "Study",
    "Sleep",
    "Attendance",
    "Assignments",
    "Projects",
    "Screen",
    "Clubs",
    "Events",
    "Certs",
    "LinkedIn",
]


def grades_to_numeric(grades):
    return [GRADE_TO_NUM.get(g, 0) for g in grades]


def academic_strengths(subjects, grades_numeric):
    strengths = []
    weaknesses = []
    for name, score in zip(subjects, grades_numeric):
        if score >= 8:
            strengths.append(name)
        elif score <= 6:
            weaknesses.append(name)
    return strengths, weaknesses


def normalize_vector(values, max_values):
    vec = list(values) if isinstance(values, (list, tuple, np.ndarray)) else [values]
    max_vec = np.array(max_values, dtype=float)
    if max_vec.size == 0:
        return []
    if len(vec) < len(max_vec):
        vec = vec + [0.0] * (len(max_vec) - len(vec))
    elif len(vec) > len(max_vec):
        vec = vec[: len(max_vec)]
    vec = np.array(vec, dtype=float)
    normed = vec / max_vec
    normed = np.clip(normed, 0.0, 1.0)
    return normed.tolist()


def _vector_from_dict(data, labels):
    if isinstance(data, dict):
        return [data.get(label, 0) for label in labels]
    return list(data)


def behavior_insights(behavior_vector):
    vec = _vector_from_dict(behavior_vector, BEHAVIOR_LABELS)
    normed = normalize_vector(vec, BEHAVIOR_MAX)
    ideal = normalize_vector(IDEAL_BEHAVIOR, BEHAVIOR_MAX)
    strengths = []
    weaknesses = []
    for label, value, target in zip(BEHAVIOR_LABELS, normed, ideal):
        if value >= target:
            strengths.append(label)
        else:
            weaknesses.append(label)
    return strengths, weaknesses


def _growth_components(growth_vector):
    if isinstance(growth_vector, dict):
        clubs = growth_vector.get("ClubsScore", growth_vector.get("Clubs", 0))
        events = growth_vector.get("EventsScore", growth_vector.get("Events", 0))
        certifications = growth_vector.get("Certifications", 0)
        linkedin = growth_vector.get("LinkedInScore", 0)
        return float(clubs), float(events), float(certifications), float(linkedin)
    if isinstance(growth_vector, (list, tuple)) and len(growth_vector) >= 4:
        clubs, events, certifications, linkedin = growth_vector[:4]
        return float(clubs), float(events), float(certifications), float(linkedin)
    return 0.0, 0.0, 0.0, 0.0


def growth_score(growth_vector):
    clubs, events, certifications, linkedin = _growth_components(growth_vector)
    raw = clubs + events + certifications + linkedin
    if GROWTH_SCORE_MAX_RAW <= 0:
        return 0.0
    normalized = (raw / float(GROWTH_SCORE_MAX_RAW)) * 10.0
    return float(max(0.0, min(10.0, normalized)))


def behavior_alignment(behavior_vector):
    vec = _vector_from_dict(behavior_vector, BEHAVIOR_LABELS)
    normed = normalize_vector(vec, BEHAVIOR_MAX)
    ideal = normalize_vector(IDEAL_BEHAVIOR, BEHAVIOR_MAX)
    return cosine_similarity(normed, ideal)


def overall_score(academic_vector, behavior_vector, growth_vector):
    skill_score = float(np.mean(academic_vector)) / 10.0 if academic_vector else 0.0
    cgpa_score = skill_score
    behavior_vec = _vector_from_dict(behavior_vector, BEHAVIOR_LABELS)
    behavior_score = float(np.mean(normalize_vector(behavior_vec, BEHAVIOR_MAX)))
    growth_norm = growth_score(growth_vector) / 10.0
    grouped = [behavior_score, skill_score, growth_norm, cgpa_score]
    score = dot_product(grouped, GROUP_WEIGHTS) * 100.0
    return max(0.0, min(100.0, score))


def behavior_deviation(behavior_vector):
    vec = _vector_from_dict(behavior_vector, BEHAVIOR_LABELS)
    normed = normalize_vector(vec, BEHAVIOR_MAX)
    ideal = normalize_vector(IDEAL_BEHAVIOR, BEHAVIOR_MAX)
    diffs = [abs(a - b) for a, b in zip(normed, ideal)]
    return float(np.mean(diffs)) if diffs else 0.0


def top_skill_gaps(subjects, grades_numeric, count=3):
    pairs = list(zip(subjects, grades_numeric))
    if not pairs:
        return []
    pairs.sort(key=lambda item: item[1])
    return [name for name, _ in pairs[:count]]


def risk_level(score):
    if score >= 70:
        return "Low"
    if score >= 50:
        return "Moderate"
    return "High"


def semester_comparison(prev_score, curr_score):
    delta = curr_score - prev_score
    if delta >= 2:
        return "Improved", delta
    if delta <= -2:
        return "Declined", delta
    return "Stable", delta


def _semester_key(value):
    if isinstance(value, int):
        return (0, value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return (0, int(stripped))
    try:
        return (0, int(value))
    except (TypeError, ValueError):
        return (1, str(value))


def _latest_session(payload):
    if isinstance(payload, dict) and "grades_numeric" in payload:
        return payload
    if isinstance(payload, dict):
        if payload.get("sessions"):
            return payload.get("sessions", [])[-1]
        if payload:
            latest_sem = max(payload.keys(), key=_semester_key)
            return payload.get(latest_sem)
    return None


def _student_feature_vector(session):
    if not session:
        return None
    grades = session.get("grades_numeric", [])
    skill_score = float(np.mean(grades)) / 10.0 if grades else 0.0
    cgpa_score = skill_score
    behavior_vec = _vector_from_dict(session.get("behavior", []), BEHAVIOR_LABELS)
    behavior_score = float(np.mean(normalize_vector(behavior_vec, BEHAVIOR_MAX)))
    growth_norm = growth_score(session.get("growth", [])) / 10.0
    return [behavior_score, skill_score, growth_norm, cgpa_score]


def _category_scores(subjects, grades_numeric):
    categories = {
        "Math": ["math", "linear algebra"],
        "Coding": ["python", "programming", "c", "web", "data structures"],
        "Logic": ["algorithms", "automata", "formal"],
        "System": [
            "operating systems",
            "microprocessor",
            "computer networks",
            "dbms",
            "cloud",
            "compiler",
            "architecture",
        ],
        "Communication": ["software engineering"],
    }
    scores = {key: [] for key in categories}
    for subject, grade in zip(subjects, grades_numeric):
        lowered = str(subject).lower()
        for key, keywords in categories.items():
            if any(keyword in lowered for keyword in keywords):
                scores[key].append(grade)
                break
    return {
        key: (float(np.mean(values)) / 10.0 if values else 0.0)
        for key, values in scores.items()
    }


def _detailed_student_vector(session):
    if not session:
        return None
    subjects = session.get("subjects_list") or list(session.get("subjects", {}).keys())
    grades = session.get("grades_numeric", [])
    skill_scores = _category_scores(subjects, grades)

    behavior_vec = _vector_from_dict(session.get("behavior", []), BEHAVIOR_LABELS)
    behavior_norm = normalize_vector(behavior_vec, BEHAVIOR_MAX)
    behavior_map = dict(zip(BEHAVIOR_LABELS, behavior_norm))

    growth = session.get("growth", {})
    clubs = float(growth.get("ClubsScore", 0))
    events = float(growth.get("EventsScore", 0))
    certs = float(growth.get("Certifications", 0))
    linkedin = float(growth.get("LinkedInScore", 0))
    clubs_norm = clubs / float(MAX_CLUBS) if MAX_CLUBS else 0.0
    events_norm = events / float(MAX_EVENTS) if MAX_EVENTS else 0.0
    certs_norm = certs / float(MAX_CERTIFICATIONS) if MAX_CERTIFICATIONS else 0.0
    linkedin_max = (MAX_LINKEDIN_CONNECTIONS / 50.0) + (MAX_LINKEDIN_POSTS * 0.5)
    linkedin_norm = linkedin / float(linkedin_max) if linkedin_max else 0.0

    return [
        skill_scores.get("Math", 0.0),
        skill_scores.get("Coding", 0.0),
        skill_scores.get("Logic", 0.0),
        skill_scores.get("System", 0.0),
        skill_scores.get("Communication", 0.0),
        behavior_map.get("StudyHours", 0.0),
        behavior_map.get("SleepHours", 0.0),
        behavior_map.get("Attendance", 0.0),
        behavior_map.get("Assignments", 0.0),
        behavior_map.get("ProjectSubmissions", 0.0),
        behavior_map.get("ScreenTime", 0.0),
        clubs_norm,
        events_norm,
        certs_norm,
        linkedin_norm,
    ]


def build_student_matrix(students, mode="summary"):
    # Build A where each column is a student's feature vector.
    vectors = []
    srn_order = []
    if not students:
        return np.zeros((len(STUDENT_FEATURE_LABELS), 0)), srn_order
    for srn, payload in students.items():
        session = _latest_session(payload)
        vector = _student_feature_vector(session) if mode == "summary" else _detailed_student_vector(session)
        if vector is None:
            continue
        vectors.append(vector)
        srn_order.append(srn)

    if not vectors:
        label_count = len(STUDENT_FEATURE_LABELS) if mode == "summary" else len(EIGEN_FEATURE_LABELS)
        return np.zeros((label_count, 0)), srn_order

    matrix = np.array(vectors, dtype=float).T
    return matrix, srn_order


def compute_scores_matrix(matrix, weights):
    if matrix.size == 0:
        return []
    weight_vec = np.array(weights, dtype=float)
    scores = np.dot(weight_vec, matrix) * 100.0
    return scores.tolist()

def mean_profile_vector(matrix):
    if matrix.size == 0:
        return []
    # Mean across student columns to get the average profile.
    return mean_vector(matrix.T)


def distance_from_mean(student_vector, mean_vec):
    if student_vector is None or mean_vec is None:
        return 0.0
    return float(np.linalg.norm(np.array(student_vector, dtype=float) - np.array(mean_vec, dtype=float)))


def distance_thresholds(distances, low_quantile=0.33, high_quantile=0.66, fallback=(0.15, 0.35)):
    if not distances:
        return fallback
    vec = np.array(distances, dtype=float)
    if vec.size < 3:
        return fallback
    low_val = float(np.quantile(vec, low_quantile))
    high_val = float(np.quantile(vec, high_quantile))
    if low_val >= high_val:
        return fallback
    return low_val, high_val


def compute_covariance(matrix):
    if matrix.size == 0:
        return None
    if not np.isfinite(matrix).all():
        matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
    # Covariance across features using student columns as observations.
    return np.cov(matrix)


def eigen_analysis(cov_matrix):
    if cov_matrix is None:
        return [], []
    if not np.isfinite(cov_matrix).all():
        return [], []
    values, vectors = np.linalg.eig(cov_matrix)
    return np.real(values), np.real(vectors)
