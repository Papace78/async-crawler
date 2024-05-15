from typing import Dict
from unittest.mock import MagicMock, patch

from crawler.core import Crawler
from crawler.transforms import preprocess_crawl_tags, preprocess_search_tags
from crawler.videos import VideoId, VideoIdAscendingGenerator


def test_preprocess_crawl_tags():
    tags = ["Xyz", "xyz Xyz"]
    expected = ["xyz", "xyz-xyz"]
    actual = preprocess_crawl_tags(tags)
    assert actual == expected


def test_preprocess_search_tags():
    tags = [{"tag_name": "Xyz"}, {"tag_name": "Xyz Xyz"}]
    expected = ["xyz", "xyz-xyz"]
    actual = preprocess_search_tags(tags)
    assert actual == expected


@patch("crawler.core.pendulum")
@patch("crawler.core.Client")
def test_selection_crawl_preprocess(client: MagicMock, pendulum: MagicMock) -> None:
    crawl_preprocess = MagicMock()
    search_preprocess = MagicMock()
    Crawler.TAGS_PROCESSORS = {
        Crawler.SEARCH_RESOURCE: search_preprocess,
        Crawler.VIDEO_BY_ID_RESOURCE: crawl_preprocess,
    }
    crawler = Crawler()
    crawler.crawl(VideoIdAscendingGenerator(seed=VideoId("1231"), limit=1))
    search_preprocess.assert_not_called()
    crawl_preprocess.assert_called_once()


@patch("crawler.core.pendulum")
@patch("crawler.core.Client")
def test_selection_search_preprocess(
    client: MagicMock, pendulum: MagicMock, search_payload: Dict[str, Dict]
) -> None:
    crawl_preprocess = MagicMock()
    search_preprocess = MagicMock()
    client.return_value.get.return_value.json.return_value = search_payload
    Crawler.TAGS_PROCESSORS = {
        Crawler.SEARCH_RESOURCE: search_preprocess,
        Crawler.VIDEO_BY_ID_RESOURCE: crawl_preprocess,
    }
    crawler = Crawler()
    crawler.search()
    search_preprocess.assert_called()
    crawl_preprocess.assert_not_called()
