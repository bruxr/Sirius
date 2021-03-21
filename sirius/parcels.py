import requests
from pprint import pprint
from datetime import datetime, timedelta
from dateutil.parser import parse
from bs4 import BeautifulSoup


def get_jinio_parcel(code):
    """Retrieve details about a parcel carried by Jinio"""

    url = f"https://jinio.com.ph/tracker?tracking_no={code}"
    params = {"c": "app"}
    headers = {"C_JX": "response"}
    res = requests.post(data=params, headers=headers, url=url)

    if ("Tracking No. doesn't exist!" in res.text):
        raise RuntimeError(f"Jinio parcel does not exist")

    data = {}
    for item in res.json()["c_js"]:
        if "i" in item:
            data[item["i"]] = item["c"]

    now = datetime.now()
    start_date = parse(data["estimatedFromDate"] + " " + str(now.year))
    end_date = parse(data["estimatedToDate"] + " " + str(now.year))

    if start_date > end_date:
        end_date = parse(data["estimatedToDate"] + " " + str(now.year - 1))

    result = {}
    result["start"] = start_date
    result["end"] = end_date

    result["tracking"] = []
    soup = BeautifulSoup(data["tracker_log_list"], "html.parser")
    nodes = soup.find_all("li", class_="columns")
    for node in nodes:
        date_nodes = node.find_all("div", class_="node")
        if (len(date_nodes) == 0):
            continue

        date = parse(date_nodes[0].get_text() + " " + str(now.year))
        if start_date > date:
            date = parse(date_nodes[0].get_text() + " " + str(now.year - 1))

        info_text = ": ".join(str(node).split("<br/>")[1:])
        info_text = info_text.replace("</li>", "")
        result["tracking"].append({
            "date": date,
            "message": info_text,
        })

    return result


def get_gogoxpress_parcel(code):
    """Retrieve details about a parcel carried by GoGo Xpress"""
    url = f"https://api.gogoxpress.com/v1/track/{code}"
    headers = {"Accept": "application/json"}
    res = requests.get(headers=headers, url=url)

    if res.status_code == 400:
        raise RuntimeError("GoGo Xpress parcel does not exist")

    if not res.ok:
        raise RuntimeError("GoGo Xpress API error")

    data = res.json()
    result = {}
    result["start"] = parse(data["data"]["attributes"]["created_at"])
    result["end"] = result["start"] + timedelta(days=16)

    result["tracking"] = []
    for event in data["data"]["attributes"]["events"]:
        message = event["status_name"]
        if (event["remarks"]):
            message = message + ": " + event["remarks"].replace(":", ", ")

        result["tracking"].append({
            "date": parse(event["status_updated_at"]),
            "message": message,
        })

    return result
