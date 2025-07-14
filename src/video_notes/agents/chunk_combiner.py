"""Chunk combiner agent for combining relevant chunk summaries into a cohesive summary.

This agent takes multiple chunk summaries and combines them into a unified,
comprehensive summary using AI services.
"""

from pydantic import BaseModel, Field

from . import ai_client


class CombinedSummary(BaseModel):
    """Output model for combined summary."""

    summary: str = Field(..., description="The combined comprehensive summary")
    success: bool = Field(..., description="Whether combination was successful")
    error_message: str | None = Field(None, description="Error message if combination failed")
    word_count: int = Field(..., description="Word count of the combined summary", ge=0)
    chunks_processed: int = Field(
        ..., description="Number of chunk summaries that were processed", ge=0
    )


def combine_relevant_chunks(
    chunk_summaries: list[str],
    model: str = "gemma3:12b",
) -> CombinedSummary:
    """Combine multiple chunk summaries into a cohesive final summary.

    This agent takes individual chunk summaries and creates a unified,
    comprehensive summary that maintains coherence and emphasizes
    the most important information.

    Args:
        chunk_summaries: List of individual chunk summaries to combine
        model: Ollama model name to use for generating the combined summary

    Returns:
        CombinedSummary with the unified summary and metadata
    """
    # Validate input
    if not chunk_summaries:
        return CombinedSummary(
            summary="",
            success=False,
            error_message="No chunk summaries provided",
            word_count=0,
            chunks_processed=0,
        )

    # Filter out empty summaries
    valid_summaries = [summary.strip() for summary in chunk_summaries if summary.strip()]

    if not valid_summaries:
        return CombinedSummary(
            summary="",
            success=False,
            error_message="All chunk summaries are empty",
            word_count=0,
            chunks_processed=0,
        )

    # Build the combination prompt
    prompt_parts = []

    prompt_parts.append(
        "Create a comprehensive, well-structured final summary that synthesizes all the "
        "key information."
    )
    prompt_parts.append("")

    # Add instructions for synthesis
    prompt_parts.extend(
        [
            "",
            "Guidelines for synthesis:",
            "- Identify and emphasize the most important themes and insights",
            "- Remove redundancy while preserving key details",
            "- Ensure logical flow and coherence",
            "- Use proper markdown formatting with headers, emphasis, and structure",
            "- Maintain the overall narrative and context",
            "",
            "Section summaries to combine:",
            "",
        ]
    )

    # Add each chunk summary with delimiters
    for i, summary in enumerate(valid_summaries, 1):
        prompt_parts.extend([f"### Section {i}:", summary, ""])

    prompt_parts.append("Now create the comprehensive final summary:")

    user_content = "\n".join(prompt_parts)

    # Create messages for AI service
    messages = [
        {
            "role": "system",
            "content": "You are an expert at synthesizing information from multiple sources into "
            "cohesive, comprehensive summaries. Always use proper markdown formatting "
            "including headers, bullet points, **bold** for emphasis, and *italic* for "
            "additional emphasis. Focus on creating a logical narrative flow.",
        },
        {"role": "user", "content": user_content},
    ]

    try:
        # Generate combined summary using AI client
        combined_text = ai_client.generate_with_messages(messages, model)

        if combined_text is None or not combined_text.strip():
            return CombinedSummary(
                summary="",
                success=False,
                error_message="AI client returned no response or empty response",
                word_count=0,
                chunks_processed=len(valid_summaries),
            )

        # Calculate word count
        word_count = len(combined_text.split())

        return CombinedSummary(
            summary=combined_text.strip(),
            success=True,
            error_message=None,
            word_count=word_count,
            chunks_processed=len(valid_summaries),
        )

    except Exception as e:
        return CombinedSummary(
            summary="",
            success=False,
            error_message=f"Combination failed: {str(e)}",
            word_count=0,
            chunks_processed=len(valid_summaries),
        )
