from pnwater.ml.dataset import generate_dataset
from pnwater.rivers import RIVERS


def test_dataset_shape_and_labels():
    X, y = generate_dataset(n_normal_per_river=10, n_anomalous_per_river=5, seed=1)

    expected_total = len(RIVERS) * (10 + 5)
    assert len(X) == len(y) == expected_total
    assert sum(y) == len(RIVERS) * 5
    assert all(len(row) == 4 for row in X)


def test_dataset_is_deterministic_given_a_seed():
    X1, y1 = generate_dataset(n_normal_per_river=20, n_anomalous_per_river=5, seed=7)
    X2, y2 = generate_dataset(n_normal_per_river=20, n_anomalous_per_river=5, seed=7)
    assert X1 == X2
    assert y1 == y2


def test_anomalous_rows_have_at_least_one_large_z_score():
    X, y = generate_dataset(n_normal_per_river=20, n_anomalous_per_river=20, seed=3)
    anomaly_rows = [row for row, label in zip(X, y) if label == 1]
    assert all(max(abs(v) for v in row) >= 3.0 for row in anomaly_rows)
