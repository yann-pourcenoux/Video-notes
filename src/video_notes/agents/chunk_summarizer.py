"""Chunk summarizer agent for generating summaries of individual text chunks.

This agent takes a text chunk and summarization parameters to generate
a focused summary using AI services.
"""

from typing import Self

from pydantic import BaseModel, Field, model_validator

from . import ai_client


def get_messages(content: str, chunk_number: int) -> list[dict[str, str]]:
    """Generate messages for chunk summarization.

    Args:
        content: The text content to summarize
        chunk_number: The section number for context

    Returns:
        List of message dictionaries for AI client
    """
    chunk_summarization_template = """This is section {chunk_number} of a longer transcript.

Extract and summarize the most important information. Focus on:
• Key concepts and main ideas
• Important facts, data points, or statistics
• Actionable insights or practical takeaways
• Notable quotes or examples

Content to summarize:
{content}"""

    user_content = chunk_summarization_template.format(chunk_number=chunk_number, content=content)

    system_content = """You are an expert at creating concise, well-structured summaries.

FORMATTING REQUIREMENTS:
• Always use bullet points (•) to organize information
• Use **bold** for key terms, concepts, and important names
• Keep each bullet point to 1-2 lines maximum
• Start each summary with 3-5 main bullet points
• Prioritize actionable insights and concrete information
• Avoid lengthy paragraphs - break content into digestible points
• Use clear, direct language without unnecessary words

EXAMPLE OUTPUT FORMAT:
```markdown
# Machine Learning Fundamentals

Discussion covers basic concepts and practical applications in modern AI systems.

## Core Concepts
- **Neural Networks**: Computational models inspired by biological neurons
- **Training Data**: Large datasets used to teach algorithms patterns
- **Overfitting**: When models memorize training data but fail on new examples

## Practical Applications
- **Image Recognition**: Used in medical diagnosis and autonomous vehicles
- **Natural Language**: Powers chatbots and translation services
```"""

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


class ChunkInput(BaseModel):
    """Input model for chunk summarization."""

    chunk_content: str = Field(..., description="The text content to summarize")
    chunk_index: int = Field(..., description="Index of the chunk in the sequence", ge=0)
    focus_areas: list[str] = Field(
        default_factory=list, description="Areas to focus on during summarization"
    )

    temperature: float = Field(0.0, description="AI generation temperature", ge=0.0, le=1.0)


class ChunkSummary(BaseModel):
    """Output model for chunk summary."""

    summary: str = Field(..., description="The generated summary text")
    chunk_index: int = Field(..., description="Index of the original chunk")
    success: bool = Field(..., description="Whether summarization was successful")
    error_message: str | None = Field(None, description="Error message if summarization failed")
    word_count: int = Field(
        default=0, description="Word count of the generated summary (auto-calculated)"
    )

    @model_validator(mode="after")
    def calculate_word_count(self) -> Self:
        """Automatically calculate word count from the summary text."""
        if self.summary:
            self.word_count = len(self.summary.split())
        else:
            self.word_count = 0
        return self


def summarize_chunk(
    chunk_content: str,
    chunk_index: int,
    model: str = "gemma3:12b",
) -> ChunkSummary:
    """Summarize a single text chunk using AI service.

    This agent takes a chunk of text and generates a focused summary
    based on the specified focus areas.

    Args:
        chunk_content: The text content to summarize
        chunk_index: Index of the chunk in the sequence
        model: Ollama model name to use for generation
        temperature: AI generation temperature

    Returns:
        ChunkSummary with the generated summary and metadata
    """
    # Validate input
    if not chunk_content.strip():
        return ChunkSummary(
            summary="",
            chunk_index=chunk_index,
            success=False,
            error_message="Empty chunk content provided",
        )

        # Create messages for AI service
    messages = get_messages(chunk_content, chunk_index + 1)

    try:
        # Generate summary using AI client
        summary_text = ai_client.generate_with_messages(messages, model)

        if summary_text is None or not summary_text.strip():
            return ChunkSummary(
                summary="",
                chunk_index=chunk_index,
                success=False,
                error_message="AI client returned no response or empty response",
            )

        return ChunkSummary(
            summary=summary_text.strip(),
            chunk_index=chunk_index,
            success=True,
            error_message=None,
        )

    except Exception as e:
        return ChunkSummary(
            summary="",
            chunk_index=chunk_index,
            success=False,
            error_message=f"Summarization failed: {str(e)}",
        )
