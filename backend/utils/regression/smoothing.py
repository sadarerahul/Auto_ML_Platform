# utils/regression/smoothing.py
"""
Utility functions for smoothing numeric series.
Place this file at: backend/utils/regression/smoothing.py
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.signal import medfilt
from statsmodels.nonparametric.smoothers_lowess import lowess


# ───────────────────────────── LOWESS ──
def lowess_smooth(series: pd.Series, frac: float = 0.1) -> pd.Series:
    """Locally Weighted Scatter-plot Smoothing (LOWESS).

    Parameters
    ----------
    series : pd.Series
        Numeric series to smooth (index preserved).
    frac : float, optional
        Fraction of total rows used as local window size (0–1).

    Returns
    -------
    pd.Series
        Smoothed series.
    """
    sm = lowess(series.values,
                np.arange(len(series)),
                frac=frac,
                return_sorted=False)
    return pd.Series(sm, index=series.index)


# ───────────────────────────── MEDIAN FILTER ──
def median_filter(series: pd.Series, kernel: int = 5) -> pd.Series:
    """Sliding-window median filter."""
    if kernel % 2 == 0:
        kernel += 1                      # kernel must be odd
    sm = medfilt(series.values, kernel_size=kernel)
    return pd.Series(sm, index=series.index)


# ───────────────────────────── HAMPEL FILTER ──
def hampel_filter(series: pd.Series,
                  window: int = 7,
                  n_sigmas: float = 3.0) -> pd.Series:
    """Replace outliers by local median using Hampel identifier."""
    if window % 2 == 0:
        window += 1                      # window must be odd
    k     = 1.4826                       # MAD→σ scale
    half  = window // 2
    y     = series.copy()

    for i in range(half, len(series) - half):
        win = series.iloc[i-half:i+half+1]
        med = win.median()
        mad = k * np.abs(win - med).median()
        if mad and np.abs(series.iloc[i] - med) > n_sigmas * mad:
            y.iat[i] = med
    return y