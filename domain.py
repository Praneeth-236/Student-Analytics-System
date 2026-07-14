from constants import DOMAIN_SUBJECTS
from linear_algebra import dot_product, norm


def _subject_grade_map(subjects, grades_numeric):
    return {name: score for name, score in zip(subjects, grades_numeric)}


def compute_domain_score(student_grades, domain_subjects, studied_subjects=None):
    if studied_subjects is None:
        considered = list(domain_subjects)
    else:
        considered = [subject for subject in domain_subjects if subject in studied_subjects]
    if not considered:
        return {
            "score": 0.0,
            "coverage": 0.0,
            "confidence": "Low",
            "potential": 0.0,
        }

    available = [subject for subject in considered if subject in student_grades]
    if not available:
        return {
            "score": 0.0,
            "coverage": 0.0,
            "confidence": "Low",
            "potential": 0.0,
        }

    student_vector = [float(student_grades[subject]) for subject in available]
    ideal_vector = [10.0 for _ in available]
    denom = norm(student_vector) * norm(ideal_vector)
    similarity = dot_product(student_vector, ideal_vector) / denom if denom else 0.0
    coverage = len(available) / len(considered)
    final_score = similarity * (0.5 + 0.5 * coverage)

    if final_score > 0.7:
        confidence = "High"
    elif final_score >= 0.4:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "score": float(final_score),
        "coverage": float(coverage),
        "confidence": confidence,
        "potential": float(similarity),
    }


def recommend_domain(subjects, grades_numeric, studied_subjects=None):
    student_grades = _subject_grade_map(subjects, grades_numeric)
    ranked = []
    for domain, domain_subjects in DOMAIN_SUBJECTS.items():
        metrics = compute_domain_score(student_grades, domain_subjects, studied_subjects)
        ranked.append({"domain": domain, **metrics})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
