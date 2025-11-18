from pyclbr import Class
from typing import List, Dict, Any, Optional
import httpx
from fastapi import HTTPException
from backEnd.core.config import settings

class YoutubeClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://www.googleapis.com/youtube/v3"):
        cfg_key = getattr(settings, "youtube_api_key", None)
        self.api_key = api_key or cfg_key
        self.base_url = base_url

        if not self.api_key:
            raise  RuntimeError("Youtube API key is not set.")
    async def get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        params = {**params, "key": self.api_key}
        timeout = httpx.Timeout(settings.api_timeout)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_body = e.response.json()
                print(f"DEBUG: YouTube Error Response: {error_body}")
                error_message = error_body.get("error", {}).get("message", "Unknown error")
                error_reason = error_body.get("error", {}).get("errors", [{}])[0].get("reason", "unknown")
                detail = f"YouTube API error ({e.response.status_code}): {error_message} (reason: {error_reason})"
            except:
                detail = f"YouTube API returned error: {e.response.status_code} - {e.response.text}"

            print(f"DEBUG: Error detail: {detail}")
            raise HTTPException(status_code=502, detail=detail)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Youtube API request failed: {str(e)}")
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="Youtube API request timed out")
    async def search_videos(self,
                            query: str,
                            max_results: int = 4,
                            region_code: Optional[str] = None,
                            relevance_language: str= "en",
                            order: str = "date") -> Dict[str, Any]:
        """Search for videos matching a query.We’ll use this for '<city> local news' style searches"""
        params: Dict[str, Any] = {
            "part": "snippet",
            "q":query,
            "type": "video",
            "maxResults": max_results,
            "order": order,
            "relevanceLanguage": relevance_language,
            # possibility to add safeSearch
        }
        if region_code:
            params["regionCode"] = region_code
        return await self.get("search", params)