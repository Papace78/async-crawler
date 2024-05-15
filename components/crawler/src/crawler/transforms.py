from typing import Dict, List


def preprocess_search_tags(tags: List[Dict[str, str]]) -> List[str]:
    return [tag["tag_name"].lower().replace(" ", "-") for tag in tags]


def preprocess_crawl_tags(tags: List[str]) -> List[str]:
    return [tag.lower().replace(" ", "-") for tag in tags]
