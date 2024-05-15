from pathlib import Path
import json

import pytest


@pytest.fixture
def search_payload():
    with open(Path(__file__).parent / "resources" / "payload_search.json") as f:
        return json.load(f)


@pytest.fixture
def crawl_payload():
    with open(Path(__file__).parent / "resources" / "payload_crawl.json") as f:
        return json.load(f)
