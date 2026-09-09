# Current vegetation indices & thresholds (as implemented)

> **Purpose (PRD-005 T1).** A factual, code-derived inventory of every vegetation index and every
> threshold currently used in the backend, with exact values and the file/line where each lives.
> This is the *input* to the scientific validation (T3/T4): the numbers below are what we must
> defend or recalibrate. **Nothing here is validated** — it is only a faithful mirror of the code.
>
> Cross-check command: `grep -n THRESHOLD backend/app/alerts.py` and read the docstrings in
> `backend/app/vegetation_indices.py`. Every row cites a line so the user can verify exactness
> (acceptance criterion: "current-thresholds.md matches the code exactly").
>
> **Source of truth as of branch `DAN-10-prd-005-validation-dossier`** — commit is recorded in the PR.

## 1. Indices computed

All four indices are computed on Sentinel-2 bands in `backend/app/vegetation_indices.py`.

| Index | Formula (as coded) | Bands (Sentinel-2) | Function | Lines |
|-------|--------------------|--------------------|----------|-------|
| NDVI  | `(NIR − Red) / (NIR + Red)` | Red=B4, NIR=B8 | `calculate_ndvi` | 7–37 |
| NDMI  | `(NIR − SWIR) / (NIR + SWIR)` | NIR=B8, SWIR=B11 | `calculate_ndmi` | 40–70 |
| ARVI  | `(NIR − (2·Red − Blue)) / (NIR + (2·Red − Blue))` | Red=B4, NIR=B8, Blue=B2 | `calculate_arvi` | 73–113 |
| OSAVI | `(NIR − Red) / (NIR + Red + L)`, `L = 0.16` | Red=B4, NIR=B8 | `calculate_osavi` | 116–156 |

Notes:
- OSAVI soil-adjustment factor `L` defaults to **0.16** (`vegetation_indices.py:139`).
- Invalid/zero-division pixels are set to `NaN` in every index.

## 2. Interpretation bands documented in docstrings

These bands appear in docstrings only (they are **not** enforced in code, but they are what the
product presents/implies as "healthy" ranges, so they are in scope for validation).

### NDVI (`vegetation_indices.py:14–17`)
| Range | Documented meaning |
|-------|--------------------|
| `< 0.2` | Bare soil, dead vegetation |
| `0.2 – 0.5` | Sparse vegetation |
| `0.5 – 0.7` | Healthy vegetation |
| `> 0.7` | Very dense healthy vegetation |

### NDMI (`vegetation_indices.py:46–50`)
| Range | Documented meaning |
|-------|--------------------|
| `< −0.2` | Severe drought stress |
| `−0.2 – 0.0` | Moderate water stress |
| `0.0 – 0.4` | Adequate moisture |
| `> 0.4` | High moisture / waterlogged |

### ARVI (`vegetation_indices.py:84–87`)
| Range | Documented meaning |
|-------|--------------------|
| `< 0` | Non-vegetated surfaces |
| `0.2 – 0.4` | Sparse vegetation |
| `0.4 – 0.6` | Moderate vegetation |
| `> 0.6` | Dense healthy vegetation |

### OSAVI (`vegetation_indices.py:128–131`)
| Range | Documented meaning |
|-------|--------------------|
| `< 0.2` | Bare soil, minimal vegetation |
| `0.2 – 0.4` | Sparse vegetation |
| `0.4 – 0.6` | Moderate vegetation coverage |
| `> 0.6` | Dense vegetation |

## 3. Health score model (`calculate_health_score`, `vegetation_indices.py:159–249`)

Output is an integer `0–100`, clamped.

**NDVI sub-score** (`:186–195`): linear map of NDVI `[0,1] → [0,100]` (`score = NDVI·100`);
NDVI `< 0 → 0`, `> 1 → 100`.

