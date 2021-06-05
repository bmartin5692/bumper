# Docker Hub

To download the image from Docker Hub you can run the following:

`docker pull bmartin5692/bumper`

[View Bumper on Docker Hub](https://hub.docker.com/r/bmartin5692/bumper)

# Build a Docker image

To build the docker image yourself you can run the following:
`docker build -t bmartin5692/bumper .`

This requires Docker 17.09 or newer, but has also been tested with podman.

# Docker usage

To run the image in docker some environment settings and port mappings are required:

**Ports Required: (-p)**

- 443 - `-p 443:443`
- 8007 - `-p 8007:8007`
- 8883 - `-p 8883:8883`
- 5223 - `-p 5223:5223`

**Environment Settings: (-e)**

`BUMPER_ANNOUNCE_IP` should be used so the actual host IP is reported to bots that checkin.
  
  - BUMPER_ANNOUNCE_IP - `-e "BUMPER_ANNOUNCE_IP=X.X.X.X"`

**Volume Settings: (-v)**

Optionally you can map existing directories for logs, data, and certs.

- data/logs/certs
- Data - `-v /home/user/bumper/data:/bumper/data`

**Full Example:**

````
docker run -it -e "BUMPER_ANNOUNCE_IP=X.X.X.X" -p 443:443 -p 8007:8007 -p 8883:8883 -p 5223:5223 -v /home/user/bumper/data:/bumper/data --name bumper bmartin5692/bumper
````

# Docker-compose

A docker-compose example can be found in the ["example" folder](https://github.com/bmartin5692/bumper/tree/master/example/docker-compose).

The docker-compose starts two services:
- bumper itself
- nginx proxy, which redirects MQTT traffic on port `443` to port `8883`

The redirection is required as the app v2+ and robots with a newer firmware are connecting to the mqtt server on port 433.
