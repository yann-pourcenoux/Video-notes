"""Video processing workflow with focused, single-responsibility functions.

This module provides a clear, step-by-step workflow for processing YouTube videos
into AI-generated summaries. Each function has a single responsibility and the
overall flow is easy to follow and understand.
"""

from pathlib import Path

import streamlit as st
from pydantic import BaseModel

from video_notes.agents import (
    ChunkParameters,
    combine_relevant_chunks,
    compute_chunk_parameters,
    generate_filename_from_video_info,
    generate_final_markdown,
    summarize_chunk,
)
from video_notes.models import (
    ProcessingConfig,
    ProcessingResult,
    TextChunker,
    VideoInfo,
)
from video_notes.services.video import extract_video_info, get_transcript_content
from video_notes.utils import write_text_file


class VideoData(BaseModel):
    """Container for video information and transcript content.

    Attributes:
        video_info (VideoInfo): The video information
        transcript_text (str): The transcript text
    """

    video_info: VideoInfo
    transcript_text: str


class ContentResult(BaseModel):
    """Container for generated content and filenames.

    Attributes:
        summary_content (str): The summary content
        summary_filename (str): The summary filename
        transcript_filename (str): The transcript filename
    """

    summary_content: str
    summary_filename: str
    transcript_filename: str


def extract_video_data(youtube_url: str) -> VideoData | None:
    """Extract video information and download transcript.

    Args:
        youtube_url: YouTube video URL to process.
        verbose: Whether to print detailed progress information.

    Returns:
        VideoData with video info and transcript, or None if failed.
    """
    with st.spinner("🔄 Step 1: Downloading transcript to memory..."):
        # Extract video information
        video_info = extract_video_info(youtube_url)

        if not video_info.video_id:
            st.error("❌ Failed to extract video ID from URL")
            return None

        # Get transcript content
        transcript_content = get_transcript_content(video_info)

        if not transcript_content:
            st.error("❌ Failed to download transcript")
            return None

    st.success(f"✅ Downloaded transcript ({len(transcript_content)} characters)")

    return VideoData(video_info=video_info, transcript_text=transcript_content)


def create_hierarchical_summary(
    transcript_text: str,
    chunk_params: ChunkParameters,
    model: str,
    notes: str | None = None,
) -> str | None:
    """Create summary using hierarchical chunking strategy for long content.

    Args:
        transcript_text (str): Raw transcript text to summarize.
        chunk_params (ChunkParameters): Chunking parameters from analysis.
        model (str): AI model to use for summarization.
        notes (str | None): Manual notes for focused summary.

    Returns:
        Generated summary content, or None if failed.
    """
    with st.spinner("📄 Step 3a: Creating and summarizing chunks..."):
        # Create text chunker with computed parameters
        chunker = TextChunker(
            chunk_size=chunk_params.chunk_size, overlap=chunk_params.chunk_overlap
        )

        # Split text into chunks
        chunks = chunker.chunk_text(transcript_text)
        st.write(f"   • Created {len(chunks)} chunks")

        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            summary_result = summarize_chunk(
                chunk_content=chunk.content,
                chunk_index=chunk.chunk_index,
                model=model,
                notes=notes,
            )

            if summary_result.success:
                chunk_summaries.append(summary_result.summary)
                st.write(
                    f"   • Summarized chunk {chunk.chunk_index + 1} "
                    f"({summary_result.word_count} words)"
                )
            else:
                st.warning(
                    f"   • Failed to summarize chunk {chunk.chunk_index + 1}: "
                    f"{summary_result.error_message}"
                )

        if not chunk_summaries:
            st.error("❌ Failed to summarize any chunks")
            return None

    with st.spinner(f"🔗 Step 3b: Combining {len(chunk_summaries)} chunk summaries..."):
        # Combine chunk summaries
        combined_result = combine_relevant_chunks(
            chunk_summaries=chunk_summaries,
            model=model,
            notes=notes,
        )

        if combined_result.summary:
            st.write(
                f"   • Combined summary created ({combined_result.chunks_processed} "
                f"chunks processed)"
            )
            return combined_result.summary
        else:
            st.info("   • Using fallback: joining summaries with newlines")
            # Fallback: join summaries with newlines
            return "\n\n".join(chunk_summaries)


def create_direct_summary(transcript_text: str, model: str, notes: str | None = None) -> str | None:
    """Create summary directly for short content without chunking.

    Args:
        transcript_text: Raw transcript text to summarize.
        model: AI model to use for summarization.
        notes: Manual notes for focused summary.

    Returns:
        Generated summary content, or None if failed.
    """
    with st.spinner("📝 Step 3: Summarizing short text directly..."):
        # Summarize directly without chunking
        summary_result = summarize_chunk(
            chunk_content=transcript_text,
            chunk_index=0,
            model=model,
            notes=notes,
        )

        if summary_result.success:
            st.write(f"   • Direct summary created ({summary_result.word_count} words)")
            return summary_result.summary
        else:
            st.error(f"   • Failed to create summary: {summary_result.error_message}")
            return None


