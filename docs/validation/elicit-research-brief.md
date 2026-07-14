# Elicit research brief — validating vegetation indices for olive groves

> **Purpose (PRD-005 T2).** A ready-to-run research brief for the **user** to drive with Elicit AI
> and primary literature. It contains (A) the research questions, (B) an empty, structured findings
> template to fill with *cited* values, and (C) recording rules.
>
> **Hard rule (from PRD-005 `human_in_loop_protocol` + `out_of_scope`):** agents never invent
> citations or numbers. Every value in the template must be typed in by the user with a real source.
> Agents only assemble the dossier (T4) *after* this template is filled.
>
> Context the researcher needs going in: our current, **unvalidated** thresholds are inventoried in
> [`current-thresholds.md`](./current-thresholds.md). Olive groves are a **sparse canopy over
> bare/grassy soil** monitored at **10 m Sentinel-2** resolution (mixed tree+soil pixels).

## A. Research questions

Group each Elicit query around one question; capture the papers it surfaces in §B.

1. **Best indices for sparse tree-crop canopies.** Which vegetation indices are most reliable for
   discontinuous olive canopies over exposed soil at 10 m — NDVI, soil-adjusted (OSAVI/SAVI/MSAVI),
   atmospherically-resistant (ARVI), red-edge, or moisture (NDMI/NDWI)? What are their documented
   strengths/weaknesses for olives specifically?
2. **Soil-adjustment factor.** For OSAVI/SAVI on sparse olive canopy, what value of the soil factor
   `L` is recommended, and does the generic `L = 0.16` (our current default) hold, or should it be
   tuned for high soil exposure?
3. **Defensible NDVI ranges for olives.** What NDVI values correspond to healthy vs. stressed olive
   trees at 10 m (accounting for the mixed soil pixel), as opposed to generic dense-crop bands?
4. **Defensible NDMI / water-stress ranges.** What NDMI (or NDWI/CWSI) ranges indicate drought
   stress vs. adequate moisture vs. waterlogging in olives? Is `−0.2` a defensible drought floor and
   `0.5` a defensible waterlogging ceiling?
5. **Seasonality.** How do olive index values vary by phenological season (flowering, fruit set,
   veraison, harvest, dormancy)? Should thresholds/baselines be seasonal (we currently bucket by
   meteorological season with a 3-sample minimum)?
6. **10 m resolution limits.** What are the documented limitations of Sentinel-2 10 m pixels for
   per-tree or per-grove olive assessment (mixed pixels, minimum grove size, sub-pixel canopy)? When
   is 10 m insufficient?
7. **Change/anomaly detection.** Is a fixed absolute NDVI-drop threshold (our `−0.15`) defensible, or
   should change detection be relative to a per-grove seasonal baseline (our `2σ` anomaly rule)?
8. **Disease/severity correlations.** Are there peer-reviewed correlations (e.g. the r²≈0.73–0.76
   ARVI/OSAVI↔disease figures already asserted in our code) between these indices and olive stress,
   Xylella, or Verticillium? Confirm, correct, or retract those uncited claims.

## B. Findings template (user fills — cited only)

For **each source** the user judges relevant, copy one block and complete every field. Leave a field
blank rather than guessing. "Applies to which of our params" should reference the row(s) in
`current-thresholds.md` a finding would change.

### Source S<n>
- **Citation (full):** _authors, year, title, venue/DOI_
- **Link / DOI:**
- **Study crop & region:**
- **Sensor & resolution:**
- **Index/indices studied:**
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):**
- **Reported uncertainty / caveats:**
- **Applies to which of our params (cite §/row in current-thresholds.md):**
- **Supports / contradicts our current value:** _supports | contradicts | refines | n/a_
- **User confidence in applicability (H/M/L) + note:**

_(repeat the block per source)_

### Consolidated recommendation table (fill after reading sources)

| Our param (ref current-thresholds.md) | Current value | Proposed value | Source(s) S# | Confidence | Notes |
|---------------------------------------|---------------|----------------|--------------|------------|-------|
| NDVI "healthy" band (§2) | 0.5–0.7 |  |  |  |  |
| OSAVI soil factor `L` (§1) | 0.16 |  |  |  |  |
| Drought floor NDMI (§4) | −0.2 |  |  |  |  |
| Waterlog ceiling NDMI (§4) | 0.5 |  |  |  |  |
| NDVI-drop alert (§4) | −0.15 |  |  |  |  |
| Anomaly σ threshold (§5) | 2.0 |  |  |  |  |
| Health-score weights (§3) | ARVI/OSAVI/NDVI/NDMI = .30/.30/.20/.20 |  |  |  |  |
| Baseline min samples / seasons (§5) | 3 / meteorological | | | | |

### Open questions / unresolved after research
- _list anything the literature did not settle — feeds a possible follow-up PRD or ground-truth work_

## C. Recording rules

- **One source, one block.** Do not merge multiple papers into one citation.
- **No numbers without a source.** Blank > guessed.
- **Prefer olive-specific + Mediterranean + Sentinel-2/10 m** studies; mark generic-crop sources as
  lower confidence.
- **Flag contradictions** explicitly rather than averaging them away.
- When the template is filled, hand back to the runner/agent for **T4** (assemble
  `olive-index-dossier.md` and propose recalibrated thresholds strictly from these cited values).
