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
>
> **Status (2026-08-03).** T3 is done. §B below is **filled** — transcribed verbatim-in-substance
> from the user's completed research recorded as comments on Linear **DAN-16**. Nothing in §B was
> researched, inferred, or completed by an agent: where the user's findings did not state a value
> (DOI, r², RMSE, region), the field reads *"Not reported in source material."* rather than being
> filled from model knowledge. This unblocks **T4**.

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

_(repeat the block per source — the block above is the blank exemplar; the filled sources follow)_

---

### Filled sources (from Linear DAN-16, research completed 2026-08-02/03)

> **Headline finding — read this before the table.** Across every question that asked for a number,
> the literature the user surfaced **does not support absolute, transferable index thresholds for
> olive groves.** Absolute NDVI/OSAVI/NDMI values shift with canopy density, cultivar, row spacing,
> soil brightness, inter-row grass, season, irrigation and 10 m pixel mixing. The consistent
> recommendation is an **orchard-relative seasonal baseline** — compare each pixel/grove with its own
> healthy seasonal envelope, require persistence and spatial coherence, and calibrate any percentile
> or σ cut-off against field data. This invalidates the *form* of most of our current constants
> (§2 interpretation bands, §4 alert constants), not just their values.

> **Second headline finding — the `r² > 0.7` figure cannot be inherited by our pipeline.** Hornero
> et al. 2020 (S1) produced that coefficient from a **modelling pipeline**: a Sentinel-2A two-year
> time series *plus* airborne hyperspectral imagery *plus* field observations *plus* a **3-D
> radiative-transfer model** that explicitly corrected for seasonal background variation and soil
> spectra. And it describes the **temporal variation** of ARVI/OSAVI, not single-date index values.
> A Sentinel-2-only pipeline applying raw index thresholds **cannot claim that statistic**.
> Attributing it to a static index threshold — which is what `vegetation_indices.py` §6 currently
> does — is a **category error**, not merely an imprecise citation.
>
> **Defensible replacement claim:** *seasonal change in ARVI/OSAVI is a useful orchard-scale
> indicator of Xylella-associated decline when canopy structure, season and soil background are
> modelled or corrected for — and it is not evidence that either index is Xylella-specific.*

Source-material notes that apply to **every** block below:
- **No DOI or link was recorded for any paper** in the research comments, so every `Link / DOI`
  field reads *"Not reported in source material."* No DOI has been reconstructed.
- `Study crop & region` / `Sensor & resolution` are populated **only** where the source material
  (title text or an explicit statement) supplied them.
- Papers cited under several research questions get **one block**, per the §C "one source, one
  block" rule; the questions each bears on are named in the `Applies to which of our params` field.

### Source S1 — Hornero et al., 2020
- **Citation (full):** Hornero et al., 2020. *Monitoring the incidence of Xylella fastidiosa infection in olive orchards using ground-based evaluations, airborne imaging spectroscopy and Sentinel-2 time series through 3-D radiative transfer modelling.* Remote Sensing of Environment.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive orchards, **Apulia, Italy**. Validation covered **more than 3,000 trees across 16 orchards**. (Note for our own dossier: Apulia is **not** the region of this product's validation grove.)
- **Sensor & resolution:** A **combination** — Sentinel-2A **two-year time series**, airborne hyperspectral imagery, field observations, **and a 3-D radiative-transfer model** that explicitly accounted for seasonal background variation and soil-spectrum effects. Resolutions not reported in source material.
- **Index/indices studied:** ARVI and OSAVI (as Sentinel-2 structural and physiological indices), evaluated as **temporal variation**, not as single-date values.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** The **temporal variation of ARVI and OSAVI showed the strongest performance among the evaluated Sentinel-2 structural and physiological indices**, with coefficient of determination reported as **r² > 0.7 for disease-severity and disease-incidence estimation**. The accessible abstract does **not expose separate exact r² values for ARVI versus OSAVI**, nor a single coefficient for incidence alone — it reports the combined result as greater than 0.7. Do **not** quote "ARVI = X" or "OSAVI = Y" from this record without extracting the results table or figure from the full paper.
- **Reported uncertainty / caveats:** **The result is an output of a modelling pipeline, not of a raw index.** It depends on correcting or modelling canopy structure, season and soil background (3-D radiative transfer) with airborne hyperspectral imagery in the loop — it is not a property of a Sentinel-2 reflectance threshold. It is also evidence about **seasonal change**, not absolute values. It is strong evidence that seasonal change in ARVI/OSAVI is useful for **orchard-scale** Xylella monitoring, and **not** evidence that either index is Xylella-**specific**.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q8. §6 "ARVI correlates strongly with disease incidence and severity (r²=0.73–0.76)" and "OSAVI achieves high correlation with field observations (r²=0.73–0.76)".
- **Supports / contradicts our current value:** **contradicts** — our docstrings attach this statistic to a **static index threshold** in a Sentinel-2-only pipeline with no canopy-structure, season or soil-background correction. That is a category error, not merely an imprecise citation: the pipeline that produced `r² > 0.7` is not the pipeline we run, and the quantity it predicted (temporal variation) is not the quantity we threshold. The `0.73–0.76` range is additionally unconfirmed.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Directly on-topic for Xylella, but **not transferable to our current implementation** — see the two callouts above and Open question 1.)

