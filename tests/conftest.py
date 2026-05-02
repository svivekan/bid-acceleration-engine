"""Shared pytest fixtures for bid-acceleration-engine tests."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_bid_path() -> Path:
    """Path to the simple RFP sample bid document."""
    path = Path(__file__).parent / "fixtures" / "sample_bids" / "simple_rfp.txt"
    return path


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Temporary output directory for test artifacts."""
    return tmp_path
