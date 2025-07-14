"""Agents for video notes processing.

This package contains small, focused agents that handle specific tasks
in the video processing pipeline. Each agent is a pure function with
clear input/output contracts using Pydantic for validation.
"""

from . import ai_client
from .chunk_combiner import (
    CombinedSummary,
    combine_relevant_chunks,
)
from .chunk_sizing import ChunkParameters, compute_chunk_parameters
from .chunk_summarizer import ChunkSummary, summarize_chunk
from .filename_generator import (
    FilenameResult,
    generate_filename,
    generate_filename_from_video_info,
)
from .final_markdown import generate_final_markdown

__all__ = [
    # Modules
    "ai_client",
    # Functions
    "compute_chunk_parameters",
    "summarize_chunk",
    "combine_relevant_chunks",
    "generate_filename",
    "generate_filename_from_video_info",
    "generate_final_markdown",
    # Pydantic Models
    "ChunkParameters",
    "ChunkSummary",
    "CombinedSummary",
    "FilenameResult",
]