### Source S2 — Hornero et al., 2018
- **Citation (full):** Hornero et al., 2018. *Using Sentinel-2 Imagery to Track Changes Produced by Xylella Fastidiosa in Olive Trees.* IEEE International Geoscience and Remote Sensing Symposium (IGARSS).
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive trees (per title); **more than 3,300 trees**. Region not reported in source material.
- **Sensor & resolution:** Sentinel-2; **188 images**. Resolution not reported in source material.
- **Index/indices studied:** OSAVI; **OSAVI1510** (a narrow-band index).
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Using 188 Sentinel-2 images and more than 3,300 trees, found **OSAVI best/superior for incidence trends**, with the **largest separation between disease levels during summer**; a **different narrow-band index, OSAVI1510, was better for severity change**. No r²/RMSE reported in source material.
- **Reported uncertainty / caveats:** The source material describes OSAVI1510 only as "a different narrow-band index" — it does **not** state which wavelength/band it requires or whether Sentinel-2 can supply it. Treat the availability of OSAVI1510 to our pipeline as **unverified** (see Open question 4); do not assume it is computable from the bands we already ingest.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q8. §6 uncited r² claims; §1 index set (OSAVI1510 is not among our four indices); also bears on §5 seasonal bucketing via the summer-separation result.
- **Supports / contradicts our current value:** refines — supports OSAVI's role for Xylella **incidence trends** (a temporal quantity), but contributes **no r² value**, so it does not substantiate §6's `0.73–0.76`; and it indicates our index set may be the wrong one for **severity** specifically.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material.

### Source S3 — Calderón et al., 2015
- **Citation (full):** Calderón et al., 2015. *Early Detection and Quantification of Verticillium Wilt in Olive Using Hyperspectral and Thermal Imagery over Large Areas.* Remote Sensing.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive (per title); "large areas". Region not reported in source material.
- **Sensor & resolution:** Airborne hyperspectral and thermal imagery. Resolution not reported in source material.
- **Index/indices studied:** Canopy temperature, chlorophyll fluorescence, structural / chlorophyll / carotenoid / xanthophyll traits, and disease-specific indices. **Not** ARVI/OSAVI.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** **79.2% overall accuracy with SVM**; early low-severity classification was uneven.
- **Reported uncertainty / caveats:** Early, low-severity cases classified unevenly. The discriminating signal sits in airborne hyperspectral/thermal data — **not available to a Sentinel-2-only pipeline**.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q8. §6 uncited r² claims, specifically their extension to Verticillium.
- **Supports / contradicts our current value:** contradicts — the strongest Verticillium evidence rests on sensors we do not have; no comparably direct study establishes ARVI or OSAVI as the best Verticillium indicators.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material.

### Source S4 — Sancho-Adamson et al., 2019
- **Citation (full):** Sancho-Adamson et al., 2019. *Use of RGB Vegetation Indexes in Assessing Early Effects of Verticillium Wilt of Olive in Asymptomatic Plants in High and Low Fertility Scenarios.* Remote Sensing.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive, asymptomatic plants, high- and low-fertility scenarios (per title). Region not reported in source material.
- **Sensor & resolution:** RGB. Not reported in source material beyond that.
- **Index/indices studied:** RGB indices **NGRDI** and **TGI**.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** In asymptomatic plants, **NGRDI and TGI detected inoculation-related changes even when stomatal conductance and chlorophyll fluorescence did not**. No r²/RMSE reported in source material.
- **Reported uncertainty / caveats:** Implies early Verticillium response is **not captured by a single generic greenness index**.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q8. §6 uncited r² claims; §2 interpretation bands (a generic greenness band will miss early disease).
- **Supports / contradicts our current value:** contradicts — argues against relying on one broad-band greenness index for early disease.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material.

### Source S5 — Poblete et al., 2021
- **Citation (full):** Poblete et al., 2021. *Discriminating Xylella fastidiosa from Verticillium dahliae infections in olive trees using thermal- and hyperspectral-based plant traits.* ISPRS Journal of Photogrammetry and Remote Sensing.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive trees, **27 orchards**, mixed-pathogen setting. Region not reported in source material.
- **Sensor & resolution:** Thermal and hyperspectral. Resolution not reported in source material.
- **Index/indices studied:** Combined hyperspectral and thermal traits including **SIF**, **CWSI**, and narrow-band indices.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** **92% overall accuracy for Xylella** and **98% for Verticillium** in the mixed-pathogen setting.
- **Reported uncertainty / caveats:** Xylella and Verticillium both disrupt xylem function and can produce **similar water-stress-like symptoms**; discrimination required the combined thermal + narrow-band trait set. ARVI/OSAVI alone should not be treated as pathogen-specific biomarkers.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q8. §6 uncited r² claims; bears on the whole product claim of pathogen attribution.
- **Supports / contradicts our current value:** contradicts — pathogen discrimination is not achievable from our four broad-band indices.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material.

