#!/usr/bin/env bash

uvicorn main:app \
    --port=54321 \
    --host=0.0.0.0 \
    --reload \
