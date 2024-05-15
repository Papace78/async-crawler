from typing import Any, Optional

from httpx import Response
from pendulum import DateTime
import pendulum

from crawler.callbacks.base import CallBack
from crawler.utils import get_nested


class StopCrawlException(Exception):
    """Raises when crawling must stop"""

    def __init__(self, msg: str, *args: object) -> None:
        super().__init__(*args)
        self.msg = msg


class PublicationTimeRangeStopper(CallBack):
    def __init__(
        self, start_datetime: Optional[DateTime] = None, end_datetime: Optional[DateTime] = None
    ) -> None:
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    def after_response(self, response: Response) -> None:
        payload = response.json()

        datetime_string = get_nested(payload, ["video", "publish_date"])
        if not datetime_string:
            return

        datetime = pendulum.parse(datetime_string)
        if self.start_datetime and datetime < self.start_datetime:
            raise StopCrawlException(
                f"Publish date is prior to start_datetime: "
                f"{datetime.to_iso8601_string()} < {self.start_datetime.to_iso8601_string()}"
            )
        if self.end_datetime and datetime >= self.end_datetime:
            raise StopCrawlException(
                f"Publish date is subsequent to end_datetime: "
                f"{datetime.to_iso8601_string()} >= {self.end_datetime.to_iso8601_string()}"
            )


class TooManyRequestStopper(CallBack):
    def after_response(self, response: Response) -> Any:
        payload = response.json()
        if payload.get("code") == 1005:
            raise StopCrawlException(payload.get("message", "Too many requests."))


class FailurePatienceStopper(CallBack):
    def __init__(self, patience: int = 100) -> None:
        self.patience = patience
        self.consecutive_missing = 0

    def after_response(self, response: Response) -> None:
        payload = response.json()
        if payload.get("code"):
            self.increment()
        else:
            self.reset()

    def increment(self) -> None:
        self.consecutive_missing += 1
        if self.consecutive_missing >= self.patience:
            raise StopCrawlException(f"Stopped after {self.patience} consecutive failure")

    def reset(self) -> None:
        self.consecutive_missing = 0