### Source S6 — Leolini et al., 2022
- **Citation (full):** Leolini et al., 2022. *Use of Sentinel-2 Derived Vegetation Indices for Estimating fPAR in Olive Groves.* Agronomy.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive groves. Region not reported in source material.
- **Sensor & resolution:** Sentinel-2 (pixel-scale; the 10 m mixed-pixel problem is the study's subject).
- **Index/indices studied:** MCARI2/OSAVI, OSAVI, NDVI (for fPAR estimation).
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Using a **disentangling/rescaling procedure** to separate olive-tree and inter-row grass contributions, **MCARI2/OSAVI was among the better performers** for fPAR validation, and the corrected indices performed better than treating the raw pixel value as a direct canopy measurement. No r²/RMSE reported in source material.
- **Reported uncertainty / caveats:** Tree **and** grass jointly contribute to the Sentinel-2 signal; raw 10 m indices must not be read as pure canopy measurements. Inter-row grass can make a stressed olive canopy look healthier.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q1, Q2, Q5, Q6, Q7. §1 (index set, no canopy-fraction term), §2 (interpretation bands), §5 (baselines).
- **Supports / contradicts our current value:** contradicts/refines — our pipeline has no canopy-fraction or inter-row term, so every §2 band and §4 constant is being applied to a mixed signal.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Olive + Sentinel-2 + mixed pixel — the single most cross-cutting source in this research, cited under five of the eight questions.)

### Source S7 — Zarco-Tejada et al., 2004
- **Citation (full):** Zarco-Tejada et al., 2004. *Hyperspectral indices and model simulation for chlorophyll estimation in open-canopy tree crops.* Venue not reported in source material. (Recorded in the source comments as "Zarco-Tejadaa et al." — assumed a typo for Zarco-Tejada; not corrected in the citation string beyond this note.)
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Open-canopy tree crops (per title). Region not reported in source material.
- **Sensor & resolution:** Hyperspectral imagery plus model simulation; explicitly compares crown-level with lower-resolution aggregated pixels. Exact resolutions not reported in source material.
- **Index/indices studied:** Hyperspectral chlorophyll indices (specific indices not reported in source material).
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Relationships derived from **pure crown pixels did not transfer directly to lower-resolution pixels containing soil and shadow**; a canopy model is required. No r²/RMSE reported in source material.
- **Reported uncertainty / caveats:** In sparse olive pixels, adjusting the index alone cannot separate "more soil", "less crown" and "stressed crown" — canopy fraction must be modelled explicitly.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q1, Q2, Q6. §1 (OSAVI `L`, index set), §2 (interpretation bands).
- **Supports / contradicts our current value:** contradicts — undermines applying crown-derived index bands to a 10 m aggregated pixel, which is what §2 does.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Generic open-canopy tree crops, not olive-specific — per §C rules this would be a lower-confidence, generic-crop source.)

### Source S8 — Cantini et al., 2023
- **Citation (full):** Cantini et al., 2023. *Direct and indirect ground estimation of leaf area index to support interpretation of NDVI data from satellite images in hedgerow olive orchards.* Smart Agricultural Technology.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** **Hedgerow** olive orchards. Region not reported in source material.
- **Sensor & resolution:** Sentinel-2, plus ground LAI measurements aggregated to the Sentinel-2 grid.
- **Index/indices studied:** NDVI (against LAI).
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Whole-orchard Sentinel-2 NDVI ranged **0.28 to 0.81 over two years**, with summer values around **0.28–0.36 in one year** and **0.39–0.41 in another**. LAI measured across the plants represented in each pixel was **directly correlated** with Sentinel-2 NDVI. No r² value reported in source material.
- **Reported uncertainty / caveats:** The observed range is described as variation large enough to make a **fixed Mediterranean NDVI cut-off unreliable**. NDVI's absolute value depends heavily on canopy density, season, and what occupies the inter-row.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q1, Q3, Q6. **§2 NDVI band `0.5–0.7` = "healthy"**; §1 index choice.
- **Supports / contradicts our current value:** **contradicts** — a hedgerow (i.e. dense) olive orchard sat at 0.28–0.41 in summer, well below our "healthy" 0.5–0.7 band, while presumably not being unhealthy.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Olive + Sentinel-2 + explicit NDVI numbers — the most directly damaging source for §2.)

