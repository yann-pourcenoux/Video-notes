"""Text processing models for transcript handling."""

import re

from pydantic import BaseModel


class TextChunk(BaseModel):
    """Represents a chunk of text with metadata.

    This class holds a segment of text along with position information
    and metadata for processing purposes.

    Attributes:
        content: The actual text content of the chunk
        start_position: Starting character position in original text
        end_position: Ending character position in original text
        chunk_index: Sequential index of this chunk
    """

    content: str
    start_position: int
    end_position: int
    chunk_index: int

    @property
    def length(self) -> int:
        """Get the character length of the chunk.

        Returns:
            Number of characters in the chunk content.
        """
        return len(self.content)


class TextChunker:
    """Text chunking utility for breaking large text into manageable pieces.

    This class handles the logic of splitting large transcripts into smaller
    chunks with configurable size and overlap for processing by AI models.
    """

    def __init__(self, chunk_size: int = 4000, overlap: int = 200) -> None:
        """Initialize text chunker with size and overlap parameters.

        Args:
            chunk_size: Maximum number of tokens per chunk.
            overlap: Number of tokens to overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[TextChunk]:
        """Split text into overlapping chunks based on tokens.

        Args:
            text: Input text to be chunked.

        Returns:
            List of TextChunk objects representing the split text.
        """
        if not text.strip():
            return []

        # Estimate characters per token (rough approximation: 4 chars per token)
        chars_per_token = 4
        max_chars = self.chunk_size * chars_per_token
        overlap_chars = self.overlap * chars_per_token

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            # Calculate end position for this chunk
            end = min(start + max_chars, len(text))

            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 20% of the chunk
                search_start = max(start + int(max_chars * 0.8), start + 1)
                sentence_end = self._find_sentence_boundary(text, search_start, end)
                if sentence_end > start:
                    end = sentence_end

            # Extract chunk content
            chunk_content = text[start:end].strip()

            if chunk_content:
                chunk = TextChunk(
                    content=chunk_content,
                    start_position=start,
                    end_position=end,
                    chunk_index=chunk_index,
                )
                chunks.append(chunk)
                chunk_index += 1

            # Calculate next start position with overlap
            if end >= len(text):
                break

            # Move start position, accounting for overlap
            next_start = max(end - overlap_chars, start + 1)
            start = next_start

        return chunks

    def _find_sentence_boundary(self, text: str, search_start: int, max_end: int) -> int:
        """Find a good sentence boundary for chunking.

        Args:
            text: The full text being chunked.
            search_start: Position to start searching for boundaries.
            max_end: Maximum position to consider.

        Returns:
            Position of sentence boundary, or max_end if none found.
        """
        # Look for sentence endings: ., !, ?
        sentence_pattern = r"[.!?]\s+"

        # Search backwards from max_end to find the last sentence ending
        search_text = text[search_start:max_end]
        matches = list(re.finditer(sentence_pattern, search_text))

        if matches:
            # Return position after the last sentence ending found
            last_match = matches[-1]
            return search_start + last_match.end()

        # If no sentence ending found, look for other boundaries
        # Try paragraph breaks first
        paragraph_pattern = r"\n\s*\n"
        matches = list(re.finditer(paragraph_pattern, search_text))
        if matches:
            last_match = matches[-1]
            return search_start + last_match.end()

        # Try single line breaks
        line_pattern = r"\n"
        matches = list(re.finditer(line_pattern, search_text))
        if matches:
            last_match = matches[-1]
            return search_start + last_match.end()

        # No good boundary found, return max_end
        return max_end

    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in text.

        Args:
            text: Text to analyze.

        Returns:
            Estimated token count.
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4


class TranscriptAnalyzer:
    """Utility class for analyzing transcript characteristics."""

    @staticmethod
    def estimate_transcript_length(text: str) -> str:
        """Estimate transcript length category.

        Args:
            text: Transcript text to analyze.

        Returns:
            Length category string.
        """
        length = len(text)

        if length < 2000:
            return "very_short"
        elif length < 8000:
            return "short"
        elif length < 20000:
            return "medium"
        elif length < 50000:
            return "long"
        else:
            return "very_long"
