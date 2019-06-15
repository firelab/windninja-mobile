import argparse
import os
import uuid
from datetime import datetime
import pytz
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="action to perform", choices=["create", "expire", "delete", "update"])
    # create requires
    parser.add_argument("--expires", help="the expires date - format YYYY-MM-DDTHH:MM", type=lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%M"), default="1111-1-1")
    parser.add_argument("--zone", help="the expires date time zone", choices=["GMT", "EST", "CST", "MST", "PST", "AKST"], default="GMT")
    parser.add_argument("--message", help="the notification message", default="server message to application users")
    args = parser.parse_args()

    if args.action.lower() != "create":
        print ("{0} is not yet implemented".format(args.action))
        return 

    if args.zone == "GMT":
        tz = pytz.utc
    elif args.zone == "EST":
        tz = pytz.timezone("US/Eastern")
    elif args.zone == "CST":
        tz = pytz.timezone("US/Central")
    elif args.zone == "MST":
        tz = pytz.timezone("US/Mountain")
    elif args.zone == "PST":
        tz = pytz.timezone("US/Pacific")

    expires = tz.localize(args.expires)

    id = str(uuid.uuid4())
    notification = {
        "id": id,
        "expires": expires.astimezone(pytz.utc).isoformat(),
        "message": args.message
    }

    filename = "{0}.json".format(id)
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

    with open(path, "w+") as f:
        json.dump(notification, f, indent=2, sort_keys=False)

    print("Notification file created: {}".format(path))

if __name__ == '__main__':
    main()