import json
from ping3 import ping, verbose_ping

# Because we cannot ping every host we must group them by region.
# Hit one IP in each region, take the fastest of those and start drilling in there.
# As the list grows, the group nesting can grow also to keep runtime low

# Get the region after finding the fastest ip
def find_region(dict, data):
    for region in dict:
        for k, v in dict[region].items():
            if k == data:
                return region

# Only supports 2x pings which are averaged.
# TODO: Use a list comprehention to elegantly calulate over a variable number of pings
def do_ping(ip, timeout=0.7):
    time = []
    for p in range(2):
        time.append(ping(dest_addr=ip, unit="ms", size=1, timeout=timeout))

    if time[0] != None and time[1] != None:
        ms = (time[0] + time[1]) / 2
        ms = int("{:.0f}".format(ms))
        return ms
    else:
        print(f"No response from {ip}")
        return False

def main():
    # https://doc.octoperf.com/runtime/aws/
    f = open("./locations.json", "r")
    locations = json.loads(f.read())
    f.close()

    # First, check each region to find where we are
    distances = {}
    for x in locations:
        print(f"testing {x}")
        for name, ip in locations[x].items():

            ms = do_ping(ip)
            if ms == False:
                print(f"failed on {ip}")
                continue

            distances[name] = ms

            print(f"You are {ms}ms away from {name}")

            # Only try the first IP
            break

        # Get the min value from the dict
        closest = min(distances, key=distances.get)

    print(f"Closest node is {closest} at {distances[closest]}ms")

    # Second, dive into the region and check every DC
    suspected_region = find_region(locations, closest)
    print(f"Focusing on nodes inside the region: {suspected_region}")

    distances = {}
    for name, ip in locations[suspected_region].items():

        ms = do_ping(ip=ip, timeout=0.5)
        if ms == False: continue

        distances[name] = ms

        closest = min(distances, key=distances.get)

        print(f"Testing {name}")

    suspected_region = find_region(locations, closest)
    print(f"\nThe closest point to you is is {closest} in {suspected_region} at {distances[closest]}ms")

if __name__ == "__main__":
    main()
