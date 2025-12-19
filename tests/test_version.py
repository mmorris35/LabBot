"""Test package version."""

from labbot import __version__


def test_version_exists() -> None:
    """Verify version string is set."""
    assert __version__ == "0.1.0"
