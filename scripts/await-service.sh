#!/usr/bin/env bash
set -euo pipefail

await_service()
{
    local start_ts=$(date +%s)
    while :
    do
        (echo -n > /dev/tcp/$1/$2) > /dev/null
        if [[ $? -eq 0 ]]; then
            break
        fi
        sleep 1
    done
    local end_ts=$(date +%s)

    echo "$1:$2 is available after $((end_ts - start_ts)) seconds"
}

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <host> <port>"
    exit 1
fi

await_service $1 $2
