import pytest

from viscollapse.download import build_cache_path, cache_filename_from_url, download_file
from viscollapse.manifests import ChecksumMismatchError, sha256_file, verify_sha256


def test_build_cache_path_uses_url_filename(tmp_path):
    url = "https://example.org/public/path/example_product.fits.gz"

    assert cache_filename_from_url(url) == "example_product.fits.gz"
    assert build_cache_path(url, cache_dir=tmp_path) == tmp_path / "example_product.fits.gz"


def test_download_file_requires_url(tmp_path):
    with pytest.raises(ValueError, match="url is required"):
        download_file("", dest=tmp_path / "unused.dat")


def test_sha256_verification_on_small_local_file(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("synthetic readiness test data\n", encoding="utf-8")
    expected = sha256_file(source)

    assert verify_sha256(source, expected) == expected

    with pytest.raises(ChecksumMismatchError, match="SHA-256 mismatch"):
        verify_sha256(source, "0" * 64)


def test_download_file_supports_local_file_url_and_checksum(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("local public-data scaffold test\n", encoding="utf-8")
    expected = sha256_file(source)

    destination = tmp_path / "cache" / "copied.txt"
    result = download_file(source.as_uri(), dest=destination, expected_sha256=expected)

    assert result == destination
    assert destination.read_text(encoding="utf-8") == "local public-data scaffold test\n"


def test_download_file_reports_checksum_mismatch(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("checksum mismatch test\n", encoding="utf-8")

    with pytest.raises(ChecksumMismatchError, match="SHA-256 mismatch"):
        download_file(source.as_uri(), dest=tmp_path / "copied.txt", expected_sha256="0" * 64)
