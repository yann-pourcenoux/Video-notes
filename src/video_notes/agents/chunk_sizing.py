"""Chunk sizing agent for determining optimal text chunking parameters.

This agent analyzes transcript text and computes the optimal chunk size
and overlap parameters for processing.
"""

from enum import Enum

from pydantic import BaseModel, Field


class TextLengthCategory(Enum):
    """Categories for text length classification."""

    VERY_SHORT = "very_short"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    VERY_LONG = "very_long"


class TextAnalysis(BaseModel):
    """Input model for text analysis."""

    text: str = Field(..., description="The transcript text to analyze")
    text_length: int = Field(..., description="Length of the text in characters")


class ChunkParameters(BaseModel):
    """Output model for chunk sizing parameters."""

    chunk_size: int = Field(..., description="Optimal chunk size in characters", gt=0)
    chunk_overlap: int = Field(..., description="Optimal overlap in characters", ge=0)
    category: TextLengthCategory = Field(..., description="Text length category")
    should_use_hierarchical: bool = Field(
        ..., description="Whether hierarchical summarization is recommended"
    )


# Optimal chunk size mapping based on text length category
CHUNK_SIZE_MAP = {
    TextLengthCategory.VERY_SHORT: 2000,  # No chunking needed
    TextLengthCategory.SHORT: 3000,  # Small chunks for better granularity
    TextLengthCategory.MEDIUM: 4000,  # Standard chunk size
    TextLengthCategory.LONG: 5000,  # Larger chunks for efficiency
    TextLengthCategory.VERY_LONG: 6000,  # Maximum chunk size
}

# Optimal overlap mapping based on text length category
OVERLAP_MAP = {
    TextLengthCategory.VERY_SHORT: 100,  # Minimal overlap
    TextLengthCategory.SHORT: 150,  # Small overlap
    TextLengthCategory.MEDIUM: 200,  # Standard overlap
    TextLengthCategory.LONG: 300,  # More overlap for continuity
    TextLengthCategory.VERY_LONG: 400,  # Maximum overlap for context preservation
}

# Hierarchical summarization recommendation mapping based on text length category
HIERARCHICAL_MAP = {
    TextLengthCategory.VERY_SHORT: False,  # No hierarchical needed for very short text
    TextLengthCategory.SHORT: False,  # No hierarchical needed for short text
    TextLengthCategory.MEDIUM: True,  # Use hierarchical for medium text
    TextLengthCategory.LONG: True,  # Use hierarchical for long text
    TextLengthCategory.VERY_LONG: True,  # Use hierarchical for very long text
}


def compute_chunk_parameters(text: str) -> ChunkParameters:
    """Compute optimal chunk size and overlap parameters for text processing.

    This agent analyzes the input text characteristics and determines
    the best chunking strategy based on text length and complexity.

    Args:
        text (str): The transcript text to analyze

    Returns:
        ChunkParameters with optimal chunk_size, overlap, and processing strategy
    """
    text_length = len(text)
    category = _categorize_text_length(text_length)

    chunk_size = CHUNK_SIZE_MAP[category]
    chunk_overlap = OVERLAP_MAP[category]

    # Determine if hierarchical summarization should be used
    should_use_hierarchical = HIERARCHICAL_MAP[category]

    return ChunkParameters(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        category=category,
        should_use_hierarchical=should_use_hierarchical,
    )


def _categorize_text_length(text_length: int) -> TextLengthCategory:
    """Categorize text by length.

    Args:
        text_length (int): Length of text in characters

    Returns:
        TextLengthCategory: Category based on text length
    """
    if text_length < 2000:
        return TextLengthCategory.VERY_SHORT
    elif text_length < 8000:
        return TextLengthCategory.SHORT
    elif text_length < 20000:
        return TextLengthCategory.MEDIUM
    elif text_length < 50000:
        return TextLengthCategory.LONG
    else:
        return TextLengthCategory.VERY_LONG
