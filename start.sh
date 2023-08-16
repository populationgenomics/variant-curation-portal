#!/bin/bash -eu

if [ -z "${REMOTE_USER:-}" ]; then
  echo -e "\033[1;33mWarning: no REMOTE_USER set\033[0m"
fi

cd $(dirname "${BASH_SOURCE}")

export DJANGO_SETTINGS_MODULE="curation_portal.settings.development"

export NODE_ENV=development

./manage.py runserver &
DJANGO_PID=$!
echo "Django PID: $DJANGO_PID"

yarn run webpack-dev-server --hot &
WEBPACK_PID=$!
echo "Webpack PID: $WEBPACK_PID"

# Wait a few seconds for webpack-dev-server to start successfully, then start Django
echo "Waiting for webpack-dev-server to start..."
sleep 10

if [ -z "$WEBPACK_PID" ]; then
  echo -e "\033[1;31mError: webpack-dev-server failed to start\033[0m"
  pkill -P ${DJANGO_PID}
  exit 1
fi

if [ -z "$DJANGO_PID" ]; then
  echo -e "\033[1;31mError: Django failed to start\033[0m"
  kill ${WEBPACK_PID}
  exit 1
fi

echo "Success! Press Ctrl+C to stop."

trap "kill ${WEBPACK_PID}; pkill -P ${DJANGO_PID}; exit 1" INT

wait
