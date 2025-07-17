"""A Streamlit application for taking notes from YouTube videos."""

import streamlit as st

from video_notes.agents import (
    compute_chunk_parameters,
    generate_final_markdown,
)
from video_notes.services import get_available_models
from video_notes.services.video import validate_youtube_url
from video_notes.services.workflow import (
    create_direct_summary,
    create_hierarchical_summary,
    extract_video_data,
)

# Define a default model for summarization
DEFAULT_MODEL = "gemma3:12b"


def process_video_url(youtube_url: str, manual_notes: str, model: str) -> str | None:
    """Processes a YouTube URL to generate summarized notes.

    This function fetches video information, downloads the transcript,
    summarizes the content, and combines it with manual notes into a
    final markdown format.

    Args:
        youtube_url: The URL of the YouTube video.
        manual_notes: Optional manual notes to include in the final output.
        model: The model to use for summarization.

    Returns:
        The generated markdown notes as a string, or None if processing fails.
    """
    with st.spinner("Step 1: Fetching video data and transcript..."):
        video_data = extract_video_data(youtube_url)
        if not video_data or not video_data.transcript_text:
            st.error("Could not retrieve video transcript. Please check the URL.")
            return None

    with st.spinner("Step 2: Analyzing transcript for summarization..."):
        chunk_params = compute_chunk_parameters(video_data.transcript_text)

    with st.spinner("Step 3: Generating summary..."):
        if chunk_params.should_use_hierarchical:
            with st.spinner("Step 3: Generating hierarchical summary..."):
                summary_text = create_hierarchical_summary(
                    transcript_text=video_data.transcript_text,
                    chunk_params=chunk_params,
                    model=model,
                    notes=manual_notes,
                )
        else:
            with st.spinner("Step 3: Generating direct summary..."):
                summary_text = create_direct_summary(
                    transcript_text=video_data.transcript_text,
                    model=model,
                    notes=manual_notes,
                )

        if not summary_text:
            st.error("Failed to generate summary.")
            return None

    with st.spinner("Step 4: Finalizing markdown..."):
        final_notes = generate_final_markdown(
            summary_content=summary_text,
            video_title=video_data.video_info.title,
            video_url=video_data.video_info.url,
            author=video_data.video_info.author,
            publish_date=video_data.video_info.publish_date,
            duration=video_data.video_info.duration_formatted,
        )

    return final_notes


def main() -> None:
    """Main function to run the Streamlit application."""
    st.title("Video Note Taker")

    # Initialize session state for storing notes
    if "final_notes" not in st.session_state:
        st.session_state.final_notes = None

    available_models = get_available_models()

    if not available_models:
        st.warning("Could not connect to Ollama. Please make sure Ollama is running.")
        selected_model = st.text_input("Enter the model name manually", value=DEFAULT_MODEL)
    else:
        default_index = (
            available_models.index(DEFAULT_MODEL) if DEFAULT_MODEL in available_models else 0
        )
        selected_model = st.selectbox(
            "Choose a model",
            options=available_models,
            index=default_index,
        )

    youtube_url = st.text_input("YouTube Video URL")
    manual_notes = st.text_area("Manual Notes")

    if st.button("Generate Notes"):
        if validate_youtube_url(youtube_url):
            final_notes = process_video_url(youtube_url, manual_notes, selected_model)
            st.session_state.final_notes = final_notes
        else:
            st.error("Please enter a valid YouTube URL.")
            st.session_state.final_notes = None

    if st.session_state.final_notes:
        st.markdown("---")
        st.code(st.session_state.final_notes, language="markdown")


if __name__ == "__main__":
    main()
