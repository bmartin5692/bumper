# Requirements

- An Ecovacs wifi-enabled robot
- A computer on your local network to run the Bumper server
- Python 3.7 and pipenv OR Docker
- A network router that has functionality for overriding DNS queries
- A client that can connect to Bumper and talk to the robot over the Ecovacs protocol.
  - The "Ecovacs" or "Ecovacs Home" Android or iOS apps can be used if configured properly. 
    - See the docs on [Using Bumper with the official Android/iOS App](Use_With_App.md).
  - [Sucks](https://github.com/wpietri/sucks) can also be used, which can act as a client and control the robots via command-line.
    - See the doc on [Using Bumper with Sucks](Use_With_Sucks.md)

# Quick Start Usage

 - Configure your Ecovacs vacuum using the official mobile app (if you haven't done this already)
 - Configure your DNS server as described in the [DNS Setup](DNS_Setup.md) doc. 

## Choose Installation Type

 - Docker - [See Docker Details](Docker.md)
 - Manual/Python
 	- Download bumper then run `pipenv install` to install dependencies
	- Start bumper - see the [Starting Bumper](#starting-bumper) section.

  - Control your robots like normal
  	- [Using Bumper with the official Android/iOS App](Use_With_App.md)
	- [Using Bumper with Sucks](Use_With_Sucks.md)

# Starting Bumper

Bumper requires certificates to function.  If certificates aren't found it will prompt to generate them for you.

For more information on generating certificates manually, see the [Creating Certs](Create_Certs.md) doc

- Start Bumper with `pipenv run python -m bumper`
  - If prompted to generate certificates choose yes or no

- Reboot your robot
	- **Note:** Some models may require removing and re-inserting the battery pack.
	- This doesn't seem to be required for models that don't have easily accessible batteries such as the 900/901.
- If your configuration is correct, the robot will connect to Bumper within about 30 seconds. Bumper will output information about the connection status. 

# Troubleshooting

Logs are output in the /logs directory.

If there is an issue, enable debug logging with the `--debug` switch for additional detail.