Reverse engineering the protocols and default apps/APIs requires some patience and work.  I've found using a Kali Linux VM that hosts an access point with MitMProxy works well.  I followed a number of articles in order to get started, which helped in creating the below VM setup and scripts.

> References:
> 
> - https://blog.heckel.xyz/2013/07/01/how-to-use-mitmproxy-to-read-and-modify-https-traffic-of-your-phone/
> - https://docs.mitmproxy.org/stable/howto-wireshark-tls/
> - https://www.yeahhub.com/create-fake-ap-dnsmasq-hostapd-kali-linux/
> - http://www.geekmind.net/2011/01/linux-wifi-operation-not-possible-due.html

# VM Setup

**Requirements**

- Kali Linux VM
  - Bridge mode network
  - USB Wifi Dongle (used a Ralink variant)

Create three files in the same directory (/root/accesspoint):

**Start_Sniff.sh**

```bash
#!/bin/bash
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 443 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 8883 -j REDIRECT --to-port 8080
sudo nmcli radio wifi off
sudo rfkill unblock wlan
ifconfig wlan0 up 192.168.1.1 netmask 255.255.255.0
route add -net 192.168.1.0 netmask 255.255.255.0 gw 192.168.1.1

#Open in new tabs
gnome-terminal -x sh -c "SSLKEYLOGFILE="/root/sslmitmkeylog.txt" mitmweb -m transparent -w "/root/mitmout_new.txt" --tcp-hosts 192.168.1.\d+ --ssl-insecure --raw; bash"
gnome-terminal -x sh -c "dnsmasq -C /root/accesspoint/dnsmasq.conf -d; bash"
gnome-terminal -x sh -c "hostapd /root/accesspoint/hostapd.conf; bash"
```

**dnsmasq.conf**

```bash
interface=wlan0
dhcp-range=192.168.1.2,192.168.1.30,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
server=8.8.8.8
log-queries
log-dhcp
listen-address=127.0.0.1
# Set DNS settings per Bumper documentation as needed below
#address=/msg-na.ecouser.net/192.168.1.1
#address=/mq-ww.ecouser.net/192.168.1.1
```

**hostapd.conf**

```bash
interface=wlan0
driver=nl80211
ssid=bumper_mitm
hw_mode=g
channel=11
macaddr_acl=0
ignore_broadcast_ssid=0
auth_algs=1
wpa=2
wpa_passphrase=IAmNotSafe
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
wpa_group_rekey=86400
ieee80211n=1
wme_enabled=1
```

# Sniffing

Run Start_Sniff.sh to begin. Ensure the bot and apps connect via the Wifi network being sniffed.

- For API/App Interactions you should see the details in the mitmproxy window.
- For XMPP/MQTT you will need to use WireShark.
  - Ensure you point WireShark at the sslmitmkeylog file in order to decrypt any encrypted communications.


This documentation won't go into the details of reviewing the logs/traffic.  The reader will need to identify how to use WireShark etc for this.


## XMPPPeek - MITM XMPP traffic between the Android or iOS App and the Ecovacs server

###### *Stolen from the [Sucks Documentation](https://github.com/wpietri/sucks/blob/master/developing.md#mitm-xmpp-traffic-between-the-android-or-ios-app-and-the-ecovacs-server)*

XMPPPeek can also be used to man in the middle the traffic between the Android/iOS App and the Ecovacs server.

1. Download [xmpppeek](https://www.beneaththewaves.net/Software/XMPPPeek.html)
1. Create a self-signed certificate with the following command

`openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`

1. Edit xmpppeek.py and change port to 5223

1. Look at the [DNS docs](DNS_Setup.md) for information on which Ecovacs XMPP server is the right one for your Country. For example, a US user will be using `msg-na.ecouser.net`. Find and note the IP address for the server.

1. Make sure the mobile App talks to your machine instead of the server. This can be
accomplished modifying your router's DNS configuration to have the Ecovacs domain
name point to your IP.

1. Run xmppeek as follows.

`python ./xmpppeek.py <ECOVACS XMPP SERVER IP> cert.pem key.pem`

