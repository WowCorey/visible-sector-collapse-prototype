from pathlib import Path

from viscollapse.data_sources import REQUIRED_SOURCE_FIELDS, load_public_sources


def test_public_source_manifest_loads_and_has_required_fields():
    manifest = load_public_sources()
    sources = manifest["sources"]
    names = {source["name"] for source in sources}

    assert "Planck Legacy Archive" in names
    assert "NASA LAMBDA Planck Products" in names
    assert "CLASS" in names
    assert "CAMB" in names

    for source in sources:
        assert set(REQUIRED_SOURCE_FIELDS).issubset(source)
        assert "verify" in source["status"].lower() or "citation required" in source["status"].lower()


def test_gitignore_protects_large_public_data_artifacts():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    required_patterns = [
        "data/raw/",
        "data/cache/",
        "data/external/",
        "*.fits",
        "*.fits.gz",
        "*.hdf5",
        "*.h5",
        "*.npy",
        "*.npz",
    ]
    for pattern in required_patterns:
        assert pattern in gitignore
