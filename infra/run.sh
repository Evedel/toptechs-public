#!/usr/bin/env bash

set -euxo pipefail

spwd="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $spwd

dcx="/usr/local/bin/docker-compose"

mkdir -p ../logs/nginx
mkdir -p ../logs/netdata
mkdir -p ../logs/api

touch ../logs/nginx/access.log
touch ../logs/nginx/error.log

touch ../logs/netdata/access.log
touch ../logs/netdata/error.log
touch ../logs/netdata/debug.log

touch ../logs/api/state.log
touch ../logs/api/access.log

baseimg='evedel/go-api-base'
basevrs='v1'
baseexists="$( docker images | grep $baseimg | grep $basevrs )"

if [ "$baseexists" == "" ]; then
  docker build -t "$baseimg:$basevrs" -f ../back/Dockerfile-base ../back/
fi

if [ "$1" == "dev" ]; then
  # server_addr: localhost,
  $dcx -f dc-$1.yml rm -v
  $dcx -f dc-$1.yml up --build --detach
fi

if [ "$1" == "prod" ]; then
  # server_addr: '54.66.184.25',
  perl -i -pe "s/server_addr: \"http:\/\/localhost\",/server_addr: \"https:\/\/toptechs\.xyz\",/g" ../front/script.js

  $dcx -f dc-$1.yml rm -v
  bash -c "CURRENT_UID=$(id -u):$(id -g) $dcx -f dc-$1.yml up --build -d"
fi