def generate_content_files(
    summary_content: str,
    video_info: VideoInfo,
) -> ContentResult | None:
    """Generate filenames and create final markdown content.

    Args:
        summary_content: Generated summary content.
        video_info: Video metadata.

    Returns:
        ContentResult with final content and filenames, or None if failed.
    """
    st.write("📂 Step 4: Generating filenames...")

    # Generate appropriate filenames
    filename_result = generate_filename_from_video_info(
        video_info=video_info,
        include_date=False,
    )

    st.write(f"   • Summary file: {filename_result.summary_filename}")
    st.write(f"   • Transcript file: {filename_result.transcript_filename}")

    st.write("📋 Step 5: Creating final markdown...")

    # Generate final markdown with metadata
    markdown_content = generate_final_markdown(
        summary_content=summary_content,
        video_title=video_info.title,
        author=video_info.author,
        video_url=video_info.url,
        duration=video_info.duration_formatted,
        publish_date=video_info.publish_date,
    )

    if not markdown_content:
        st.error("   • Failed to create markdown: No content generated")
        return None

    return ContentResult(
        summary_content=markdown_content,
        summary_filename=filename_result.summary_filename,
        transcript_filename=filename_result.transcript_filename,
    )


def save_output_files(
    content_result: ContentResult,
    transcript_text: str,
    output_folder: str = ".",
    save_transcript: bool = False,
) -> tuple[bool, str | None]:
    """Save the generated content and transcript to files.

    Args:
        content_result: Generated content and filenames.
        transcript_text: Raw transcript text to save.
        output_folder: Directory where output files should be saved.
        save_transcript: Whether to save the transcript file.

    Returns:
        Tuple of (success, error_message).
    """
    with st.spinner("🔄 Step 6: Saving files..."):
        output_path = Path(output_folder)
        summary_path = output_path / content_result.summary_filename

        # Save transcript file only if requested
        if save_transcript:
            transcript_path = output_path / content_result.transcript_filename
            transcript_success = write_text_file(str(transcript_path), transcript_text)

            if not transcript_success:
                st.error(f"Failed to save transcript file: {transcript_path}")
                return (
                    False,
                    f"Failed to save transcript file: {transcript_path}",
                )

        # Save summary file
        summary_success = write_text_file(str(summary_path), content_result.summary_content)

        if not summary_success:
            st.error(f"Failed to save summary file: {summary_path}")
            return False, f"Failed to save summary file: {summary_path}"

    st.success("✅ Files saved successfully!")

    return True, None


def process_video(config: ProcessingConfig) -> ProcessingResult:
    """Process YouTube video through the complete workflow.

    Args:
        config (ProcessingConfig): Processing configuration object.

    Returns:
        ProcessingResult with processing status and file paths.
    """
    # Step 1: Extract video data
    video_data = extract_video_data(config.youtube_url)
    if not video_data:
        return ProcessingResult(
            success=False,
            error_message="Failed to extract video information or download transcript",
        )

    # Step 2: Analyze content
    st.write("🔄 Step 2: Analyzing content and generating summary...")

    chunk_params = compute_chunk_parameters(video_data.transcript_text)

    # Step 3: Generate summary using appropriate strategy
    if chunk_params.should_use_hierarchical:
        summary_content = create_hierarchical_summary(
            transcript_text=video_data.transcript_text,
            chunk_params=chunk_params,
            model=config.model,
            notes=config.notes,
        )
    else:
        summary_content = create_direct_summary(
            transcript_text=video_data.transcript_text,
            model=config.model,
            notes=config.notes,
        )

    if not summary_content:
        return ProcessingResult(success=False, error_message="Failed to generate summary content")

    # Step 4: Generate final content and filenames
    content_result = generate_content_files(
        summary_content,
        video_data.video_info,
    )
    if not content_result:
        return ProcessingResult(
            success=False,
            error_message="Failed to generate final content and filenames",
        )

    # Step 5: Save files
    save_success, error_message = save_output_files(
        content_result,
        video_data.transcript_text,
        config.output_folder,
        config.save_transcript,
    )
    if not save_success:
        return ProcessingResult(success=False, error_message=error_message)

    st.balloons()
    st.success("🎉 Processing complete!")

    # Prepare full file paths for the result
    from pathlib import Path

    output_path = Path(config.output_folder)
    full_summary_path = output_path / content_result.summary_filename

    # Only include transcript path if transcript was saved
    full_transcript_path = None
    if config.save_transcript:
        full_transcript_path = output_path / content_result.transcript_filename

    return ProcessingResult(
        success=True,
        transcript_file=str(full_transcript_path) if full_transcript_path else None,
        summary_file=str(full_summary_path),
    )
