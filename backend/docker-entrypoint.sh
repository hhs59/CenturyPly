#!/bin/sh
set -eu

# Volumes are mounted at runtime, after Docker build-time ownership changes.
photobooth_data_dir="${DASHBOARD_DATA_DIR:-/app/backend/data}"
if [ "$(id -u)" = "0" ]; then
    mkdir -p "$photobooth_data_dir"
    chown appuser:appuser "$photobooth_data_dir"
    exec gosu appuser "$@"
fi
exec "$@"
