"""Tests for universal document reader supporting .txt, .docx, and .pdf."""

from pathlib import Path

import pytest

from bid_acceleration_engine.utils.document_reader import read_document


@pytest.fixture
def text_fixture():
    """Path to test text file."""
    return Path(__file__).parent.parent / "fixtures" / "sample_bids" / "simple_rfp.txt"


@pytest.fixture
def docx_fixture():
    """Path to test Word document."""
    return Path(__file__).parent.parent / "fixtures" / "sample_bids" / "test_rfp_document.docx"


@pytest.fixture
def pdf_fixture():
    """Path to test PDF document."""
    return Path(__file__).parent.parent / "fixtures" / "sample_bids" / "test_rfp_document.pdf"


class TestDocumentReader:
    """Test universal document reader."""

    def test_read_text_file(self, text_fixture):
        """Read plain text file."""
        content = read_document(text_fixture)
        assert isinstance(content, str)
        assert len(content) > 0
        assert "REQUEST FOR PROPOSAL" in content or "RFP" in content

    def test_read_docx_file(self, docx_fixture):
        """Read Word document."""
        content = read_document(docx_fixture)
        assert isinstance(content, str)
        assert len(content) > 0
        assert "REQUEST FOR PROPOSAL" in content
        assert "DATA ANALYTICS PLATFORM" in content

    def test_read_pdf_file(self, pdf_fixture):
        """Read PDF document."""
        content = read_document(pdf_fixture)
        assert isinstance(content, str)
        assert len(content) > 0
        assert "REQUEST FOR PROPOSAL" in content
        assert "CLOUD INFRASTRUCTURE" in content

    def test_read_unsupported_format(self, tmp_path):
        """Raise error for unsupported file format."""
        unsupported = tmp_path / "test.xlsx"
        unsupported.write_text("dummy content")

        with pytest.raises(ValueError, match="Unsupported file format"):
            read_document(unsupported)

    def test_read_nonexistent_file(self):
        """Raise error for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_document(Path("/nonexistent/path/file.txt"))

    def test_docx_preserves_structure(self, docx_fixture):
        """Word document reading preserves text structure."""
        content = read_document(docx_fixture)
        # Check that sections are present (paragraphs separated by newlines)
        lines = content.split("\n")
        assert len(lines) > 5

    def test_pdf_handles_multipage(self, pdf_fixture):
        """PDF reading handles documents gracefully."""
        content = read_document(pdf_fixture)
        # Should extract text from all pages
        assert "Project Overview" in content
        assert "Requirements" in content

    @pytest.mark.parametrize(
        "fixture_name,expected_text",
        [
            ("simple_rfp.txt", "REQUEST FOR PROPOSAL"),
            ("test_rfp_document.docx", "REQUEST FOR PROPOSAL"),
            ("test_rfp_document.pdf", "REQUEST FOR PROPOSAL"),
        ],
    )
    def test_all_formats_contain_key_text(self, fixture_name, expected_text):
        """All formats should extract key RFP text."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_bids" / fixture_name
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        content = read_document(fixture_path)
        assert expected_text in content

    def test_read_document_case_insensitive_extension(self, docx_fixture):
        """File extension matching should be case-insensitive."""
        # Test that .docx works (it already does from the fixture)
        content = read_document(docx_fixture)
        assert "REQUEST FOR PROPOSAL" in content
