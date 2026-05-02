"""File I/O utilities."""

from pathlib import Path

from pydantic import BaseModel


def read_text_file(path: Path) -> str:
    """Read a text file and return its contents.

    Args:
        path: Path to the text file.

    Returns:
        File contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return path.read_text(encoding="utf-8")


def write_json(
    data: BaseModel,
    path: Path,
    overwrite: bool = False,
) -> None:
    """Write a Pydantic model to a JSON file.

    Args:
        data: Pydantic model instance to serialize.
        path: Path where to write the JSON file.
        overwrite: If False, raises FileExistsError if file already exists.
                   If True, overwrites any existing file.

    Raises:
        FileExistsError: If file exists and overwrite=False.
    """
    if path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {path}")

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with mode='json' for proper type handling
    json_str = data.model_dump_json(indent=2)
    path.write_text(json_str, encoding="utf-8")
