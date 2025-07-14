"""Filename generator agent for creating appropriate output filenames.

This agent generates clean, descriptive filenames based on video metadata
and content analysis for both summary and transcript files.
"""

import re
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from video_notes.models.video import VideoInfo


class FilenameInput(BaseModel):
    """Input model for filename generation."""

    video_title: str | None = Field(None, description="Video title from metadata")
    video_id: str | None = Field(None, description="YouTube video ID")
    primary_theme: str | None = Field(None, description="Primary detected theme")
    custom_prefix: str | None = Field(None, description="Custom prefix for filename")
    max_length: int = Field(100, description="Maximum filename length", gt=0, le=255)
    include_date: bool = Field(False, description="Whether to include current date in filename")


class FilenameResult(BaseModel):
    """Output model for generated filenames."""

    summary_filename: str = Field(..., description="Generated filename for summary file")
    transcript_filename: str = Field(..., description="Generated filename for transcript file")
    base_name: str = Field(..., description="Base name used for both files")
    sanitized_title: str | None = Field(None, description="Sanitized version of the video title")


def generate_filename(
    video_title: str | None = None,
    video_id: str | None = None,
    primary_theme: str | None = None,
    custom_prefix: str | None = None,
    max_length: int = 100,
    include_date: bool = False,
) -> FilenameResult:
    """Generate appropriate filenames for video summary and transcript.

    This agent creates clean, descriptive filenames based on available
    metadata and content analysis. It ensures filenames are filesystem-safe
    and within specified length limits.

    Args:
        video_title: Video title from metadata
        video_id: YouTube video ID
        primary_theme: Primary detected theme
        custom_prefix: Custom prefix for filename
        max_length: Maximum filename length
        include_date: Whether to include current date in filename

    Returns:
        FilenameResult with generated filenames and metadata
    """
    # Build base name components
    name_parts = []

    # Add custom prefix if provided
    if custom_prefix:
        sanitized_prefix = _sanitize_filename_part(custom_prefix)
        if sanitized_prefix:
            name_parts.append(sanitized_prefix)

    # Add sanitized title as primary component
    sanitized_title = None
    if video_title:
        sanitized_title = _sanitize_title_for_filename(video_title)
        if sanitized_title:
            name_parts.append(sanitized_title)

    # If no title available, use theme or fallback
    if not name_parts:
        if primary_theme and primary_theme != "general":
            theme_name = primary_theme.replace("_", "-")
            name_parts.append(f"{theme_name}-content")
        elif video_id:
            name_parts.append(f"video-{video_id}")
        else:
            name_parts.append("video-summary")

    # Add date if requested
    if include_date:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")
        name_parts.append(date_str)

    # Join parts and ensure length limit
    base_name = "-".join(name_parts)
    base_name = _truncate_filename(base_name, max_length - 20)  # Reserve space for extensions

    # Ensure we have a valid base name
    if not base_name or base_name in [".", ".."]:
        base_name = "video-summary"

    # Generate final filenames
    summary_filename = f"{base_name}.md"
    transcript_filename = f"{base_name}-transcript.txt"

    return FilenameResult(
        summary_filename=summary_filename,
        transcript_filename=transcript_filename,
        base_name=base_name,
        sanitized_title=sanitized_title,
    )


def generate_filename_from_video_info(
    video_info: "VideoInfo",
    primary_theme: str | None = None,
    custom_prefix: str | None = None,
    max_length: int = 100,
    include_date: bool = False,
) -> FilenameResult:
    """Generate filenames from VideoInfo object.

    Convenience function that extracts relevant information from VideoInfo
    and generates appropriate filenames.

    Args:
        video_info: VideoInfo object with metadata
        primary_theme: Primary detected theme
        custom_prefix: Custom prefix for filename
        max_length: Maximum filename length
        include_date: Whether to include current date in filename

    Returns:
        FilenameResult with generated filenames and metadata
    """
    return generate_filename(
        video_title=video_info.title,
        video_id=video_info.video_id,
        primary_theme=primary_theme,
        custom_prefix=custom_prefix,
        max_length=max_length,
        include_date=include_date,
    )


def _sanitize_title_for_filename(title: str) -> str:
    """Sanitize video title for use in filename.

    Args:
        title: Raw video title

    Returns:
        Sanitized title suitable for filename
    """
    if not title:
        return ""

    # Convert to lowercase for consistency
    clean_title = title.lower()

    # Remove or replace common problematic patterns
    # Remove content in parentheses/brackets (often metadata)
    clean_title = re.sub(r"[(\[].+?[)\]]", "", clean_title)

    # Remove URLs
    clean_title = re.sub(r"http[s]?://\S+", "", clean_title)

    # Replace common separators with spaces
    clean_title = re.sub(r"[|_\-:;]+", " ", clean_title)

    # Remove special characters but keep alphanumeric, spaces, and hyphens
    clean_title = re.sub(r"[^\w\s\-]", "", clean_title)

    # Replace multiple whitespaces with single space
    clean_title = re.sub(r"\s+", " ", clean_title)

    # Strip whitespace
    clean_title = clean_title.strip()

    # Replace spaces with hyphens
    clean_title = clean_title.replace(" ", "-")

    # Remove multiple consecutive hyphens
    clean_title = re.sub(r"-+", "-", clean_title)

    # Remove leading/trailing hyphens
    clean_title = clean_title.strip("-")

    return clean_title


def _sanitize_filename_part(part: str) -> str:
    """Sanitize a filename part (prefix, etc.).

    Args:
        part: Raw filename part

    Returns:
        Sanitized filename part
    """
    if not part:
        return ""

    # Remove special characters but keep alphanumeric, hyphens, and underscores
    clean_part = re.sub(r"[^\w\-_]", "", part)

    # Convert to lowercase
    clean_part = clean_part.lower()

    # Remove multiple consecutive separators
    clean_part = re.sub(r"[-_]+", "-", clean_part)

    # Remove leading/trailing separators
    clean_part = clean_part.strip("-_")

    return clean_part


def _truncate_filename(filename: str, max_length: int) -> str:
    """Truncate filename to specified length while preserving readability.

    Args:
        filename: Filename to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated filename
    """
    if not filename or max_length <= 0:
        return ""

    if len(filename) <= max_length:
        return filename

    # Try to truncate at word boundaries (hyphens)
    if "-" in filename:
        parts = filename.split("-")
        result = parts[0]

        for part in parts[1:]:
            if len(result + "-" + part) <= max_length:
                result += "-" + part
            else:
                break

        if len(result) >= 10:  # Ensure we have a reasonable length
            return result

    # If word boundary truncation doesn't work, just truncate at max length
    return filename[:max_length].rstrip("-_")


def validate_filename(filename: str) -> bool:
    """Validate that a filename is safe for filesystem use.

    Args:
        filename: Filename to validate

    Returns:
        True if filename is valid and safe
    """
    if not filename:
        return False

    # Check for invalid characters
    invalid_chars = r'<>:"/\\|?*'
    if any(char in filename for char in invalid_chars):
        return False

    # Check for reserved names (Windows)
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved_names:
        return False

    # Check length (most filesystems support 255 chars)
    if len(filename) > 255:
        return False

    # Check for leading/trailing spaces or dots
    if filename != filename.strip(" ."):
        return False

    return True
