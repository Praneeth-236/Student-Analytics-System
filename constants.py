APP_TITLE = "PES Mentor-Based Student Intelligence System"

DATA_FILE = "students_data.json"
DATA_BACKUP_FILE = "students_data.backup.json"
AUDIT_LOG_FILE = "audit.log"
DATA_VERSION = 2
SESSION_LIMIT_PER_SEMESTER = 2
LOCK_FILE = "students_data.lock"
LOCK_TIMEOUT_SECONDS = 5
PASSWORD_MIN_LENGTH = 6
PASSWORD_REQUIRE_DIGIT = True
LOCKOUT_THRESHOLD = 5
LOCKOUT_MINUTES = 10

GRADE_TO_NUM = {
    "S": 10,
    "A": 9,
    "B": 8,
    "C": 7,
    "D": 6,
    "E": 5,
    "F": 0,
}
NUM_TO_GRADE = {v: k for k, v in GRADE_TO_NUM.items()}
GRADE_OPTIONS = list(GRADE_TO_NUM.keys())

SUBJECTS_BY_SEMESTER = {
    1: ["Python for Computational Problem Solving"],
    2: ["Problem Solving with C"],
    3: [
        "Digital Design & Computer Organization",
        "Data Structures and Applications",
        "Mathematics for CSE",
        "Web Technologies",
        "Automata & Formal Languages",
    ],
    4: [
        "Microprocessor & Architecture",
        "Computer Networks",
        "Design & Analysis of Algorithms",
        "Operating Systems",
        "Linear Algebra",
    ],
    5: [
        "DBMS",
        "Machine Learning",
        "Software Engineering",
        "Elective 1",
        "Elective 2",
    ],
    6: [
        "Cloud Computing",
        "Object Oriented Analysis & Design",
        "Compiler Design",
        "Elective 3",
        "Elective 4",
    ],
}

BEHAVIOR_LABELS = [
    "StudyHours",
    "SleepHours",
    "Attendance",
    "Assignments",
    "ProjectSubmissions",
    "ScreenTime",
]
BEHAVIOR_MAX = [12, 10, 100, 10, 10, 12]
IDEAL_BEHAVIOR = [8, 7, 85, 8, 7, 3]

GROWTH_LABELS = [
    "ClubsScore",
    "EventsScore",
    "Certifications",
    "LinkedInScore",
]

CLUB_TYPE_WEIGHTS = {
    "Technical": 1.0,
    "Domain-based": 0.8,
    "Cultural": 0.5,
}

EVENT_TYPE_WEIGHTS = {
    "Technical": 1.0,
    "Non-technical": 0.6,
}

MAX_CLUBS = 5
MAX_EVENTS = 10
MAX_CERTIFICATIONS = 5
MAX_LINKEDIN_CONNECTIONS = 500
MAX_LINKEDIN_POSTS = 20
GROWTH_SCORE_MAX_RAW = (
    (MAX_CLUBS * CLUB_TYPE_WEIGHTS["Technical"])
    + (MAX_EVENTS * EVENT_TYPE_WEIGHTS["Technical"])
    + MAX_CERTIFICATIONS
    + (MAX_LINKEDIN_CONNECTIONS / 50.0)
    + (MAX_LINKEDIN_POSTS * 0.5)
)

GROUP_WEIGHTS = [0.3, 0.3, 0.2, 0.2]

ALERT_GRADE_DROP = 1.0
ALERT_ATTENDANCE_LOW = 75
ALERT_SCREEN_HIGH = 6
ALERT_STUDY_LOW = 4
ALERT_DSA_LOW = 7
ALERT_OS_LOW = 7

DOMAIN_SUBJECTS = {
    "AI/ML": ["Mathematics for CSE", "Machine Learning", "Linear Algebra"],
    "Data Science": ["Mathematics for CSE", "DBMS", "Machine Learning"],
    "Web Dev": ["Web Technologies", "DBMS"],
    "Systems/Core": [
        "Data Structures and Applications",
        "Operating Systems",
        "Microprocessor & Architecture",
    ],
    "Cybersecurity": ["Computer Networks", "Operating Systems", "Cryptography"],
    "Cloud/DevOps": ["Cloud Computing", "Operating Systems", "DBMS"],
}

USERS = {
    "mentor.meera": {"role": "mentor", "password_hash": "ecad8b23f9cb39ee6e5f46bb92dfa076ce15bebd15afd046995a87beaa6b6bf2"},
    "admin": {"role": "admin", "password_hash": "114663ab194edcb3f61d409883ce4ae6c3c2f9854194095a5385011d15becbef"},
    "hod": {"role": "hod", "password_hash": "0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e"},
}

MENTOR_USER_MAP = {
    "mentor.meera": "Dr. Meera",
}

ROLE_PAGES = {
    "mentor": ["Student Selection", "Semester Input", "Analysis Dashboard", "Mentor Dashboard"],
    "admin": [
        "Mentor Selection",
        "Student Selection",
        "Analysis Dashboard",
        "Mentor Dashboard",
        "College Insights",
        "Admin Setup",
        "Admin Reports",
    ],
    "hod": [
        "Mentor Selection",
        "Student Selection",
        "Analysis Dashboard",
        "Mentor Dashboard",
        "College Insights",
        "Admin Reports",
    ],
}

SEARCH_PAGE_SIZE = 50

MENTOR_ASSIGNMENTS = {
    "Dr. Meera": ["SRN001", "SRN002", "SRN003"],
    "Prof. Rohan": ["SRN004", "SRN005"],
    "Ms. Asha": ["SRN006", "SRN007"],
}

STUDENTS = {
    "SRN001": {"name": "Aarav N", "mentor": "Dr. Meera"},
    "SRN002": {"name": "Diya P", "mentor": "Dr. Meera"},
    "SRN003": {"name": "Ishaan R", "mentor": "Dr. Meera"},
    "SRN004": {"name": "Kavya S", "mentor": "Prof. Rohan"},
    "SRN005": {"name": "Ritvik M", "mentor": "Prof. Rohan"},
    "SRN006": {"name": "Tanvi K", "mentor": "Ms. Asha"},
    "SRN007": {"name": "Yash V", "mentor": "Ms. Asha"},
}
