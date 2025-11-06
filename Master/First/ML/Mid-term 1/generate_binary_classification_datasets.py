#!/usr/bin/env python3
import os
import numpy as np
from dataclasses import dataclass


@dataclass
class DatasetSpec:
    name: str
    n_samples: int
    n_features: int
    noise_rate: float  # fraction in [0,1]


def _stratified_train_test_split(y, test_size=0.2, rng=None):
    """Return train_idx, test_idx with class stratification for y in {-1,+1}."""
    rng = np.random.default_rng() if rng is None else rng
    pos = np.flatnonzero(y > 0)
    neg = np.flatnonzero(y < 0)
    rng.shuffle(pos)
    rng.shuffle(neg)
    n_pos_test = max(1, int(round(test_size * len(pos))))
    n_neg_test = max(1, int(round(test_size * len(neg))))
    test_idx = np.concatenate([pos[:n_pos_test], neg[:n_neg_test]])
    train_idx = np.concatenate([pos[n_pos_test:], neg[n_neg_test:]])
    rng.shuffle(test_idx)
    rng.shuffle(train_idx)
    return train_idx, test_idx


def generate_linear_gaussian(n_samples, n_features, noise_rate=0.0, seed=0, mean=0.0, std=1.0):
    """
    X ~ N(mean, std^2 I); draw random separating hyperplane (w, b=0),
    y = sign(w·X), then flip independent fraction 'noise_rate' of labels.
    Returns (X, y, w_true, b_true, flip_mask).
    """
    rng = np.random.default_rng(seed)

    # Features
    X = rng.normal(loc=mean, scale=std, size=(n_samples, n_features)).astype(np.float32)

    # Random separating hyperplane
    w = rng.normal(size=(n_features,)).astype(np.float64)
    w_norm = np.linalg.norm(w) + 1e-12
    w /= w_norm  # unit vector
    b = 0.0

    # Clean labels in {-1,+1}
    scores = X.astype(np.float64) @ w + b
    y = np.where(scores >= 0.0, 1, -1).astype(np.int8)

    # Label-flip noise
    if not (0.0 <= noise_rate <= 1.0):
        raise ValueError("noise_rate must be in [0,1].")
    n_flip = int(round(noise_rate * n_samples))
    flip_mask = np.zeros(n_samples, dtype=bool)
    if n_flip > 0:
        flip_idx = rng.choice(n_samples, size=n_flip, replace=False)
        flip_mask[flip_idx] = True
        y[flip_idx] = -y[flip_idx]

    return X, y, w.astype(np.float32), float(b), flip_mask


def save_npz(path, **arrays):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez_compressed(path, **arrays)


def main():
    # Your three datasets: (d, n) = (2,100), (10,1000), (500,50000)
    # Set per-dataset noise levels here (can all be the same).
    noise_level = 0.10  # 10% label flips
    seed = 12345

    specs = [
        DatasetSpec(name="linsep_d2_n200",    n_samples=200,    n_features=2,   noise_rate=noise_level),
        DatasetSpec(name="linsep_d10_n1000",  n_samples=1000,   n_features=10,  noise_rate=noise_level),
        DatasetSpec(name="linsep_d500_n50000",n_samples=50000,  n_features=500, noise_rate=noise_level),
    ]

    out_dir = "synthetic_linear_gaussian"
    test_size = 0.25

    meta = []
    for i, spec in enumerate(specs):
        # To make runs reproducible but distinct per dataset, offset seed
        ds_seed = seed + i * 1_000

        X, y, w_true, b_true, flip_mask = generate_linear_gaussian(
            n_samples=spec.n_samples,
            n_features=spec.n_features,
            noise_rate=spec.noise_rate,
            seed=ds_seed,
        )

        # Stratified split
        rng = np.random.default_rng(ds_seed + 17)
        train_idx, test_idx = _stratified_train_test_split(y, test_size=test_size, rng=rng)
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test   = X[test_idx],  y[test_idx]

        # Save
        path = os.path.join(out_dir, f"{spec.name}.npz")
        save_npz(
            path,
            X_train=X_train, y_train=y_train,
            X_test=X_test,   y_test=y_test,
            # uncomment if we want to save the solution as well
            # w_true=w_true,   b_true=np.array([b_true], dtype=np.float32),
            flip_mask=flip_mask,
            noise_rate=np.array([spec.noise_rate], dtype=np.float32),
            seed=np.array([ds_seed], dtype=np.int64),
            feature_dim=np.array([spec.n_features], dtype=np.int32),
            n_samples=np.array([spec.n_samples], dtype=np.int32),
            test_size=np.array([test_size], dtype=np.float32),
        )

        # Keep metadata for quick overview
        meta.append({
            "name": spec.name,
            "path": path,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "dim": spec.n_features,
            "noise_rate": spec.noise_rate,
            "class_balance_train": float(np.mean(y_train > 0)),
            "class_balance_test": float(np.mean(y_test > 0)),
            "flips": int(flip_mask.sum()),
        })

    # Print a brief summary
    print("=== Generation summary ===")
    for m in meta:
        print(
            f"{m['name']}: dim={m['dim']}, train={m['n_train']}, test={m['n_test']}, "
            f"noise={m['noise_rate']:.2f}, pos_frac(train)={m['class_balance_train']:.3f}, "
            f"pos_frac(test)={m['class_balance_test']:.3f}, flips={m['flips']}, file={m['path']}"
        )

if __name__ == "__main__":
    main()
