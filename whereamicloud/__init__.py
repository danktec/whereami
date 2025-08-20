#!/usr/bin/env python3

import json
import sys
import urllib.request
from ping3 import ping as ping3ping
from tcppinglib import tcpping, TCPHost

__version__ = "1.2.1"
QUIET = False
LOCATION_FILE_LOCAL = "/tmp/locations.json"
LOCATION_FILE_REMOTE = "https://raw.githubusercontent.com/danktec/whereamicloud/refs/heads/main/locations.json"


def get_locations_file(location_url):
    if urllib.request.urlretrieve(location_url, LOCATION_FILE_LOCAL):
        print(f"Downloaded {LOCATION_FILE_LOCAL}...")
        return True
    else:
        print(f"Failed to fetch locations from {LOCATION_FILE_REMOTE}")
        return False


def validate_json(locations: str) -> bool:
    with open(locations) as file:
        try:
            json.load(file)
            return True
        except json.decoder.JSONDecodeError:
            print(f"Invalid JSON detected in {locations} please fix")
            return False


def find_region(dict: dict, data: str) -> str:
    for region in dict:
        for k, v in dict[region].items():
            if k == data:
                return region


def ping(ip: str, timeout: float = 0.7) -> (float, str):
    time = []
    for p in range(2):
        time.append(icmp_ping(ip=ip, timeout=timeout))

    if time[0] is not None and time[1] is not None:
        ms = (time[0] + time[1]) / 2
        ms = int("{:.0f}".format(ms))
        return ms, "ICMP"
    else:
        host = http_ping(ip, timeout=timeout)
        ms = int("{:.0f}".format(host.avg_rtt))
        return ms, "HTTP"


# If ICMP Ping fails, do an HTTP ping on port 80
def http_ping(address: str, timeout: float) -> TCPHost:
    host = tcpping(address, port=80, timeout=timeout, count=1, interval=1)
    return host


# Only supports 2x pings which are averaged.
# TODO: Use a list comprehention to elegantly calulate over a variable number of pings
def icmp_ping(ip: str, timeout: float = 0.7) -> str:
    host = ping3ping(dest_addr=ip, unit="ms", size=1, timeout=timeout)
    return host


def main():
    if get_locations_file(LOCATION_FILE_REMOTE) is False:
        sys.exit(1)
    elif validate_json(LOCATION_FILE_LOCAL) is False:
        sys.exit(1)
    else:
        try:
            f = open(LOCATION_FILE_LOCAL, "r")
            locations = json.loads(f.read())
            f.close()
        except FileNotFoundError:
            print(f"Problem loading {LOCATION_FILE_LOCAL} file")
            sys.exit(1)

    print("Starting Continental Scan...")

    # Continental location
    distances = {}
    for continent in locations:
        for city in locations[continent].items():
            for host in city[1].values():

                ms, type = ping(host)

                distances[city[0]] = ms

                if QUIET is False:
                    print(f"You are {ms}ms away from continent {continent} : using {type}")
                break
            break

    # Get the min value from the dict
    closest = min(distances, key=distances.get)

    suspected_continent = find_region(locations, closest)
    print(f"Closest continent is {suspected_continent} at {distances[closest]}ms (checked {closest})\n")
    print(f"Starting city scan inside {suspected_continent}...")

    # Now dive check cities inside continents
    distances = {}
    for region_name, cities in locations[suspected_continent].items():
        for name, ip in cities.items():

            ms, type = ping(ip)

            distances[name] = ms

            if QUIET is False:
                print(f"You are {ms}ms away from {name} in {region_name} : using {type}")

            # Only try the first node in each region
            break

        # Get the min value from the dict
        closest = min(distances, key=distances.get)

    suspected_city = find_region(locations[suspected_continent], closest)
    print(f"Closest city is {suspected_city} at {distances[closest]}ms (checked {closest})\n")

    print(f"Starting datacenter scan inside {suspected_city}")

    # Second, dive into the city and check every DC listed
    distances = {}
    for name, ip in locations[suspected_continent][suspected_city].items():

        ms, type = ping(ip=ip, timeout=1)

        distances[name] = ms

        closest = min(distances, key=distances.get)

        if QUIET is False:
            print(f"You are {ms}ms away from {name} in {suspected_city} : using {type}")

    print(f"\nThe closest node is {closest} in {suspected_city} at {distances[closest]}ms")


if __name__ == "__main__":
    main()
