# Linear Algebra Chapter Map (Project Usage)

This document maps each chapter topic to how it is used in the project.

## Chapter 1: Systems of Linear Equations
Core idea: solve $Ax=b$

Where used:
- Matrix-vector style scoring uses $W^T \cdot A$ to aggregate features into scores in [analysis.py](analysis.py).
- The concept of solving systems motivates the matrix form used for cohort analysis.

## Chapter 2: Matrices
Core idea: data representation and transformation

Where used:
- Student data is assembled into a matrix $A$ with one column per student via `build_student_matrix()` in [analysis.py](analysis.py).
- The matrix is displayed in College Insights (features × students) in [dashboards.py](dashboards.py).

## Chapter 3: Determinants
Core idea: check invertibility and solve systems

Where used:
- Not directly used in code. Determinant-based inversion is not required for the current analytics.

## Chapter 4: Vector Spaces
Core idea: structure of vectors

Where used:
- Behavior, skill, and growth data are treated as vectors for normalization, comparison, and aggregation in [analysis.py](analysis.py).
- Student profiles are vectors in the student matrix $A$.

## Chapter 5: Inner Product Spaces
Core idea: measure similarity and distance

Where used:
- Dot product in `dot_product()` for weighted sums in [linear_algebra.py](linear_algebra.py).
- Norm in `norm()` and distance calculations for trend change and profile distance in [linear_algebra.py](linear_algebra.py) and [analysis.py](analysis.py).
- Cosine similarity in `behavior_alignment()` to compare behavior with ideal vectors in [analysis.py](analysis.py).

## Chapter 6: Eigenvalues & Eigenvectors
Core idea: important directions in data

Where used:
- Covariance matrix $C = \text{cov}(A)$ computed in `compute_covariance()` in [analysis.py](analysis.py).
- Eigen decomposition in `eigen_analysis()` to find dominant performance drivers, displayed in College Insights in [dashboards.py](dashboards.py).

## Chapter 7: Linear Transformations
Core idea: transforming vectors

Where used:
- Normalization in `normalize_vector()` is a per-component linear scaling in [analysis.py](analysis.py).
- Weighted aggregation for scoring is a linear transformation from feature space to a single score via $W^T \cdot A$.

Example used in code documentation:

```python
transformed = np.dot(weights, student_vector)
```

“We apply a linear transformation using a weight vector to convert student data into a performance score.”
