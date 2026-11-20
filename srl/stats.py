"""Paired bootstrap over queries (10,000 resamples, seed 0) and the exact McNemar test."""

from __future__ import annotations

import math

import numpy as np

B = 10_000


def boot_paired(a, b, seed: int = 0) -> tuple[float, float, float]:
    """Mean of a - b and its 95% percentile interval, resampling paired units."""
    d = np.asarray(a, float) - np.asarray(b, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), (B, len(d)))
    lo, hi = np.percentile(d[idx].mean(axis=1), [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def boot_stat(n: int, stat, seed: int = 0) -> tuple[float, float, float]:
    """A statistic of resampled unit indices (stat(idx) -> float), e.g. a difference of two rates computed on
    overlapping subsets of the same queries."""
    rng = np.random.default_rng(seed)
    full = stat(np.arange(n))
    vals = np.array([stat(rng.integers(0, n, n)) for _ in range(B)])
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return float(full), float(lo), float(hi)


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from the discordant counts b (a=1, b=0) and c (a=0, b=1)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def discordant(a, b) -> tuple[int, int]:
    a, b = np.asarray(a, int), np.asarray(b, int)
    return int(((a == 1) & (b == 0)).sum()), int(((a == 0) & (b == 1)).sum())
