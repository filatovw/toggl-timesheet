import dataclasses
import argparse
import logging
from toggl_timesheet.log import get_logger


@dataclasses.dataclass
class Config:
    year: int
    month: int


def parse_args() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", "-y", type=int, required=True, help="Year")
    parser.add_argument("--month", "-m", type=int, required=True, help="Month")
    parsed = parser.parse_args()
    return Config(parsed.year, parsed.month)


def run(logger: logging.Logger) -> None:
    pass


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    logger = get_logger("GET_RAW_DATA", logging.INFO)
    run(logger)
