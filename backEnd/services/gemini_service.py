import json
from typing import Any, Dict, List

import httpx

from backEnd.core.config import settings


class GeminiService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ):
        self.api_key = api_key if api_key is not None else settings.api_gemini_ai_key
        self.model = model or settings.gemini_model
        self.base_url = base_url.rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def generate_weather_insight(self, weather_context: Dict[str, Any]) -> Dict[str, Any] | None:
        if not self.enabled:
            return None

        prompt = self._build_prompt(weather_context)
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.25,
                "maxOutputTokens": 1200,
                "thinkingConfig": {"thinkingBudget": 0},
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "enum": ["low", "moderate", "elevated"],
                        },
                        "headline": {"type": "string"},
                        "risks": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "changes": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "actions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["severity", "headline", "risks", "changes", "actions"],
                },
            },
        }

        url = f"{self.base_url}/models/{self.model}:generateContent"
        timeout = httpx.Timeout(settings.api_timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key,
                },
                json=payload,
            )
            response.raise_for_status()

        response_payload = response.json()
        if self._finish_reason(response_payload) == "MAX_TOKENS":
            return None

        text = self._extract_text(response_payload)
        if not text:
            return None

        try:
            generated = json.loads(text)
        except json.JSONDecodeError:
            return None

        return self._normalize_insight(generated)

    def _build_prompt(self, weather_context: Dict[str, Any]) -> str:
        compact_context = {
            "place": weather_context.get("place"),
            "date": weather_context.get("date"),
            "current": weather_context.get("current"),
            "hourly_next_24h": weather_context.get("hourly", [])[:8],
            "daily": weather_context.get("daily", [])[:3],
            "rule_based_draft": weather_context.get("insight"),
        }
        return (
            "Create a concise consumer weather brief for a dashboard card. "
            "Use only the provided forecast data. Do not invent historical yesterday data; "
            "describe changes across the upcoming 24 hours instead. "
            "Return JSON only with this exact shape: "
            "{severity: low|moderate|elevated, headline: string, risks: string[], "
            "changes: string[], actions: string[]}. "
            "Use at most 3 items in each array. Keep each item under 90 characters. "
            "Actions should be simple and specific, like umbrella timing or best run window.\n\n"
            f"Weather data:\n{json.dumps(compact_context, ensure_ascii=False)}"
        )

    def _extract_text(self, payload: Dict[str, Any]) -> str:
        candidates = payload.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts") or []
        return "".join(part.get("text", "") for part in parts).strip()

    def _finish_reason(self, payload: Dict[str, Any]) -> str:
        candidates = payload.get("candidates") or []
        if not candidates:
            return ""
        return str(candidates[0].get("finishReason") or "")

    def _normalize_insight(self, value: Dict[str, Any]) -> Dict[str, Any] | None:
        severity = str(value.get("severity", "low")).lower()
        if severity not in {"low", "moderate", "elevated"}:
            severity = "low"

        headline = str(value.get("headline") or "").strip()
        risks = self._string_list(value.get("risks"))
        changes = self._string_list(value.get("changes"))
        actions = self._string_list(value.get("actions"))

        if not headline or not risks or not changes or not actions:
            return None

        return {
            "severity": severity,
            "headline": headline[:140],
            "risks": risks,
            "changes": changes,
            "actions": actions,
            "source": "gemini",
        }

    def _string_list(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        cleaned = []
        for item in value:
            text = str(item).strip()
            if text:
                cleaned.append(text[:120])
            if len(cleaned) == 3:
                break
        return cleaned
