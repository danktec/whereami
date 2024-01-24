# Where Am I?
whereami is a tool which answers the question of where a system is located on Earth. Or on another planet,
or space, as long as the system can reach other systems with ICMP or HTTP.

## How does it work?
whereami uses Ping / ICMP Echo Requests and a list of KNOWN systems to approximately
infer where it must be located based on the response times of other systems.

## TLDR:
```bash
python3 -m pip install poetry
poetry build
python3 -m pip install dist/whereami-1.0.0-py2.py3-none-any.whl --force-reinstall
```

## What is the point?
Believe it or not, it can be somewhat difficult - or even impossible - to pinpoint exactly where
a system is located - even as you're using it. You usually only ever have an approximation.

There are various classic systems and techniques which can help:
* Traceroute
* Whois
* BGP Looking Glass
* DNS
* GeoIP Databases

Used together, we can get a pretty good indicator of WHERE in the world our
system is, and which networks host it, But getting a really close pinpoint is much harder. 

Generally the databases are not current and the information about physical location is variable and opaque, by design.

This is because ISP's, DataCenter Providers and Cloud Hosting Providers don't want to give away
too much information for security and privacy reasons.
They'll tell you a system is inside a region and inside an availability-zone but not which DataCenter and
certainly not any information about internal datacenter architecture.

## But why would i care?
If you're deploying distributed/connected workloads and resources in various locations, their distance in hops
matters from a performance and reliability perspective.

Generally speaking, the less distance a packet needs to travel the less it will cost and the more reliable
its journey will be.

Sure, you can put everything in a single DC or region, at the cost of performance for edge customers.
You can also garner cost savings by running selected workloads on cheaper hardware.

## So how does this tool know its own location?
It's a very simple concept, pinging out to known hosts and narrowing down to find the fastest one.

If a host is INSIDE our datacenter, then we will get the lowest possible response-time to our ping.

The real power comes from the data in locations.json. The more accurate and complete data, the better the performance
of this tool.

If the dataset of locations and pingable IP's covers every datacenter in the world, this tool can easily
determine that it's in the same DC as the fastest responding host.

## Contributing
We need to build out the locations.json file to contain as many known hosts inside datacenters as possible.

If you own a system which consistently responds to pings and you know the datacenter within which it's located, you can
add it under the appropriate region in locations.json

## locations.json File Format
This file should provide as many different providers and DC's as possible under each region for best accuracy.

locations.json
```json
{
    "[region]":
        {
            "[provider_name-dc_code]": "[pingable_address]",
            "[...]": "[...]"
        },
    "[...]": {}
}
```

## Scraped Data

Cloudping https://www.cloudping.info/ Has a list of HTTP pingable IP's which I've scraped into JSON. 
Credit to Michael Leonhard for putting this list together https://gitlab.com/leonhard-llc/cloudping.info

```bash
wget https://www.cloudping.info/ | grep -A 3 "<tr>" | grep "<td" > test.csv
```

```python3
import json
f = open("test.csv")
lines = f.readlines()
output = {}
for line in lines:
    if line.find("<td>") > 0:
        left = line.split(">")[1]
        right = left.split("<")
        region_name = right[0]
        output[region_name] = {}

    # Get the provider    
    if line.find("<b>") > 0:
        provider_name = line.split('/')[2]

    # Get the ping URL
    if line.find("pingUrl") > 0:
        ping_url = line.split("/")[2]
        output[region_name][provider_name] = ping_url


print(json.dumps(output))
```

TODO:
    * Break up the existing regions into continents to get a faster look up time.
    * Add HTTP ping
    * Add click or argparse for --verbose output and other options
    * Distribute as pip module