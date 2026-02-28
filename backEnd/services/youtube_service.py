from typing import Any, Dict, List, Optional

from .youtube_client import YoutubeClient


class YoutubeService:
    """High-level service to fetch local news videos for a city."""
    def __init__(self, client: Optional[YoutubeClient] = None):
        try:
            self.client = client or YoutubeClient()
        except Exception:
            # Best-effort: if YouTube isn't configured, the weather API should still work.
            self.client = None

    async def get_local_news_videos(
        self,
        city: str,
        country_code: Optional[str] = None,
        max_results: int = 4,
    ) -> List[Dict[str, Any]]:
        """Returns a list of local news videos for the given city."""

        if not self.client:
            return []

        query = f"{city} local news"

        region_code = None
        if country_code and len(country_code.strip()) == 2:
            region_code = country_code.strip().upper()

        data = await self.client.search_videos(
            query=query,
            region_code=region_code or "US",
            max_results=max_results,
        )
        items = data.get("items", [])

        videos: List[Dict[str, Any]] = []
        for item in items:
            id_info = item.get("id", {})
            video_id = id_info.get("videoId")
            snippet = item.get("snippet", {})
            if not video_id or not snippet:
                continue

            thumbnails = snippet.get("thumbnails", {}) or {}
            thumb = thumbnails.get("medium") or thumbnails.get("high") or thumbnails.get("default") or {}

            videos.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "channel_title": snippet.get("channelTitle"),
                    "published_at": snippet.get("publishedAt"),
                    "thumbnail_url": thumb.get("url"),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

        return videos
