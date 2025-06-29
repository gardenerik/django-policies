#!/bin/bash

uv run coverage run --source=../django_policies/ ./manage.py test
uv run coverage html
