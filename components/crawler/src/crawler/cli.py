import asyncio
import typer
import rich
import pandas as pd
import pendulum

from crawler.callbacks.stopping import (
    PublicationTimeRangeStopper,
    TooManyRequestStopper,
    FailurePatienceStopper,
)
from crawler.core import Crawler, AsyncCrawler
from crawler.videos import VideoId, VideoIdAscendingGenerator, VideoIdDescendingGenerator


app = typer.Typer(add_completion=False)


@app.command()
def crawl(
    offset: str = typer.Option(
        ...,
        "-o",
        "--offset",
        help="Reference id to start search from or to end search at, eg.: 102779211.",
    ),
    n_videos: int = typer.Option(1, "-n", "--n-videos", help="Number of id to search."),
    since: str = typer.Option(None, help="Minimum publication datetime of video."),
    until: str = typer.Option(None, help="Maximum publication datetime of video."),
    ascending: bool = typer.Option(
        True,
        "--ascending/--descending",
        help="Crawling order: starting offset --ascending by default / from offset --descending to be specified.",
    ),
    output: str = typer.Option(None, help="Output location to dump results."),
    failure_patience: int = typer.Option(
        500, help="How many consecutive failures trigger crawling stop."
    ),
):
    """Crawl xyz API by id"""
    start_datetime = pendulum.parse(since) if since else None
    end_datetime = pendulum.parse(until) if until else None

    callbacks = [
        TooManyRequestStopper(),
        FailurePatienceStopper(patience=failure_patience),
        PublicationTimeRangeStopper(start_datetime=start_datetime, end_datetime=end_datetime),
    ]

    generator_class = VideoIdAscendingGenerator if ascending else VideoIdDescendingGenerator
    id_generator = generator_class(seed=VideoId(offset), limit=n_videos)

    crawler = Crawler(callbacks=callbacks)
    results = crawler.crawl(id_generator=id_generator)

    if output:
        df = pd.DataFrame.from_records(results)
        df.to_parquet(output)

    else:
        rich.print(results)


@app.command()
def search(
    n_pages: int = typer.Option(1, "-n", "--n-pages", help="Number of pages to search."),
    output: str = typer.Option(None, help="Output location to dump results."),
):
    """Search xyz API by n_pages"""
    crawler = Crawler()
    results = crawler.search(n_pages=n_pages)

    if output:
        df = pd.DataFrame.from_records(results)
        df.to_parquet(output)

    else:
        rich.print(results)


@app.command()
def get(video_id: str):
    crawler = Crawler()
    payload = crawler.get_video(video_id=video_id)
    rich.print(payload)


@app.command()
def crawl_async(
    offset: str = typer.Option(
        ...,
        "-o",
        "--offset",
        help="Reference id to start search from or to end search at, eg.: 102779211.",
    ),
    n_videos: int = typer.Option(1, "-n", "--n-videos", help="Number of id to search."),
    ascending: bool = typer.Option(
        True,
        "--ascending/--descending",
        help="Crawling order: starting offset --ascending by default / from offset --descending to be specified.",
    ),
    output: str = typer.Option(None, help="Output location to dump results."),
    max_concurrency: int = typer.Option(50, help="Maximum concurrent requests."),
):
    """Crawl xyz API by id asynchronously"""

    generator_class = VideoIdAscendingGenerator if ascending else VideoIdDescendingGenerator
    id_generator = generator_class(seed=VideoId(offset), limit=n_videos)

    crawler = AsyncCrawler(max_concurrency=max_concurrency)
    results = asyncio.run(crawler.crawl(id_generator=id_generator))

    if output:
        df = pd.DataFrame.from_records(results)
        df.to_parquet(output)

    else:
        rich.print(results)


@app.command()
def search_async(
    n_pages: int = typer.Option(1, "-n", "--n-pages", help="Number of pages to search."),
    output: str = typer.Option(None, help="Output location to dump results."),
    max_concurrency: int = typer.Option(50, help="Maximum concurrent requests."),
):
    """Search xyz API by n_pages asynchonously"""
    crawler = AsyncCrawler(max_concurrency=max_concurrency)
    results = asyncio.run(crawler.search(n_pages=n_pages))

    if output:
        df = pd.DataFrame.from_records(results)
        df.to_parquet(output)

    else:
        rich.print(results)