### Source S9 — Huete, 1988
- **Citation (full):** Huete, 1988. *Adjusting vegetation indices for soil influences.* International Agrophysics.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Not reported in source material.
- **Sensor & resolution:** Not reported in source material.
- **Index/indices studied:** SAVI (soil-adjusted vegetation index), soil-adjustment factor `L`.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** SAVI was designed to reduce **first-order soil–vegetation interaction and soil-brightness effects** in red–NIR indices. The source material gives the `L` interpretation as: `L ≈ 1.0` very sparse vegetation / strong soil influence; `L ≈ 0.5` conventional mixed-cover default; `L ≈ 0` dense vegetation, where SAVI approaches NDVI. **OSAVI fixes the adjustment at `0.16` rather than estimating `L` per image** — the source material states this but attributes no citation to the `0.16` value itself.
- **Reported uncertainty / caveats:** The source material's own recommendation is **not** to automatically swap OSAVI for SAVI at `L = 1.0` for sparse olive; see S6/S7 on canopy fraction.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q2. **§1 OSAVI `L = 0.16`** (`vegetation_indices.py:139`).
- **Supports / contradicts our current value:** refines — establishes what `L` means and that `0.16` is the *generic* OSAVI constant, but supplies **no olive-specific justification** for it. The `0.16` value itself remains uncited.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Foundational, generic-crop — lower confidence per §C.)

### Source S10 — Battista et al., 2023
- **Citation (full):** Battista et al., 2023. *Estimating the effect of water shortage on olive trees by the combination of meteorological and Sentinel-2 data.* European Journal of Remote Sensing.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive trees (bi-layer olive grove: trees + understory grass). Region not reported in source material.
- **Sensor & resolution:** Sentinel-2 combined with meteorological data.
- **Index/indices studied:** NDVI, NDMI (and the tree-vs-grass partition of both).
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** In a bi-layer olive grove, **understory grass responds faster to water shortage than the deeper-rooted olive trees**, so raw Sentinel-2 NDVI or NDMI may **not represent the tree component** unless the signal is partitioned. No threshold values, r² or RMSE reported in source material.
- **Reported uncertainty / caveats:** Tree water status can lag the faster response of understory grass — a raw index decline may be grass stress, not tree stress, and vice versa.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q3, Q4, Q7. §2 NDVI/NDMI bands, **§4 `DROUGHT_STRESS_THRESHOLD = −0.2`**, §4 `NDVI_DROP_THRESHOLD = −0.15`.
- **Supports / contradicts our current value:** contradicts — our drought and NDVI-drop constants are applied to an unpartitioned pixel, so they may be firing on inter-row grass.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Olive + Sentinel-2 + water stress — directly on-topic for §4.)

### Source S11 — Navrozidis et al., 2019
- **Citation (full):** Navrozidis et al., 2019. *Olive Trees Stress Detection Using Sentinel-2 Images.* IEEE International Geoscience and Remote Sensing Symposium (IGARSS).
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive trees, Verticillium-stress regions. Region not reported in source material.
- **Sensor & resolution:** Sentinel-2.
- **Index/indices studied:** "A spectral index" plus time-series analysis; the specific index is not named in the source material.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Used a spectral index and **time series as an anomaly indicator** to map stress and identify anomalies in **Verticillium-stress regions**. No threshold, r² or RMSE reported in source material.
- **Reported uncertainty / caveats:** The source material states explicitly that this **does not establish a transferable NDVI cut-off**, and that NDVI should be treated as a broad stress/anomaly indicator rather than a diagnostic threshold.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q3, Q7. §2 NDVI bands, §5 anomaly rule.
- **Supports / contradicts our current value:** supports the **anomaly/time-series form** of §5; contradicts the absolute-band form of §2.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (The only Sentinel-2 Verticillium-stress mapping source found — load-bearing for Open question 2.)

### Source S12 — Asgari et al., 2023
- **Citation (full):** Asgari et al., 2023. *Potential application of spectral indices for olive water status assessment in (semi-)arid regions: A case study in Khuzestan Province, Iran.* Plant Direct.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive, **Khuzestan Province, Iran**, (semi-)arid.
- **Sensor & resolution:** **Leaf-level** spectral measurements (not satellite).
- **Index/indices studied:** Spectral indices for water status (specific indices not reported in source material).
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Found spectral indices **associated with relative water content and soil water content**, but performance **differed among indices and among irrigation regimes**. No threshold values, r² or RMSE reported in source material.
- **Reported uncertainty / caveats:** Leaf-level, not 10 m pixel; and not Mediterranean. Index performance was regime-dependent.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q4. **§4 `DROUGHT_STRESS_THRESHOLD = −0.2` / `WATERLOG_THRESHOLD = 0.5`**, §2 NDMI bands.
- **Supports / contradicts our current value:** refines — supports that spectral water indices track water status at all, but supplies **no NDMI cut-off** and therefore does not defend `−0.2` or `0.5`.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Leaf-level + non-Mediterranean region — lower confidence per §C.)

