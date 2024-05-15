from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoId:
    """
    The id of a xyz video is a string of digits, such as 103904751.
    It was noticed that the newer videos id (~2021 and on) all end with "1".
    Their id thus increment in decimals rather than units.

    When calling .get xyz api, we need the full id, ending with a "1".
    When calling successive GET, we need to increment the id decimal by decimal, removing the last "1".

    Examples:

        >>> video_id = VideoId("1231")
        >>> video_id.
        "1231"

        >>> video_id.numerical_value
        123

        >>> video_id.next().numerical_value
        124
    """

    id: str

    @property
    def numerical_value(self) -> int:
        return int(self.id) // 10

    @classmethod
    def from_numerical(cls, value: int) -> "VideoId":
        return cls(f"{value}1")

    def next(self) -> "VideoId":
        return VideoId.from_numerical(self.numerical_value + 1)

    def previous(self) -> "VideoId":
        return VideoId.from_numerical(self.numerical_value - 1)

    def __str__(self):
        return self.id

    def __eq__(self, other) -> bool:
        return self.id == other.id


class VideoIdGenerator:
    """Abstract base class for video id generation. Should act as a generator of `VideoIdGenerator`"""
    def __next__(self) -> VideoId: ...
    def __iter__(self) -> "VideoIdGenerator":
        return self


class VideoIdAscendingGenerator(VideoIdGenerator):
    """
    Monotonic VideoIdGenerator generating incremental VideoId

    Args:
        seed: The seed VideoId to start incrementing from (included)
        limit: The maximum number of id to generate. If None, generator will indefinitely increment.

    Examples:

        >>> [video_id.id for video_id in VideoIdAscendingGenerator(seed=VideoId("1231"), limit=3)]
        ["1231", "1241", "1251"]

        >>> [video_id.numerical_value for video_id in VideoIdAscendingGenerator(seed=VideoId("1231"), limit=3)]
        [123, 124, 125]

    """
    def __init__(self, seed: VideoId, limit: Optional[int] = None) -> None:
        self.limit = limit
        self.count = 0
        self.seed = seed
        self.current_id = self.seed

    def __next__(self):
        if self.limit and self.count >= self.limit:
            raise StopIteration(f"Reached max number of VideoId to generate: {self.limit}")

        video_id = VideoId.from_numerical(self.seed.numerical_value + self.count)
        self.count += 1
        return video_id

    def __len__(self):
        return self.limit


class VideoIdDescendingGenerator(VideoIdAscendingGenerator):
    """
    Monotonic VideoIdGenerator generating decremental VideoId

    Args:
        seed: The seed VideoId to start incrementing from (excluded)
        limit: The maximum number of id to generate. If None, generator will indefinitely decrement.

    Examples:

        >>> [video_id.id for video_id in VideoIdAscendingGenerator(seed=VideoId("1231"), limit=3)]
        ["1221", "1211", "1201"]

        >>> [video_id.numerical_value for video_id in VideoIdAscendingGenerator(seed=VideoId("1231"), limit=3)]
        [122, 121, 120]

    """
    def __next__(self):
        if self.limit and self.count >= self.limit:
            raise StopIteration(f"Reached max number of VideoId to generate: {self.limit}")

        self.count += 1
        video_id = VideoId.from_numerical(self.seed.numerical_value - self.count)
        return video_id
