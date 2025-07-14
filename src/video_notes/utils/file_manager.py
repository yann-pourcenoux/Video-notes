"""File management utilities for video notes processing."""

import re
from pathlib import Path

import click


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Sanitize filename by removing invalid characters and limiting length.

    Args:
        filename: Original filename to sanitize.
        max_length: Maximum allowed filename length.

    Returns:
        Sanitized filename safe for filesystem use.
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Replace multiple spaces with single space
    sanitized = re.sub(r"\s+", " ", sanitized)

    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()

    # Limit length
    if len(sanitized) > max_length:
        # Try to truncate at word boundary
        truncated = sanitized[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.8:  # If we can keep most of it
            sanitized = truncated[:last_space]
        else:
            sanitized = truncated

    # Ensure we have a valid filename
    if not sanitized:
        sanitized = "untitled"

    return sanitized


def write_text_file(file_path: str, content: str) -> bool:
    """Write text content to file.

    Args:
        file_path: Path where to write the file.
        content: Text content to write.

    Returns:
        True if writing was successful.
    """
    try:
        # Ensure parent directory exists
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return True
    except Exception as e:
        click.echo(f"❌ Error writing file {file_path}: {e}", err=True)
        return False


def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory.

    Returns:
        True if directory exists or was created successfully.
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        click.echo(f"❌ Error creating directory {directory_path}: {e}", err=True)
        return False


def get_safe_filename(filename: str, extension: str = "", max_length: int = 100) -> str:
    """Get a safe filename with optional extension.

    Args:
        filename: Base filename to sanitize.
        extension: File extension to add (with or without dot).
        max_length: Maximum total filename length including extension.

    Returns:
        Safe filename with extension.
    """
    # Normalize extension
    if extension and not extension.startswith("."):
        extension = f".{extension}"

    # Reserve space for extension
    available_length = max_length - len(extension) if extension else max_length

    # Sanitize the base filename
    safe_base = sanitize_filename(filename, available_length)

    return f"{safe_base}{extension}" if extension else safe_base