### Source S13 — Sánchez-Piñero et al., 2022
- **Citation (full):** Sánchez-Piñero et al., 2022. *Evaluation of a simplified methodology to estimate the CWSI in olive orchards.* Agricultural Water Management.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive orchards. Region not reported in source material.
- **Sensor & resolution:** Canopy-temperature / thermal (CWSI). Not further reported in source material.
- **Index/indices studied:** CWSI.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** **CWSI could identify rainfed stress**, while **separating full irrigation from regulated deficit irrigation was more limited**. No numeric CWSI cut-offs are attributed to this study in the source material.
- **Reported uncertainty / caveats:** CWSI requires a **locally and seasonally calibrated non-water-stressed baseline**; olive CWSI baselines change with time of day and season.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q4, Q5. §4 NDMI drought constants (as the thermal-confirmation half of a two-stage rule), §5 seasonal bucketing.
- **Supports / contradicts our current value:** n/a to a specific constant — we compute no CWSI. Relevant as the recommended **confirmation** step our pipeline lacks.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material.

### Source S14 — Gregorio et al., 2017
- **Citation (full):** Gregorio et al., 2017. *Assessing a crop water stress index derived from aerial thermal imaging and infrared thermometry in super-high density olive orchards.* Agricultural Water Management.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** **Super-high-density** olive orchards. Region not reported in source material.
- **Sensor & resolution:** Aerial thermal imaging and infrared thermometry.
- **Index/indices studied:** CWSI.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** **Non-water-stressed baselines were not constant through the season**, although aerial CWSI **remained sensitive to imposed differences in tree water status**. No numeric cut-offs attributed to this study in the source material.
- **Reported uncertainty / caveats:** Directly demonstrates that a fixed seasonal baseline is unsafe even for a thermal index in a *uniform* orchard design.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q4, and by extension §5 (baseline construction).
- **Supports / contradicts our current value:** contradicts the notion of a season-invariant reference; supports orchard- and season-specific baselining.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Super-high-density canopy — the opposite of our sparse-canopy target case; note the contradiction with S8's hedgerow figures rather than averaging them.)

### Source S15 — Abubakar et al., 2023
- **Citation (full):** Abubakar et al., 2023. *Delineation of Orchard, Vineyard, and Olive Trees Based on Phenology Metrics Derived from Time Series of Sentinel-2.* Remote Sensing.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Orchard, vineyard and olive trees; **Southern France** is named in the source material for the green-chlorophyll result.
- **Sensor & resolution:** Sentinel-2 time series.
- **Index/indices studied:** Phenology metrics from Sentinel-2 time series; **temporal green-chlorophyll features**.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Sentinel-2 **time-series phenology metrics can distinguish olive systems**, but should be **calibrated locally when phenology shifts**. In Southern France, **temporal green-chlorophyll features were particularly useful** for identifying olive classes. No numeric thresholds, r² or RMSE reported in source material.
- **Reported uncertainty / caveats:** Local calibration required; olive is evergreen so its seasonal curve is a **modulated plateau**, not a deciduous green-up/senescence curve.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q5, Q7. **§5 seasonal bucketing (meteorological seasons, `MIN_SAMPLES = 3`)**, §5 anomaly rule.
- **Supports / contradicts our current value:** refines — supports *seasonal* treatment in principle, but argues for phenology-aware, locally calibrated windows rather than fixed meteorological month buckets.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material.

### Source S16 — Carrillo et al., 2021
- **Citation (full):** Carrillo et al., 2021. *Satellite imagery and climate variables suggest variations in the phenology of olive groves in Southern Spain.* Remote Sensing.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Olive groves, **Southern Spain**.
- **Sensor & resolution:** Satellite imagery (sensor/resolution not further reported in source material) plus climate variables.
- **Index/indices studied:** NDVI, NDWI, NMDI — as **annual** indicators: minimum, maximum, seasonal range, date of maximum/minimum.
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Used annual NDVI/NDWI/NMDI summary metrics to track olive-grove dynamics and reported that **good and bad production years were reflected in the indices**. No absolute thresholds, r² or RMSE reported in source material.
- **Reported uncertainty / caveats:** The usable signal is the **seasonal trajectory and its timing**, not a single date-specific index value.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q5, Q7. §5 baselines/seasons, §4 fixed-drop alert.
- **Supports / contradicts our current value:** contradicts a single-date absolute rule; supports trajectory-based metrics.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material. (Olive + Mediterranean — high relevance to §5.)

### Source S17 — Rouault et al., 2024
- **Citation (full):** Rouault et al., 2024. *Phenological and Biophysical Mediterranean Orchard Assessment Using Ground-Based Methods and Sentinel 2 Data.* Remote Sensing.
- **Link / DOI:** Not reported in source material.
- **Study crop & region:** Mediterranean orchards (per title). Specific crop and sub-region not reported in source material.
- **Sensor & resolution:** Sentinel-2 plus ground-based methods.
- **Index/indices studied:** Sentinel-2-derived biophysical variables (specific variables not reported in source material).
- **Key quantitative finding (values, ranges, `L`, r²/RMSE, etc.):** Sentinel-2-derived biophysical variables **can support fruit-set detection**, but the **inter-row contribution must be quantified** because orchard pixels mix trees and ground cover. No numeric values, r² or RMSE reported in source material.
- **Reported uncertainty / caveats:** Same mixed-pixel caveat as S6/S7/S10.
- **Applies to which of our params (cite §/row in current-thresholds.md):** Q5. §5 seasonal baselines.
- **Supports / contradicts our current value:** refines — phenological staging is feasible from Sentinel-2, but only with an inter-row correction we do not have.
- **User confidence in applicability (H/M/L) + note:** Not reported in source material.

