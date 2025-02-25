FROM ubuntu:latest
LABEL authors="jonny"

ENTRYPOINT ["top", "-b"]