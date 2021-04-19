# Creating Certs

Bumper requires specially crafted certificates to work properly.  In the spirit of security, Bumper will not ship with default certificates.  Users will need to generate and provide their own certificates.  

Certificates should be placed in the `{bumper_home}/certs` directory.  If certificates are located elsewhere [environment variables](Env_Var.md) can be set that point to their location.

Users can generate certificates in the following ways:

| Method                                            | Description                                                                                                         |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [Create_Certs](#creating-certs-using-createcerts) | ***(Preferred)*** This is a utility that has been created to assist in generating the certificates required easily. |
| [OpenSSL](#manually-create-certs-with-openssl)    | Users can manually create the same certificates as Create_Certs by utilizing OpenSSL.                               |
| [Custom CA/Self](#using-a-custom-caself)          | If a user has their own CA the certificates can be generated there and used within Bumper.                          |

**Certificate Requirements:**

* A CA Cert must be provided that can be imported into devices (phones, browsers, etc).
* Server certificate should include [SANs (Subject Alternate Names)](#subject-alternative-name) for all of the *.ecovacs, etc domains.

## Creating certs using Create_Certs

Create_Certs was created to ease creation of certificates specifically for Bumper.  Binaries are provided for Windows/Linux/OSX/RPi (ARMv5) in the Create_Certs directory.

| Binary                   | Platform             |
| ------------------------ | -------------------- |
| create_certs_linux       | Linux                |
| create_certs_osx         | macOS/x              |
| create_certs_windows.exe | Windows              |
| create_certs_rpi         | RaspberryPi (ARM v5) |

Create_Certs is written in Go which allows cross-platform compiling. If the binaries don't work on your platform, install Go. 

With Go installed you can:

* Execute the go code - `go run create_certs/src/create_certs.go` 
* Build a new binary for your platform - `go build create_certs/src/create_certs.go`

### Usage

Create_Certs will automatically create the required certificates in the directory it is executed from.  For best results change to the {bumper_home}/certs directory prior to executing, otherwise you'll need to move the certs after.

1. `cd certs`
2. Execute create_certs (using the binary fitting your platform) - `../create_certs/create_certs_{platform}`
3. The certificates are generated and should be available in the current directory (certs)

## Subject Alternative Name

The server certificate requires a number of SAN (Subject Alternative Names) be added.  Create_Certs handles this automatically by loading any SANs listed in the `create_certs/Bumper_SAN.txt` file.  If creating certificates manually via OpenSSl/Custom CA these will need to be added.

## Manually create certs with OpenSSL

I get it, you don't trust create_certs and want to do it manually.  The easiest way to create the required certs is at https://certificatetools.com/.  In fact the below OpenSSL commands come straight from that site, post creation via the GUI.

### Create a Root CA

1. Create csrconfig_ca.txt for use in later commands

***csrconfig_ca.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper CA
organizationName = Bumper
[ req_ext ]
keyUsage=critical,keyCertSign,cRLSign
basicConstraints=critical,CA:true,pathlen:1
````

1. Create certconfig_ca.txt for use in later commands

***certconfig_ca.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper CA
organizationName = Bumper
[ req_ext ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
keyUsage=critical,keyCertSign,cRLSign
basicConstraints=critical,CA:true,pathlen:1
````

1. Generate the RSA private key 
    
    `openssl genrsa -out ca.key 4096`

1. Create the CSR
    
    `openssl req -new -nodes -key ca.key -config csrconfig_ca.txt -out ca.csr`

1. Self-sign your CSR
    
    `openssl req -x509 -nodes -in ca.csr -days 1095 -key ca.key -config certconfig_ca.txt -extensions req_ext -out ca.crt`

### Create the Server Certificate

1. Create csrconfig_bumper.txt for use in later commands

***csrconfig_bumper.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper Server
organizationName = Bumper
[ req_ext ]
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth,clientAuth
basicConstraints=critical,CA:false
subjectAltName = @alt_names
[ alt_names ]
DNS.0 = ecovacs.com
DNS.1 = *.ecovacs.com
DNS.2 = ecouser.net
DNS.3 = *.ecouser.net
DNS.4 = ecovacs.net
DNS.5 = *.ecovacs.net
DNS.6 = *.ww.ecouser.net
DNS.7 = *.dc-eu.ww.ecouser.net
DNS.8 = *.dc.ww.ecouser.net
DNS.9 = *.area.ww.ecouser.net
````

1. Create certconfig_bumper.txt for use in later commands

***certconfig_bumper.txt***
````
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = Bumper Server
organizationName = Bumper
[ req_ext ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth,clientAuth
basicConstraints=critical,CA:false
subjectAltName = @alt_names
[ alt_names ]
DNS.0 = ecovacs.com
DNS.1 = *.ecovacs.com
DNS.2 = ecouser.net
DNS.3 = *.ecouser.net
DNS.4 = ecovacs.net
DNS.5 = *.ecovacs.net
DNS.6 = *.ww.ecouser.net
DNS.7 = *.dc-eu.ww.ecouser.net
DNS.8 = *.dc.ww.ecouser.net
DNS.9 = *.area.ww.ecouser.net
````

1. Generate the RSA private key
    
    `openssl genrsa -out bumper.key 4096`

1. Create the CSR

    `openssl req -new -nodes -key bumper.key -config csrconfig_bumper.txt -out bumper.csr`

1. Sign your CSR with a root CA cert
    
    `openssl x509 -req -in bumper.csr -days 365 -CA ca.crt -CAkey ca.key -extfile certconfig_bumper.txt -extensions req_ext -CAcreateserial -out bumper.crt`

## Using a Custom CA/Self

This should work siimilar to the OpenSSL method.  Ensure the server certificate has the proper [SANs](#subject-alternative-name) in place.