"""Radiometric scaling for Sentinel-2 L2A products.

L2A products store surface reflectance as integer digital numbers (DN), not as
physical reflectance. Converting requires the product's own quantification
value and, from processing baseline 04.00 (January 2022) onwards, a per-band
additive offset:

    reflectance = (DN + BOA_ADD_OFFSET) / BOA_QUANTIFICATION_VALUE

Both terms matter, for different reasons:

* The **quantification value** (~10000) is a scale factor. Ratio indices such
  as NDVI, NDMI and ARVI are invariant to it, but OSAVI is not — its soil
  adjustment term L=0.16 is defined for reflectance in [0, 1] and is inert
  against a denominator of several thousand, which silently collapses OSAVI
  onto NDVI.
* The **additive offset** (−1000 on baseline 04.00+) does *not* cancel in a
  ratio. Ignoring it biases every index for post-January-2022 scenes only,
  putting an artefact step into any multi-year series that straddles it.

Both values are read from the product metadata rather than hard-coded, since
they are baseline-dependent and pre-04.00 products carry no offset at all.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np

logger = logging.getLogger(__name__)

# Product metadata filenames, most specific first.
METADATA_FILENAMES = ("MTD_MSIL2A.xml", "MTD_MSIL1C.xml")


def _local_name(tag: str) -> str:
    """Strip any XML namespace from a tag name."""
    return tag.rsplit("}", 1)[-1]


def _normalise_band(name: str) -> str:
    """Normalise a physical band name to the B01..B12 / B8A convention.

    Sentinel-2 metadata writes the red band as ``B4`` while the JP2 filenames
    and this codebase use ``B04``. Both must resolve to the same key.
    """
    candidate = name.strip().upper()
    if not candidate.startswith("B"):
        raise ValueError(f"Not a Sentinel-2 band name: {name!r}")

    suffix = candidate[1:]
    if suffix.isdigit():
        return f"B{int(suffix):02d}"
    return candidate  # e.g. B8A


@dataclass(frozen=True)
class ScalingMetadata:
    """Radiometric scaling parameters read from a product's metadata."""

    quantification_value: float
    offsets: Dict[str, float]

    def offset_for(self, band: str) -> float:
        """Return the additive offset for a physical band name (e.g. ``B04``).

        Products predating processing baseline 04.00 carry no offsets at all,
        in which case zero is the correct answer for every band. But once a
        product *does* declare offsets, a band missing from that list is a
        genuine mismatch and raises rather than defaulting to zero — a silent
        zero here is the same class of bug this module exists to fix.
        """
        key = _normalise_band(band)

        if not self.offsets:
            return 0.0

        if key not in self.offsets:
            raise KeyError(
                f"Band {key} has no BOA_ADD_OFFSET in product metadata "
                f"(known bands: {sorted(self.offsets)})"
            )
        return self.offsets[key]


def parse_scaling_metadata(xml_text: str) -> ScalingMetadata:
    """Parse quantification value and per-band offsets from product metadata XML.

    Args:
        xml_text: Contents of MTD_MSIL2A.xml

    Returns:
        ScalingMetadata with offsets keyed by normalised physical band name.
    """
    root = ET.fromstring(xml_text)

    quantification_value = None
    band_ids_to_name: Dict[str, str] = {}
    raw_offsets: Dict[str, float] = {}

    for element in root.iter():
        tag = _local_name(element.tag)

        if tag == "BOA_QUANTIFICATION_VALUE" and element.text:
            quantification_value = float(element.text.strip())

        elif tag == "Spectral_Information":
            band_id = element.attrib.get("bandId")
            physical_band = element.attrib.get("physicalBand")
            if band_id is not None and physical_band is not None:
                band_ids_to_name[band_id] = _normalise_band(physical_band)

        elif tag == "BOA_ADD_OFFSET" and element.text:
            band_id = element.attrib.get("band_id")
            if band_id is None:
                raise ValueError("BOA_ADD_OFFSET element without a band_id attribute")
            raw_offsets[band_id] = float(element.text.strip())

    if quantification_value is None:
        raise ValueError("No BOA_QUANTIFICATION_VALUE found in product metadata")

    offsets: Dict[str, float] = {}
    for band_id, offset in raw_offsets.items():
        if band_id not in band_ids_to_name:
            raise ValueError(
                f"BOA_ADD_OFFSET declares band_id {band_id} with no matching "
                "Spectral_Information entry — cannot resolve it to a band"
            )
        offsets[band_ids_to_name[band_id]] = offset

    return ScalingMetadata(quantification_value=quantification_value, offsets=offsets)


def load_scaling_metadata(product_path: Path) -> ScalingMetadata:
    """Locate and parse the metadata file inside an unpacked Sentinel-2 product.

    Raises:
        FileNotFoundError: if no product metadata is present. Guessing default
            scaling would reintroduce exactly the defect this module fixes.
    """
    product_path = Path(product_path)

    for filename in METADATA_FILENAMES:
        candidate = product_path / filename
        if candidate.is_file():
            return parse_scaling_metadata(candidate.read_text())

    # Some products nest one directory deeper once unzipped.
    for filename in METADATA_FILENAMES:
        matches = sorted(product_path.glob(f"*/{filename}"))
        if matches:
            return parse_scaling_metadata(matches[0].read_text())

    raise FileNotFoundError(
        f"No product metadata ({' or '.join(METADATA_FILENAMES)}) under {product_path}"
    )


def dn_to_reflectance(
    dn: np.ndarray,
    quantification_value: float,
    add_offset: float = 0.0,
) -> np.ndarray:
    """Convert Sentinel-2 digital numbers to surface reflectance.

    NaN pixels (nodata, cloud-masked) pass through untouched, so this must be
    applied *after* nodata masking — a DN of 0 means "no data", whereas a
    reflectance of 0.0 is a legitimate measurement.

    Args:
        dn: Digital number array, already float and already nodata-masked
        quantification_value: BOA_QUANTIFICATION_VALUE from product metadata
        add_offset: BOA_ADD_OFFSET for this band (0.0 before baseline 04.00)

    Returns:
        Reflectance array of the same shape, nominally in [0, 1]
    """
    if quantification_value == 0:
        raise ValueError("quantification_value must be non-zero")

    return (dn.astype(np.float32) + np.float32(add_offset)) / np.float32(
        quantification_value
    )
