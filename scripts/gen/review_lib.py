"""English review text keyed by the original Google reviewer ID; originals stay intact."""
import json
from pathlib import Path

EN = json.loads((Path(__file__).parent / "rv" / "en.json").read_text())
DATES = {
    "преди месец": "a month ago",
    "преди седмица": "a week ago",
    "преди 2 седмици": "2 weeks ago",
    "преди 3 седмици": "3 weeks ago",
    "преди 4 седмици": "4 weeks ago",
    "преди 2 часа": "2 hours ago",
    **{f"преди {n} дни": f"{n} days ago" for n in (3, 4, 5, 6)},
}


def text_en(review):
    return EN[review[4]] if review[5].strip() else ""


def date_en(when):
    return DATES[when]
