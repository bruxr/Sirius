from celery import Celery
from celery.schedules import crontab
from pprint import pprint

from .db import get_db
from .parcels import get_jinio_parcel, get_gogoxpress_parcel


app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        update_parcels.s(),
    )


@app.task
def update_parcels():
    db = get_db()
    parcels = db.find({
        "selector": {
            "kind": "PARCEL",
            "delivered": {"$exists": False},
        },
        "fields": ["_id"],
    })
    parcels = list(parcels)

    for doc in parcels:
        update_parcel_status.delay(doc["_id"])


def serialize_tracking(item):
    return {
        "message": item["message"],
        "timestamp": item["timestamp"].isoformat(),
    }


@app.task
def update_parcel_status(id):
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
