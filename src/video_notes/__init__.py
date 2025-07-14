"""Video Notes - AI-powered YouTube transcript processor.

A Python package for downloading YouTube transcripts and generating
AI-powered summaries using local LLM models via Ollama.
"""

from video_notes.agents import (
    chunk_combiner,
    chunk_sizing,
    chunk_summarizer,
    filename_generator,
    final_markdown,
)
from video_notes.cli import cli
from video_notes.models.processing import (
    ProcessingConfig,
    ProcessingResult,
    SummaryConfig,
)
from video_notes.models.text import TextChunk, TextChunker
from video_notes.models.video import VideoInfo
from video_notes.services.prompt_builder import PromptBuilder
from video_notes.services.video import (
    extract_video_id,
    extract_video_info,
    format_video_info_display,
    get_transcript_content,
    get_video_metadata_summary,
    validate_youtube_url,
)
from video_notes.services.workflow import process_video
from video_notes.utils import (
    ensure_directory_exists,
    get_safe_filename,
    sanitize_filename,
    write_text_file,
)

__version__ = "0.1.0"

__all__ = [
    # Core functions
    "process_video",
    "PromptBuilder",
    # Data models
    "ProcessingConfig",
    "ProcessingResult",
    "SummaryConfig",
    "VideoInfo",
    "TextChunk",
    "TextChunker",
    # Agents
    "chunk_combiner",
    "chunk_sizing",
    "chunk_summarizer",
    "filename_generator",
    "final_markdown",
    # Video services
    "extract_video_id",
    "extract_video_info",
    "format_video_info_display",
    "get_transcript_content",
    "get_video_metadata_summary",
    "validate_youtube_url",
    # Utilities
    "ensure_directory_exists",
    "get_safe_filename",
    "sanitize_filename",
    "write_text_file",
    # CLI
    "cli",
]
