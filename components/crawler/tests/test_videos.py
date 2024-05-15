from crawler.videos import VideoId, VideoIdAscendingGenerator, VideoIdDescendingGenerator


def test_video_id_numerical_value():
    video_id = VideoId("1231")
    assert video_id.numerical_value == 123


def test_video_id_from_numerical():
    video_id = VideoId.from_numerical(123)
    assert video_id == VideoId("1231")


def test_next_video_id():
    video_id = VideoId("1231")
    assert video_id.next() == VideoId("1241")


def test_previous_video_id():
    video_id = VideoId("1231")
    assert video_id.previous() == VideoId("1221")


def test_ascending_video_id_gen():
    generator = VideoIdAscendingGenerator(seed=VideoId("1231"), limit=3)
    expected = [
        VideoId("1231"),
        VideoId("1241"),
        VideoId("1251"),
    ]
    actual = [video_id for video_id in generator]
    assert actual == expected


def test_descending_video_id_gen():
    generator = VideoIdDescendingGenerator(seed=VideoId("1231"), limit=3)
    expected = [
        VideoId("1221"),
        VideoId("1211"),
        VideoId("1201"),
    ]
    actual = [video_id for video_id in generator]
    assert actual == expected