### Consolidated recommendation table (fill after reading sources)

> **All "current value" entries below are UNVERIFIED in this pass.** They were transcribed from
> planning material, not re-read out of the Python source by whoever filled this table.
> [`current-thresholds.md`](./current-thresholds.md) claims to be code-derived and cites file/line
> for each — **treat that file, and ultimately the code, as the source of truth** and re-verify each
> value before acting on a row. No code was read or changed while filling this section.
>
> The `Q#` column maps each row back to the §A research question, so coverage of all eight is
> checkable. A "Verdict" column was added to the original template columns (see §C note below).

| Q# | Our param (ref current-thresholds.md) | Current value *(unverified)* | Proposed value (literature-supported) | Verdict | Source(s) S# | Confidence | Notes |
|----|---------------------------------------|------------------------------|---------------------------------------|---------|--------------|------------|-------|
| Q3 | NDVI "healthy" band (§2) | 0.5–0.7 | No absolute band. Healthy = within the orchard's own seasonal envelope; watch = persistent negative departure (provisionally lower 20–25th pct of the healthy baseline); severe = lower 5–10th pct, field-confirmed | **Retract** | S8, S10, S11 | Not reported | S8 measured a *hedgerow* (dense) olive orchard at 0.28–0.81 over two years and 0.28–0.41 in summer — i.e. below our "healthy" floor while not unhealthy. Percentiles are calibration starting points, not biological constants |
| Q2 | OSAVI soil factor `L` (§1) | 0.16 | Keep `0.16` as a **benchmark**, but tune empirically: compute SAVI at `L = 0, 0.1, 0.25, 0.5, 0.75, 1.0`, stratify by olive-crown fraction and background class (bare soil / dry grass / green grass), and select on **soil-background stability**, not best in-sample disease correlation | **Unproven — keep, justify, do not retune blind** | S9, S6, S7 | Not reported | `0.16` is the generic OSAVI constant; **no olive-specific justification and no citation for the value itself appears anywhere in the source material**. Do *not* auto-swap to SAVI `L=1.0`; where inter-row grass is substantial the right fix is background masking / fractional-cover modelling, not more `L` tuning |
| Q4 | Drought floor NDMI (§4) | −0.2 | No absolute floor. Two-stage rule: spectral trigger = NDMI below the orchard's seasonal baseline for ≥2 observations (moderate ≈ lower 20–25th pct, severe ≈ lower 5–10th pct), then **thermal confirmation** via CWSI or anomalous canopy temperature | **Retract** | S12, S10, S13, S14 | Not reported | No source supplies any absolute NDMI cut-off for olives. Also fix the index definition: state B8/B8A + B11 (NDWI-Gao) explicitly; B11 is 20 m and must be resampled. McFeeters NDWI is a different, open-water index |
| Q4 | Waterlog ceiling NDMI (§4) | 0.5 | **Not addressed by any source in this research.** No paper surfaced supports or refutes an NDMI waterlogging ceiling for olives | **Unsupported — no evidence either way** | — | Not reported | Genuine gap; see Open question 3 |
| Q7 | NDVI-drop alert (§4) | −0.15 | Replace the fixed absolute drop with a standardized anomaly against a phenology-aware baseline: `Z = (VI − median(VI_healthy,season)) / (1.4826 × MAD)`; watch at `Z ≤ −1.5`, alert at `Z ≤ −2`. Relative alternative: 15–20% decline from the seasonal baseline, stronger alert ≈25–30% | **Retract (form is wrong, not just the number)** | S15, S16, S6, S10, S11 | Not reported | Must add **persistence** (≥2 consecutive valid observations, or 3 within 30 days) and **spatial coherence**; and separate management events (harvest, pruning, mowing, tillage, irrigation) from stress. A single-date drop is commonly cloud, shadow, BRDF or harvest traffic |
| Q7 | Anomaly σ threshold (§5) | 2.0 | Keep `2σ`-equivalent as the **alert** level but add a `1.5σ` "watch" level, and prefer the **MAD-based** robust `Z` over a plain standard deviation | **Refine** | S15, S16, S11 | Not reported | The `Z ≤ −2` alert / `Z ≤ −1.5` watch pair is described in the source material as a **calibration starting point, not a universal biological limit**. MAD is recommended because cloud contamination and management events create outliers |
| Q8 | Health-score weights (§3) | ARVI/OSAVI/NDVI/NDMI = .30/.30/.20/.20 | **No source supports any weighting.** Nothing in this research proposes or validates a composite weighting of these four indices | **Retract the "research-backed" wording** | — | Not reported | §6 flags the phrase "research-backed" as uncited; this research does not rescue it. See Open question 3 |
| Q5 | Baseline min samples / seasons (§5) | 3 / meteorological | Phenology-aware, locally calibrated windows rather than fixed meteorological months; a rolling **21–45-day** baseline window; compare like-with-like (spring vs spring). Olive is evergreen — expect a **modulated plateau**, not a deciduous green-up/senescence curve | **Refine** | S15, S16, S17, S6, S13 | Not reported | **No source states a minimum sample count**, so `MIN_SAMPLES = 3` is neither supported nor refuted (Open question 3). Watch the winter trap: NDVI/OSAVI can rise Nov–Feb because of **inter-row grass after winter rain**, not olive recovery |
| Q1 | Index set for sparse olive canopy (§1) | NDVI + NDMI + ARVI + OSAVI, no canopy-fraction term | **OSAVI + MCARI2/OSAVI + canopy fraction + a soil/grass mask**, with NDVI kept as a reference/cover proxy; add red-edge and thermal where available. Model the mixed pixel: `VI_pixel = f_olive·VI_olive + (1−f_olive)·VI_background` | **Refine — the missing piece is canopy fraction, not the index list** | S6, S7, S8 | Not reported | The gap is not NDVI-vs-OSAVI; it is that we have **no canopy-fraction term and no inter-row mask**, so every index we compute is a mixed-signal measurement. Use surface reflectance, not TOA; keep the band convention fixed (B4/B8; do not mix B8 and B8A without recalibration) |
| Q6 | 10 m pixel as the unit of assessment (§1–§2) | Sentinel-2 10 m pixel treated as a canopy measurement | Use 10 m for **orchard-scale and within-orchard temporal monitoring only**. Minimum defensible disease feature set: OSAVI or NDVI + red-edge + canopy fraction + seasonal anomaly + thermal/moisture, validated against field-labelled trees or plots | **Scope limit — per-tree diagnosis is out of reach** | S6, S7, S8 | Not reported | A 10 m pixel mixes crown, bare soil, shadow, grass and sometimes other crops. Saturation (dense crowns) *and* dilution (sparse crowns) both occur, so a weak index response does **not** imply weak tree stress. Absolute thresholds transfer poorly between orchards |
| Q8 | Uncited ARVI/OSAVI↔disease r² claim (§6) | r² = 0.73–0.76, uncited, asserted for disease incidence **and** severity | Cite as **"r² > 0.7 (Hornero et al. 2020)"** and only for **seasonal change in ARVI/OSAVI, at orchard scale, for Xylella-associated decline, in a pipeline that corrects for canopy structure/season/soil background** | **Correct — do not simply re-cite** | S1, S2, S3, S4, S5 | Not reported | The `0.73–0.76` range is still unconfirmed (full-text results table not extracted). See the second headline callout: our static-threshold, Sentinel-2-only use of this number is a category error. Verticillium attribution must be dropped — see Open question 2 |

