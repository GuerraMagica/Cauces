FROM ubuntu:24.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates curl cmake ninja-build g++ libssl-dev python3 \
    g++-mingw-w64-x86-64-posix && rm -rf /var/lib/apt/lists/*
WORKDIR /work
