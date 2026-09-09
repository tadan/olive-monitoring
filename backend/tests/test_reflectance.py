"""Tests for Sentinel-2 L2A radiometric scaling."""
import numpy as np
import pytest

from app.reflectance import (
    ScalingMetadata,
    dn_to_reflectance,
    load_scaling_metadata,
    parse_scaling_metadata,
)

# Trimmed MTD_MSIL2A.xml, processing baseline 04.00 (offsets present).
MTD_WITH_OFFSETS = """<?xml version="1.0" encoding="UTF-8"?>
<n1:Level-2A_User_Product xmlns:n1="https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd">
  <n1:General_Info>
    <Product_Image_Characteristics>
      <QUANTIFICATION_VALUES_LIST>
        <BOA_QUANTIFICATION_VALUE unit="none">10000</BOA_QUANTIFICATION_VALUE>
        <AOT_QUANTIFICATION_VALUE unit="none">1000.0</AOT_QUANTIFICATION_VALUE>
      </QUANTIFICATION_VALUES_LIST>
      <BOA_ADD_OFFSET_VALUES_LIST>
        <BOA_ADD_OFFSET band_id="0">-1000</BOA_ADD_OFFSET>
        <BOA_ADD_OFFSET band_id="1">-1000</BOA_ADD_OFFSET>
        <BOA_ADD_OFFSET band_id="3">-1000</BOA_ADD_OFFSET>
        <BOA_ADD_OFFSET band_id="7">-1000</BOA_ADD_OFFSET>
        <BOA_ADD_OFFSET band_id="10">-1000</BOA_ADD_OFFSET>
      </BOA_ADD_OFFSET_VALUES_LIST>
      <Spectral_Information_List>
        <Spectral_Information bandId="0" physicalBand="B1"/>
        <Spectral_Information bandId="1" physicalBand="B2"/>
        <Spectral_Information bandId="3" physicalBand="B4"/>
        <Spectral_Information bandId="7" physicalBand="B8"/>
        <Spectral_Information bandId="10" physicalBand="B11"/>
      </Spectral_Information_List>
    </Product_Image_Characteristics>
  </n1:General_Info>
</n1:Level-2A_User_Product>
"""

# Pre-04.00 product: quantification value only, no offset list.
MTD_WITHOUT_OFFSETS = """<?xml version="1.0" encoding="UTF-8"?>
<n1:Level-2A_User_Product xmlns:n1="https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd">
  <n1:General_Info>
    <Product_Image_Characteristics>
      <QUANTIFICATION_VALUES_LIST>
        <BOA_QUANTIFICATION_VALUE unit="none">10000</BOA_QUANTIFICATION_VALUE>
      </QUANTIFICATION_VALUES_LIST>
      <Spectral_Information_List>
        <Spectral_Information bandId="3" physicalBand="B4"/>
      </Spectral_Information_List>
    </Product_Image_Characteristics>
  </n1:General_Info>
</n1:Level-2A_User_Product>
"""


def test_dn_to_reflectance_divides_by_quantification_value():
    """A DN of 2000 with no offset is reflectance 0.2."""
    dn = np.array([[2000.0, 900.0]], dtype=np.float32)

    reflectance = dn_to_reflectance(dn, quantification_value=10000.0)

    assert pytest.approx(reflectance[0, 0], abs=1e-6) == 0.2
    assert pytest.approx(reflectance[0, 1], abs=1e-6) == 0.09


def test_dn_to_reflectance_applies_additive_offset_before_dividing():
    """Baseline 04.00+ needs (DN + offset) / quantification, not DN / quantification."""
    dn = np.array([[2000.0]], dtype=np.float32)

    reflectance = dn_to_reflectance(dn, quantification_value=10000.0, add_offset=-1000.0)

    # (2000 - 1000) / 10000 = 0.1, NOT 0.2
    assert pytest.approx(reflectance[0, 0], abs=1e-6) == 0.1


def test_dn_to_reflectance_preserves_nan_nodata():
    """Pixels already masked as NaN stay NaN rather than becoming a real value."""
    dn = np.array([[np.nan, 2000.0]], dtype=np.float32)

    reflectance = dn_to_reflectance(dn, quantification_value=10000.0, add_offset=-1000.0)

    assert np.isnan(reflectance[0, 0])
    assert pytest.approx(reflectance[0, 1], abs=1e-6) == 0.1


def test_parse_scaling_metadata_reads_quantification_value():
    metadata = parse_scaling_metadata(MTD_WITH_OFFSETS)

    assert isinstance(metadata, ScalingMetadata)
    assert metadata.quantification_value == 10000.0


def test_parse_scaling_metadata_maps_offsets_to_physical_band_names():
    """band_id is an index into the product's own band list, not a band number."""
    metadata = parse_scaling_metadata(MTD_WITH_OFFSETS)

    # band_id 1 -> B2 (blue), 3 -> B4 (red), 7 -> B8 (nir), 10 -> B11 (swir)
    assert metadata.offset_for("B02") == -1000.0
    assert metadata.offset_for("B04") == -1000.0
    assert metadata.offset_for("B08") == -1000.0
    assert metadata.offset_for("B11") == -1000.0


def test_parse_scaling_metadata_without_offset_list_yields_zero_offsets():
    """Products before processing baseline 04.00 carry no offset; zero is correct."""
    metadata = parse_scaling_metadata(MTD_WITHOUT_OFFSETS)

    assert metadata.quantification_value == 10000.0
    assert metadata.offset_for("B04") == 0.0


def test_parse_scaling_metadata_rejects_unknown_band():
    """An unmapped band must fail loudly rather than silently scale without its offset."""
    metadata = parse_scaling_metadata(MTD_WITH_OFFSETS)

    with pytest.raises(KeyError):
        metadata.offset_for("B12")


def test_load_scaling_metadata_reads_product_metadata_file(tmp_path):
    product = tmp_path / "S2A_MSIL2A_20260101T100031.SAFE"
    product.mkdir()
    (product / "MTD_MSIL2A.xml").write_text(MTD_WITH_OFFSETS)

    metadata = load_scaling_metadata(product)

    assert metadata.quantification_value == 10000.0
    assert metadata.offset_for("B04") == -1000.0


def test_load_scaling_metadata_raises_when_metadata_missing(tmp_path):
    """No metadata means no defensible scaling — refuse rather than assume."""
    product = tmp_path / "empty.SAFE"
    product.mkdir()

    with pytest.raises(FileNotFoundError):
        load_scaling_metadata(product)