### Open questions / unresolved after research

_Unresolved. Each of these feeds a possible follow-up PRD or ground-truth work; none may be treated
as settled by T4._

1. **The exact Hornero 2020 r² is still unverified — but the provenance is now known.**
   *Resolved:* the `r² > 0.7` figure comes from a pipeline combining a Sentinel-2A two-year time
   series, airborne hyperspectral imagery, field observations and **3-D radiative-transfer
   modelling** (which explicitly corrected for seasonal background variation and soil spectra),
   validated on >3,000 trees across 16 orchards in **Apulia**. It describes the **temporal
   variation** of ARVI and OSAVI, not single-date values. **Consequence: a Sentinel-2-only pipeline
   applying raw index thresholds cannot inherit this statistic at all** — see the second headline
   callout.
   *Still open:* the specific **0.73–0.76** range is not confirmed. The accessible abstract reports
   only the combined `r² > 0.7`, with no separate coefficient for ARVI vs OSAVI and none for
   incidence alone. **The reason it is unverified is now "full-text results table not yet
   extracted", not "provenance unknown."** Until someone pulls the results table/figure from the
   full paper, cite it as **"r² > 0.7 (Hornero et al. 2020)"** and quote no per-index value.
   *Also note:* Apulia is a different region from this product's validation grove, so regional
   transferability is a separate unresolved question.

2. **Verticillium attribution — narrow the product's disease scope.**
   ARVI and OSAVI are **not validated as Verticillium-specific predictors**. Navrozidis et al. 2019
   (S11) *did* map Verticillium-associated stress from Sentinel-2, so there is a detectable stress
   signal. But the evidence that actually **discriminates** the pathogen — Calderón et al. 2015
   (S3), Poblete et al. 2021 (S5) — rests on **airborne hyperspectral and thermal data this pipeline
   does not have**. Xylella and Verticillium both disrupt xylem function and produce similar
   water-stress-like symptoms.
   **The defensible position is that Sentinel-2 can flag stress but CANNOT attribute it to
   Verticillium specifically.** That is deliberately weaker than "no detectable signal" — the
   stronger claim is *not* supported by this research and must not be written into product copy.
   **Recording the consequence:** the product's disease scope is being narrowed to
   **Xylella-associated decline** on this basis. *(Any corresponding change to code or product copy
   is out of scope for this document and is being handled separately.)*

