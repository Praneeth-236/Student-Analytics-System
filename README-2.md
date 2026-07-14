# PES Mentor-Based Student Intelligence System

This project is a Streamlit-based academic mentoring dashboard for tracking student performance across semesters. It captures subject grades, structured behavior metrics, and growth activities, then turns them into clear scores and insights for mentors and admins.

## What the app does

- Collects semester data for each student (grades, behavior, growth).
- Computes overall scores and risk levels using consistent weighting.
- Shows academic strengths/weaknesses, behavior alignment, and growth scores.
- Provides mentor dashboards with cohort summaries and student classification.
- Offers college-level insights such as averages, weak subjects, and domain trends.
- Uses matrix and eigen analysis to identify dominant performance drivers.

## Who it is for

- Mentors who need to assess individual students.
- Admins and HODs who need aggregate, college-level views.

## Key features

- Semester input with realistic behavior and growth measures.
- Linear algebra-based scoring and trend analysis.
- Matrix-based cohort scoring and distance classification.
- Eigen-based performance driver analysis in College Insights.

## Tech stack

- Python
- Streamlit
- NumPy

## How to run

1. Install dependencies (Streamlit, NumPy).
2. Run:

```bash
streamlit run app.py
```

This will open the app in your browser for local use.
