from datetime import UTC, datetime
from pathlib import Path

import pytest

from cdk_mf_consumer.utils import get_partitioned_path


@pytest.mark.parametrize(
    "test_id,base_dir,item_type,timestamp,s3_bucket,expected",
    [
        (
            "should_create_local_path",
            Path("data/raw"),
            "story",
            datetime(2024, 1, 15, tzinfo=UTC),
            None,
            Path("data/raw/type=story/year=2024/month=01/day=15")
        ),
        (
            "should_create_s3_path",
            Path("data/raw"),
            "comment",
            datetime(2024, 1, 15, tzinfo=UTC),
            "my-bucket",
            "s3://my-bucket/data/raw/type=comment/year=2024/month=01/day=15"
        ),
        (
            "should_handle_string_base_dir",
            "data/raw",
            "user",
            datetime(2024, 1, 15, tzinfo=UTC),
            None,
            Path("data/raw/type=user/year=2024/month=01/day=15")
        ),
        (
            "should_handle_different_months",
            Path("data/raw"),
            "story",
            datetime(2024, 12, 15, tzinfo=UTC),
            None,
            Path("data/raw/type=story/year=2024/month=12/day=15")
        ),
    ],
    ids=lambda x: x[0] if isinstance(x, tuple) else str(x)
)
def test_should_generate_partitioned_path_with_expected_format(
    test_id: str,
    base_dir: Path | str,
    item_type: str,
    timestamp: datetime,
    s3_bucket: str | None,
    expected: Path | str
) -> None:
    result = get_partitioned_path(base_dir, item_type, timestamp, s3_bucket)
    assert result == expected


def test_should_handle_single_digit_month_with_leading_zero() -> None:
    result = get_partitioned_path(
        Path("data/raw"),
        "story",
        datetime(2024, 5, 15, tzinfo=UTC)
    )
    assert "month=05" in str(result)


def test_should_handle_single_digit_day_with_leading_zero() -> None:
    result = get_partitioned_path(
        Path("data/raw"),
        "story",
        datetime(2024, 12, 5, tzinfo=UTC)
    )
    assert "day=05" in str(result)


def test_should_preserve_base_path_structure() -> None:
    base_dir = Path("my/custom/path/data")
    result = get_partitioned_path(
        base_dir,
        "story",
        datetime(2024, 1, 15, tzinfo=UTC)
    )
    assert str(result).startswith(str(base_dir))


def test_should_handle_s3_path_with_subdirectories() -> None:
    result = get_partitioned_path(
        Path("nested/data/path"),
        "story",
        datetime(2024, 1, 15, tzinfo=UTC),
        s3_bucket="my-bucket"
    )
    assert result == "s3://my-bucket/nested/data/path/type=story/year=2024/month=01/day=15"
