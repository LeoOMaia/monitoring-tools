import datetime

# import json
# import sys

import pybgpstream

RIPE_RIS = [
    "rrc00",
    "rrc01",
    "rrc03",
    "rrc04",
    "rrc05",
    "rrc06",
    "rrc07",
    "rrc10",
    "rrc11",
    "rrc12",
    "rrc13",
    "rrc14",
    "rrc15",
    "rrc16",
    "rrc17",
    "rrc18",
    "rrc19",
    "rrc20",
    "rrc21",
    "rrc22",
    "rrc23",
    "rrc24",
    "rrc25",
    "rrc26",
]
ROUTE_VIEWS = [
    "route-views.amsix",
    "route-views.bknix",
    "route-views.chicago",
    "route-views.chile",
    "route-views.eqix",
    "route-views.flix",
    "route-views.fortaleza",
    "route-views.gixa",
    "route-views.gorex",
    "route-views.isc",
    "route-views.kixp",
    "route-views.linx",
    "route-views.mwix",
    "route-views.napafrica",
    "route-views.nwax",
    "route-views.ny",
    "route-views.perth",
    "route-views.phoix",
    "route-views.peru",
    "route-views.rio",
    "route-views.sfmix",
    "route-views.sg",
    "route-views.soxrs",
    "route-views.sydney",
    "route-views.telxatl",
    "route-views.uaeix",
    "route-views.wide",
    "route-views2",
    "route-views2.saopaulo",
    "route-views3",
    "route-views4",
    "route-views5",
    "route-views6",
]


def parse_line_string_to_json(input_string):
    line_data = input_string.split("|")

    # Create a dictionary with the desired JSON structure
    json_data = {
        "record_type": line_data[0],
        "type": line_data[1],
        "timestamp": float(line_data[2]),
        "project": line_data[3],
        "collector": line_data[4],
        "router": line_data[5] if line_data[5] else None,
        "router_ip": line_data[6] if line_data[6] else None,
        "peer_asn": int(line_data[7]),
        "peer_address": line_data[8],
        "prefix": line_data[9],
        "next-hop": line_data[10],
        "as-path": line_data[11].split(),
        "communities": line_data[12].split(),
        "old-state": line_data[13] if line_data[13] else None,
        "new-state": line_data[14] if line_data[14] else None,
    }

    return json_data


def datetime_str_to_timestamp(datetime_str):
    """Convert a datetime string in ISO 8601 format to a Unix timestamp.

    Args:
        datetime_str (str): Datetime string in ISO 8601 format.

    Returns:
        int: Unix timestamp.
    """
    utc_datetime = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc)
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    delta = utc_datetime - epoch
    timestamp = delta.total_seconds()
    return int(timestamp)


def download_bgpstream(
    collectors=["rrc00"],
    start_time="2023-04-26T15:38:23.449190Z",
    end_time="2023-05-04T14:08:23.504529Z",
    prefixes=["138.185.229.0/24"],
    record_type="ribs",
):
    """Return a list of BGPStream objects for a given time interval, collector, prefix and record type.

    Args:
        collectors (List(str)): Names of the BGP collectors.
        start_time (str): Start time of the interval in ISO 8601 format.
        end_time (str): End time of the interval in ISO 8601 format.
        prefix (List)): List of prefixes to filter the BGP updates.
        record_type (str): Type of BGP updates to read - 'ribs' or 'updates'.

    Returns:
        A list of BGPStream objects configured with the given parameters.
    """
    FILTER = "prefix more {}"

    start_time = datetime_str_to_timestamp(start_time)
    end_time = datetime_str_to_timestamp(end_time)

    filter_string = "ipversion 4"
    for pfx in prefixes:
        filter_string += f" and {FILTER.format(pfx)}"

    stream = pybgpstream.BGPStream(
        from_time=start_time,
        until_time=end_time,
        filter=filter_string,
        record_type=record_type,
        collectors=collectors,
    )

    elem_list = []
    for elem in stream:
        elem_list.append(parse_line_string_to_json(str(elem).replace('"', '"')))

    return elem_list
