"""Processing result models for video notes operations."""

from pydantic import BaseModel, Field


class SummaryConfig(BaseModel):
    """Configuration for text summarization.

    This class holds configuration options for AI-powered summarization,
    including style preferences, length limits, and focus areas.

    Attributes:
        max_length (int | None): The maximum length of the summary in characters
        focus_areas (list[str]): The areas to focus on during summarization
        style (str): The style format for the summary
    """

    max_length: int | None = Field(default=None)
    focus_areas: list[str] = Field(default_factory=list)
    style: str = Field(default="paragraph", description="Summary style format")


class ProcessingConfig(BaseModel):
    """Configuration for transcript processing.

    This class holds all configuration options for processing YouTube transcripts.

    Attributes:
        youtube_url (str): The YouTube video URL to process
        model (str): The AI model to use for processing
        output_folder (str): The directory where output files should be saved
        save_transcript (bool): Whether to save the transcript file (defaults to False)
    """

    youtube_url: str
    model: str
    output_folder: str = Field(default=".")
    save_transcript: bool = Field(default=False)


class ProcessingResult(BaseModel):
    """Result of transcript processing operation.

    This class encapsulates the result of any processing operation,
    including success status, output file paths, and error information.

    Attributes:
        success (bool): Whether the operation completed successfully
        transcript_file (str | None): Path to the generated transcript file
        summary_file (str | None): Path to the generated summary file
        error_message (str | None): Error description if operation failed
    """

    success: bool
    transcript_file: str | None = Field(default=None)
    summary_file: str | None = Field(default=None)
    error_message: str | None = Field(default=None)
