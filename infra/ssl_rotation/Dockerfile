FROM debian:10
COPY ./automatic-sll-renewal /app/automatic-sll-renewal
COPY ./env /app/env
RUN apt update && apt install -y curl cron