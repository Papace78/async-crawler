import asyncio
import logging
from typing import Any, Dict, List, Optional

from httpx import AsyncClient, Client
from tenacity import retry, wait_exponential
from rich.progress import track
import pendulum

from crawler.callbacks.base import CallBack
from crawler.callbacks.stopping import StopCrawlException
from crawler.videos import VideoIdGenerator

from .transforms import preprocess_crawl_tags, preprocess_search_tags


class BaseCrawler:
    SEARCH_RESOURCE = "xyz.Videos.searchVideos"
    VIDEO_BY_ID_RESOURCE = "xyz.Videos.getVideoById"
    TAGS_PROCESSORS = {
        SEARCH_RESOURCE: preprocess_search_tags,
        VIDEO_BY_ID_RESOURCE: preprocess_crawl_tags,
    }

    def __init__(self, callbacks: Optional[List[CallBack]] = None, thumbsize: str = "big"):
        self.callbacks = callbacks or []
        self.thumbsize = thumbsize
        self.params = {
            "output": "json",
            "thumbsize": thumbsize,
        }

    def search(self, n_pages=1, params=None): ...

    def crawl(self, id_generator: VideoIdGenerator) -> List[Dict]: ...

    @staticmethod
    def process(video_info: dict, resource: str):
        process_tags = Crawler.TAGS_PROCESSORS[resource]
        return {
            "id": str(video_info["video_id"]),
            "published_on": pendulum.parse(video_info["publish_date"], tz="UTC").to_date_string(),
            "published_at": pendulum.parse(
                video_info["publish_date"], tz="UTC"
            ).to_iso8601_string(),
            "title": str(video_info["title"]),
            "duration": video_info["duration"],
            "views": int(video_info["views"]),
            "rating": float(video_info["rating"]),
            "ratings": int(video_info["ratings"]),
            "thumbs": [thumb["src"] for thumb in video_info["thumbs"]],
            "tags": process_tags(video_info["tags"]),
            "url": str(video_info["url"]),
        }

class Crawler(BaseCrawler):
    def __init__(self, callbacks: Optional[List[CallBack]] = None, thumbsize: str = "big"):
        BaseCrawler.__init__(self, callbacks=callbacks, thumbsize=thumbsize)
        self.client = Client(base_url="https://api.xyz.com", params=self.params)

    def search(self, n_pages=1, params=None):
        params = params or {}
        search_params = {**self.params, **params, **{"data": self.SEARCH_RESOURCE}}

        responses = []
        for page in range(1, n_pages + 1):
            search_params = {**search_params, **{"page": page}}
            responses.append(self.client.get("/", params=search_params).json())

        return [
            self.process(r["video"], resource=search_params["data"])
            for response in responses
            for r in response["videos"]
            if r.get("code") != 2002
        ]

    def crawl(self, id_generator: VideoIdGenerator) -> List[Dict]:
        crawl_params = {**self.params, **{"data": self.VIDEO_BY_ID_RESOURCE}}

        payloads = []
        for video_id in track(id_generator):
            crawl_params = {**crawl_params, **{"video_id": f"{video_id}"}}
            try:
                response = self.get("/", params=crawl_params)
            except StopCrawlException as err:
                logging.warning(err.msg)
                break

            payload = response.json()
            payloads.append(payload)

        return [
            self.process(p["video"], resource=crawl_params["data"])
            for p in payloads
            if p.get("code") != 2002
        ]

    def get(self, *args, **kwargs):
        response = self.client.get(*args, **kwargs)
        for callback in self.callbacks:
            callback.after_response(response)
        return response

    def get_video(self, video_id: str) -> Dict[str, Any]:
        params = {"video_id": video_id, "data": self.VIDEO_BY_ID_RESOURCE}
        response = self.get("/", params=params)
        payload = response.json()
        return (
            self.process(payload["video"], resource=self.VIDEO_BY_ID_RESOURCE)
            if payload.get("code") != 2002
            else payload
        )


class AsyncCrawler(BaseCrawler):
    def __init__(self, max_concurrency: int = 50, thumbsize: str = "big"):
        BaseCrawler.__init__(self, thumbsize=thumbsize)
        self.max_concurrency = max_concurrency
        self.aclient = AsyncClient(base_url="https://api.xyz.com", params=self.params)
        self.semaphore = asyncio.Semaphore(self.max_concurrency)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10))
    async def aget(self, *args, **kwargs):
        async with self.semaphore:
            return await self.aclient.get(*args, **kwargs)

    async def search(self, n_pages=1, params=None):
        params = params or {}
        search_params = {**self.params, **params, **{"data": self.SEARCH_RESOURCE}}

        responses = [
            self.aget("/", params={**search_params, **{"page": page}})
            for page in range(1, n_pages + 1)
        ]
        awaited_responses = [
            (await response).json()
            for response in track(asyncio.as_completed(responses), total=len(responses))
        ]

        return [
            self.process(r["video"], resource=search_params["data"])
            for response in awaited_responses
            for r in response["videos"]
            if r.get("code") != 2002
        ]

    async def crawl(self, id_generator: VideoIdGenerator) -> List[Dict]:
        crawl_params = {**self.params, **{"data": self.VIDEO_BY_ID_RESOURCE}}

        responses = [
            self.aget("/", params={**crawl_params, **{"video_id": f"{video_id}"}})
            for video_id in id_generator
        ]
        awaited_responses = [
            (await response).json()
            for response in track(asyncio.as_completed(responses), total=len(responses))
        ]

        return [
            self.process(r["video"], resource=crawl_params["data"])
            for r in awaited_responses
            if r.get("code") != 2002
        ]
