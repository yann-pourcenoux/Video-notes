"""Video-related data models for video notes processing."""

from pydantic import BaseModel, Field


class VideoInfo(BaseModel):
    """Information about a YouTube video.

    This class holds metadata about a YouTube video including its URL,
    title, author, and other relevant information extracted from the video.

    Attributes:
        url (str): The YouTube video URL
        title (str | None): Video title (if available)
        video_id (str | None): YouTube video ID extracted from URL
        description (str | None): Video description text
        author (str | None): Video author/channel name
        view_count (int | None): Number of views
        length (int | None): Video duration in seconds
        publish_date (str | None): Video publication date
    """

    url: str = Field(..., description="The YouTube video URL")
    title: str | None = Field(default=None, description="Video title (if available)")
    video_id: str | None = Field(default=None, description="YouTube video ID extracted from URL")
    description: str | None = Field(default=None, description="Video description text")
    author: str | None = Field(default=None, description="Video author/channel name")
    view_count: int | None = Field(default=None, description="Number of views (if available)")
    length: int | None = Field(default=None, description="Video duration in seconds (if available)")
    publish_date: str | None = Field(default=None, description="Video publication date")

    @property
    def has_metadata(self) -> bool:
        """Check if video metadata is available.

        Returns:
            bool: True if either title or video_id is available.
        """
        return self.title is not None or self.video_id is not None

    @property
    def duration_formatted(self) -> str | None:
        """Get formatted duration (HH:MM:SS or MM:SS).

        Returns:
            Optional[str]: Formatted duration string or None if length unavailable.
        """
        if self.length is None:
            return None

        hours = self.length // 3600
        minutes = (self.length % 3600) // 60
        seconds = self.length % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
