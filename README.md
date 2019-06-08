# Bumper 

Bumper is a standalone and self-hosted implementation of the central server used by Ecovacs vacuum robots.  Bumper allows you to have full control of your Ecovacs robots, without the robots or app talking to the Ecovacs servers and transmitting data outside of your home.

**Note:** The current master branch is unstable, and in active development.

| Master Build Status | Status                                                                 |
| ------------------- | ---------------------------------------------------------------------- |
| AppVeyor (Win32)    | ![AppVeyor](https://img.shields.io/appveyor/ci/bmartin5692/bumper.svg) |
| TravisCI (Linux)    | ![Travis (.org)](https://img.shields.io/travis/bmartin5692/bumper.svg) |

Code Test Coverage: ![Codecov](https://img.shields.io/codecov/c/github/bmartin5692/bumper.svg)

***Testing needed***
Bumper needs users to assist with testing in order to ensure compatability as bumper moves forward!  If you've tested Bumper with your bot, please open an issue with details on success or issues.

***Please note**: this software is experimental and not ready for production use. Use at your own risk.* 

## Compatibility

As work to reverse the protocols and provide a self-hosted central server is still in progress, Bumper has had limited testing.  There are a number of EcoVacs models that it hasn't been tested against.  Bumper should be compatible with most wifi-enabled robots that use either the Ecovacs Android/iOS app or the Ecovacs Home Android/iOS app, but has only been reported to work on the below:

| Model           | Protocol Used | Bumper Version Tested | EcoVacs App Tested   |
| --------------- | ------------- | --------------------- | -------------------- |
| Deebot 900/901  | MQTT          | master                | Ecovacs/Ecovacs Home |
| Deebot 600      | MQTT          | master                | Ecovacs Home         |
| Deebot Ozmo 601 | XMPP          | master                | Ecovacs              |
| Deebot Ozmo 930 | XMPP          | master                | Ecovacs              |
| Deebot M81 Pro  | XMPP          | v0.1.0                | Ecovacs              |

For more information about the protocols and how Bumper works, see the [How does it work?](docs/How_It_Works.md) page in the docs. If you test against another model and it works, please open an issue to report it.

## Why?

For fun, mostly :)

But seriously, there are a several reasons for eliminating the central server:

1. Convenience: It works without an internet connection or if Ecovacs servers are down
2. Performance: No need for messages to travel to Ecovacs server and back.
3. Security: We can completely isolate the robot from the public Internet.

## Requirements

- An Ecovacs wifi-enabled robot
- A computer on your local network to run the Bumper server
- Python 3.7 and pipenv
- A network router that has functionality for overriding DNS queries
- A client that can connect to Bumper and talk to the robot over the Ecovacs protocol.
  - The "Ecovacs" or "Ecovacs Home" Android or iOS apps can be used if configured properly. 
    - See the docs on [Using Bumper with the official Android/iOS App](docs/Use_With_App.md).
  - [Sucks](https://github.com/wpietri/sucks) can also be used, which can act as a client and control the robots via command-line.
    - See the doc on [Using Bumper with Sucks](docs/Use_With_Sucks.md)

## Quick Start Usage

 - Download bumper then run `pipenv install` to install dependencies
 - Configure your Ecovacs vacuum using the official mobile app (if you haven't done this already)
 - Configure your DNS server as described in the [DNS Setup](docs/DNS_Setup.md) doc. 
 - Start bumper - see the [Starting Bumper](#starting-bumper) section.
 - Control your robots like normal
   - [Using Bumper with the official Android/iOS App](docs/Use_With_App.md)
   - [Using Bumper with Sucks](docs/Use_With_Sucks.md)

### Starting Bumper

Bumper requires certificates to function.  If certificates aren't found it will prompt to generate them for you.

For more information on generating certificates manually, see the [Creating Certs](docs/Create_Certs.md) doc

- Start Bumper with `pipenv run python -m bumper`
  - If prompted to generate certificates choose yes or no

- Reboot your robot
	- **Note:** Some models may require removing and re-inserting the battery pack.
	- This doesn't seem to be required for models that don't have easily accessible batteries such as the 900/901.
- If your configuration is correct, the robot will connect to Bumper within about 30 seconds. Bumper will output information about the connection status. 

#### Command-Line Usage

`start_bumper.py` is a helper script that starts up Bumper for you.  It has a number of available command-line arguments that can be viewed by adding the `-h` flag.

  ````
  usage: start_bumper.py [-h] [--listen LISTEN] [--announce ANNOUNCE] [--debug]

  optional arguments:
    -h, --help           show this help message and exit
    --listen LISTEN      start serving on address
    --announce ANNOUNCE  announce address to bots on checkin
    --debug              enable debug logs
  ````

#### Environment Variables

Bumper looks for a number of Environment Variables at initialization allowing for customizing a number of settings.  For more information see the [Environment Variables](docs/Env_Var.md) doc.

## Thanks

A big thanks to the original project creator @torbjornaxelsson, without his work this project would have taken much longer to build. 

Bumper wouldn't exist without [Sucks](https://github.com/wpietri/sucks), an open source client for Ecovacs robots. Big thanks to @wpietri and contributors!

### Bumper Origins

@torbjornaxelsson created Bumper originally in 2017 and the project reached its original goal and remained in a stable, but stale state with the last commit in Dec 2017.  

Since the original release of Bumper newer bots have been released that use different protocols, and in early 2019 it was decided that @bmartin5692 would take over development moving forward.  This fork was detached and all future development of bumper will take place here.  

#### Archive

The original bumper code base has been branched off as [v0.1.0](https://github.com/bmartin5692/bumper/tree/v0.1.0) and will remain in the original state.  This branch *may* work for older models (M81 Pro, N79S, etc.), but the master branch should be tried first as it contains many changes and fixes over the original with active development moving forward.
