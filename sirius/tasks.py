from celery import Celery
from pprint import pprint

from .db import get_db
from .parcels import get_jinio_parcel, get_gogoxpress_parcel


app = Celery('tasks', broker='pyamqp://guest@localhost//')


def serialize_tracking(item):
    return {
        "message": item["message"],
        "timestamp": item["timestamp"].isoformat(),
    }


@app.task
def get_parcel_status(id):
    db = get_db()
    doc = db.get(id)

    if doc is None:
        raise RuntimeError(f"Parcel with ID {id} not found.")

    if doc["courier"] == "jinio":
        parcel = get_jinio_parcel(doc["code"])
    elif doc["courier"] == "gogoxpress":
        parcel = get_gogoxpress_parcel(doc["code"])

    if "tracking" not in doc:
        doc["tracking"] = list(map(serialize_tracking, parcel["tracking"]))
        db.save(doc)
    else:
        last_saved_message = doc["tracking"][0]["message"]
        last_fetched_message = doc["tracking"][0]["message"]
        if last_saved_message != last_fetched_message:
            doc["tracking"] = list(map(serialize_tracking, parcel["tracking"]))
            db.save(doc)
