import asyncio
import base64
import hashlib

from httpx import AsyncClient
from rich.progress import track
from typing import List



class Thumbnail:
    """
    Examples:
        >>> thumbnail = Thumbnail(content)
        >>> thumbnail.
        content

        >>> thumbnail.base64
        str_urlsafe_b64_

        >>> thumbnail.hash
        str_unique_hash_
    """

    def __init__(self, content: bytes):
        self.content = content

    @property
    def base64(self) -> str:
        return base64.urlsafe_b64encode(self.content).decode("utf-8")

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


class aThumbnailsContent:
    """
    Args:
        max_concurrency: Maximum number of thumbnails to download at a time (default = 50)

    Example:
        >>> thumbnails_url_list = List[url_as_str]
        >>> aThumbnailsContent().download(thumbnails_url_list)
        List[content]
    """

    def __init__(self, max_concurrency: int = 50):
        self.aclient = AsyncClient()
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def aget(self, *args, **kwargs):
        async with self.semaphore:
            return await self.aclient.get(*args, **kwargs)

    async def get_contents(self, thumbnails_url_list: List[str]):
        responses = [self.aget(image) for image in thumbnails_url_list]
        awaited_responses = [
            (await response).content
            for response in track(asyncio.as_completed(responses), total=len(responses))
        ]
        return awaited_responses

    def download(self, thumbnails_url_list: List[str]) -> List[bytes]:
        return asyncio.run(self.get_contents(thumbnails_url_list))
