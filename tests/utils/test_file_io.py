"""Tests for file_io utility."""

from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import BaseModel

from bid_acceleration_engine.utils.file_io import read_text_file, write_json


class SampleModel(BaseModel):
    """Simple test model."""

    id: str
    name: str
    value: int


def test_read_text_file(tmp_path):
    """Test reading a text file."""
    test_file = tmp_path / "test.txt"
    test_content = "Hello, World!\nLine 2"
    test_file.write_text(test_content)

    result = read_text_file(test_file)
    assert result == test_content


def test_read_text_file_not_found():
    """Test that reading a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_text_file(Path("/nonexistent/path/file.txt"))


def test_write_json_creates_file(tmp_path):
    """Test writing a Pydantic model to JSON."""
    output_path = tmp_path / "output.json"
    model = SampleModel(id=str(uuid4()), name="Test", value=42)

    write_json(model, output_path)

    assert output_path.exists()
    content = output_path.read_text()
    assert "Test" in content
    assert "42" in content


def test_write_json_creates_parent_directories(tmp_path):
    """Test that write_json creates parent directories if they don't exist."""
    output_path = tmp_path / "subdir" / "nested" / "output.json"
    model = SampleModel(id=str(uuid4()), name="Test", value=42)

    write_json(model, output_path)

    assert output_path.exists()
    assert output_path.parent.exists()


def test_write_json_raises_on_existing_file(tmp_path):
    """Test that write_json raises FileExistsError if file exists and overwrite=False."""
    output_path = tmp_path / "output.json"
    model = SampleModel(id=str(uuid4()), name="Test", value=42)

    # Write once
    write_json(model, output_path)
    assert output_path.exists()

    # Try to write again without overwrite
    with pytest.raises(FileExistsError):
        write_json(model, output_path, overwrite=False)


def test_write_json_overwrites_with_flag(tmp_path):
    """Test that write_json overwrites when overwrite=True."""
    output_path = tmp_path / "output.json"
    model1 = SampleModel(id=str(uuid4()), name="First", value=1)
    model2 = SampleModel(id=str(uuid4()), name="Second", value=2)

    # Write first model
    write_json(model1, output_path)
    content1 = output_path.read_text()
    assert "First" in content1

    # Overwrite with second model
    write_json(model2, output_path, overwrite=True)
    content2 = output_path.read_text()
    assert "Second" in content2
    assert "First" not in content2


def test_write_json_format_is_valid_json(tmp_path):
    """Test that written JSON is valid and deserializable."""
    output_path = tmp_path / "output.json"
    model = SampleModel(id=str(uuid4()), name="Test", value=42)

    write_json(model, output_path)

    # Read back and deserialize
    content = output_path.read_text()
    recovered = SampleModel.model_validate_json(content)
    assert recovered.name == "Test"
    assert recovered.value == 42


def test_write_json_indented(tmp_path):
    """Test that written JSON is nicely indented."""
    output_path = tmp_path / "output.json"
    model = SampleModel(id=str(uuid4()), name="Test", value=42)

    write_json(model, output_path)

    content = output_path.read_text()
    # Check for indentation (should have newlines and spaces)
    assert "\n" in content
    assert "  " in content


def test_write_json_round_trip(tmp_path):
    """Test that a model can be written and read back without data loss."""
    output_path = tmp_path / "output.json"
    original = SampleModel(id=str(uuid4()), name="RoundTrip", value=999)

    write_json(original, output_path)
    recovered = SampleModel.model_validate_json(output_path.read_text())

    assert recovered.id == original.id
    assert recovered.name == original.name
    assert recovered.value == original.value
