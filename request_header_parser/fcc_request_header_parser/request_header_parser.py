import json


def generate_response(headers, remote_addr):
    return json.dumps(
        {
            "ipaddress": headers.get("X-Forwarded-For")
            or remote_addr,  # TODO proxy awareness
            "language": headers.get("Accept-Language"),
            "software": headers.get("User-Agent"),
        }
    )
