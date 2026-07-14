# Student Performance Analytics System using Linear Algebra
A data-driven student performance analytics platform built using **Python, NumPy, and Streamlit**. The project applies **Linear Algebra** and **Statistical Analysis** to identify the major factors influencing student performance instead of simply displaying marks.

The system is designed for real classroom and mentoring workflows. It analyzes **academic performance, behavioral habits, and extracurricular growth** to provide personalized insights, identify strengths and weaknesses, and discover hidden performance patterns using **Covariance Matrices** and **Eigenvalue Decomposition**.

---

## 📌 Features

- 📊 Student performance dashboard
- 📚 Academic strength and weakness analysis
- 🧠 Behavioral analysis based on study habits
- 🚀 Growth analysis using certifications, clubs, events, and LinkedIn activity
- 📈 Overall weighted performance score
- 📉 Semester-wise performance comparison
- ⚠️ Risk level prediction
- 🧭 Mentor action plan recommendations
- 🎯 Top skill gap identification
- 📐 Student feature matrix visualization
- 🔍 Covariance matrix computation
- 🧮 Eigenvalue and Eigenvector analysis
- ⭐ Automatic identification of the most influential performance factors

---

## 🎯 Real-Time Use Cases

### For mentors
- Enter semester data during review sessions and instantly see whether a student is improving or slipping.
- Check academic weaknesses, behavior alignment, and growth progress in one dashboard instead of using separate records.
- Spot students who need intervention early using the risk score and alert system.
- Follow the mentor action plan to turn alerts into concrete next steps such as remedial practice, attendance tracking, or a 2-week improvement plan.

### For class coordinators and admins
- Compare students across a mentor group to find normal, attention-needed, and outlier profiles.
- Review domain recommendations to see whether a student fits AI/ML, Web Dev, Systems, Cloud, or similar tracks.
- Use audit logs and saved sessions to track how academic decisions were made over time.

### For HODs and department reviews
- Monitor semester-wise trends across students and mentors.
- Identify weak subjects that appear repeatedly across the department.
- Use covariance and eigen analysis to understand which factors are most strongly linked to performance.

### For students
- See what habits are helping or hurting performance.
- Understand whether low scores are coming from academics, behavior, or low growth activity.
- Get a clearer picture of the next improvement area before the next semester review.

---

## 🧠 Project Workflow

```text
Student Data
      │
      ▼
Feature Engineering
(Academics + Behavior + Growth)
      │
      ▼
Student Feature Matrix
      │
      ▼
Normalization
      │
      ▼
Overall Performance Score
      │
      ├──────────────► Skill Gap Analysis
      ├──────────────► Behavior Analysis
      ├──────────────► Growth Analysis
      ▼
Covariance Matrix
      │
      ▼
Eigenvalue Decomposition
      │
      ▼
Top Performance Drivers
      │
      ▼
Interactive Dashboard
```

---

# 🏗️ System Architecture

```text
Input Layer
│
├── Academic Scores
├── Behavior Metrics
└── Growth Activities

        │

Feature Engineering

        │

Student Feature Matrix

        │

Linear Algebra Engine
│
├── Dot Product
├── Matrix Operations
├── Covariance Matrix
├── Euclidean Distance
├── Cosine Similarity
└── Eigen Analysis

        │

Analytics Engine
│
├── Overall Score
├── Risk Prediction
├── Skill Gaps
├── Behavior Alignment
└── Performance Drivers

        │

Streamlit Dashboard
```

---

# 📊 Parameters Used

## Academic

- Subject Grades
- Skill Categories
- CGPA Score

## Behavioral

- Study Hours
- Sleep Hours
- Attendance
- Assignment Completion
- Project Submission
- Screen Time

## Growth

- Clubs
- Events
- Certifications
- LinkedIn Activity

---

# 📐 Linear Algebra Concepts Used

### Matrix Representation
Each student is represented as a **feature vector**, and all students are combined into a **student matrix**.

---

### Dot Product
Used to calculate the weighted overall performance score.

$$
Score = W^T \cdot X
$$

where:

- **W** = Weight Vector
- **X** = Student Feature Vector

---

### Euclidean Distance
Measures how far a student is from the average student profile.

$$
Distance = ||Student - Mean||
$$

---

### Cosine Similarity
Measures how closely a student's behavior aligns with the ideal behavior profile.

$$
Similarity=\frac{A\cdot B}{||A||||B||}
$$

---

### Covariance Matrix
Identifies relationships between different performance factors.

Examples:

- Study Hours ↔ Academic Performance
- Screen Time ↔ Performance
- Attendance ↔ CGPA

---

### Eigenvalue Decomposition
Extracts the dominant patterns within the covariance matrix.

- **Eigenvalues** → Importance of each pattern
- **Eigenvectors** → Features responsible for that pattern

The system identifies the top contributing features affecting overall student performance.

---

# 📊 Performance Insights Generated
The application provides:

- Overall Performance Score
- Academic Strengths
- Academic Weaknesses
- Behavioral Strengths
- Behavioral Weaknesses
- Growth Score
- Semester Comparison
- Risk Level
- Top Skill Gaps
- Student Feature Matrix
- Dominant Performance Drivers
- Feature Importance Ranking

---

# 🛠️ Technologies Used

- Python
- NumPy
- Streamlit
- Pandas
- Linear Algebra
- Statistical Analysis

---

# 🚀 Future Improvements

- Machine Learning-based performance prediction
- PCA for dimensionality reduction
- Student clustering using K-Means
- Personalized improvement recommendations
- Faculty analytics dashboard
- Time-series performance forecasting
- Automated report generation
- Deep learning-based performance prediction

---

# 📸 Screenshots

> Add screenshots of:

- Dashboard
- Student Matrix
- Covariance Matrix
- Performance Analysis
- Eigen Analysis
- Overall Analytics

---

# 🎯 Learning Outcomes
This project demonstrates practical applications of:

- Linear Algebra
- Matrix Operations
- Feature Engineering
- Statistical Analysis
- Data Visualization
- Python Programming
- Streamlit Application Development
- Educational Data Analytics

---

# 👨‍💻 Author
**Praneeth Shetty**

**GitHub:** *(Add your GitHub profile link here)*

**LinkedIn:** *(Add your LinkedIn profile link here)*

---

## ⭐ Key Highlights

- Built a complete educational analytics platform using **Linear Algebra**.
- Represented students as mathematical feature vectors for analysis.
- Applied **Dot Products**, **Euclidean Distance**, **Cosine Similarity**, **Covariance Matrices**, and **Eigenvalue Decomposition** to uncover hidden performance patterns.
- Delivered explainable insights instead of only numerical scores, making student performance analysis more interpretable and actionable.

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
