#!/bin/sh
gunicorn "app:server" --timeout 60 --workers 4
