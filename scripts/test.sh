#! /usr/bin/env sh

./scripts/wait-for.sh postgres:5432 -- echo "postgres is up"
./scripts/wait-for.sh rabbitmq:5672 -- echo "rabbitmq is up"

cd src/services
python -m pytest