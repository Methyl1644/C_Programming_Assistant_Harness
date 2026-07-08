"""Smoke test: verify cpa_harness package can be imported and version is correct."""


def test_import_cpa_harness():
    import cpa_harness
    assert cpa_harness.__version__ == "0.1.0"
