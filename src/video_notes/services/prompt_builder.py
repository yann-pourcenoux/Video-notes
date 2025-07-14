"""Shared prompt building utilities for AI services."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from video_notes.models.processing import SummaryConfig


class PromptBuilder:
    """Utility class for building consistent prompts for Ollama.

    This class provides a unified way to construct prompts based on SummaryConfig
    settings, with support for both message format and single prompt format.
    """

    @staticmethod
    def build_summary_messages(
        text: str, config: "SummaryConfig", content_type: str = "video transcript"
    ) -> list[dict[str, str]]:
        """Build messages for text summarization based on configuration.

        Args:
            text: The text to summarize.
            config: Configuration for the summarization.
            content_type: Type of content being summarized (e.g., "video transcript", "text").

        Returns:
            list[dict[str, str]]: Messages with system and user roles.
        """
        # Build user prompt parts
        prompt_parts = []

        # Add style instruction
        style_instructions = {
            "bullet_points": "Create a summary in bullet point format.",
            "paragraph": "Create a summary in paragraph format.",
            "outline": "Create a summary in outline format with headers and subpoints.",
        }

        style_instruction = style_instructions.get(config.style, style_instructions["paragraph"])
        prompt_parts.append(style_instruction)

        # Add length instruction
        if config.max_length:
            prompt_parts.append(f"Keep the summary under {config.max_length} words.")

        # Add focus instruction
        if config.focus_areas:
            focus_list = ", ".join(config.focus_areas)
            prompt_parts.append(f"Focus particularly on these areas: {focus_list}.")

        # Add the main instruction and text
        prompt_parts.extend([f"Please summarize the following {content_type}:", "", text])

        user_content = "\n".join(prompt_parts)

        return [
            {"role": "system", "content": PromptBuilder.get_system_message()},
            {"role": "user", "content": user_content},
        ]

    @staticmethod
    def build_summary_prompt(
        text: str, config: "SummaryConfig", content_type: str = "video transcript"
    ) -> str:
        """Build a prompt for text summarization.

        This is a legacy method, use build_summary_messages instead.

        Args:
            text: The text to summarize.
            config: Configuration for the summarization.
            content_type: Type of content being summarized (e.g., "video transcript", "text").

        Returns:
            str: The constructed prompt (user content only).
        """
        messages = PromptBuilder.build_summary_messages(text, config, content_type)
        return messages[1]["content"]  # Return user content only

    @staticmethod
    def build_chunk_summary_messages(chunk_content: str) -> list[dict[str, str]]:
        """Build messages for summarizing a text chunk.

        Args:
            chunk_content: Content of the chunk to summarize.

        Returns:
            list[dict[str, str]]: Messages for chunk summarization.
        """
        user_content = f"Summarize the following text in a concise manner:\n\n{chunk_content}"

        return [
            {"role": "system", "content": PromptBuilder.get_system_message()},
            {"role": "user", "content": user_content},
        ]

    @staticmethod
    def build_chunk_summary_prompt(chunk_content: str) -> str:
        """Build a prompt for summarizing a text chunk (legacy method).

        Args:
            chunk_content: Content of the chunk to summarize.

        Returns:
            str: The constructed prompt for chunk summarization.
        """
        messages = PromptBuilder.build_chunk_summary_messages(chunk_content)
        return messages[1]["content"]  # Return user content only

    @staticmethod
    def build_final_summary_messages(
        chunk_summaries: list[str],
    ) -> list[dict[str, str]]:
        """Build messages for creating a final summary from chunk summaries.

        Args:
            chunk_summaries: List of individual chunk summaries.

        Returns:
            list[dict[str, str]]: Messages for final summary creation.
        """
        # Combine all chunk summaries with XML-style delimiters
        combined_summaries = "\n\n".join(
            f"<summary>\n{summary}\n</summary>" for summary in chunk_summaries
        )

        user_content = (
            "You are given several summaries from different sections of a long text. "
            "Each section summary is enclosed in <summary> tags. Create a comprehensive, "
            "well-structured final summary that combines all the key information.\n\n"
            f"Section summaries:\n{combined_summaries}\n\n"
            "Return ONLY the comprehensive summary with no introduction, preamble, or "
            "explanatory text:"
        )

        return [
            {"role": "system", "content": PromptBuilder.get_system_message()},
            {"role": "user", "content": user_content},
        ]

    @staticmethod
    def build_final_summary_prompt(chunk_summaries: list[str]) -> str:
        """Build a prompt for creating a final summary from chunk summaries (legacy method).

        Args:
            chunk_summaries: List of individual chunk summaries.

        Returns:
            str: The constructed prompt for final summary creation.
        """
        messages = PromptBuilder.build_final_summary_messages(chunk_summaries)
        return messages[1]["content"]  # Return user content only

    @staticmethod
    def calculate_max_tokens(config: "SummaryConfig") -> int:
        """Calculate maximum tokens based on configuration.

        Args:
            config: Configuration for the summarization.

        Returns:
            int: Maximum number of tokens for the response.
        """
        if config.max_length:
            # Rough estimation: 1 word ≈ 1.3 tokens
            return int(config.max_length * 1.3)

        # Default max tokens for summaries
        return 1000

    @staticmethod
    def get_system_message() -> str:
        """Get the standard system message for AI assistants.

        Returns:
            str: Standard system message for video transcript summarization.
        """
        return (
            "You are a helpful assistant that creates high-quality summaries of video transcripts."
        )

    @staticmethod
    def messages_to_prompt(messages: list[dict[str, str]]) -> str:
        """Convert messages to a single prompt string for Ollama.

        Args:
            messages: List of messages with role and content.

        Returns:
            str: Combined prompt string with system context and user request.
        """
        system_content = ""
        user_content = ""

        for message in messages:
            if message["role"] == "system":
                system_content = message["content"]
            elif message["role"] == "user":
                user_content = message["content"]

        if system_content:
            return f"{system_content}\n\n{user_content}"
        else:
            return user_content
