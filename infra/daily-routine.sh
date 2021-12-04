#!/usr/bin/env bash

# AWS machines are in UTC timezone. 8am UTC is 7pm AEDT
# crontab entry
# 00 * * * * bash /home/ubuntu/HottestTechs/infra/daily-routine.sh >> /home/ubuntu/HottestTechs/logs/crontab-daily-routine.log 2>&1 || curl -s --user 'api:YOUR_API_KEY' https://api.mailgun.net/v3/toptechs.xyz/messages -F from='Ubuntu Box <ubuntu-box@toptechs.xyz>' -F to=MY_EMAIL_ADDRESS -F subject='Critical Alarm' -F text='scapper failed'

set -euxo pipefail

spwd="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $spwd
dcx="/usr/local/bin/docker-compose"
aws="/usr/bin/aws"
doc="/usr/bin/docker"

running_now=$(docker ps | grep 'infra_scrapper' || echo "none")
echo "$running_now"

if [ "$running_now" != "none" ]; then
  exit 1
fi

$dcx -f dc-python.yml run --rm scrapper
echo "scrapper done"
$dcx -f dc-python.yml run --rm filerotator
echo "filerotator done"
cp ../scrap/hottesttechs.db ../back/hottesttechs.db
$aws s3 sync /home/ubuntu/HottestTechs/backups s3://${toptechs-s3-bucket} --delete
echo "backups done"
./run.sh prod
echo "restart done"

$doc rmi $(docker images -f "dangling=true" -q) -f
echo "cleanup done"
