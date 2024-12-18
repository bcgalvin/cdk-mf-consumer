from datetime import datetime
from pathlib import Path


def get_partitioned_path(
    base_dir: Path | str,
    item_type: str,
    timestamp: datetime,
    s3_bucket: str | None = None
) -> Path | str:
    partitioned_path = (Path(base_dir) /
            f"type={item_type}" /
            f"year={timestamp.year}" /
            f"month={timestamp.month:02d}" /
            f"day={timestamp.day:02d}")
    
    if s3_bucket:
        return f"s3://{s3_bucket}/{partitioned_path}"
    return partitioned_path
