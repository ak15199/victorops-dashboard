import sys

from flask import Flask, render_template, jsonify
import pendulum
import re
from tabulate import tabulate

import logfactory
from session import Http
from secrets import Secrets



API_URL = "https://api.victorops.com/api-public/v1/incidents"
MAPPINGS = {
    "second": "sec",
    "minute": "min",
    "hour": "hr",
    "week": "wk",
    "month": "mon",
}

app = Flask(__name__, template_folder="../../static/templates", static_folder="static")
secrets = Secrets()
http = Http(secrets)
logger = logfactory.create(__name__)


def _humanize(begin=0, end=0):
    if begin and end:
        diff = begin.diff_for_humans(end, True)
        for old, new in MAPPINGS.items():
            diff = diff.replace(old, new)
    else:
        diff = ""
        begin = pendulum.now()
        end = pendulum.now()

    return {
            "value": str(begin.diff(end).in_seconds()).zfill(10),
            "string": diff
            }


def _readable_age(datetime):
    dt = pendulum.parse(datetime)

    return _humanize(dt, pendulum.now())


def _action_time(transitions, action):
    for transition in transitions:
        if transition["name"] == action:
            return transition["at"]

    raise KeyError


def _time_to_action(start, transitions, action):
    try:
        begin = pendulum.parse(start)
        end = pendulum.parse(_action_time(transitions, action))

        return _humanize(begin, end)
    except KeyError:
        return _humanize()


def _gather():
    critical = 0
    acked = 0

    incidents = http.get(API_URL, "incidents")
    for incident in incidents:
        transitions = incident["transitions"]
        start_time = incident["startTime"]

        # generate tallies
        if incident["entityState"] == "CRITICAL":
            critical += 1

        if incident["currentPhase"] == "ACKED":
            acked += 1

        # comma separate item lists
        for delist in ("pagedTeams", "pagedUsers"):
            incident[delist] = ", ".join((incident[delist]))

        # get rid of columns we don't care about
        for purge in ("host", "lastAlertTime", "lastAlertId", "entityDisplayName",
                "transitions", "entityId", "entityType", "pagedPolicies", "startTime"):
            incident.pop(purge, None)

        # add relative intervals for date columns. we'll purge hidden values in js
        incident["Age"] = _readable_age(start_time)

        # misc changes for formatting
        try:
            incident["routingKey"] = incident["routingKey"].replace("routing", "")
        except KeyError:
            incident["routingKey"] = ""


        # make headings prettier
        for key in list(incident.keys()):
            new_key = re.sub("([a-z])([A-Z])","\g<1> \g<2>", key).title().strip()
            incident[new_key] = incident.pop(key)

        # add synthetic columns
        incident["TTA"] = _time_to_action(start_time, transitions, "ACKED")
        incident["TTR"] = _time_to_action(start_time, transitions, "RESOLVED")

    logger.debug("    Done")
    return {
        "incidents": sorted(incidents, key=lambda e: e["Incident Number"]),
        "critical": critical,
        "acked": acked,
        }


@app.route("/incidents.json")
def incidents():
    logger.debug("GET /incidents.json")

    data = _gather()

    return jsonify(data)


@app.route("/")
def root():
    logger.debug("GET /")

    return render_template("incidents.html")


if __name__ == "__main__":

    logger.debug("Starting...")
    app.debug = True
    app.run(host="0.0.0.0", port=8080)
