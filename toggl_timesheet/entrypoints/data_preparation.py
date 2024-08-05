import pathlib
import dataclasses
import argparse
import logging
from toggl_timesheet.log import get_logger
import polars as pl
from datetime import timedelta

def to_timedelta(duration: str):
    h, m, s = [int(x) for x in duration.split(":")]
    delta = timedelta(hours=h, minutes=m, seconds=s)
    return delta.seconds


@dataclasses.dataclass
class Config:
    input_path: pathlib.Path
    output_path: pathlib.Path


def parse_args() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", "-i", type=str, required=True, help="path to the deltalake DWH")
    parser.add_argument("--output-path", "-o", type=str, default="./data/silver", help="path to the deltalake DWH")
    parsed = parser.parse_args()
    return Config(input_path=pathlib.Path(parsed.input_path), output_path=pathlib.Path(parsed.output_path))


def run(logger: logging.Logger) -> None:
    config = parse_args()
    config.output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pl.read_csv(config.input_path, has_header=True)
    # df = df.select([pl.col("Project"), pl.col("Description"), pl.col("Start date"), pl.col("Duration")]) 
    df = df.with_columns(pl.col("Start date").str.to_date())
    # df = df.with_columns(pl.col("Duration").map_elements(lambda x: to_timedelta(x), int).alias("timedelta"))
    df = df.group_by(pl.col("Start date")).agg(pl.col("Description").unique().alias("Descriptions"))
    df = df.with_columns(Descriptions=pl.col("Descriptions").list.join(", ").alias("Descriptions")).sort(["Start date"])
    df.write_csv(config.output_path, quote_style="always")



if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    logger = get_logger("GET_RAW_DATA", logging.INFO)
    run(logger)
