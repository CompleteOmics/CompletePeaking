import csv
from typing import List, Tuple, Optional, Iterable

import numpy as np
from scipy.signal import savgol_filter, find_peaks

Dataset = Tuple[np.ndarray, np.ndarray, str, float, str]


def _log(msg: str, verbose: bool):
    if verbose:
        print(msg)


def read_data(csv_file_path: str, *, verbose: bool = False) -> List[Dataset]:
    """
    Reads CSV; returns list of (times, intensities, molecule, explicit_rt, file_name).
    Expected header:
        Times, Intensities, Molecule, ExplicitRetentionTime, FileName
    """
    _log(f"📥 Loading input CSV: {csv_file_path}", verbose)
    datasets: List[Dataset] = []
    with open(csv_file_path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        try:
            header = next(reader)
        except StopIteration:
            _log("⚠️ CSV file is empty.", verbose)
            return datasets

        _log(f"   Detected header: {header}", verbose)

        for row_num, row in enumerate(reader, start=2):
            try:
                if len(row) < 5:
                    _log(f"   ⚠️ Row {row_num} skipped: not enough columns", verbose)
                    continue

                file_name = row[4].strip()
                if not file_name:
                    _log(f"   ⚠️ Row {row_num} skipped: missing FileName", verbose)
                    continue

                times = np.array([float(x) for x in row[0].split(",") if x.strip()])
                intensities = np.array([float(x) for x in row[1].split(",") if x.strip()])
                if len(times) != len(intensities):
                    raise ValueError(
                        f"Times/Intensities length mismatch "
                        f"({len(times)} vs {len(intensities)})"
                    )

                molecule = row[2].strip()
                explicit_rt = float(row[3].strip())

                datasets.append((times, intensities, molecule, explicit_rt, file_name))
                _log(
                    f"   ✅ Row {row_num}: loaded Molecule='{molecule}', "
                    f"File='{file_name}', points={len(times)}, explicitRT={explicit_rt}",
                    verbose,
                )
            except Exception as e:
                _log(f"   ⚠️ Row {row_num} skipped: {e}", verbose)

    _log(f"📦 Loaded {len(datasets)} dataset(s).", verbose)
    return datasets


def preprocess_data(intensities: np.ndarray, *, verbose: bool = False) -> np.ndarray:
    """
    Smooth intensities with Savitzky–Golay filter.
    Chooses smallest odd window length >=3 and <=11 (bounded by array length).
    """
    window_length = min(11, len(intensities) - (len(intensities) + 1) % 2)
    if window_length < 3:
        window_length = 3
    if window_length % 2 == 0:
        window_length += 1

    _log(
        f"   🔧 Smoothing intensities (Savitzky–Golay): window_length={window_length}, polyorder=3",
        verbose,
    )
    return savgol_filter(intensities, window_length=window_length, polyorder=3)


def detect_peak(
    times: np.ndarray,
    intensities: np.ndarray,
    explicit_rt: float,
    *,
    rt_half_window: float = 1.0,
    verbose: bool = False,
) -> Tuple[float, float, int]:
    """
    Find apex near explicit RT; return (apex_time, apex_intensity, apex_index).
    Searches within [explicit_rt - rt_half_window, explicit_rt + rt_half_window].
    Falls back to full range if the window has no points.
    """
    _log(
        f"   🔎 Detecting peak: search window = "
        f"[{explicit_rt - rt_half_window:.4f}, {explicit_rt + rt_half_window:.4f}]",
        verbose,
    )
    mask = (times >= explicit_rt - rt_half_window) & (times <= explicit_rt + rt_half_window)
    times_win, ints_win = times[mask], intensities[mask]

    if not times_win.size:
        _log("   ⚠️ No points in RT window; searching entire trace.", verbose)
        times_win, ints_win = times, intensities

    peaks, _ = find_peaks(ints_win)
    if not peaks.size:
        raise ValueError("No peaks found in search region")

    apex_idx_win = peaks[np.argmax(ints_win[peaks])]
    full_idx = np.where(mask)[0] if mask.any() else np.arange(len(times))
    apex_idx = full_idx[apex_idx_win]

    _log(
        f"   ✅ Apex found at time={times[apex_idx]:.4f}, intensity={intensities[apex_idx]:.2f}, "
        f"index={int(apex_idx)}",
        verbose,
    )
    return times[apex_idx], intensities[apex_idx], int(apex_idx)


def find_peak_limits_combined(
    times: np.ndarray,
    intensities: np.ndarray,
    apex_idx: int,
    *,
    fraction_of_apex: float = 0.05,
    max_extension: int = 50,
    debug: bool = False,
    verbose: bool = False,
) -> Tuple[float, float]:
    """
    Find left/right peak boundaries around apex using:
      1) second-derivative zero crossings for initial bounds
      2) extension toward baseline using a threshold:
         threshold = baseline + fraction_of_apex * (apex - baseline)

    Returns (left_time, right_time).
    """
    _log(
        f"   📐 Finding boundaries: fraction_of_apex={fraction_of_apex}, "
        f"max_extension={max_extension}",
        verbose,
    )

    # Smooth again for derivative calculations (kept same as your original)
    sm = savgol_filter(intensities, window_length=11, polyorder=3)
    second_deriv = np.gradient(np.gradient(sm, times), times)
    zeros = np.where(np.diff(np.sign(second_deriv)))[0]

    start_idx = zeros[zeros < apex_idx][-1] if (zeros < apex_idx).any() else 0
    end_idx = zeros[zeros > apex_idx][0] if (zeros > apex_idx).any() else len(sm) - 1

    if debug or verbose:
        _log(
            f"   • Initial zero-crossing bounds: [{times[start_idx]:.4f}, {times[end_idx]:.4f}] "
            f"(idx {start_idx}..{end_idx})",
            True,
        )

    apex_int = sm[apex_idx]
    left_reg = sm[max(0, start_idx - max_extension) : start_idx]
    right_reg = sm[end_idx : min(len(sm), end_idx + max_extension)]

    if len(left_reg) and len(right_reg):
        baseline = min(np.percentile(left_reg, 20), np.percentile(right_reg, 20))
    elif len(left_reg):
        baseline = np.percentile(left_reg, 20)
    elif len(right_reg):
        baseline = np.percentile(right_reg, 20)
    else:
        baseline = float(np.min(sm))

    thresh = baseline + fraction_of_apex * (apex_int - baseline)

    if debug or verbose:
        _log(
            f"   • Apex={apex_int:.2f} | Baseline≈{baseline:.2f} | Threshold={thresh:.2f}",
            True,
        )

    left = start_idx
    while left > 0 and sm[left] > thresh and left > start_idx - max_extension:
        left -= 1

    right = end_idx
    while right < len(sm) - 1 and sm[right] > thresh and right < end_idx + max_extension:
        right += 1

    _log(
        f"   ✅ Extended bounds: [{times[left]:.4f}, {times[right]:.4f}] "
        f"(idx {left}..{right})",
        verbose or debug,
    )
    return times[left], times[right]
