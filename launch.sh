#!/bin/sh
gunicorn "app:server" --timeout 90 --workers 4
