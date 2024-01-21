# Where Am I?
whereami is a tool which answers the question of where a system is located on Earth. Or on another planet,
or space, as long as the system can reach other systems with ICMP.

## How does it work?
whereami uses Ping / ICMP Echo Requests and a list of KNOWN systems to approximately
infer where it must be located based on the response times of other systems.

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

## So how does this tool know its own location?
It's a very simple concept, pinging out to known hosts and narrowing down to find the closest one.

If a host is INSIDE our datacenter, then we will get the lowest possible response-time to our ping.

The real power comes from the data in locations.json. The more accurate and complete data, the better the performance
of this tool.

If the dataset of locations and pingable IP's covers every datacenter in the world, this tool can easily
determine that it's in the same DC as the fastest responding host.

## Contributing
We need to build out the locations.json file to contain as many known hosts inside datacenters as possible.

If you own a system which consistently responds to pings and you know the datacenter within which it's located, you can
add it under the appropriate region in locations.json

## File Format

locations.json
```json
{
    "[region]":
        {
            "[provider_name-datacenter_name]": "[pingable_ip_address]",
            "[...]": "[...]"
        },
    "[...]": {}
}
```

TODO: standardize the provider / datacenter name format.