3. **Questions the eight research comments did not actually answer.** Genuine gaps, distinct from
   "the literature says no":
   - **NDMI waterlogging ceiling (`0.5`, §4).** Q4 asked whether `0.5` is a defensible waterlogging
     ceiling. The findings cover **drought** thoroughly and say **nothing about waterlogging** in
     olives, in either direction. Unaddressed, not refuted.
   - **Health-score composite weights (`.30/.30/.20/.20`, §3).** No question was aimed squarely at
     the weighting, and no source proposes any composite weighting of these four indices. The
     "research-backed" label in the code remains wholly unsupported.
   - **`MIN_SAMPLES = 3` (§5).** Q5 asked about seasonal bucketing and got a rich answer; the
     **minimum sample count** was never addressed by any source.
   - **`years_back = 3` baseline lookback (§5).** Never addressed. The sources call for
     "healthy years" / multi-year baselines without specifying how many.
   - **`HEALTH_SCORE_CRITICAL = 40` / `HEALTH_SCORE_WARNING = 60` (§4)** and the piecewise NDMI
     sub-score curve (§3). Entirely unaddressed by this research.
   - **ARVI's own interpretation bands (§2).** ARVI appears only in the Xylella discussion; nothing
     supports its standalone `0.2–0.4 / 0.4–0.6 / >0.6` bands.
   - **Baselines exist for NDVI/NDMI only, while ARVI/OSAVI feed the health score (§7).** The
     research strongly implies ARVI/OSAVI need baselines too (they are the Xylella-relevant pair,
     and only as *temporal variation*), but no source addresses this asymmetry directly.

4. **Is OSAVI1510 computable from Sentinel-2 at all?** Hornero et al. 2018 (S2) found OSAVI1510
   better than OSAVI for **severity change**. The source material calls it only "a different
   narrow-band index" and **does not state which wavelength/band it requires, nor whether Sentinel-2
   provides it**. Do not assume either way. Verify against the paper before proposing it as an
   index; if Sentinel-2 cannot supply the band, that is a hard ceiling on satellite-only **severity**
   estimation and belongs in the dossier's limitations section.

## C. Recording rules

- **One source, one block.** Do not merge multiple papers into one citation.
- **No numbers without a source.** Blank > guessed.
- **Prefer olive-specific + Mediterranean + Sentinel-2/10 m** studies; mark generic-crop sources as
  lower confidence.
- **Flag contradictions** explicitly rather than averaging them away.
- When the template is filled, hand back to the runner/agent for **T4** (assemble
  `olive-index-dossier.md` and propose recalibrated thresholds strictly from these cited values).

### Transcription notes (2026-08-03) — deviations from the template, for review

§B was filled by transcribing the user's research from Linear DAN-16. Four formatting judgement
calls were made; flagging them so they can be overruled:

1. **`"Not reported in source material."` instead of blank.** §C says "Blank > guessed". An explicit
   phrase was used instead of an empty field so a reader can tell "the research did not record this"
   apart from "nobody filled this in yet". No field was completed from model knowledge.
2. **Source headings carry the short citation** (`### Source S1 — Hornero et al., 2020`) rather than
   the bare `### Source S<n>` of the exemplar. Navigation only; heading level is unchanged.
3. **A `Q#` and a `Verdict` column were added** to the consolidated table, and `Proposed value` was
   relabelled `Proposed value (literature-supported)`. The original eight rows are **unchanged and
   in their original order**; three rows (Q1, Q6, Q8-r²) were appended so all eight §A questions are
   covered. `Confidence` was kept even though the research recorded no confidence ratings.
4. **Papers cited under several questions get one block**, per the §C "one source, one block" rule,
   with the questions listed in `Applies to which of our params`. Contradictions between papers
   (e.g. S8's hedgerow NDVI figures vs S14's super-high-density orchard) are left standing in their
   own blocks rather than reconciled.

Source-material items that could **not** be transcribed:
- The markdown file attached as a threaded reply to the Q2 comment could not be retrieved — its
  Linear signed URL had expired (HTTP 401). Per the reply's own text it is a re-formatted copy of
  the Q2 comment body (the LaTeX did not render in Linear), so no unique content is believed lost.
  If it does contain anything extra, this file does not have it.
- No DOI, link, or confidence rating was recorded for any of the 17 papers. None was reconstructed.
- One paper's author string is recorded in the source as "Zarco-Tejadaa" (S7); assumed a typo for
  Zarco-Tejada and noted in the block rather than silently corrected. S7's venue is not recorded.
