from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.signal import medfilt
from statsmodels.nonparametric.smoothers_lowess import lowess


# ───────────────────────────── LOWESS ────────────────────────────────
def lowess_smooth(series: pd.Series, frac: float = 0.1, preserve_nans: bool = True) -> pd.Series:
    """
    Locally Weighted Scatter-plot Smoothing (LOWESS).

    Parameters
    ----------
    series : pd.Series
        Numeric series to smooth (index preserved).
    frac : float
        Fraction of total rows to use for each local regression (0 < frac < 1).
    preserve_nans : bool
        If True, NaNs in original series are preserved in output.

    Returns
    -------
    pd.Series
        Smoothed series aligned to original index.
    """
    if not 0 < frac < 1:
        raise ValueError("LOWESS `frac` must be between 0 and 1.")

    if preserve_nans:
        not_null = series.dropna()
        smooth_vals = lowess(not_null.values, np.arange(len(not_null)), frac=frac, return_sorted=False)
        result = pd.Series(index=series.index, dtype=float)
        result.loc[not_null.index] = smooth_vals
        return result
    else:
        sm = lowess(series.values, np.arange(len(series)), frac=frac, return_sorted=False)
        return pd.Series(sm, index=series.index)


# ───────────────────────────── MEDIAN FILTER ─────────────────────────
def median_filter(series: pd.Series, kernel: int = 5) -> pd.Series:
    """
    Apply a sliding-window median filter to the input series.

    Parameters
    ----------
    series : pd.Series
        Input numeric series.
    kernel : int
        Size of sliding window (must be odd).

    Returns
    -------
    pd.Series
        Smoothed series using local medians.
    """
    if kernel < 1:
        raise ValueError("Median filter `kernel` must be positive.")
    if kernel % 2 == 0:
        kernel += 1  # enforce odd size
    smoothed = medfilt(series.values, kernel_size=kernel)
    return pd.Series(smoothed, index=series.index)


# ───────────────────────────── HAMPEL FILTER ─────────────────────────
def hampel_filter(series: pd.Series, window: int = 7, n_sigmas: float = 3.0) -> pd.Series:
    """
    Replace outliers using Hampel identifier — based on local median + MAD.

    Parameters
    ----------
    series : pd.Series
        Input numeric series.
    window : int
        Half-window size (must be odd).
    n_sigmas : float
        Number of standard deviations to use as threshold.

    Returns
    -------
    pd.Series
        Series with outliers replaced by median.
    """
    if window < 1:
        raise ValueError("Hampel `window` size must be positive.")
    if window % 2 == 0:
        window += 1

    k = 1.4826  # scale factor for Gaussian-distributed data
    half = window // 2
    y = series.copy()

    for i in range(half, len(series) - half):
        window_slice = series.iloc[i - half : i + half + 1]
        median = window_slice.median()
        mad = k * np.abs(window_slice - median).median()
        if mad and np.abs(series.iloc[i] - median) > n_sigmas * mad:
            y.iat[i] = median

    return y