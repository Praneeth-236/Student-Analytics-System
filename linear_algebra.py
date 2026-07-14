import numpy as np


def dot_product(a, b):
    return float(np.dot(np.array(a, dtype=float), np.array(b, dtype=float)))


def norm(a):
    return float(np.linalg.norm(np.array(a, dtype=float)))


def mean_vector(matrix):
    if matrix is None or len(matrix) == 0:
        return []
    return np.mean(np.array(matrix, dtype=float), axis=0).tolist()


def cosine_similarity(a, b):
    a_norm = norm(a)
    b_norm = norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return dot_product(a, b) / (a_norm * b_norm)
