import typing as t
import json
import os
import argparse
import logging
from base64 import b64encode
import pathlib
from datetime import datetime, timedelta, timezone


from toggl_timesheet.log import get_logger
import requests

DATALAKE_PATH = pathlib.Path("./data")

class TogglClient:

    BASE_URL = "https://api.track.toggl.com/api"

    def __init__(self, logger: logging.Logger, token: str, session: requests.Session | None = None) -> None:
        self._logger = logger
        self._session = session
        self._headers = {
           "content-type": "application/json",
            "Authorization": "Basic {}".format(
                b64encode(f"{token}:api_token".encode()).decode("ascii"),
            ), 
        }

    @property
    def session(self) -> requests.Session:
        if not self._session:
            self._session = requests.Session()
        return self._session

    def get_organizations(self) -> dict[str, t.Any]:
        with self.session as session:
            response = session.get(self.BASE_URL + "/v9/me/organizations", headers=self._headers)
            response.raise_for_status()
            return response.json()

    def get_workspaces(self) -> dict[str, t.Any]:
        with self.session as session:
            response = session.get(self.BASE_URL + "/v9/workspaces", headers=self._headers)
            response.raise_for_status()
            return response.json()

    def get_time_entries(self, workspace_id: int, start_date: datetime, end_date: datetime) -> bytes:
        # https://engineering.toggl.com/docs/reports/detailed_reports#post-export-detailed-report-1
        # API results for Detailed Reports are paginated, returning 50 entries at a time. Several headers returned with each call are crucial for pagination:
        # X-Next-ID: ID of the next time entry.
        # X-Next-Row-Number: Row number of the next time entry.
        # For efficient pagination in a detailed report, use the value returned in the X-Next-Row-Number header as the first_row_number parameter in your subsequent request.
        date_format = "%Y-%m-%d"
        import ipdb
        with self.session as session:
            response = session.post(
                self.BASE_URL + f"v3/workspace/{workspace_id}/search/time_entries.csv",
                headers=self._headers,
                json={
                    "duration_format": "improved",
                    "grouped": False,
                    "hide_amounts": False,
                    "order_by": "date",
                    "order_dir": "ASC",
                    "page_size": 0,
                    "start_date": start_date.strftime(date_format),
                    "end_date": end_date.strftime(date_format),
                }
            )
            ipdb.set_trace()
            response.raise_for_status()
            return response.content

def get_last_day_of_month(start_date: datetime) -> datetime:
    if start_date.month == 12:
        end_date = start_date.replace(year=(start_date.year + 1), month=1)
    else:
        end_date = start_date.replace(month=start_date.month + 1) - timedelta(days=1) 

    return end_date

def run(logger: logging.Logger) -> None:
    token = os.environ["TOGGL_API_TOKEN"]
    client = TogglClient(logger, token)

    # get organization
    organizations = client.get_organizations()
    with open(DATALAKE_PATH / "organizations.json", "w") as fout:
        json.dump(organizations, fp=fout, indent=2)

    # get workspace
    workspaces = client.get_workspaces()
    with open(DATALAKE_PATH / "workspaces.json", "w") as fout:
        json.dump(workspaces, fp=fout, indent=2)

    workspace_id = [x["id"] for x in workspaces if x["admin"] is True][0]

    start_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    end_date = get_last_day_of_month(start_date)

    data = client.get_time_entries(workspace_id, start_date, end_date)
    path = [
        start_date.strftime("%Y"),
        start_date.strftime("%m"),
        "time_entries.csv"
    ]
    report_path = pathlib.Path(DATALAKE_PATH, *path)
    with open(report_path, "wb") as fout:
        fout.write(data)
    import ipdb; ipdb.set_trace()

    pass


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    logger = get_logger("GET_RAW_DATA", logging.INFO)
    run(logger)