**NDMI sub-score** (`:197–210`), piecewise:
| NDMI range | Sub-score |
|------------|-----------|
| `< −0.3` | `0` |
| `−0.3 – 0.0` | `40 + (NDMI + 0.3)/0.3 · 40`  (i.e. 40→80) |
| `0.0 – 0.4` | `80 + NDMI/0.4 · 20`  (i.e. 80→100) |
| `> 0.4` | `max(0, 100 − (NDMI − 0.4)·50)` |

**ARVI / OSAVI sub-scores** (`:212–230`): same linear `[0,1] → [0,100]` map as NDVI.

**Composite weights:**
| Mode | Condition | Weights | Lines |
|------|-----------|---------|-------|
| Multi-index | ARVI *and* OSAVI provided | ARVI 0.30, OSAVI 0.30, NDVI 0.20, NDMI 0.20 | 232–242 |
| Legacy | ARVI/OSAVI absent | NDVI 0.70, NDMI 0.30 | 243–246 |

## 4. Alert thresholds (`AlertDetector`, `backend/app/alerts.py:21–26`)

| Constant | Value | Line |
|----------|-------|------|
| `NDVI_DROP_THRESHOLD` | `−0.15` (absolute NDVI drop vs. prior reading) | 22 |
| `DROUGHT_STRESS_THRESHOLD` | `−0.2` (NDMI floor) | 23 |
| `WATERLOG_THRESHOLD` | `0.5` (NDMI ceiling) | 24 |
| `HEALTH_SCORE_CRITICAL` | `40` | 25 |
| `HEALTH_SCORE_WARNING` | `60` | 26 |

Severity escalation logic:
| Alert | Rule | Lines |
|-------|------|-------|
| NDVI drop | `critical` if drop `≤ −0.25`, else `warning`; compares to most recent reading within **30 days** back | 96–97, 83–87 |
| Drought stress | fires when NDMI `≤ −0.2`; `critical` if `≤ −0.4` (severe) or `≤ −0.3`, else `warning` | 139–158 |
| Waterlogging | fires when NDMI `≥ 0.5`; `warning` if `< 0.6`, else `critical` | 196–197 |
| Health score | `critical` if `< 40`, `warning` if `< 60` | 241–249 |

## 5. Baseline / anomaly parameters (`BaselineManager`, `backend/app/baseline.py`)

| Parameter | Value | Line |
|-----------|-------|------|
| Seasons (Northern Hemisphere) | winter=[12,1,2], spring=[3,4,5], summer=[6,7,8], fall=[9,10,11] | 18–23 |
| `MIN_SAMPLES` (min for reliable baseline) | `3` | 26 |
| `calculate_baseline` lookback | `years_back = 3` | 57–63 |
| Anomaly threshold | `std_dev_threshold = 2.0` (σ from seasonal mean) | 250–257 |
| Metrics with baselines | `ndvi`, `ndmi` only (ARVI/OSAVI excluded) | 77, 185 |

## 6. Unsourced claims already in the code (flag for validation)

The following quantitative claims appear in docstrings **without citations** and must be verified or
removed during T3/T4 (the PRD forbids agent-invented citations, so these are user-verify items):

| Claim | Location |
|-------|----------|
| "ARVI correlates strongly with disease incidence and severity (r²=0.73–0.76) in olive groves" | `vegetation_indices.py:89–90` |
| "OSAVI achieves high correlation with field observations (r²=0.73–0.76)" | `vegetation_indices.py:133–134` |
| Composite weighting described as "research-backed" | `vegetation_indices.py:232` |

## 7. Known gaps this inventory surfaces (for the brief, not conclusions)

- Interpretation bands (§2) are generic and **not olive-specific**; they are documented, not enforced.
- Alert thresholds (§4) are hard-coded constants, not derived from any per-grove baseline.
- OSAVI `L=0.16` is the generic default; no justification for sparse olive canopy is recorded.
- Baselines exist for NDVI/NDMI only; ARVI/OSAVI feed the health score but have no anomaly baseline.
