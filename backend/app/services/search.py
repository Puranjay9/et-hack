"""Search API wrapper with Redis caching."""

import json
import os
from typing import List, Dict, Any, Optional

import httpx
import redis


class SearchService:
    def __init__(self):
        self.api_key = os.getenv("SEARCH_API_KEY", "")
        self.api_url = os.getenv("SEARCH_API_URL", "https://www.searchapi.io/api/v1/search")
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self._redis = None

    @property
    def redis_client(self):
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    def search(
        self,
        query: str,
        num_results: int = 10,
        cache_ttl: int = 86400,
    ) -> List[Dict[str, Any]]:
        """Search with Redis caching (TTL 24h default)."""
        cache_key = f"search:{query}:{num_results}"

        # Check cache
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Call Search API
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    self.api_url,
                    params={
                        "engine": "google",
                        "q": query,
                        "api_key": self.api_key,
                        "num": num_results,
                    },
                )
                response.raise_for_status()
                results = response.json().get("organic_results", [])

                # Normalize results
                normalized = [
                    {
                        "title": r.get("title", ""),
                        "link": r.get("link", ""),
                        "snippet": r.get("snippet", ""),
                        "position": r.get("position", 0),
                    }
                    for r in results
                ]

                # Cache results
                self.redis_client.set(cache_key, json.dumps(normalized), ex=cache_ttl)

                return normalized

        except Exception as e:
            return []

    def search_sponsors(
        self,
        industry: str,
        event_type: str = "college event",
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Specialized search for sponsor discovery."""
        queries = [
            f"{industry} companies sponsoring {event_type}",
            f"top {industry} brands for college sponsorship",
            f"{industry} corporate sponsors events",
        ]

        all_results = []
        seen_links = set()

        for query in queries:
            results = self.search(query, num_results=num_results)
            for r in results:
                if r["link"] not in seen_links:
                    seen_links.add(r["link"])
                    all_results.append(r)

        return all_results


# Singleton instance
search_service = SearchService()
