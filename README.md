# Mathematical Functions and Formulas

This project uses a small set of linear algebra helpers plus scoring and averaging formulas to turn academic, behavior, and growth data into consistent signals for mentoring and analytics.

## linear_algebra.py

- `dot_product(a, b)`
  - What: computes $a \cdot b$.
  - Why: used for weighted sums and cosine similarity.
- `norm(a)`
  - What: computes the Euclidean length $\|a\|_2$.
  - Why: used to normalize vectors and measure changes.
- `mean_vector(matrix)`
  - What: column-wise mean of a matrix.
  - Why: useful when aggregating multiple vectors.
- `cosine_similarity(a, b)`
  - What: $\frac{a \cdot b}{\|a\|\,\|b\|}$, with a zero-safe fallback.
  - Why: compares direction (pattern similarity) of behavior vectors.

## analysis.py

- `grades_to_numeric(grades)`
  - What: maps letter grades to numeric values.
  - Why: enables averaging and numeric scoring.
- `normalize_vector(values, max_values)`
  - What: element-wise normalization $v_i / m_i$ with clipping to $[0,1]$.
  - Why: puts different scales on a common range for fair averaging.
- `growth_score(growth_vector)`
  - What: sums growth components then normalizes to 0-10.
  - Why: produces a single growth metric from structured inputs.
- `behavior_insights(behavior_vector)`
  - What: compares normalized behavior to the normalized ideal vector.
  - Why: surfaces strengths vs. weaknesses per behavior label.
- `behavior_alignment(behavior_vector)`
  - What: cosine similarity between behavior and ideal behavior.
  - Why: measures how closely behavior matches target patterns.
- `overall_score(academic_vector, behavior_vector, growth_vector)`
  - What: weighted sum of behavior, skill, growth, and CGPA, scaled to 0-100.
  - Why: consistent overall score used across dashboards and trends.
- `behavior_deviation(behavior_vector)`
  - What: mean absolute deviation from ideal behavior.
  - Why: highlights how far behavior drifts from targets.
- `top_skill_gaps(subjects, grades_numeric, count)`
  - What: sorts grades to find lowest scores.
  - Why: identifies skills needing attention.
- `build_student_matrix(students, mode="summary")`
  - What: constructs a matrix $A$ with one student vector per column.
  - Why: enables matrix multiplication and cohort-level analysis.
- `compute_scores_matrix(matrix, weights)`
  - What: computes $W^T \cdot A$ for all students.
  - Why: scores all students in one matrix multiplication.
- `mean_profile_vector(matrix)`
  - What: computes the mean student profile from the matrix.
  - Why: provides the cohort average vector.
- `distance_from_mean(student_vector, mean_vector)`
  - What: computes $\|S - \mu\|_2$.
  - Why: classifies how far a student is from the cohort average.
- `distance_thresholds(distances)`
  - What: derives low/high cutoffs from distance quantiles.
  - Why: adaptive classification for Normal/Needs Attention/Outlier.
- `compute_covariance(A)`
  - What: covariance matrix $C = \text{cov}(A)$.
  - Why: captures feature co-variation across students.
- `eigen_analysis(C)`
  - What: eigenvalues and eigenvectors of $C$.
  - Why: finds dominant performance drivers.

## app.py

Behavior aggregation (semester input):
- Study hours:
  - What: $0.6 \times \text{normal} + 0.4 \times \text{exam}$
  - Why: normal days dominate the term, but exams still matter.
- Sleep hours:
  - What: $0.7 \times \text{normal} + 0.3 \times \text{exam}$
  - Why: weights routine sleep higher than exam periods.
- Screen time:
  - What: $0.5 \times \text{normal} + 0.3 \times \text{exam} + 0.2 \times \text{holiday}$
  - Why: balances regular usage with spikes in exams or holidays.

Growth aggregation (semester input):
- Clubs score:
  - What: $\text{count} \times \text{club type weight}$
  - Why: rewards technical or domain-focused activities more.
- Events score:
  - What: $\text{count} \times \text{event type weight}$
  - Why: technical events contribute more to growth.
- LinkedIn score:
  - What: $\text{connections}/50 + 0.5 \times \text{posts}$
  - Why: balances network growth and activity.

Trend analytics (analysis dashboard):
- Score trend uses `overall_score()` per semester.
- Vector change uses $\|\Delta\|_2$ with `norm()` to label stable/moderate/large shifts.

Matrix-based scoring (mentor dashboard):
- Scores use $W^T \cdot A$ via `compute_scores_matrix()`.
- Distances use $\|S - \mu\|_2$ for profile classification.

Eigen analysis (college insights):
- Covariance $C$ and eigen decomposition identify dominant feature directions.
- Top factors are chosen by the largest eigenvalue and its eigenvector.

## alerts.py

- Grade drop check:
  - What: average grade difference $\overline{g}_{prev} - \overline{g}_{curr}$.
  - Why: detects broad declines rather than single-subject noise.
- Threshold checks:
  - Attendance, screen time, and study hours are compared to constants.
  - Why: trigger simple early warnings for mentors.

## college.py

- `semester_averages()`
  - What: mean of `overall_score()` by semester.
  - Why: summarizes performance per cohort term.
- `weak_subjects()`
  - What: average grade per subject, sorted ascending.
  - Why: highlights commonly weak subjects across students.
- `college_suggestions()`
  - What: averages attendance and screen time to produce guidance.
  - Why: produces macro-level recommendations.

## constants.py

These values define the numeric scales used by the formulas above:
- `BEHAVIOR_MAX` and `IDEAL_BEHAVIOR` for normalization and alignment.
- `CLUB_TYPE_WEIGHTS` and `EVENT_TYPE_WEIGHTS` for growth scoring.
- `GROWTH_SCORE_MAX_RAW` to normalize growth into 0-10.
- `GROUP_WEIGHTS` to blend behavior, skill, growth, and CGPA into the final score.

## Vectors, Matrices, and Linear Combinations

- Vectors
  - Behavior, growth, and academic grades are treated as vectors in [analysis.py](analysis.py).
  - `behavior_alignment()` compares behavior and ideal behavior vectors using cosine similarity.
  - `behavior_deviation()` uses element-wise differences against the ideal vector.
- Matrices
  - `mean_vector(matrix)` in [linear_algebra.py](linear_algebra.py) computes column-wise averages.
  - Although the UI collects vectors, multiple sessions can be treated as a matrix when averaging.
- Linear combinations
  - `overall_score()` uses `dot_product()` with `GROUP_WEIGHTS` to combine four normalized scores.
  - The behavior aggregates in [app.py](app.py) are weighted sums of normal/exam/holiday inputs.
  - Growth aggregates in [app.py](app.py) are weighted counts by type (clubs/events).
- Eigen decomposition
  - `compute_covariance()` builds $C = \text{cov}(A)$ from the student matrix.
  - `eigen_analysis()` finds eigenvalues/eigenvectors to identify dominant performance drivers.
