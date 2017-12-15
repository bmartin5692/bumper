Bumper
=====

A standalone implementation of the central server used by Ecovacs
Deebot cleaning robots to relay data between the robot and client.

Tested on Ecovacs Deebot M81 Pro but should be compatible with
most wifi-enabled robots that use the Ecovacs Android app.

*Please note: this software is experimental and not ready
for production use. Use at your own risk.*


## Why?

For fun, mostly :)

But seriously, there are a serveral reasons for
elminating the central server:

1. Convenience: It works without an internet connection or if
Ecovacs servers are down
2. Performance: No need for messages to travel to Ecovacs server
and back.
3. Security: We can completely isolate the robot from the public
Internet.


## Requirements

- An Ecovacs wifi-enabled robot
- A computer on your local network to run the Bumper server 
- Python 3 and pipenv
- A network router that has functionality for overriding DNS queries
- A client that can connect to Bumper and talk to the robot over the
Ecovacs protocol.
I recomend [Sucks](https://github.com/wpietri/sucks).
It can run on the same computer and requires only minimal modification
to work with Bumper.


## Usage

- Run `pipenv install` to install dependencies

- Configure your Ecovacs vacuum using the official mobile app
(if you haven't done this already)

- Configure your router DNS to point the domain lbo.ecovacs.net to
the machine that will run the Bumper server

- Start Bumper with `pipenv run python bumper.py`

- Reboot your robot (remove and re-insert the battery pack,
then power it on)

- If your configuration is correct, the robot will connect to Bumper
within about 30 seconds. Bumper will output informaiton about the
connection status.

- Configure your client - see below.


## Using with Sucks

Instructions (verified to work with Sucks 0.8.3)

- Download and install [Sucks](https://github.com/wpietri/sucks)
- See the [example script](examples/sucks.py) for how to connect


## Using with the official Android/iOS App

Bumper *can* be used with the official app, but with limitations. Your
phone needs to use your DNS server with custom settings, and the app
authenticates via Ecovacs central servers every time you start it.

- Configure your DNS server to point the domains msg-na.ecouser.net and
msg-ww.ecouser.net to the machine running Bumpy. Note: Depending on
country, your phone may be using a different domain.

- Login to the app. It will authenticate and ask for a list of robots
from Ecovacs central servers.

- The app will now connect to Bumper and try to ping the robot. Bumper
responds to this ping to tell the app that the robot is online.

- You should now be able to control the robot from the app.


## How does it work?

Ecovacs robots communicate over the XMPP (jabber) protocol. Messages
are relayed by a central XMPP server.

Bumper exposes a simulated XMPP server that implements the nessecary
functions for relaying messages between a robot and a client.

When the robot boots up it sends a HTTP request to lbo.ecovacs.net:8007
asking for the IP address and port of the XMPP server. Because of our
DNS override, this request will be received by Bumper. We tell the robot
to connect over XMPP to our local machine. Voilá!


## Thanks

Bumper woulden't exist without [Sucks](https://github.com/wpietri/sucks),
an open source client for Ecovacs robots. Big thanks to @wpietri and
contributors!