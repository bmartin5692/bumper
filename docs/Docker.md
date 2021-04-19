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

Below a docker-compose example with an nginx proxy, which redirects mqtt traffic on port `443` to port `8883`
The redirection is required as the app v2+ and robots with a newer firmware are connecting to the mqtt server on port 433.

```yaml
---
version: "3.6"

networks:
  bumper:
    internal: true
    ipam:
      config:
        - subnet: 172.19.200.0/24

services:
  nginx:
    depends_on:
      - bumper
    image: nginx:alpine
    networks:
      default:
      bumper:
    expose:
      - 443
      - 5223
      - 8007
      - 8883
    restart: unless-stopped
    volumes:
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
      - ./nginx/:/etc/nginx:ro # See config file below

  bumper:
    image: bmartin5692/bumper
    restart: unless-stopped
    networks:
      bumper:
        ipv4_address: 172.19.200.10

    environment:
      PUID: 1000
      PGID: 1000
      TZ: Europe/Rome
      BUMPER_ANNOUNCE_IP: XXX # Insert your IP
      BUMPER_LISTEN: 0.0.0.0
      # BUMPER_DEBUG: "true"
      LOG_TO_STDOUT: "true"
    volumes:
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
      - ./config:/bumper/data
      - ./certs:/bumper/certs
```

## Nginx configuration

```
error_log stderr;
pid /var/run/nginx.pid;

events { }

stream {
        map_hash_bucket_size 64;

        map $ssl_preread_server_name $internalport {
                # redirect all requests, which contain "mq" in the SNI -> MQTT
                ~^.*(mq).*\.eco(vacs|user)\.(net|com)$    8883;

                # the rest of eco(user|vacs) requests
                ~^.*\.eco(vacs|user)\.(net|com)$          443;

                # mapping default to MQTT as the bots are connecting directly to the ip without SNI
                default                                   8883;
        }

        server {
                listen 443;
                ssl_preread  on;
                # Ip must match the one configurated above in the docker-compose
                proxy_pass 172.19.200.10:$internalport;
        }

        server {
                listen 5223;
                proxy_pass 172.19.200.10:5223;
        }

        server {
                listen 8007;
                proxy_pass 172.19.200.10:8007;
        }

        server {
                listen 8883;
                proxy_pass 172.19.200.10:8883;
        }
}

```