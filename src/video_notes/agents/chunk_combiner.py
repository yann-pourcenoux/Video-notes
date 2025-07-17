"""Chunk combiner agent for combining relevant chunk summaries into a cohesive summary.

This agent takes multiple chunk summaries and combines them into a unified,
comprehensive summary using AI services.
"""

from pydantic import BaseModel

from video_notes.agents.ai_client import generate_with_messages


class CombinedSummary(BaseModel):
    """Represents the combined summary of multiple chunks."""

    summary: str
    chunks_processed: int


def get_messages(chunk_summaries: list[str], notes: str | None = None) -> list[dict[str, str]]:
    """Generate messages for combining chunk summaries.

    Args:
        chunk_summaries: A list of chunk summary strings.
        notes: Optional manual notes to guide the summary.

    Returns:
        A list of message dictionaries for the AI client.
    """
    summaries_text = "\n\n---\n\n".join(chunk_summaries)

    base_prompt = (
        "You have been given a series of summaries from a long video transcript. "
        "Your task is to synthesize them into a single, cohesive, and "
        "well-structured summary.\n\n"
        "Focus on creating a final output that:\n"
        "- **Integrates Key Themes**: Identify and merge the main ideas, concepts, "
        "and narratives from all summaries.\n"
        "- **Maintains Logical Flow**: Organize the content in a clear, logical order.\n"
        "- **Eliminates Redundancy**: Remove duplicate information and consolidate "
        "related points.\n"
        "- **Preserves Critical Information**: Ensure that essential facts, data, "
        "and takeaways are retained."
    )

    if notes:
        notes_guidance = (
            "A user has provided the following notes to guide the final summary. "
            "Pay special attention to these points, ensuring they are prominently "
            "addressed in the final output.\n\n"
            f"USER NOTES:\n{notes}"
        )
        user_content = "\n\n".join(
            [
                base_prompt,
                notes_guidance,
                f"Here are the summaries:\n{summaries_text}",
            ]
        )
    else:
        user_content = f"{base_prompt}\n\nHere are the summaries:\n{summaries_text}"

    system_message = (
        "You are an expert at synthesizing information from multiple sources into "
        "cohesive, comprehensive summaries. Always use proper markdown formatting "
        "including headers, bullet points, **bold** for emphasis, and *italic* for "
        "additional emphasis. Focus on creating a logical narrative flow."
    )

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_content},
    ]


def combine_relevant_chunks(
    chunk_summaries: list[str],
    model: str = "gemma:7b",
    notes: str | None = None,
) -> CombinedSummary:
    """Combine multiple chunk summaries into a cohesive final summary.

    This agent takes individual chunk summaries and creates a unified,
    comprehensive summary that maintains coherence and emphasizes
    the most important information.

    Args:
        chunk_summaries: List of individual chunk summaries to combine.
        model: The name of the Ollama model to use.
        notes: Optional manual notes to guide the summary.

    Returns:
        CombinedSummary with the unified summary and metadata.
    """
    if not chunk_summaries:
        return CombinedSummary(summary="", chunks_processed=0)

    valid_summaries = [s for s in chunk_summaries if s.strip()]
    if not valid_summaries:
        return CombinedSummary(
            summary="No valid chunk summaries were provided to combine.",
            chunks_processed=0,
        )

    messages = get_messages(valid_summaries, notes=notes)

    response = generate_with_messages(messages=messages, model=model)

    if not response:
        return CombinedSummary(summary="", chunks_processed=len(valid_summaries))

    return CombinedSummary(
        summary=response,
        chunks_processed=len(valid_summaries),
    )
