#!/bin/bash
SCRIPTPATH=$(dirname "$BASH_SOURCE")
OUTPUTPATH=$(dirname $(dirname "$BASH_SOURCE"))
echo "Building for Windows: $OUTPUTPATH/create_certs_windows.exe"
GOOS=windows go build -o $OUTPUTPATH/create_certs_windows.exe $SCRIPTPATH/create_certs.go
echo "Building for OSX $OUTPUTPATH/create_certs_osx"
GOOS=darwin go build -o $OUTPUTPATH/create_certs_osx $SCRIPTPATH/create_certs.go
echo "Building for Linux $OUTPUTPATH/create_certs_linux"
GOOS=linux go build -o $OUTPUTPATH/create_certs_linux $SCRIPTPATH/create_certs.go
echo "Building for ARM (Raspberry Pi) $OUTPUTPATH/create_certs_rpi"
GOOS=linux GOARCH=arm GOARM=5 go build -o $OUTPUTPATH/create_certs_rpi $SCRIPTPATH/create_certs.go
echo "Build Complete"