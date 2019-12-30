FROM python:3.7-alpine as base

FROM base as builder

# add build utils (gcc, others)
RUN apk add build-base

FROM base

COPY . /bumper

WORKDIR /bumper

# install required python packages
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-m", "bumper"]
