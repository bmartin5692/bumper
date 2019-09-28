# How does Bumper work? 

![Bumper Diagram](./images/BumperDiagram.png "Bumper Diagram")

Bumper runs multiple services to re-create what the central EcoVacs servers provide the bots and users. At this point two different protocols have been seen, **XMPP** and **MQTT**.

**Services**

| Service     | Description                                      | Ports        | Source File     |
| ----------- | ------------------------------------------------ | ------------ | --------------- |
| Web Servers | Provide authentication and for MQTT bots command | 443 and 8007 | `confserver.py` |
| XMPP Server | For bots that utilize this protocol              | 5223         | `xmppserver.py` |
| MQTT Server | For bots that utilize this protocol              | 8883         | `mqttserver.py` |

**App/Authentication**

EcoVacs servers provide authentication of accounts and match those up to registered robots.  Once authenticated, users can control the robots via the app.  ***Bumper*** provides an implementation of the central servers providing authentication and matching.

**Robots**

So far two protocols have been identified that various models of EcoVacs robots use: **XMPP** and **MQTT**.  These appear to be mutually exclusive and your robot model will use one of these two protocols for communication.  ***Bumper*** provides an implementation of both protocols handling communication between the app and robots.

----

### Login/Authentication/RestAPI

***Bumper*** provides a fully simulated central server that handles login/authentication for the app/clients.  

The EcoVacs app encrypts the username/password with the public key of EcoVacs when authenticating.  Since we don't have the private key to decrypt, there is no way to provide true security and authentication.

Future versions may add additional options here for security.

Bots have no authentication and once a robot has been configured to access your WiFi it never needs to communicate with EcoVac's servers again.

----

### XMPP

*Example Model:* Ozmo 601/930

The robot utilizes XMPP for control.  When the robot boots up it sends a HTTP request to `lbo.ecovacs.net:8007` asking for the IP address and port of the XMPP server. Because of our DNS override, this request will be received by Bumper. We tell the robot to connect over XMPP to our local machine.

Both the app and robot connect to the central XMPP server, which relays messages between the app and robot.  The messages contain commands for the robot to execute or responses and statuses of the robot. 

***Bumper*** exposes a simulated XMPP server that implements the necessary functions for relaying messages between a robot and a client, acting as the central server.

**Note:** It's been observed that the apps will attempt to utilize XMPP regardless of robot model.  For models that utilize MQTT, no activity is performed over XMPP just pings.

----

### MQTT

*Example Model:* Deebot 600/900/901

The robot utilizes MQTT for control.  On startup it connects to an MQTT broker (`mq-{countrycode}.ecovacs.com`) and subscribes to a `p2p` topic where commands are issued.  
The app also connects to the MQTT broker and subscribes to a `attr` topic where the robot will periodically post status and location updates.

The app receives status updates, for example battery status or robot position information, periodically via the `attr` topic.

However, commands issued via the app/client are not published directly to the `p2p` topic that the robot subscribes to.  When the app sends a command such as "Clean", this is sent via a Rest API to the server at `portal-{countrycode}.ecouser.net`.

The Rest API provided by `portal-{countrycode}.ecouser.net` receives the command and passes it to a "helper" bot that has permission to publish to the `p2p` topic the robot is subscribed to.  The "helper" bot waits for a response to be published by the robot and then passes that response back to the server for the Rest API to send back as a response.

***Bumper*** provides a simulated RestAPI and "helper" bot, performing the same function as the central server above.
