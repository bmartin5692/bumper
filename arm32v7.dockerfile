FROM alpine as builder

# Download QEMU, see https://github.com/docker/hub-feedback/issues/1261
ENV QEMU_URL https://github.com/balena-io/qemu/releases/download/v3.0.0%2Bresin/qemu-3.0.0+resin-arm.tar.gz
RUN apk add curl && curl -L ${QEMU_URL} | tar zxvf - -C . --strip-components 1

FROM arm32v7/python:3.7-alpine as base

# Add QEMU
COPY --from=builder qemu-arm-static /usr/bin

FROM base as builder

# add build utils (gcc, others)
RUN apk add build-base

FROM base

COPY . /bumper

WORKDIR /bumper

# install required python packages
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-m", "bumper"]
