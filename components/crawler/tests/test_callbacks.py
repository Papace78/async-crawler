from contextlib import nullcontext
from typing import Dict
from unittest.mock import MagicMock, Mock, patch

from httpx import Response
import pendulum
import pytest

from crawler.callbacks.base import CallBack
from crawler.callbacks.stopping import (
    FailurePatienceStopper,
    PublicationTimeRangeStopper,
    StopCrawlException,
    TooManyRequestStopper,
)
from crawler.core import Crawler
from crawler.videos import VideoId, VideoIdAscendingGenerator


@patch("crawler.core.Client")
def test_callbacks_are_called(client_mock: MagicMock, crawl_payload: Dict[str, Dict]) -> None:
    client = client_mock()
    client.get.return_value.json.return_value = crawl_payload

    callback = Mock(CallBack)
    crawler = Crawler(callbacks=[callback])

    crawler.crawl(VideoIdAscendingGenerator(seed=VideoId("1231"), limit=1))
    callback.after_response.assert_called_once_with(client.get.return_value)


@pytest.mark.parametrize(
    argnames=("payload", "should_raise"),
    argvalues=[
        ({"video": {"publish_date": "2023-03-01 00:00:00"}}, False),
        ({"video": {"publish_date": "2023-02-03 12:00:00"}}, False),
        ({"video": {"publish_date": "2023-01-01 00:00:00"}}, True),
        ({"video": {"publish_date": "2023-03-04 12:00:00"}}, True),
        ({"video": {"publish_date": "2023-03-03 12:00:00"}}, True),
        ({"video": {"no_date_key": "..."}}, False),
    ],
)
def test_datetime_limit_callback(payload, should_raise):
    response = Mock(Response)
    response.json.return_value = payload
    callback = PublicationTimeRangeStopper(
        start_datetime=pendulum.parse("2023-02-03T12:00:00Z"),
        end_datetime=pendulum.parse("2023-03-03T12:00:00Z"),
    )
    with pytest.raises(StopCrawlException) if should_raise else nullcontext():
        callback.after_response(response)


@pytest.mark.parametrize(
    argnames=("start", "end", "should_raise"),
    argvalues=[
        ("2023-02-02T00:00:00Z", None, False),
        ("2023-02-04T00:00:00Z", None, True),
        ("2023-02-03T00:00:00Z", None, False),
        (None, "2023-02-02T00:00:00Z", True),
        (None, "2023-02-04T00:00:00Z", False),
        (None, "2023-02-03T00:00:00Z", True),
    ],
)
def test_datetime_limit_single_sided_callback(start, end, should_raise):
    response = Mock(Response)
    response.json.return_value = {"video": {"publish_date": "2023-02-03 00:00:00"}}
    callback = PublicationTimeRangeStopper(
        start_datetime=pendulum.parse(start) if start else None,
        end_datetime=pendulum.parse(end) if end else None,
    )
    with pytest.raises(StopCrawlException) if should_raise else nullcontext():
        callback.after_response(response)


def test_failure_patience():
    callback = FailurePatienceStopper(patience=2)
    callback.increment()
    callback.reset()
    callback.increment()
    with pytest.raises(StopCrawlException):
        callback.increment()


@pytest.mark.parametrize(
    argnames=("payload", "should_raise"),
    argvalues=[
        ({}, False),
        ({"code": 2002}, False),
        ({"code": 1005}, True),
    ],
)
def test_too_many_request(payload, should_raise):
    response_class = Mock(Response)
    response = response_class()
    response.json.return_value = payload
    callback = TooManyRequestStopper()
    with pytest.raises(StopCrawlException) if should_raise else nullcontext():
        callback.after_response(response)
