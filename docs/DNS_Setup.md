# DNS
You need to configure your router to point DNS locally to where Bumper is running.  
The easiest way is overriding the main domains used by EcoVacs using DNSMasq/PiHole, by adding address entries in a custom config.

## Custom DNSMasq Config

Typically written at /etc/dnsmasq.d/{##}-{name}.conf
    - Ex: `/etc/dnsmasq.d/02-custom.conf`

**File Contents:**
````
address=/ecouser.net/{bumper server ip}
address=/ecovacs.com/{bumper server ip}
address=/ecovacs.net/{bumper server ip}
````
**Note:** *Replace `{bumper server ip}` with your server's IP*

If using PiHole, reload FTL to apply changes:
`sudo service pihole-FTL reload`

## Manual Override

If overriding DNS for the top-level domains isn't an option, you'll need to configure your router DNS to point a number of domains used by the app/robot to the Bumper server.  

**Note:** Depending on country, your phone/robot may be using a different domain.  Most of these domains contain country-specific placeholders.  

Not all domains have been documented at this point, and this list will be updated as more are identified/seen. The preferred way to ensure Bumper works is to override the full domains as above.

  - Example: If you see `eco-{countrycode}-api.ecovacs.com` and you live in the US/North America you would use: `eco-us-api.ecovacs.com`

| Address                                 | Description                                    |
| --------------------------------------- | ---------------------------------------------- |
| `lb-{countrycode}.ecovacs.net`          | Load-balancer that is checked by the app/robot |
| `lb-{countrycode}.ecouser.net`          | Load-balancer that is checked by the app/robot |
| `lbus.ecouser.net`                      | Load-balancer that is checked by the app/robot |
| `lb{countrycode}.ecouser.net`           | Load-balancer that is checked by the app/robot |
| `eco-{countrycode}-api.ecovacs.com`     | Used for Login                                 |
| `gl-{countrycode}-api.ecovacs.com`      | Used by EcoVacs Home app                       |
| `gl-{countrycode}-openapi.ecovacs.com`  | Used by EcoVacs Home app                       |
| `portal-{countrycode}.ecouser.net`      | Used for Login and Rest API                    |
| `portal-ww.ecouser.net`                 | Used for various Rest APIs                     |
| `msg-{countrycode}.ecouser.net`         | Used for XMPP                                  |
| `msg-ww.ecouser.net`                    | Used for XMPP                                  |
| `mq-ww.ecouser.net`                     | Used for MQTT                                  |
| `mq-{countrycode}.ecouser.net`          | Used for MQTT                                  |
| `gl-{countrycode}-api.ecovacs.com`      | Used by Ecovacs Home app for API               |
| `recommender.ecovacs.com`               | Used by Ecovacs Home app                       |
| `bigdata-international.ecovacs.com`     | Telemetry/tracking                             |
| `bigdata-northamerica.ecovacs.com`      | Telemetry/tracking                             |
| `bigdata-{unknown regions}.ecovacs.com` | Telemetry/tracking                             |
