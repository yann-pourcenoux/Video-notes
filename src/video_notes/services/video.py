"""Video service for extracting video information and downloading transcripts."""

import logging
import re

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

from video_notes.models.video import VideoInfo


def extract_video_id(url: str) -> str | None:
    """Extract video ID from YouTube URL.

    Args:
        url: YouTube video URL.

    Returns:
        Video ID or None if not found.
    """
    patterns = [
        r"(?:v=|youtu\.be/|embed/|watch\?v=)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/.*[?&]v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_video_info(url: str) -> VideoInfo:
    """Extract video information from YouTube URL.

    Args:
        url: YouTube video URL.

    Returns:
        VideoInfo object with extracted information.
    """
    video_info = VideoInfo(url=url)

    # Extract video ID first
    video_id = extract_video_id(url)
    if video_id:
        video_info.video_id = video_id
    else:
        # If no ID, we can't proceed with other fetches, but we return the object
        # with the URL, as the function is not designed to fail here.
        return video_info

    try:
        # Use yt-dlp to extract comprehensive metadata
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info:
                # Extract available metadata
                video_info.title = info.get("title")
                video_info.description = info.get("description")
                video_info.author = info.get("uploader") or info.get("channel")
                video_info.view_count = info.get("view_count")
                video_info.length = info.get("duration")  # in seconds

                # Format publish date if available
                upload_date = info.get("upload_date")
                if upload_date:
                    # Convert YYYYMMDD to YYYY-MM-DD
                    try:
                        formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                        video_info.publish_date = formatted_date
                    except (ValueError, IndexError):
                        video_info.publish_date = upload_date

    except Exception:
        # Log the warning but don't fail, as the function can return partial info.
        logging.warning("Could not extract full video metadata.", exc_info=True)

    return video_info


def get_transcript_content(video_info: VideoInfo) -> str | None:
    """Download transcript content using youtube-transcript-api.

    Args:
        video_info: Video information.

    Returns:
        Transcript content or None if failed.
    """
    if not video_info.video_id:
        raise ValueError("Cannot get transcript without a video ID.")

    try:
        # Try to get transcript in English first, then any available language
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_info.video_id)

        # Try to find English transcript first
        transcript = None
        try:
            transcript = transcript_list.find_transcript(["en"])
        except Exception:
            # If English not available, get any available transcript
            try:
                transcript = transcript_list.find_transcript(
                    transcript_list._manually_created_transcripts.keys()
                )
            except Exception:
                # If no manual transcripts, try generated ones
                try:
                    transcript = transcript_list.find_generated_transcript(
                        transcript_list._generated_transcripts.keys()
                    )
                except Exception:
                    # Log the warning and continue; will be handled by the check below.
                    logging.warning("Could not find a specific transcript type.", exc_info=True)

        if not transcript:
            raise ValueError(f"No transcripts available for video {video_info.video_id}")

        # Fetch the transcript data
        transcript_data = transcript.fetch()

        # Combine all transcript text
        content_parts = []
        for entry in transcript_data:
            if isinstance(entry, dict):
                content_parts.append(entry.get("text", ""))
            else:
                # Handle object with attributes
                text = getattr(entry, "text", "")
                content_parts.append(text)

        content = " ".join(content_parts)

        return content.strip()

    except Exception as e:
        raise ValueError(f"Error downloading transcript: {e}") from e


def validate_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL.

    Args:
        url: URL to validate.

    Returns:
        True if the URL is a valid YouTube URL.
    """
    return extract_video_id(url) is not None


def get_video_metadata_summary(video_info: VideoInfo) -> dict[str, str | int | None]:
    """Get a summary of video metadata for display or logging.

    Args:
        video_info: Video information object.

    Returns:
        Dictionary containing key metadata fields.
    """
    return {
        "video_id": video_info.video_id,
        "title": video_info.title,
        "author": video_info.author,
        "duration": video_info.duration_formatted,
        "view_count": video_info.view_count,
        "publish_date": video_info.publish_date,
        "has_metadata": video_info.has_metadata,
    }


def format_video_info_display(video_info: VideoInfo) -> str:
    """Format video information for display purposes.

    Args:
        video_info: Video information object.

    Returns:
        Formatted string representation of video info.
    """
    lines = []
    lines.append(f"🎥 Video ID: {video_info.video_id or 'Unknown'}")

    if video_info.title:
        lines.append(f"📺 Title: {video_info.title}")

    if video_info.author:
        lines.append(f"👤 Author: {video_info.author}")

    if video_info.duration_formatted:
        lines.append(f"⏱️  Duration: {video_info.duration_formatted}")

    if video_info.view_count:
        lines.append(f"👀 Views: {video_info.view_count:,}")

    if video_info.publish_date:
        lines.append(f"📅 Published: {video_info.publish_date}")

    return "\n".join(lines)
