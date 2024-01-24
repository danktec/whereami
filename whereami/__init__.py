#!/usr/bin/env python3

import json
import sys
from ping3 import ping, verbose_ping
from tcppinglib import tcpping

__version__ = "1.0.0"
QUIET = False

def find_region(dict, data):
    for region in dict:
        for k, v in dict[region].items():
            if k == data:
                return region

# If ICMP Ping fails, do an HTTP ping on port 80
def http_ping(address):
    host = tcpping(address, port=80, timeout=1, count=1, interval=1)
    return host

# Only supports 2x pings which are averaged.
# TODO: Use a list comprehention to elegantly calulate over a variable number of pings
def icmp_ping(ip, timeout=0.7):
    time = []
    for p in range(2):
        time.append(ping(dest_addr=ip, unit="ms", size=1, timeout=timeout))

    if time[0] != None and time[1] != None:
        ms = (time[0] + time[1]) / 2
        ms = int("{:.0f}".format(ms))
        return ms, "ICMP"
    else:
        host = http_ping(ip)
        ms = int("{:.0f}".format(host.avg_rtt))
        return ms, "HTTP"

def main():
    try:
        f = open("./locations.json", "r")
        locations = json.loads(f.read())
        f.close()
    except FileNotFoundError as ex:
        print("Problem loading locations.json file")
        sys.exit(1)

    print("Starting Continental Scan...")

    # Contenental location
    distances = {}
    for continent in locations:
        for city in locations[continent].items():
            for host in city[1].values():

                ms, type = icmp_ping(host)

                distances[city[0]] = ms

                if QUIET == False:
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

            ms, type = icmp_ping(ip)

            distances[name] = ms

            if QUIET == False:
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

        ms, type = icmp_ping(ip=ip, timeout=1)

        distances[name] = ms

        closest = min(distances, key=distances.get)

        if QUIET == False:
            print(f"You are {ms}ms away from {name} in {suspected_city} : using {type}")

    suspected_region = find_region(locations, closest)
    print(f"The closest node is {closest} in {suspected_city} at {distances[closest]}ms")

if __name__ == "__main__":
    main()
