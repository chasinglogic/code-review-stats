import argparse
import os
import json
import sys
from collections import defaultdict, namedtuple
from datetime import datetime
from typing import Dict, DefaultDict, NamedTuple, List

import arrow

from lib.date_utils import *
from lib.models import *

IGNORE_EMPLOYEES = [
    "surbhikhr",
    "jacob-hughes",
    "RiccardoTonini",
    "luanampb",
]

parser = argparse.ArgumentParser(
    description="Parses the output of download_data.py into a list of reviews and their status, either 'on_time', 'late', or 'no_response'"
)
parser.add_argument(
    "-o",
    "--output-file",
    help="file to output; if omitted uses stdout",
)
parser.add_argument(
    "-tz",
    default="America/Los_Angeles",
    help="timezone to use for calculating business hours for review status",
)
args = parser.parse_args()


def transform_data(data):
    reviews: List[Review] = []
    for pr in data:
        # dict from name of login of requested reviewer -> time review should be done
        requested_reviews: Dict[str, arrow.Arrow] = {}

        # raw data transformation step
        for item in pr["timelineItems"]["nodes"]:
            # transform all datetime strings into localized arrow datetime objects
            if "createdAt" in item:
                item["createdAt"] = arrow.get(item["createdAt"]).to(args.tz)
            if "submittedAt" in item:
                item["submittedAt"] = arrow.get(item["submittedAt"]).to(args.tz)

        # computation step
        for item in pr["timelineItems"]["nodes"]:
            typename = item["__typename"]
            if typename == "ReviewRequestedEvent":
                if not "login" in item["requestedReviewer"]:
                    continue

                reviewer = item["requestedReviewer"]["login"]
                time_due = get_due_time(item["createdAt"])

                requested_reviews[reviewer] = time_due

            elif typename == "PullRequestReview":
                time = item["submittedAt"]
                reviewer = item["author"]["login"]

                if reviewer in requested_reviews:
                    time_due = requested_reviews[reviewer]

                    if time <= time_due:
                        reviews.append(
                            Review(reviewer, ReviewStatus.ON_TIME, time_due.isoformat())
                        )
                    else:
                        reviews.append(
                            Review(reviewer, ReviewStatus.LATE, time_due.isoformat())
                        )

                    requested_reviews.pop(reviewer, None)
                else:
                    # someone submitted a review even though nobody requested it
                    # we don't need to do anything in this case
                    pass

            elif typename == "ReviewRequestRemovedEvent":
                if not "login" in item["requestedReviewer"]:
                    continue

                reviewer = item["requestedReviewer"]["login"]
                time = item["createdAt"]

                if reviewer in requested_reviews:
                    time_due = requested_reviews[reviewer]

                    # request for review was removed, *but* it is already after when the review should've been completed
                    if time > time_due:
                        reviews.append(
                            Review(reviewer, ReviewStatus.LATE, time_due.isoformat())
                        )
                    # request for review was removed, before when the review should've been completed
                    else:
                        reviews.append(
                            Review(
                                reviewer, ReviewStatus.NO_RESPONSE, time_due.isoformat()
                            )
                        )

                    requested_reviews.pop(reviewer, None)
                else:
                    # unusual state we don't expect to ever happen:
                    print(
                        f"Review request removed but reviewer #{reviewer} not found",
                        file=sys.stderr,
                    )

            elif typename in ["ClosedEvent", "MergedEvent"]:
                time = item["createdAt"]

                # for every requested review when the PR is closed, see if it should've been completed yet or not
                for reviewer, time_due in requested_reviews.items():
                    if time > time_due:
                        reviews.append(
                            Review(reviewer, ReviewStatus.LATE, time_due.isoformat())
                        )
                    else:
                        reviews.append(
                            Review(
                                reviewer, ReviewStatus.NO_RESPONSE, time_due.isoformat()
                            )
                        )

            else:
                print(f"Unknown type: {typename}", file=sys.stderr)

    return [r for r in reviews if r.reviewer not in IGNORE_EMPLOYEES]


def write_transformed_file(reviews, output_filename):
    # TODO: we should handle review requests that are still open, on an open PR, without a response
    # this is slightly trickier because we may need to depend on the system time of the user to tell if the review is late
    with open(output_filename, "w") as output_file:
        output_file.write(
            json.dumps([review._asdict() for review in reviews], indent=2) + "\n"
        )


def get_file_list(directory):
    return [f for f in os.listdir(directory) if f != "transformed.json"]


backend_reviews = []
backend_data_dir = os.path.join("data", "backend")
for backend_input_file in get_file_list(backend_data_dir):
    with open(os.path.join(backend_data_dir, backend_input_file)) as fh:
        data = json.load(fh)
        backend_reviews.extend(transform_data(data))

backend_output_filename = os.path.join("data", "backend", "transformed.json")
write_transformed_file(backend_reviews, backend_output_filename)


frontend_reviews = []
frontend_data_dir = os.path.join("data", "frontend")
for frontend_input_file in get_file_list(frontend_data_dir):
    with open(os.path.join(frontend_data_dir, frontend_input_file)) as fh:
        data = json.load(fh)
        frontend_reviews.extend(transform_data(data))

frontend_output_filename = os.path.join("data", "frontend", "transformed.json")
write_transformed_file(frontend_reviews, frontend_output_filename)


ta_reviews = []
ta_data_dir = os.path.join("data", "ta")
for ta_input_file in get_file_list(ta_data_dir):
    with open(os.path.join(ta_data_dir, ta_input_file)) as fh:
        data = json.load(fh)
        ta_reviews.extend(transform_data(data))

ta_output_filename = os.path.join("data", "ta", "transformed.json")
write_transformed_file(ta_reviews, ta_output_filename)
